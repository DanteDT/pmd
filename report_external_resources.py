#!/usr/bin/env python3
import re
from pathlib import Path
import utils.config as config

config_data = config.load_config()
xhtml_dir = Path(config_data["proj_dirs"]["ch_xhtml"])

pattern_url = re.compile(r'(?:https?|ftps?)://[^"\s\'<>\)]*')
pattern_oc = re.compile(r'onclick="[^"]*')
pattern_js = re.compile(r'src="[^"]+\.js"')

mtx_pattern = {"URLs": pattern_url, 
               "OnClick": pattern_oc,
               "JavaScript": pattern_js}

# Named lists to hold matches of each type
match_url = {}
match_oc = {}
match_js = {}

counts = {topic: 0 for topic in mtx_pattern.keys()}
unicnt = {topic: 0 for topic in mtx_pattern.keys()}

fncount = 0

mtx_by_file = {"URLs": match_url,
               "OnClick": match_oc,
               "JavaScript": match_js}

for xhtml_file in sorted(xhtml_dir.glob("*.xhtml")):
    with open(xhtml_file, 'r', encoding='utf-8', errors='ignore') as fn:
        fncount += 1
        content = fn.read()
        for topic, pat in mtx_pattern.items():
            tcount = counts[topic]
            mtx = pat.findall(content)
            count = len(mtx)
            tcount += count
            if count > 0:
                mtx_by_file[topic].update({xhtml_file.name: mtx})
                counts[topic] = tcount

# For each topic, accumulate {"unique match": [filenames]}
# and sort each list by filename
unique_matches = {topic: {} for topic in mtx_pattern.keys()}
for topic, files in mtx_by_file.items():
    for filename, matches in files.items():
        for match in matches:
            unique_matches[topic].setdefault(match, []).append(filename)
    for match, filenames in unique_matches[topic].items():
        unique_matches[topic][match] = sorted(filenames)
        unicnt[topic] += len(filenames)

# Write to log file
log1_path = Path(r"log-rpt_ext_by_filename.log")
log2_path = Path(r"log-rpt_ext_by_resource.log")
with open(log1_path, 'w', encoding='utf-8') as log:
    log.write(f"External URLs Found in XHTML Files\n")
    log.write(f"Logged external resources from {fncount} files:\n -  URLs ({counts['URLs']})\n - OnClick ({counts['OnClick']})\n - JavaScript ({counts['JavaScript']}).\n")
    log.write(f"{'=' * 80}\n\n")

    if mtx_by_file:
        for topic, mtx in mtx_by_file.items():
            log.write(f"{topic}:\n")
            log.write(f"{'-' * 80}\n")
            if mtx:
                for filename, matches in sorted(mtx.items()):
                    log.write(f"{filename} ({len(matches)} matches):\n")
                    for match in sorted(set(matches)):
                        log.write(f"  - {match}\n")
                    log.write("\n")
            else:
                log.write("  None found.\n\n")

        for tpc in counts.keys():
            cnt = counts[tpc]
            log.write(f"Total {tpc} matches: {cnt}\n")
    else:
        log.write("No external URLs found.\n")

with open(log2_path, 'w', encoding='utf-8') as log:
    log.write(f"External URLs by Resource\n")
    log.write(f"Logged unique ext resources:\n   - URLs ({unicnt['URLs']})\n  - OnClick ({unicnt['OnClick']})\n  - JavaScript ({unicnt['JavaScript']}).\n")
    log.write(f"{'=' * 80}\n\n")

    if unique_matches:
        for topic, matches in unique_matches.items():
            log.write(f"{topic}:\n")
            log.write(f"{'-' * 80}\n")
            if matches:
                for match, filenames in sorted(matches.items()):
                    log.write(f"{match} ({len(filenames)} files):\n")
                    for filename in filenames:
                        log.write(f"  - {filename}\n")
                    log.write("\n")
            else:
                log.write("  None found.\n\n")
    else:
        log.write("No external URLs found.\n")

print(f"See {log1_path} and {log2_path} for details.")