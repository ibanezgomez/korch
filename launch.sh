#!/bin/bash
base_dir="/home/s/korch"
cd $base_dir
find . -depth -name "__pycache__" -type d -exec rm -Rf {} \;
python3 main.py
