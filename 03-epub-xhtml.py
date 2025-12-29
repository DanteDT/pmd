import csv
from bs4 import BeautifulSoup
import os
import utils.utilities as utl
import utils.config as config

logger = utl.init_logger()
config_data = config.load_config()
debugging = config_data["exe_mode"]["debugging"]

# Source Folders
CHAPTER_SRC = config_data["proj_dirs"]["ch_patched"]  # patched HTML chapters
CSS_SRC     = config_data["proj_dirs"]["custom_dir"]  # CSS source for EPUB
CSS_BOOK    = config_data["epub_dirs"]["css_dir"]     # path for CSS in EPUB
CSS_FILES   = sorted(os.listdir(CSS_SRC))

# New Folders
OUTPUT_DIR = config_data["proj_dirs"]["ch_xhtml"]     # output XHTML

# Load custom image insertion data, as list of tuples from CSV columns:
# - img-file: filename of the image to insert (assumed to be in 'images/' directory)
# - juxtaposition: where to insert the image ('left', 'right', 'center')
# - anchor-text: Book text used to locate insertion point
with open(os.path.join(config_data["proj_dirs"]["img_dir"], "insert_img.csv"), encoding="utf-8") as img_csv:
    image_insertions = []
    reader = csv.DictReader(img_csv)
    for row in reader:
        image_insertions.append(row)

# make image_insertions a global object, accessible to utilities
utl.image_insertions = image_insertions

# Fresh start, unless debugging
if not debugging:
    utl.init_dir(OUTPUT_DIR)
    logger.info("Initialized directory for EPUB XHTML output.")
else:
    logger.info("Debugging mode: skipping directory initialization.")

def make_epub_xhtml(chapter_html: str, chapter_number: int, css_files=None, image_insertions=None) -> str:
    """
    Wraps cleaned chapter HTML into valid XHTML suitable for EPUB3.
    - chapter_html: cleaned HTML (annotations converted, page anchors inserted)
    - chapter_number: used for title and IDs
    - css_files: list of relative CSS filenames to include (optional)
    - image_insertions: list of image insertion instructions (optional)
    Returns updated image_insertions list and a string containing valid XHTML.
    """

    # Create XHTML skeleton
    xhtml = BeautifulSoup("", "lxml-xml")
    html_tag = xhtml.new_tag(
        "html", **{
        "xmlns": "http://www.w3.org/1999/xhtml",
        "xmlns:epub": "http://www.idpf.org/2007/ops",
        "xml:lang": "en-US",
        "lang": "en-US"
    })
    xhtml.append(html_tag)

    head_tag = xhtml.new_tag("head")
    html_tag.append(head_tag)

    # Title from H1 and H2, title and subtitle classes added in cleaning step
    chapter_soup = BeautifulSoup(chapter_html, "html.parser")
    h1 = chapter_soup.find("h1", class_="title")
    h2 = chapter_soup.find("h2", class_="subtitle")

    title_tag = xhtml.new_tag("title")
    if h1 and h2:
        title_tag.string = f"{h1.get_text(strip=True)} {h2.get_text(strip=True)}"
    elif h1:
        title_tag.string = f"{h1.get_text(strip=True)}"
    else:
        title_tag.string = f"Chapter {chapter_number}"
    head_tag.append(title_tag)

    # Link CSS files if any
    if css_files:
        for css in css_files:
            if css.endswith(".css"):
                link_tag = xhtml.new_tag("link", rel="stylesheet", type="text/css", href='/'.join([CSS_BOOK, css]))
                head_tag.append(link_tag)

    # Body
    body_tag = xhtml.new_tag("body")
    html_tag.append(body_tag)

    # Insert custom images into HTML
    image_insertions, chapter_html = utl.insert_custom_images(chapter_number, chapter_html, image_insertions)

    # Insert the cleaned chapter content into body
    chapter_soup = BeautifulSoup(chapter_html, "html.parser")
    for elem in list(chapter_soup.contents):
        body_tag.append(elem)

    # Return string representation (XHTML)
    return xhtml.prettify()

for fname in sorted(os.listdir(CHAPTER_SRC)):
    if not fname.endswith(".html"):
        continue
    number = int(fname.replace("chapter-", "").replace(".html", ""))

    # For debugging specific chapters or ranges
    if debugging and number != 150:
        logger.info(f"Skipping chapter {number:03d} in debugging mode.")
        continue
    else:
        logger.info(f"Processing chapter {number:03d}: {fname}")

    with open(os.path.join(CHAPTER_SRC, fname), encoding="utf-8") as fp:
        html = fp.read()

    # Wrap in EPUB XHTML
    xhtml = make_epub_xhtml(html, number, css_files=CSS_FILES, image_insertions=image_insertions)

    # Save
    out_fname = f"chapter_{number:03d}.xhtml"
    with open(os.path.join(OUTPUT_DIR, out_fname), "w", encoding="utf-8") as out_f:
        out_f.write(xhtml)
    logger.info(f"Saved {out_fname}")

# Final log of image insertions, overwrite any prior at root of project directory
with open("log_insert_img.csv", "w", encoding="utf-8", newline='') as log_csv:
    fieldnames = ["img-file", "juxtaposition", "anchor-text", "chapters"]
    writer = csv.DictWriter(log_csv, fieldnames=fieldnames)
    writer.writeheader()
    for insertion in image_insertions:
        writer.writerow(insertion)

logger.info("SUCCESS.")
