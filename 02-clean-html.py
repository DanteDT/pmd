import os
import shutil
import re
import requests
from bs4 import BeautifulSoup, Comment, NavigableString
from urllib.parse import urljoin
import utils.utilities as utl
import utils.config as config

logger = utl.init_logger()
config_data = config.load_config()
debugging = config_data["exe_mode"]["debugging"]

# Source Folders - DO NOT initialize (remove) these, created in prior step
CHAP_RAW= config_data["proj_dirs"]["ch_raw"]

# New Folders. 
# - Clean is minimal cleanup, to test against raw. Patched is full cleanup.
# - This enables testing that patches do not compromise original content.
CHAP_CLE= config_data["proj_dirs"]["ch_clean"]
CHAP_PAT= config_data["proj_dirs"]["ch_patched"]

# Fresh start, unless debugging
if not debugging:
    utl.init_dir(CHAP_CLE)
    utl.init_dir(CHAP_PAT)
    # DO NOT INITIALIZE CHAP_RAW, created in the PRIOR step
    logger.info("Initialized directories for clean and patched HTML chapters.")
else:
    logger.info("Debugging mode: skipping directory initialization.")

# These are corrections to Power Moby HTML, for example in Chapter 35, today
# - Delicate logic, since multiple passes of the patched_html. Get the sequence right. Debug mode is helpful.
html_fixes = {"&eacute;": "é",
              "&aacute;": "á",
              "&oacute;": "ó",
              "&amp;": "&",
              "â": "–",
              """Childe_Harold's_Pilgrimage'target=""": """Childe_Harold%27s_Pilgrimage" target=""",

              """<h1>Moby-Dick </h1>\n<h2>Front Matter</h2>""":
              """   <div id="Page_Etymology">
     <img class="full_page_image" src="images/cover-add-007-etym.jpg"/>
   </div>
   <div id="Page_Extracts">
     <img class="full_page_image" src="images/cover-add-008-extr.jpg"/>
   </div>
<h1>Front Matter</h1>\n<h2>Etymology and Extracts</h2>""",

              "<h1>Chapter I</h1>": 
              """   <div id="Page_Loomings">
     <img class="full_page_image" src="images/cover-add-009-loom.jpg"/>
   </div>
<h1>Chapter I</h1>""",

              """<h1>Epilogue</h1>\n<h2>\xa0</h2>""": 
              """   <div id="Page_Epilogue">
     <img class="full_page_image" src="images/cover-back-000-epil.jpg"/>
   </div>
<h1>CXXXVI. Epilogue</h1>""",

              """href='http://translate.google.com/translate?hl=en&sl=de&u=http://de.wikipedia.org/wiki/Alexander_Heimb%25C3%25BCrger&ei=IfXUSsb2BY63lAej7OGcCQ&sa=X&oi=translate&resnum=5&ct=result&ved=0CBgQ7gEwBA&prev=/search%3Fq%3D%2522Alexander%2BHeimb%25C3%25BCrger%2522%2B%2522herr%2Balexander%2522%26hl%3Den'""":
"""href='https://de-wikipedia-org.translate.goog/wiki/Alexander_Heimb%C3%BCrger?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp' """,

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
"""<h2><span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Queen_Mab'target='_blank'&gt;Queen Mab:&lt;/a&gt; A fairy in English folklore. In Shakespeare's &lt;i&gt;Romeo and Juliet,&lt;/i&gt; she is said to ride a tiny chariot across men's noses
as they sleep.">Queen Mab</span></h2>""",

              """<p style="font: italic normal 1.4em georgia, sans-serif;
	letter-spacing: 1px; 
	margin-top: 5px;
	margin-bottom: 20px; 
	color: black;
	text-align: center">

The <span class="sidenote" title="Specksynder: chief harpooner. This is a bollixed Anglicization of the Dutch term &lt;i&gt;speksnijder&lt;/i&gt;"> Specksynder</span></p>""":
"""<h2>The <span class="sidenote" title="Specksynder: chief harpooner.
This is a bollixed Anglicization of the Dutch term &lt;i&gt;speksnijder&lt;/i&gt;."> Specksynder</span></h2>""",

               """<p style="font: italic normal 1.4em georgia, sans-serif;
	letter-spacing: 1px; 
	margin-top: 5px;
	margin-bottom: 20px; 
	color: black;
	text-align: center">

The Great <span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Heidelberg_Tun'target='_blank'&gt;Heidelburgh Tun:&lt;/a&gt; a vast wine vat in the cellar of the castle in Heidelberg, Germany
">Heidelburgh Tun</span></p>""":
"""<h2>The Great <span class="sidenote" title="&lt;a href='http://en.wikipedia.org/wiki/Heidelberg_Tun'target='_blank'&gt;Heidelburgh
Tun:&lt;/a&gt; a vast wine vat in the cellar of the castle in Heidelberg, Germany">Heidelburgh Tun</span>.</h2>""",

                "<h2>Sources</h2>": "<h1>Sources</h1>",
                "<h2>Glossary</h2>": "<h1>Glossary</h1>",
                "<h2>Blogs</h2>": "<h1>Blogs</h1>",
                "<h2>Other Press</h2>": "<h1>Other Press</h1>",
                "<h2>A Note on the Text</h2>": "<h1>A Note on the Text</h1>",
                "<h2>Resources</h2>": "<h1>Resources</h1>",

                """<p style="line-height: 1.3em"><i>Have a question, suggestion, or comment?  Please use the "Contact Us" link at left or email us directly at meg at powermobydick dot com.</i><br/><br/></p>""": """<p style="line-height: 1.3em"><i>Have a question, suggestion, or comment? Please <a href="mailto:meg@powermobydick.com">contact us</a>.</i></p>""",

                """<h2>Privacy Policy</h2>
<p>Power Moby-Dick does not collect or use any information about individual visitors to this website, but we do use Google AdSense to serve some of our ads. In order to show you the ads you're most likely to be interested in, Google AdSense may use information about your visits to this and other websites. Google AdSense does not use personal information such as your name, address, email address, or telephone number to choose the ads you see.  If you would like more information about this practice or you would like to opt out of it, visit Google's <a href="http://www.google.com/privacy_ads.html" target="_blank">Privacy Center</a>.""": 
"""<h1>Privacy Policy</h1>
<p>Power Moby-Dick does not collect or use any information about individual visitors to this website."""
}

