"""
A few manual steps are required in the final EPUB book
- Create TOC navigation from H1 and H2 HTML headers, if nav.xhtml, below, does not work for your e-reader
- Remove IE6 fixes from the .css stylesheet
- Replace named-entities like &eacute; in the text, since some e-readers do not support
"""
import os
import shutil
import subprocess
import zipfile
import uuid

from bs4 import BeautifulSoup
from epubcheck import EpubCheck
import utils.utilities as utl
import utils.config as config

logger = utl.init_logger()
config_data = config.load_config()
debugging = config_data["exe_mode"]["debugging"]
epub_ref = config_data["exe_mode"]["epub_ref"]

# Folders
IMG_SRC   = config_data["proj_dirs"]["img_dir"]     # source images
CSS_SRC   = config_data["proj_dirs"]["custom_dir"]  # Custom CSS for EPUB
XHTML_SRC = config_data["proj_dirs"]["ch_xhtml"]
CUSTOM_SRC= config_data["proj_dirs"]["custom_dir"]  # custom front and back matter

# EPUB structure - separate releases for Footnotes and Hyperlinks
EPUB_BOOK = config_data["epub_dirs"]["epub_book"].format(epub_ref)
EPUB_DIR  = config_data["epub_dirs"]["book_dir"].format(epub_ref)
MET_DIR   = os.path.join(EPUB_DIR, config_data["epub_dirs"]["meta_dir"])
OEB_DIR   = os.path.join(EPUB_DIR, config_data["epub_dirs"]["oeb_dir"])
CSS_DIR   = os.path.join(OEB_DIR, config_data["epub_dirs"]["css_dir"])
IMG_DIR   = os.path.join(OEB_DIR, config_data["epub_dirs"]["img_dir"])

# contents.opf manifest and spine entries
chapters = ['<li><a href="ca-001.xhtml">Cover 1851</a></li>',
            '        <li><a href="ca-002.xhtml">Front pages 1851</a></li>',
            '        <li><a href="ca-003.xhtml">Notes from the editor</a></li>',
            '        <li><a href="toc.xhtml">Table of Contents</a></li>'
           ]
opf_mani = ['<item id="ca-001" href="ca-001.xhtml" media-type="application/xhtml+xml" properties="svg"/>', 
            '    <item id="ca-002" href="ca-002.xhtml" media-type="application/xhtml+xml" properties="svg"/>',
            '    <item id="ca-003" href="ca-003.xhtml" media-type="application/xhtml+xml"/>',
            '    <item id="toc" href="toc.xhtml" media-type="application/xhtml+xml"/>'
            ]
opf_spin = ['<itemref idref="ca-001"/>', 
            '    <itemref idref="ca-002"/>',
            '    <itemref idref="ca-003"/>',
            '    <itemref idref="toc"/>'
            ]

# 1. Create temp folder structure, fresh start - so remove EPUB_DIR target dir
if os.path.exists(EPUB_BOOK):
  os.remove(EPUB_BOOK)
  logger.info(f"Rmoved prior dir {EPUB_BOOK}.")

utl.init_dir(EPUB_DIR)
utl.init_dir(MET_DIR)
utl.init_dir(OEB_DIR)
utl.init_dir(CSS_DIR)
utl.init_dir(IMG_DIR)

