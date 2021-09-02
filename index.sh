#!/bin/bash

mkdir ../inverted_indexes
mkdir $2
python3 nltk_download.py
python3 indexing.py "$1" "$2" > $3
