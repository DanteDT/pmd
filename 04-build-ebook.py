"""
A few manual steps are required in the final EPUB book
- Create TOC navigation from H1 and H2 HTML headers, if nav.xhtml, below, does not work for your e-reader
- Remove IE6 fixes from the .css stylesheet
- Replace named-entities like &eacute; in the text, since some e-readers do not support
"""
import os
import shutil
import zipfile
import uuid

from bs4 import BeautifulSoup
import utils.utilities as utl
import utils.config as config

logger = utl.init_logger()
config_data = config.load_config()
debugging = config_data["exe_mode"]["debugging"]

# Folders
IMG_SRC   = config_data["proj_dirs"]["img_dir"]     # source images
CSS_SRC   = config_data["proj_dirs"]["custom_dir"]  # Custom CSS for EPUB
XHTML_SRC = config_data["proj_dirs"]["ch_xhtml"]
CUSTOM_SRC= config_data["proj_dirs"]["custom_dir"]  # custom front and back matter

# EPUB structure
EPUB_BOOK = config_data["epub_dirs"]["epub_book"]
EPUB_DIR  = config_data["epub_dirs"]["book_dir"]
MET_DIR   = os.path.join(EPUB_DIR, config_data["epub_dirs"]["meta_dir"])
OEB_DIR   = os.path.join(EPUB_DIR, config_data["epub_dirs"]["oeb_dir"])
CSS_DIR   = os.path.join(OEB_DIR, config_data["epub_dirs"]["css_dir"])
IMG_DIR   = os.path.join(OEB_DIR, config_data["epub_dirs"]["img_dir"])

# contents.opf manifest and spine entries
chapters = {"Cover 1851": "ca-001.xhtml",
            "Front pages 1851": "ca-002.xhtml",
            "Notes from the editor": "ca-003.xhtml",
            "Table of Contents": "nav.xhtml"
            }
opf_mani = ['<item id="ca-001" href="ca-001.xhtml" media-type="application/xhtml+xml"/>', 
            '    <item id="ca-002" href="ca-002.xhtml" media-type="application/xhtml+xml"/>',
            '    <item id="ca-003" href="ca-003.xhtml" media-type="application/xhtml+xml"/>',
            '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
            ]
opf_spin = ['<itemref idref="ca-001"/>', 
            '    <itemref idref="ca-002"/>',
            '    <itemref idref="ca-003"/>',
            '    <itemref idref="nav"/>'
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
    if fname.endswith(".xhtml"):
        chapter_number = int(fname.replace("chapter_", "").replace(".xhtml", ""))

        with open(os.path.join(XHTML_SRC, fname), "r", encoding="utf-8") as f:
            content = f.read()

            # get chapters for TOC from H1 title tags
            soup = BeautifulSoup(content, "html.parser")
            h1 = soup.find("h1")
            if h1:
                h1_text = h1.get_text()
                chapters[h1_text] = fname

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

chapters.update({"EPUB license": "license.xhtml"})
chapters.update({"Back pages and cover 1851": "cz-001.xhtml"})
opf_mani.append('    <item id="license" href="license.xhtml" media-type="application/xhtml+xml"/>')
opf_mani.append('    <item id="cz-001" href="cz-001.xhtml" media-type="application/xhtml+xml"/>')
opf_spin.append('    <itemref idref="license"/>')
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
opf_all=f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uuid_id">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dcterms="http://purl.org/dc/terms/" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>Moby-Dick; Or, The Whale [Power]</dc:title>
    <dc:creator>Herman Melville</dc:creator>
    <dc:publisher>Power Moby Dick</dc:publisher>
    <dc:language>en</dc:language>
    <dc:identifier id="uuid_id">urn:uuid:{book_id}</dc:identifier>
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

# 7. Create minimal nav.xhtml
nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
  <head>
    <title>Table of Contents</title>
    <link type="text/css" rel="stylesheet" href="css/mobydick.css"/>
  </head>
  <body>
    <a href="http://www.powermobydick.com/">
      <img class="full_page_image" src="images/PowerMobyDickLogo.jpg"/>
    </a>
    <nav epub:type="toc" id="nav">
      <h1>Table of Contents</h1>
      <ol>
        {"\n".join([f'        <li><a href="{fname}">{title}</a></li>' for title, fname in chapters.items()])}
      </ol>
    </nav>
    <h2>Visit <a href="http://www.powermobydick.com/">Power Moby Dick</a></h2>

    <a href="http://www.powermobydick.com/">
      <img class="full_page_image" src="images/mobydicklightlowres.jpg"/>
    </a>

    <div id="Title_00004">
      <img class="full_page_image" src="images/cover-add-004-toc.jpg"/>
    </div>
    <div id="Title_00005">
      <img class="full_page_image" src="images/cover-add-005-toc.jpg"/>
    </div>
    <div id="Title_00006">
      <img class="full_page_image" src="images/cover-add-006-md.jpg"/>
    </div>

  </body>
</html>
'''
with open(os.path.join(OEB_DIR, "nav.xhtml"), "w", encoding="utf-8") as f:
    f.write(nav_xhtml)

# 8. Create EPUB zip
with zipfile.ZipFile(EPUB_BOOK, 'w') as epub:
    # mimetype must be first and uncompressed
    epub.write(f"{EPUB_DIR}/mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)

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

logger.info(f"EPUB created: {EPUB_BOOK}")
logger.info("SUCCESS.")