# 2. Copy XHTML chapter(s) into OEBPS
for fname in os.listdir(XHTML_SRC):
    '''
    Copy each chapter_xxx.xhtml into OEBPS, and build TOC entries from H1 Title and H2 Subtitle tags.
    - Rules for TOC entries:
      - Remove any leading "CHAPTER " from H1, UPPERCASED during previous cleaning
      - If only H1 title, TOC entry is H1-text (without the leading "CHAPTER ")
      - If exactly one H2 subtitle, collapse to one entry, H1-text. - H2-text.
      - Otherwise nest sibling H2 subtitles as ordered list within H1 title entry
    - Title Case for H2 text, only (leave H1 as-is)
    - Add each chapter to manifest and spine in contents.opf
    '''
    if fname.endswith(".xhtml"):
        chapter_number = int(fname.replace("chapter_", "").replace(".xhtml", ""))

        # For debugging
        if debugging and chapter_number != 139:
            continue

        with open(os.path.join(XHTML_SRC, fname), "r", encoding="utf-8") as f:
            content = f.read()

            # For back-reference to header IDs in chapters
            ttlcnt  = 0
            sttlcnt = 0

            soup = BeautifulSoup(content, "html.parser")
            h1_tags = soup.find_all("h1")

            # Build a TOC entry for every H1 title
            toc_entry = ""
            for h1_tag in h1_tags:
                ttl = h1_tag.get_text().replace("CHAPTER ", "").strip()
                ttlcnt += 1

                extra_br = ""
                if ttlcnt > 1:
                    extra_br = "\n"

                h2_tags = h1_tag.find_next_siblings("h2")

                if not h2_tags:
                    # No Subtitles, only the Chapter entry for this chapter
                    toc_entry += f'{extra_br}        <li><a href="{fname}#title_{ttlcnt:03d}">{ttl}</a></li>'
                    logger.info(f'Created Title-only TOC entry for {fname}.')
                else:
                    len_h2_tags = len(h2_tags)

                    if len_h2_tags == 1:
                        sttlcnt += 1
                        subtitle = h2_tags[0].get_text().strip().title()
                        # Only one Subtitle, collapse as suffix to Title
                        if subtitle:
                            toc_entry += f'{extra_br}        <li><a href="{fname}#title_{ttlcnt:03d}">{ttl} - {subtitle}</a></li>'
                        else:
                            toc_entry += f'{extra_br}        <li><a href="{fname}#title_{ttlcnt:03d}">{ttl}</a></li>'
                        logger.info(f'Created Title - Subtitle TOC entry for {fname}.')
                    else:
                        # Multiple Subtitle sections. Nest the subtitles within the EPUB TOC Title entry
                        toc_entry += f'{extra_br}        <li><a href="{fname}#title_{ttlcnt:03d}">{ttl}</a><ol class="nav-toc">'
                        for h2_tag in h2_tags:
                            sttlcnt += 1
                            subtitle = h2_tag.get_text().strip().title()
                            if subtitle:
                                toc_entry += f'\n            <li><a href="{fname}#subtitle_{sttlcnt:03d}">{subtitle}</a></li>'
                        toc_entry += '\n        </ol></li>'
                        logger.info(f'Created Title TOC with nested Subtitle entry for {fname}.')

        chapters.append(toc_entry)

        with open(os.path.join(OEB_DIR, fname), "w", encoding="utf-8") as f:
            f.write(content)

        # Log manifest and spine for each chapter, for contents.opf
        opf_mani.append(f'    <item id="chapter_{chapter_number:03d}" href="chapter_{chapter_number:03d}.xhtml" media-type="application/xhtml+xml"/>')
        opf_spin.append(f'    <itemref idref="chapter_{chapter_number:03d}"/>')
    logger.info(f"Copied chapter {chapter_number:03d} to EPUB {OEB_DIR}.")

# add in the custom back pieces
for fname in os.listdir(CUSTOM_SRC):
    if fname.endswith('.xhtml'):
      shutil.copy(os.path.join("custom", fname), OEB_DIR)
    logger.info(f"Copied custom file {fname} to EPUB {OEB_DIR}.")

chapters.append('        <li><a href="license.xhtml">EPUB license</a></li>')
chapters.append('        <li><a href="cz-001.xhtml">Back pages and cover 1851</a></li>')

