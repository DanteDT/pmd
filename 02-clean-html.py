import os
import shutil
import re
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import utils.utilities as utl

logger = utl.init_logger()

BASE_URL = "http://www.powermobydick.com/"

# Source Folders
CHAP_RAW= "chapters_raw"

# New Folders
CHAP_NEW= "chapters_clean"
CSS_SRC = "css"

# Fresh start
utl.init_dir(CHAP_NEW)
# DO NOT INITIALIZE CHAP_RAW since it contains original files utl.init_dir(CHAP_RAW)

# These are corrections to Power Moby HTML, for example in Chapter 35, today
# - Delicate logic, since multiple passes of the patched_html. Get the sequence right. Debug mode is helpful.
html_fixes = {"&eacute;": "é",
              "&aacute;": "á",
              "&oacute;": "ó",
              "&amp;": "&",
              """Childe_Harold's_Pilgrimage'target=""": """Childe_Harold%27s_Pilgrimage" target=""",
              "<h1>Chapter I</h1>": """<img src="images/cover-add-007-loom.jpg"/><h1>Chapter I</h1>""",
              """<h1>Epilogue</h1>
		<h2>&nbsp;</h2>""": """<img src="images/cover-back-000-epil.jpg"/><h1>Epilogue</h1>
		<h2>Epilogue</h2>""",


               """<!-- The styling for h2 is hard-coded as a paragraph here,
		because the h2 style for some reason does not allow sidenotes.  -->""": "",

              """<p style="font: italic normal 1.4em georgia, sans-serif;
	letter-spacing: 1px; 
	margin-top: 5px;
	margin-bottom: 20px; 
	color: black;
	text-align: center">

<span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Queen_Mab'target='_blank'&gt;Queen Mab:&lt;/a&gt; A fairy in English folklore. In Shakespeare's &lt;i&gt;Romeo and Juliet,&lt;/i&gt; she is said to ride a tiny chariot across men's noses as they sleep
">Queen Mab</span></p>""": 
"""<h2><span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Queen_Mab' target='_blank'&gt;Queen Mab:&lt;/a&gt; A fairy in English folklore. In Shakespeare's &lt;i&gt;Romeo and Juliet,&lt;/i&gt; she is said to ride a tiny chariot across men's noses as they sleep
">Queen Mab</span></h2>""",

              """<p style="font: italic normal 1.4em georgia, sans-serif;
	letter-spacing: 1px; 
	margin-top: 5px;
	margin-bottom: 20px; 
	color: black;
	text-align: center">

The <span class="sidenote" title="Specksynder: chief harpooner. This is a bollixed Anglicization of the Dutch term &lt;i&gt;speksnijder&lt;/i&gt;"> Specksynder</span></p>""":
"""<h2>The <span class="sidenote" title="Specksynder: chief harpooner. This is a bollixed Anglicization of the Dutch term &lt;i&gt;speksnijder&lt;/i&gt;"> Specksynder</span></h2>""",

               """<p style="font: italic normal 1.4em georgia, sans-serif;
	letter-spacing: 1px; 
	margin-top: 5px;
	margin-bottom: 20px; 
	color: black;
	text-align: center">

The Great <span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Heidelberg_Tun'target='_blank'&gt;Heidelburgh Tun:&lt;/a&gt; a vast wine vat in the cellar of the castle in Heidelberg, Germany
">Heidelburgh Tun</span></p>""":
"""<h2>The Great <span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Heidelberg_Tun'target='_blank'&gt;Heidelburgh Tun:&lt;/a&gt; a vast wine vat in the cellar of the castle in Heidelberg, Germany
">Heidelburgh Tun</span></h2>"""
}

def convert_page_paragraphs(html_string: str, chapter_num: int) -> str:
    """
    Convert page paragraphs like:
        <p><...tags...>page 315<.../tags...></p>
    into uniform page paragraphs:
        <p><i>1851 page 315</i></p>

    - Case-insensitive match on 'page'.
    - Ignores other paragraphs
    """

    soup = BeautifulSoup(html_string, "html.parser")

    for ps in soup.find_all("p"):
        # get all text inside the paragraph, ignoring any tags
        text = ps.get_text(strip=True)

        mtc = re.fullmatch(r"page\s+(\d+)", text, flags=re.IGNORECASE)
        if mtc:
            page_num = mtc.group(1)
            ps.clear()
            new_tag = soup.new_tag("i")
            new_tag.string = f"1851 page {page_num}"
            ps.append(new_tag)

    logger.info(f"Converted 1851 page paragraphs for chapter {chapter_num:04d}")
    return str(soup)

def convert_chapter_headers(html_string: str, chapter_num: int) -> str:
    """
    For a nice TOC, convert H1-H2 sequences like
    <h1>Chapter I</h1> <h2>Loomings</h2>
    into
    <h1>I. Loomings</h1> <h2>Loomings</h2>
    """
    soup = BeautifulSoup(html_string, "html.parser")

    for h1 in soup.find_all("h1"):
        # Look for next significant sibling (skip whitespace-only strings)
        nxt = h1.next_sibling
        while nxt and isinstance(nxt, NavigableString) and nxt.strip() == "":
            nxt = nxt.next_sibling

        # Check that it's an H2 (case-insensitive)
        if nxt and nxt.name and nxt.name.lower() == "h2":
            text1 = h1.get_text(strip=True).replace("Chapter ", "")
            text2 = nxt.get_text(strip=True)

            # Build replacement H1
            new_h1 = soup.new_tag("h1")
            new_h1["class"] = "combo"
            new_h1.string = f"{text1}. {text2}"

            h1.replace_with(new_h1)

    logger.info(f"Converted headers for chapter {chapter_num:04d}")
    return str(soup)

def transform_annotations_to_epub_footnotes(html_string: str, chapter_number: int) -> str:
    """
    Unified transformation for:
      1. <a class="sidenote" title="...">text</a>
      2. <span class="sidenote" title="...">text</span>
      3. <div class="sidenote" id="snNNN"> ...HTML... </div>

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
    ### PROCESS BLOCK SIDENOTES (<div class="sidenote">)
    ### ---------------------------------------------------------
    block_notes = soup.find_all("div", class_="sidenote")

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

def save_chapter(number: int, cleaned_html: str, out_dir=CHAP_NEW):
    """Write cleaned chapter HTML to disk."""

    filename = f"chapter-{number:03d}.html"
    path = os.path.join(out_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

def scrape_all():
    """Main driver: scrape TOC, loop over chapters, extract slices, save everything."""

    for fname in sorted(os.listdir(CHAP_RAW)):
        if not fname.endswith(".html"):
            continue

        number = int(fname.replace("chapter-", "").replace(".html", ""))
        # For debugging
        # if number != 31:
        #     continue

        logger.info(f"Processing chapter {number:03d}: {fname}")

        with open(os.path.join(CHAP_RAW, fname), encoding="utf-8") as fp:
            raw_html = fp.read()

        # Patch original HTML to correct and insert images
        patched_html = raw_html
        for src, rpl in html_fixes.items():
            patched_html = patched_html.replace(src, rpl)

        html = convert_page_paragraphs(patched_html, number)
        html = convert_chapter_headers(html, number)
        html = transform_annotations_to_epub_footnotes(html, number)
        html = transform_sidenotes_to_epub(html, number)

        save_chapter(number, html)

    logger.info("SUCCESS.")

if __name__ == "__main__":
    scrape_all()
