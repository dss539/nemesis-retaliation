#!/bin/bash
# clear tree and rebuild
cd /home/smithers/tts-extract/v2-dl || exit 1
rm -rf tree
cd /home/smithers/tts-extract || exit 1
python3 v2_tree.py