opf_mani.append('    <item id="license" href="license.xhtml" media-type="application/xhtml+xml"/>')
opf_mani.append('    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
opf_mani.append('    <item id="cz-001" href="cz-001.xhtml" media-type="application/xhtml+xml" properties="svg"/>')

# Do not add navigation doc to spine
opf_spin.append('    <itemref idref="license"/>')
# opf_spin.append('    <itemref idref="nav"/>')
opf_spin.append('    <itemref idref="cz-001"/>')

# 3. Copy CSS from CSS_SRC to CSS_DIR in EPUB_DIR
cssidx=0
for fname in os.listdir(CSS_SRC):
    if fname.endswith(".css"):
        cssidx+=1
        with open(os.path.join(CSS_SRC, fname), "r", encoding="utf-8") as f:
            css_content = f.read()
        with open(os.path.join(CSS_DIR, fname), "w", encoding="utf-8") as f:
            f.write(css_content)
        opf_mani.append(f'    <item id="css_{cssidx:03d}" href="css/{fname}" media-type="text/css"/>')

# 3. Copy images, jpg
for fname in os.listdir(IMG_SRC):
    if fname.endswith('.jpg'):
        shutil.copy(os.path.join(IMG_SRC, fname), IMG_DIR)
        if fname == "cover-a-001.jpg":
            prop_cover='properties="cover-image"'
        else:
            prop_cover=""
        opf_mani.append(f'    <item id="{fname.replace(".jpg", "")}" href="images/{fname}" media-type="image/jpeg" {prop_cover}/>')

# 4. Create mimetype (must be uncompressed)
with open(f"{EPUB_DIR}/mimetype", "w", encoding="utf-8") as f:
    f.write("application/epub+zip")

# 5. Create META-INF/container.xml
container_xml = '''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0"
           xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf"
              media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''
with open(os.path.join(MET_DIR, "container.xml"), "w", encoding="utf-8") as f:
    f.write(container_xml)

# 6. Create content.opf
book_id = str(uuid.uuid4())
opf_all=f'''<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dcterms="http://purl.org/dc/terms/" 
            xmlns:epub="http://www.idpf.org/2007/ops"
            xmlns:opf="http://www.idpf.org/2007/opf" 
            xmlns:svg="http://www.w3.org/2000/svg"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title id="id">Moby-Dick; Or, The Whale [Power, {epub_ref}]</dc:title>
    <dc:creator>Herman Melville</dc:creator>
    <dc:publisher>Power Moby Dick</dc:publisher>
    <dc:language>en</dc:language>
    <dc:identifier id="uuid_id">urn:uuid:{book_id}</dc:identifier>
    <meta property="dcterms:modified">1851-11-14T00:00:00Z</meta>
    <opf:meta refines="#id" property="title-type">main</opf:meta>
  </metadata>

  <manifest>
    {"\n".join([next for next in opf_mani])}
  </manifest>

  <spine>
    {"\n".join([next for next in opf_spin])}
  </spine>
</package>
'''
with open(os.path.join(OEB_DIR, "content.opf"), "w", encoding="utf-8") as f:
    f.write(opf_all)

# 7. Create toc.xhtml chapter, and nav.xhtml navigation element
# Create separate TOC and Nav, with similar content, since e-readers don't agree
# 1 - as an OEBPS/toc.xhtml, with images and without item attribute properties="nav"
# 2 - without images, as a root nav.xhtml and with item attribute properties="nav"
def write_nav_xhtml (dest="nav") -> int:
    nav_id="nav"
    head='''<head>
        <title>Navigation</title>
        <link type="text/css" rel="stylesheet" href="css/mobydick.css"/>
    </head>'''
    toc_top='''<nav epub:type="toc" id="{}">'''.format(nav_id)
    toc_end='''</nav>'''

    if dest != "nav":
        nav_id="toc"
        head='''<head>
        <title>Table of Contents</title>
        <link type="text/css" rel="stylesheet" href="css/mobydick.css"/>
    </head>'''
        toc_top='''<a href="http://www.powermobydick.com/">
            <img src="images/PowerMobyDickLogo.jpg"/>
        </a>'''
        toc_end='''<h2>Visit <a href="http://www.powermobydick.com/">Power Moby Dick</a></h2>
        <a href="http://www.powermobydick.com/">
            <img src="images/mobydicklightlowres.jpg"/>
        </a>

        <div id="Title_00004">
            <img class="full_page_image" src="images/cover-add-004-toc.jpg"/>
        </div>
        <div id="Title_00005">
            <img class="full_page_image" src="images/cover-add-005-toc.jpg"/>
        </div>
        <div id="Title_00006">
            <img class="full_page_image" src="images/cover-add-006-md.jpg"/>
        </div>'''

    nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html>
    <html lang="en-US" xml:lang="en-US" xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    {head}
    <body>
        {toc_top}
        <h1>Table of Contents</h1>
        <ol class="nav-toc">
            {"\n".join([entry for entry in chapters])}
        </ol>
        {toc_end}
    </body>
    </html>
    '''
    with open(os.path.join(OEB_DIR, f"{nav_id}.xhtml"), "w", encoding="utf-8") as f:
        f.write(nav_xhtml)

    logger.info(f"{dest.upper()} written successfully to epub as {nav_id}.xhtml")

    return 0

# Write these directly to EPUB location
write_nav_xhtml("nav")
write_nav_xhtml("toc")

# 8. Create EPUB zip
with zipfile.ZipFile(EPUB_BOOK, 'w') as epub:
    # mimetype must be first and uncompressed
    epub.write(f"{EPUB_DIR}/mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)

    # nav.xhtml with NAV property to same e-book destination
    # epub.write(f"{OEB_DIR}/nav.xhtml", "OEBPS/nav.xhtml")

    # Add META-INF folder
    for root, dirs, files in os.walk(MET_DIR):
        for file in files:
            epub.write(os.path.join(root, file),
                       os.path.join("META-INF", file))

    # Add OEBPS folder
    for root, dirs, files in os.walk(OEB_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arc_path = os.path.join("OEBPS", os.path.relpath(full_path, OEB_DIR))
            epub.write(full_path, arc_path)

# pyresult.valid for log
pyresult = EpubCheck(EPUB_BOOK)

logger.info(f"EPUB created: {EPUB_BOOK}")
if pyresult.valid:
    logger.info("EpubCheck validation SUCCESS!")
else:
    logger.warning(f"EpubCheck validation FAIL! Messages {pyresult.messages}")

# Create xls to manually review any messages
sysresult = subprocess.run(f"epubcheck --xls EPUB-{epub_ref}.xls {EPUB_BOOK}", capture_output=True, text=True)
logger.info(f"System EpubCheck stdout: {sysresult.stdout}") 

logger.info(f"EPUB created and checked: {EPUB_BOOK}, see EPUB-{epub_ref}.xls.")
