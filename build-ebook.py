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

# Folders
XHTML_DIR = "xhtml_chapters"
CSS_DIR = "css"
IMG_DIR = "images"
OUTPUT_EPUB = "Moby Dick - Herman Melville.epub"

# EPUB structure
BUILD = "BUILD"
OEBPS = f"{BUILD}/OEBPS"
META_INF = f"{BUILD}/META-INF"

# contents.opf manifest and spine entries
chapters = {"Cover 1851": "ca-001.xhtml",
            "Front pages 1851": "ca-002.xhtml",
            "Table of Contents": "nav.xhtml"
            }
opf_mani = ['<item id="ca-001" href="ca-001.xhtml" media-type="application/xhtml+xml"/>', 
            '    <item id="ca-002" href="ca-002.xhtml" media-type="application/xhtml+xml"/>',
            '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
            ]
opf_spin = ['<itemref idref="ca-001"/>', 
            '    <itemref idref="ca-002"/>',
            '    <itemref idref="nav"/>'
            ]

# 1. Create temp folder structure, fresh start - so remove BUILD target dir
if os.path.exists(OUTPUT_EPUB):
  os.remove(OUTPUT_EPUB)
if os.path.isdir(BUILD):
  shutil.rmtree(BUILD)
os.makedirs(OEBPS, exist_ok=True)
os.makedirs(META_INF, exist_ok=True)

# 2. Copy XHTML chapter(s) into OEBPS
for fname in os.listdir(XHTML_DIR):
    if fname.endswith(".xhtml"):
        chapter_number = int(fname.replace("chapter_", "").replace(".xhtml", ""))

        with open(os.path.join(XHTML_DIR, fname), "r", encoding="utf-8") as f:
            content = f.read()
        with open(os.path.join(OEBPS, fname), "w", encoding="utf-8") as f:
            f.write(content)

        # Log manifest and spine for each chapter, for contents.opf
        chapters.update({f"{chapter_number:03d}":fname})
        opf_mani.append(f'    <item id="chapter_{chapter_number:03d}" href="chapter_{chapter_number:03d}.xhtml" media-type="application/xhtml+xml"/>')
        opf_spin.append(f'    <itemref idref="chapter_{chapter_number:03d}"/>')

# add in the custom back pieces
shutil.copy(os.path.join("custom", "ca-001.xhtml"), OEBPS)
shutil.copy(os.path.join("custom", "ca-002.xhtml"), OEBPS)
shutil.copy(os.path.join("custom", "cz-001.xhtml"), OEBPS)

chapters.update({"Back pages and cover 1851": "cz-001.xhtml"})
opf_mani.append('    <item id="cz-001" href="cz-001.xhtml" media-type="application/xhtml+xml"/>')
opf_spin.append('    <itemref idref="cz-001"/>')

# 3. Copy CSS
os.makedirs(os.path.join(OEBPS, "css"), exist_ok=True)
cssidx=0
for fname in os.listdir(CSS_DIR):
    if fname.endswith(".css"):
        cssidx+=1
        with open(os.path.join(CSS_DIR, fname), "r", encoding="utf-8") as f:
            css_content = f.read()
        with open(os.path.join(OEBPS, "css", fname), "w", encoding="utf-8") as f:
            f.write(css_content)
        opf_mani.append(f'    <item id="css_{cssidx:03d}" href="css/{fname}" media-type="text/css"/>')

# 3. Copy images, jpg
os.makedirs(os.path.join(OEBPS, "images"), exist_ok=True)
for fname in os.listdir(IMG_DIR):
    if fname.endswith('.jpg'):
        shutil.copy(os.path.join(IMG_DIR, fname), os.path.join(OEBPS, "images"))
        if fname == "cover-a-001.jpg":
            prop_cover='properties="cover-image"'
        else:
            prop_cover=""
        opf_mani.append(f'    <item id="{fname.replace(".jpg", "")}" href="images/{fname}" media-type="image/jpeg" {prop_cover}/>')

# 4. Create mimetype (must be uncompressed)
with open(f"{BUILD}/mimetype", "w", encoding="utf-8") as f:
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
with open(os.path.join(META_INF, "container.xml"), "w", encoding="utf-8") as f:
    f.write(container_xml)

# 6. Create content.opf

book_id = str(uuid.uuid4())
opf_all=f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uuid_id">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dcterms="http://purl.org/dc/terms/" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>Moby Dick, Or The Whale</dc:title>
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
with open(os.path.join(OEBPS, "content.opf"), "w", encoding="utf-8") as f:
    f.write(opf_all)

# 7. Create minimal nav.xhtml
nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
  <head>
    <title>Table of Contents</title>
  </head>
  <body>
    <img src="images/PowerMobyDickLogo.jpg"/>
    <nav epub:type="toc" id="nav">
      <h1>Table of Contents</h1>
      <ol>
        {"\n".join([f'        <li><a href="{fname}">Chapter {num}</a></li>' for num, fname in chapters.items()])}
      </ol>
    </nav>
    <h3>Visit <a href="http://www.powermobydick.com/">Power Moby Dick</a></h3>
    <img src="images/PowerMobyDickLogo.jpg"/>
  </body>
</html>
'''
with open(os.path.join(OEBPS, "nav.xhtml"), "w", encoding="utf-8") as f:
    f.write(nav_xhtml)

# 8. Create EPUB zip
with zipfile.ZipFile(OUTPUT_EPUB, 'w') as epub:
    # mimetype must be first and uncompressed
    epub.write(f"{BUILD}/mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)

    # Add META-INF folder
    for root, dirs, files in os.walk(META_INF):
        for file in files:
            epub.write(os.path.join(root, file),
                       os.path.join("META-INF", file))

    # Add OEBPS folder
    for root, dirs, files in os.walk(OEBPS):
        for file in files:
            full_path = os.path.join(root, file)
            arc_path = os.path.join("OEBPS", os.path.relpath(full_path, OEBPS))
            epub.write(full_path, arc_path)

print(f"EPUB created: {OUTPUT_EPUB}")
