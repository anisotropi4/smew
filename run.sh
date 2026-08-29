#!/usr/bin/env bash

if [ ! -d data ]; then
    mkdir data
fi

URL=https://github.com/anisotropi4/smew/releases/download/v1.1.0

for file in CIF_ALL_FULL_DAILY_toc-full-20260509.CIF.gz TIPLOC-Locations-2026-08-18.csv
do
    if [ ! -f data/${file} ]; then
        curl -Lo data/${file} ${URL}/${file}
    fi
done

if [ ! -d venv ]; then
    uv venv venv
    source venv/bin/activate
    uv pip install --upgrade -r requirements.txt
else
    source venv/bin/activate
fi

./wtt-cif.py
./wtt-process.py
./wtt-point-visualize.py
