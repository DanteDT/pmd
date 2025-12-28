# Generic utilities to import to other modules
import logging
import mimetypes
import os
import requests
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

def init_logger () -> logging.Logger:
    ''' initialize a basic logger for the calling module '''
    logfile = Path(os.path.basename(sys.argv[0])).stem
    logfile = ".".join(["-".join(["log", logfile]), "log"])

    if os.path.exists(logfile):
        os.remove(logfile)

    logging.basicConfig(level=logging.INFO, 
                        filename=logfile, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info(f"Initialized log file {logfile}")
    return logger

def init_dir(DIR:str) -> int:
    if os.path.isdir(DIR):
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
        fname = os.path.basename(target_url)

    mime_type, encoding = mimetypes.guess_type(target_url)

    if mime_type in ['text/css', 'text/html']:
        ''' Download to same filetype '''
        try:
            url_text = fetch_html(target_url)
            url_file = os.path.join(out_dir, fname)
            # Do not overwrite - instead start fresh when needed
            if not os.path.exists(url_file):
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
                img_name = os.path.join(out_dir, f"{fname}.{imgext}")
                # Do not overwrite - instead start fresh when needed
                if not os.path.exists(img_name):
                    logger.info(f"Downloading image {img_name} from {target_url}.")
                    image.save(img_name)
            except IOError:
                logger.error(f"The content received was not a valid image: URL {target_url}, mimetype {mime_type}, filename {fname}.")
        else:
            logger.error(f"Failed to retrieve mimetype {mime_type} content from URL {target_url}. Status code: {rsp.status_code}")

    else:
        logger.warning(f"Extend download_url to handle mimetype {mime_type} content from URL {target_url} .")