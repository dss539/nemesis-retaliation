#!/bin/bash
# clear stale v2-dl outputs and re-download with corrected classification
cd /home/smithers/tts-extract/v2-dl || exit 1
rm -rf base unsorted tmp tree
cd /home/smithers/tts-extract || exit 1
python3 v2_download.py
