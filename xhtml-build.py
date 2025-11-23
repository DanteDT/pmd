from bs4 import BeautifulSoup
import os
import shutil

# Folders
OUTPUT_DIR = "xhtml_chapters"     # output XHTML
CHAPTER_DIR = "chapters"          # input cleaned HTML
CSS_FILES = ["css/mobydick.css"]  # relative paths in EPUB

# Fresh start
if os.path.isdir(OUTPUT_DIR):
  shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def make_epub_xhtml(chapter_html: str, chapter_number: int, css_files=None) -> str:
    """
    Wraps cleaned chapter HTML into valid XHTML suitable for EPUB3.
    - chapter_html: cleaned HTML (annotations converted, page anchors inserted)
    - chapter_number: used for title and IDs
    - css_files: list of relative CSS filenames to include (optional)
    Returns a string containing valid XHTML.
    """

    chapter_id = f"{chapter_number:03d}"
    soup = BeautifulSoup(chapter_html, "html.parser")

    # Create XHTML skeleton
    xhtml = BeautifulSoup("", "lxml-xml")
    html_tag = xhtml.new_tag(
        "html", **{
        "xmlns": "http://www.w3.org/1999/xhtml",
        "xmlns:epub": "http://www.idpf.org/2007/ops",
        "xml:lang": "en-US",
        "lang": "en"
    })
    xhtml.append(html_tag)

    head_tag = xhtml.new_tag("head")
    html_tag.append(head_tag)

    # Title
    title_tag = xhtml.new_tag("title")
    title_tag.string = f"Chapter {chapter_number}"
    head_tag.append(title_tag)

    # Link CSS files if any
    if css_files:
        for css in css_files:
            link_tag = xhtml.new_tag("link", rel="stylesheet", type="text/css", href=css)
            head_tag.append(link_tag)

    # Body
    body_tag = xhtml.new_tag("body")
    html_tag.append(body_tag)

    # Insert the cleaned chapter content into body
    chapter_soup = BeautifulSoup(html, "html.parser")
    for elem in list(chapter_soup.contents):
        body_tag.append(elem)

    # Return string representation (XHTML)
    return xhtml.prettify()

for fname in sorted(os.listdir(CHAPTER_DIR)):
    if not fname.endswith(".html"):
        continue
    chapter_number = int(fname.replace("chapter-", "").replace(".html", ""))
    with open(os.path.join(CHAPTER_DIR, fname), encoding="utf-8") as f:
        html = f.read()

    # Wrap in EPUB XHTML
    xhtml = make_epub_xhtml(html, chapter_number, css_files=CSS_FILES)

    # Save
    out_fname = f"chapter_{chapter_number:03d}.xhtml"
    with open(os.path.join(OUTPUT_DIR, out_fname), "w", encoding="utf-8") as out_f:
        out_f.write(xhtml)
    print(f"Saved {out_fname}")
