import os
import shutil
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "http://www.powermobydick.com/"

# Folders
CHAP_DIR= "chapters"
CSS_DIR = "css"

# Fresh start
if os.path.isdir(CHAP_DIR):
  shutil.rmtree(CHAP_DIR)
os.makedirs(CHAP_DIR, exist_ok=True)

# These are corrections to Power Moby HTML, for example in Chapter 35, today
html_fixes = {
    """Childe_Harold" s_pilgrimage\'target=""": """Childe_Harold%27s_Pilgrimage" target=""",
    "<h2>Loomings</h2>": """
<h2>Loomings</h2>
<div class="calibre1" id="Title_00005">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:epub="http://www.idpf.org/2007/ops" version="1.1" 
width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
<image width="100%" height="100%" 
xlink:href="images/cover-add-005.jpg"/>
</svg>
</div>
"""
}

def fetch_html(url: str) -> str:
    """Fetch raw HTML text from a URL."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

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
    nav_marker = '<p style="text-align:right">'
    cpr_marker = '<div id="copyright">'

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

def download_url(target_url: str, out_dir=CSS_DIR):
    css_name = os.path.basename(target_url)

    try:
        css_text = fetch_html(target_url)
        css_file = os.path.join(out_dir, css_name)
        if not os.path.exists(css_file):
            print(f"Downloading stylesheet: {target_url}")
            with open(css_file, "w", encoding="utf-8") as f:
                f.write(css_text)
    except Exception as e:
        print(f"Failed to download {target_url}: {e}")

def download_stylesheets(html: str, out_dir=CSS_DIR):
    """Download all linked CSS files referenced in this HTML snippet.
       Today, this is the only stylesheet
        <style type="text/css">
        @import "http://www.powermobydick.com/MobySidenote.css";
        </style>       
    """
    os.makedirs(out_dir, exist_ok=True)

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("link", rel="stylesheet")

    for tag in links:
        href = tag.get("href")
        if not href:
            continue

        css_url = urljoin(BASE_URL, href)
        download_url(css_url, out_dir)

    # There is only 1 text/css import today
    if not len(links):
        url_patt = re.compile(r'http\:.+\.css')
        links = soup.find_all("style", type="text/css")

        for tag in links:
            href = tag.contents[0]
            css_url = url_patt.search(href).group(0)
            download_url(css_url, out_dir)

def convert_page_paragraphs_to_anchors(html_string: str, chapter_number: int) -> str:
    """
    Convert paragraphs of the form:
        <p><i>page 471</i></p>
    into anchor:
        <a id="ch_XXX_page_471"></a>

    - chapter_number is zero-padded to 3 digits.
    - Case-insensitive match on 'page'.
    - Ignores any paragraphs that do not match EXACTLY one italicized page marker.
    """

    soup = BeautifulSoup(html_string, "html.parser")
    chapter_id = f"ch_{chapter_number:03d}_page_"

    # Regex: match strings like "page 471", allowing surrounding whitespace
    page_re = re.compile(r"^\s*page\s+(\d+)\s*$", re.IGNORECASE)

    for p in soup.find_all("p"):
        # Look only for <p> containing exactly one <i> tag
        if len(p.contents) == 1 and p.contents[0].name == "i":
            text = p.get_text(strip=True)
            m = page_re.match(text)
            if m:
                page_num = m.group(1)
                # Replace <p>...</p> with <a id="ch_XXX_page_N"></a>
                anchor = soup.new_tag("a", id=f"{chapter_id}{page_num}")
                p.replace_with(anchor)

    return str(soup)

def transform_annotations_to_epub_footnotes(html_string: str, chapter_number: int) -> str:
    """
    Unified transformation for:
      1. <a class="sidenote" title="...">text</a>
      2. <span class="sidenote" title="...">text</span>
      3. <div class="sideNote" id="snNNN"> ...HTML... </div>

    Converts all to:
      - inline noteref anchors using visible text (or auto-label for block sidenotes)
      - <aside epub:type="footnote"><p>...</p></aside> entries
      - A single footer container per chapter.
    """

    soup = BeautifulSoup(html_string, "html.parser")
    chapter_str = f"{chapter_number:03d}"
    fn_counter = 1
    footnotes = []

    ### ---------------------------------------------------------
    ### Helper: create a new footnote ID pair
    ### ---------------------------------------------------------
    def new_ids():
        nonlocal fn_counter
        src = f"c{chapter_str}_src{fn_counter:04d}"
        ref = f"c{chapter_str}_ref{fn_counter:04d}"
        fn_counter += 1
        return src, ref

    ### ---------------------------------------------------------
    ### Helper: parse a string containing HTML and return nodes
    ### ---------------------------------------------------------
    def parse_html_fragment(html_fragment: str):
        frag = BeautifulSoup(html_fragment, "html.parser")
        return list(frag.contents)

    ### ---------------------------------------------------------
    ### PROCESS INLINE SIDENOTES FIRST
    ### ---------------------------------------------------------
    inline_tags = soup.find_all(
        lambda tag:
            tag.has_attr("class")
            and "sidenote" in tag["class"]
            and tag.has_attr("title")
            and tag.name in ("a", "span")
    )

    for tag in inline_tags:
        visible_text = tag.get_text(strip=True)
        title_html = tag["title"]

        src_id, ref_id = new_ids()

        # Create inline source anchor
        src_anchor = soup.new_tag(
            "a",
            id=src_id,
            href=f"chapter_{chapter_str}.xhtml#{ref_id}",
            **{"epub:type": "noteref", "class": "class_source"}
        )
        src_anchor.string = visible_text

        # Replace old tag
        tag.replace_with(src_anchor)

        # Build footnote aside
        aside = soup.new_tag("aside", id=ref_id, **{"epub:type": "footnote"})
        p = soup.new_tag("p")

        # backlink
        backlink = soup.new_tag("a",
            href=f"chapter_{chapter_str}.xhtml#{src_id}",
            **{"class": "class_footnote"}
        )
        backlink.string = "↩"
        p.append(backlink)

        # Add parsed title HTML
        for node in parse_html_fragment(title_html):
            p.append(node)

        aside.append(p)
        footnotes.append(aside)

    ### ---------------------------------------------------------
    ### PROCESS BLOCK SIDENOTES (<div class="sideNote">)
    ### ---------------------------------------------------------
    block_notes = soup.find_all("div", class_="sideNote")

    for div in block_notes:
        # Extract body HTML of the sidenote
        content_nodes = list(div.contents)

        # Create new IDs
        src_id, ref_id = new_ids()

        # Auto-generate visible marker — could be superscript number, or "[note]"
        visible_marker = str(fn_counter - 1)

        inline_anchor = soup.new_tag(
            "a",
            id=src_id,
            href=f"chapter_{chapter_str}.xhtml#{ref_id}",
            **{"epub:type": "noteref", "class": "class_source"}
        )
        inline_anchor.string = visible_marker

        # Insert inline marker where the block note was
        div.replace_with(inline_anchor)

        # Build footnote
        aside = soup.new_tag("aside", id=ref_id, **{"epub:type": "footnote"})
        p = soup.new_tag("p")

        backlink = soup.new_tag(
            "a",
            href=f"chapter_{chapter_str}.xhtml#{src_id}",
            **{"class": "class_footnote"}
        )
        backlink.string = "↩"
        p.append(backlink)

        # Append original block HTML content
        for node in content_nodes:
            p.append(node)

        aside.append(p)
        footnotes.append(aside)

    ### ---------------------------------------------------------
    ### FOOTNOTE CONTAINER
    ### ---------------------------------------------------------
    if footnotes:
        container = soup.new_tag(
            "div",
            id=f"c{chapter_str}_footnotes",
            **{"class": "class_ch_footers"}
        )
        for aside in footnotes:
            container.append(aside)

        # Append at end of <body>, or end of soup if <body> missing
        if soup.body:
            soup.body.append(container)
        else:
            soup.append(container)

    return str(soup)

def transform_sidenotes_to_epub(html_string: str, chapter_number: int) -> str:
    """
    Convert inline <span class="sidenote" title="...">...</span>
    into EPUB footnotes.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_string, "html.parser")
    chapter_prefix = f"ch_{chapter_number:03d}"
    fn_counter = 1000  # start at high number to avoid colliding with original snN

    for span in soup.find_all("span", class_="sidenote"):
        note_text = span.get("title", "").strip()
        if not note_text:
            continue  # skip empty

        fn_counter += 1
        fn_id = f"{chapter_prefix}_fn_{fn_counter}"
        fn_ref_id = f"{chapter_prefix}_fnref_{fn_counter}"

        # Create inline footnote reference
        a_tag = soup.new_tag("a", href=f"#{fn_id}", id=fn_ref_id, **{"epub:type": "noteref"})
        a_tag.string = span.get_text(strip=True)
        span.replace_with(a_tag)

        # Create aside footnote
        aside = soup.new_tag("aside", id=fn_id, **{"epub:type": "footnote"})
        aside.append(BeautifulSoup(note_text, "html.parser"))
        # Append to end of body
        body = soup.body or soup
        body.append(aside)

    return str(soup)

