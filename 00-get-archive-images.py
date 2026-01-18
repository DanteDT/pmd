'''
Retrieve 688 images from scan of 1851 first edition Mody Dick
Run ONCE and never again, since no need. Nobody is rescanning that book any time soon.
'''

import logging
import os
import shutil
import sys
import utils.utilities as utl
import utils.config as cfg

logger = utl.init_logger()
config = cfg.load_config()

LIB_URL = config['ext_resource']['lib_url'] 
PAGE_DIR=config['proj_dirs']['lib_pages']

# Fresh start - should NOT be needed since only run once
#utl.init_dir(PAGE_DIR)

# Currently there are 687 actual pages. 0 is a blank image, and 687 is a test-pattern image
for image in range(1):
    url=LIB_URL.format(image=image)
    logger.info(f"Working with URL {url}")
    utl.download_url(url, PAGE_DIR, f"moby_dick-1851-page_{image:04d}")
