# Download individual page images from URLs in image-links.csv.
#  + Tab-delimited file: filename, URL
#  + Save each image as "page_<filename>.jpg"

import os
import pandas as pd
import utils.utilities as utl

img_root  = "extra_img_Blog_orig"
img_loc   = "67-img-to-download_Blog.csv"
file_path = os.path.join(img_root, img_loc)

logger = utl.init_logger()

df = pd.read_csv(file_path, delimiter='\t')
dl_good = 0
dl_fail = 0

# For each row in df, download URL and save as "page_<filename>.jpg"
for index, row in df.iterrows():
    filename = row['name']
    url = row['url']
    # Download the image from url and save as "page_<filename>.jpg"
    # (Implementation of download logic goes here)
    try:
        utl.download_url(url, img_root, f"page_{filename}.jpg")
        dl_good += 1
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        dl_fail += 1

logger.info(f"Completed processing {len(df)} images from file \"{file_path}\".")
logger.info(f":: Downloaded {dl_good} images successfully, {dl_fail} failures.")