def save_chapter(number: int, cleaned_html: str, out_dir=CHAP_DIR):
    """Write cleaned chapter HTML to disk."""

    filename = f"chapter-{number:03d}.html"
    path = os.path.join(out_dir, filename)

    patched_html = cleaned_html
    for src, rpl in html_fixes.items():
        patched_html = patched_html.replace(src, rpl)

    with open(path, "w", encoding="utf-8") as f:
        f.write(patched_html)

def scrape_all():
    """Main driver: scrape TOC, loop over chapters, extract slices, save everything."""
    print("Fetching TOC...")
    toc_html = fetch_html(BASE_URL)

    chapters = extract_chapter_urls(toc_html)
    print(f"Found {len(chapters)} chapters.")

    # First page also has the core css stylesheets
    download_stylesheets(toc_html)

    for number, chapter_url in chapters:
        print(f"Processing chapter {number:03d}: {chapter_url}")

        # if number != 35:
        #     continue

        raw_html = fetch_html(chapter_url)

        # Also save any chapter-specific CSS
        download_stylesheets(raw_html)

        html = extract_chapter_content(raw_html)
        html = convert_page_paragraphs_to_anchors(html, number)
        html = transform_annotations_to_epub_footnotes(html, number)
        html = transform_sidenotes_to_epub(html, number)

        save_chapter(number, html)

    print("Done.")

if __name__ == "__main__":
    scrape_all()
