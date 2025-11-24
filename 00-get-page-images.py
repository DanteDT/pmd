'''
Retrieve 687 images from scan of 1851 first edition Mody Dick
Run ONCE and never again, since no need. Nobody is rescanning that book any time soon.
'''

import logging
import os
import shutil
import sys
import utils.utilities as utl

PAGE_DIR="1851_pages"

logger = utl.init_logger()

# Fresh start
#utl.init_dir(PAGE_DIR)

# Currently there are 687 actual pages. 0 is blank, and 687 is a test image
for image in range(1):
    url=f"https://ia800205.us.archive.org/BookReader/BookReaderImages.php?zip=/32/items/mobydickorwhale01melv/mobydickorwhale01melv_jp2.zip&file=mobydickorwhale01melv_jp2/mobydickorwhale01melv_{image+1:04d}.jp2&id=mobydickorwhale01melv"
    logger.info(f"Working with URL {url}")
    utl.download_url(url, PAGE_DIR, f"moby_dick-1851-page_{image+1:04d}")