def basic_html_cleanup(html_string: str, chapter_num: int) -> str:
    """
    Basic HTML cleanup:
      - Remove OnClick attributes
      - Remove comments containing "dead link" or "the confidence man"
      - Remove spacer images and 1-pixel images
      - Fix <a name=> to <a id=>
      - Apply other HTML fixes from html_fixes dict
    """
    soup = BeautifulSoup(html_string, "html.parser")

    # First remove all OnClick attributes
    for tag in soup.find_all(attrs={"onclick": True}):
        del tag["onclick"]

    # Next, delete from html_string all HTML comments containing "dead link"
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "dead link" in comment.lower() or "the confidence man" in comment.lower():
            comment.extract()

    # Now remove images that are spacer images or 1 pixel height or width
    for img in soup.find_all("img"):
        if img.get("src", "").endswith("spacer.gif") or img.get("height") == "1" or img.get("width") == "1":
            img.decompose()

    # Fix <a name=> to <a id=> throughout
    for anchor in soup.find_all('a', attrs={'name': True}):
        anchor['id'] = anchor.get('name')
        del anchor['name']

    # Finally, make other HTML fixes from html_fixes dict
    patched_html = str(soup)
    for src, rpl in html_fixes.items():
        patched_html = patched_html.replace(src, rpl)

    logger.info(f"Performed basic HTML cleanup for chapter {chapter_num:04d}.")
    return patched_html

def convert_page_paragraphs(html_string: str, chapter_num: int) -> str:
    """
    Convert page paragraphs like:
        <p><...tags...>page 315<.../tags...></p>
    into uniform page paragraphs:
        <p><i>page 315</i></p>

    - Case-insensitive match on 'page'.
    - Ignores other paragraphs
    """

    soup = BeautifulSoup(html_string, "html.parser")

    # Now convert page paragraphs
    for ps in soup.find_all("p"):
        # get all text inside the paragraph, ignoring any tags
        text = ps.get_text(strip=True)

        mtc = re.fullmatch(r"page\s+(\d+)", text, flags=re.IGNORECASE)
        if mtc:
            page_num = mtc.group(1)
            ps.clear()
            new_tag = soup.new_tag("i")
            new_tag.string = f"page {page_num}"
            ps.append(new_tag)

    logger.info(f"Converted 1851 page number paragraphs for chapter {chapter_num:04d}")
    return str(soup)

def convert_chapter_headers(html_string: str, chapter_num: int) -> str:
    """
    For a nice TOC, convert H1-H2 sequences like
    <h1>Chapter I</h1> <h2>Loomings</h2>
    into
    <h1>I. Loomings</h1> <h2>Loomings</h2>
    compressing whitespace in H1 and H2 text.
    """
    soup = BeautifulSoup(html_string, "html.parser")

    for h1 in soup.find_all("h1"):
        # Look for next significant sibling (skip whitespace-only strings)
        nxt = h1.next_sibling
        while nxt and isinstance(nxt, NavigableString) and nxt.strip() == "":
            nxt = nxt.next_sibling

        # Check that it's an H2 (case-insensitive)
        if nxt and nxt.name and nxt.name.lower() == "h2":
            text1 = h1.get_text(strip=False).replace("Chapter ", "")
            text2 = nxt.get_text(strip=False)

            # Build replacement H1, compressing whitespace
            new_h1 = soup.new_tag("h1")
            new_h1["class"] = "title"
            new_h1.string = " ".join(f"{text1}. {text2}".split())

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

def save_chapter(number: int, cleaned_html: str, out_dir: str=CHAP_PAT) -> None:
    """Write cleaned chapter HTML to disk. By default to patched dir."""

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

        # For debugging specific chapters or ranges
        if debugging and number != 141:
            logger.info(f"Skipping chapter {number:03d} in debugging mode.")
            continue
        else:
            logger.info(f"Processing chapter {number:03d}: {fname}")

        with open(os.path.join(CHAP_RAW, fname), encoding="utf-8") as fp:
            raw_html = fp.read()

        html = raw_html
        html = basic_html_cleanup(html, number)

        # Save minimally cleaned HTML, for comparison with raw and with patched, to test that processes do not degrade content
        save_chapter(number, html, out_dir=CHAP_CLE)

        html = convert_page_paragraphs(html, number)
        html = convert_chapter_headers(html, number)
        html = transform_annotations_to_epub_footnotes(html, number)
        html = transform_sidenotes_to_epub(html, number)

        # Compact HTML with html formatter
        soup = BeautifulSoup(html, "html.parser")   

        # Remove excessive whitespace for any non-missing text (strings)
        for element in soup.find_all(string=True):
            if isinstance(element, NavigableString):
                cleaned_text = ' '.join(element.string.split())
                element.replace_with(cleaned_text)

        save_chapter(number, str(soup), out_dir=CHAP_PAT)

    logger.info("SUCCESS.")

if __name__ == "__main__":
    scrape_all()
