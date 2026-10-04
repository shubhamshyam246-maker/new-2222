# Automobile Sales Dashboard (Plotly & Dash)

Final Assignment, Part 2 - DV0101EN.

## Files
- `DV0101EN-Final-Assign-Part2.py` - the Dash app (submit this file)
- `make_recession_image.py` - creates `RecessionReportgraphs.png` from the real data
- `assets/style.css` - dashboard styling (loaded automatically by Dash)
- `DV0101EN-Final-Assign-Part1_completed.ipynb` - Part 1 notebook
- `SUBMISSION_CHECKLIST.md` - tick-list for submitting
- `requirements.txt` - dependencies

## Run
    pip install -r requirements.txt
    python DV0101EN-Final-Assign-Part2.py
Open http://127.0.0.1:8050 (needs internet; or place `historical_automobile_sales.csv`
next to the script as an offline fallback).

## Features
- Dropdown 1: Yearly Statistics / Recession Period Statistics
- Dropdown 2: year (1980-2023), enabled only for Yearly Statistics
- Recession report: avg sales line, sales by vehicle type bar, advertising pie,
  unemployment-vs-sales bar
- Yearly report: yearly avg line, monthly sales line, sales by vehicle type bar,
  advertising pie

## Recession image
    python make_recession_image.py
