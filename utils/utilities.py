# Generic utilities to import to other modules
import logging
import mimetypes
import os
import os.path as osp
import requests
import re
import shutil
import sys

from bs4 import BeautifulSoup
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

image_ext = {"image/bmp" : "bmp",
             "image/gif" : "gif",
             "image/jpeg": "jpg",
             "image/png" : "png"}

def init_logger (level=logging.INFO) -> logging.Logger:
    ''' initialize a basic logger for the calling module. Default level is INFO '''
    logfile = Path(osp.basename(sys.argv[0])).stem
    logfile = ".".join(["-".join(["log", logfile]), "log"])

    if osp.exists(logfile):
        os.remove(logfile)

    logging.basicConfig(level=level, 
                        filename=logfile, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info(f"Initialized log file {logfile}")
    return logger

def init_dir(DIR:str) -> int:
    if osp.isdir(DIR):
        shutil.rmtree(DIR)
        logger.info(f"Removed {DIR} for fresh start.")
    os.makedirs(DIR, exist_ok=True)
    logger.info(f"Fresh start created {DIR}")
    return 0

def get_utc_now() -> str:
    """ Today's date in EPUB 3.3 modified format CCYY-MM-DDThh:mm:ssZ """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_html(url: str) -> str:
    """Fetch raw HTML text from a URL."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def download_url(target_url: str, out_dir=".", fname=""):
    if not fname:
        fname = osp.basename(target_url)

    mime_type, encoding = mimetypes.guess_type(target_url)

    if mime_type in ['text/css', 'text/html']:
        ''' Download to same filetype '''
        try:
            url_text = fetch_html(target_url)
            url_file = osp.join(out_dir, fname)
            # Do not overwrite - instead start fresh when needed
            if not osp.exists(url_file):
                logger.info(f"Downloading URL: {target_url}")
                with open(url_file, "w", encoding="utf-8") as fp:
                    fp.write(url_text)
        except Exception as exc:
            logger.error(f"Failed to download {target_url} of mimetype {mime_type}: {exc}")

    elif mime_type == 'application/x-httpd-php':
        ''' Expect a PHP image file, only, so use Pillow to get raw image bytes '''
        rsp = requests.get(target_url)

        if rsp.status_code == 200:
            try:
                image = Image.open(BytesIO(rsp.content))
                imgext = image_ext.get(image.get_format_mimetype())
                img_name = osp.join(out_dir, f"{fname}.{imgext}")
                # Do not overwrite - instead start fresh when needed
                if not osp.exists(img_name):
                    logger.info(f"Downloading image {img_name} from {target_url}.")
                    image.save(img_name)
            except IOError:
                logger.error(f"The content received was not a valid image: URL {target_url}, mimetype {mime_type}, filename {fname}.")
        else:
            logger.error(f"Failed to retrieve mimetype {mime_type} content from URL {target_url}. Status code: {rsp.status_code}")
    elif not mime_type:
        # Unknown mimetype, try to download as binary
        try:
            rsp = requests.get(target_url, stream=True)
            rsp.raise_for_status()
            out_path = osp.join(out_dir, fname)
            # Do not overwrite - instead start fresh when needed
            if not osp.exists(out_path):
                logger.info(f"Downloading binary content from URL {target_url} to {out_path}.")
                with open(out_path, 'wb') as out_file:
                    shutil.copyfileobj(rsp.raw, out_file)
        except Exception as exc:
            logger.error(f"Failed to download binary content from URL {target_url}: {exc}")
    else:
        logger.warning(f"Extend download_url to handle mimetype {mime_type} content from URL {target_url} .")

# Function to simplify text for searching
def simplify_text(text) -> str:
    """Simplify text by removing tags, whitespace, and punctuation for searching."""
    text = re.sub(r'<[^>]+>', ' ', text)  # remove tags
    text = re.sub(r'\s+', '', text)       # remove whitespace
    text = re.sub(r'[^a-zA-Z]', '', text) # leave only alpha characters
    text = text.lower()                   # convert to lowercase
    return text

def insert_custom_images(chap_num: int, html: str, img_dir: str, img_instructions: list[dict]) -> tuple[list, str]:
    """ Insert custom images into HTML content based on insertion instructions.

    Args:
        html (str): Original HTML content.
        img_instructions (list[dict]): List of insertion instructions, each dict containing:
            - text_file: (ignore, original text reference)
            - img_name: (ignore, original image name)
            - img_rename: image to place in XHTML
            - chapter: chapter number, to filter to the images to insert
            - target_chapter: xhtml into which to insert image
            - location: TOP, MID, BOTTOM location in HTML to place image
            - preceding_text: original text preceding image
            - following_text: original text following image
            - preceding_simp: simplified text preceding image, used to match original text reference to target text
            - following_simp: simplified text following image, used to match original text reference to target text
    Returns:
        list: Updated img_instructions, "chapters" key added with chapter numbers where image was inserted.
        str: Modified HTML content with images inserted. """
    soup = BeautifulSoup(html, "html.parser")

    for insertion in img_instructions:
        target_chap_num = int(insertion.get("chapter"))
        if target_chap_num != chap_num:
            continue  # Skip if not for this chapter
        else:
            logger.debug(f"Processing image insertion for chapter {chap_num}, image {insertion.get('img_rename')}.")

        img_file = insertion.get("img_rename")
        location = insertion.get("location", "MID").upper()
        preceding_text = insertion.get("preceding_text", "").strip().lower()
        following_text = insertion.get("following_text", "").strip().lower()
        preceding_simp = insertion.get("preceding_simp", "").strip().lower()
        following_simp = insertion.get("following_simp", "").strip().lower()

        # Randomly align "narrow" images (width < 350 px)
        # - left (class="left_img") or right (class="right_img"), if location is MID
        # - otherwise center (class="center_img")
        max_side_width = 350
        img_class = "center_img"
        if location == "MID":
            # Decide left or right based on image width
            img_path = osp.join(img_dir, img_file)
            try:
                with Image.open(img_path) as img:
                    width, _ = img.size
                    if width < max_side_width:
                        img_class = "left_img" if (chap_num + hash(img_file)) % 2 == 0 else "right_img"
            except Exception as exc:
                logger.warning(f"Could not open image {img_path} to determine width: {exc}")

            # ONLY for MID locations, search for adjacent text to find anchor point
            anchor_text = {"img_loc": "before", "text": following_text} if following_text else {"img_loc": "after", "text": preceding_text}
            anchor_text_simp = {"img_loc": "before", "text": following_simp} if following_simp else {"img_loc": "after", "text": preceding_simp}

            for thistag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                anchor = None
                tag_text = thistag.get_text(separator=" ", strip=True).strip().lower()
                tag_text_simp = simplify_text(tag_text)

                if anchor_text["text"] and anchor_text["text"] in tag_text:
                    anchor = thistag
                    break
                elif anchor_text_simp["text"] and anchor_text_simp["text"] in tag_text_simp:
                    anchor = thistag
                    break
        else:
            # For TOP or BOTTOM locations:
            # Chapters are divided into TWO MAIN <DIV> sections: Text and optional Footnotes
            # - Search the FIRST tag of First <DIV> for TOP image anchors
            # - Use the last h1/h2/p of First <DIV> for BOTTOM image anchors
            first_div = soup.find('div')
            if location == "TOP":
                anchor_text = {"img_loc": "before", "text": following_text}
                anchor_text_simp = {"img_loc": "before", "text": following_simp}
                anchor = first_div.find(['h1', 'h2', 'p']) if first_div else []
            elif location == "BOTTOM":
                anchor_text = {"img_loc": "after", "text": preceding_text}
                anchor_text_simp = {"img_loc": "after", "text": preceding_simp}
                all_tags = first_div.find_all(['h1', 'h2', 'p', 'div']) if first_div else []
                anchor = all_tags[-1] if all_tags else None
            else:
                anchor = None

        if anchor:
            img_tag = soup.new_tag("img", src="/".join(["images", img_file]))
            img_tag['class'] = img_class

            # Insert the image tag as a sibling to the anchor tag, before or after as specified
            if anchor_text["img_loc"] == "after":
                anchor.insert_after(img_tag)
            else:
                anchor.insert_before(img_tag)

            # Up date this record in insertions, to add this chapter number to the insertion tracker
            insertion['chapters'] = insertion.get('chapters', []) + [chap_num]

            # Log the insertion
            logger.info(f"Inserted image {img_file} {anchor_text['img_loc']} anchor text '{anchor_text['text']}' with location '{location}'.")
        else:
            logger.warning(f"NO LOCATION for image {img_file} in chapter {chap_num}.")
            logger.warning(f":=-- Using anchor text '{anchor_text['text']}'.")
            logger.warning(f":=-- Using simple text '{anchor_text_simp['text']}'.")

    return img_instructions, str(soup)
