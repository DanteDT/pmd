'''
Retrieve Power Moby Dick chapter (HTML) and stylesheet (CSS). Scrape politely.
Run ONLY when you know that the content has been improved. Retrieve latest and stash locally.
Modify that raw content locally, iteratively as needed, in subsequent modules.
'''
import os
import shutil
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import utils.utilities as utl

logger = utl.init_logger()

BASE_URL = "http://www.powermobydick.com/"

# New Folders
CHAP_RAW= "chapters_raw"
CSS_DIR = "css"

# Fresh start
utl.init_dir(CHAP_RAW)
# DO NOT INITIALIZE CSS_DIR since it contains original files utl.init_dir(CSS_DIR)

def extract_chapter_urls(toc_html: str) -> list[tuple[int, str]]:
    """
    Parse the TOC page and return a list of (chapter_number, chapter_url).
    """
    soup = BeautifulSoup(toc_html, "html.parser")
    links = soup.find_all("a", href=True)

    chapters = []

    # chapter pages always follow pattern like Moby001.html, Moby002.html, ...
    chapter_re = re.compile(r"Moby(\d+)\.html", re.IGNORECASE)

    for link in links:
        match = chapter_re.search(link["href"])
        if match:
            chapter_number = int(match.group(1))
            chapter_url = urljoin(BASE_URL, link["href"])
            chapters.append((chapter_number, chapter_url))

    chapters.sort()
    return chapters

def extract_chapter_content(html: str) -> str:
    """
    Slice from first <div id="container"> to the <p style="text-align:right"> navigation block.
    This is Option C: literal slicing between markers, no DOM matching.
    """
    start_marker = '<div id="container"'
    nav_marker   = '<p style="text-align:right">'
    cpr_marker   = '<div id="copyright">'

    start_idx = html.find(start_marker)
    if start_idx == -1:
        raise ValueError("No <div id='container'> found in chapter.")

    end_idx = html.find(nav_marker, start_idx)
    if end_idx == -1:
        # Possible last chapter with no navigation paragraph
        # In that case, look for copyright <div> or fall back to end of HTML
        end_idx = html.find(cpr_marker, start_idx)
        if end_idx == -1:
            end_idx = len(html)

    # Slice HTML directly
    return html[start_idx:end_idx]

def download_stylesheets(html: str, out_dir=CSS_DIR):
    """
    Download linked CSS files referenced in this HTML snippet. Do not replace same same-name stylesheets.
    Today, this is the only stylesheet
	<style type="text/css">
	@import "http://www.powermobydick.com/MobySidenote.css";
	</style>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("link", rel="stylesheet")

    for tag in links:
        href = tag.get("href")
        if not href:
            continue

        css_url = urljoin(BASE_URL, href)
        utl.download_url(css_url, out_dir)

    # There is only 1 text/css import today
    if not len(links):
        url_patt = re.compile(r'https*\:.+\.css')
        links = soup.find_all("style", type="text/css")

        for tag in links:
            href = tag.contents[0]
            css_url = url_patt.search(href).group(0)
            utl.download_url(css_url, out_dir)

def save_chapter(number: int, raw_html: str, out_dir=CHAP_RAW):
    """
    Write RAW chapter HTML to disk. Process further subsequently
    """
    filename = f"chapter-{number:03d}.html"
    path = os.path.join(out_dir, filename)

    try:
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(raw_html)
    except Exception as exc:
        logger.error(f"Failed to download {raw_html}: {exc}")

def scrape_all():
    """
    Main driver: scrape TOC, loop over chapters, extract slices, save everything.
    """
    logger.info(f"Fetching TOC from base URL {BASE_URL}")
    toc_html = utl.fetch_html(BASE_URL)

    chapters = extract_chapter_urls(toc_html)
    logger.info(f"Found {len(chapters)} chapters in based URL.")

    # The TOC home page may have stylesheets
    download_stylesheets(toc_html)

    for number, chapter_url in chapters:
        logger.info(f"Processing chapter {number:03d}: {chapter_url}")

        # For debugging
        # if number != 6:
        #     break

        # From raw HTML, fetch any CSS stylesheets
        raw_html = utl.fetch_html(chapter_url)
        download_stylesheets(raw_html)
        html = extract_chapter_content(raw_html)
        save_chapter(number, html)

    logger.info("SUCCESS.")

if __name__ == "__main__":
    scrape_all()
