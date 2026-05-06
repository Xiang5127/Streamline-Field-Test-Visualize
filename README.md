# Delivery PoD Telemetry Dashboard

A Streamlit-based field-test visualization dashboard for analyzing Proof-of-Delivery (PoD) telemetry records. The app helps explore delivery capture locations, upload performance, building detection outcomes, GPS quality, latency, and raw field-test metadata.

## Deployed App

Access the live app here:

[https://streamline-field-test-visualize.streamlit.app/](https://streamline-field-test-visualize.streamlit.app/)

## Features

- **Operational KPIs**: View visible records, upload success rate, labeled cases, building detection accuracy, and override count.
- **Interactive map explorer**: Visualize capture points using Folium with optional route flow display.
- **Node details**: Inspect individual telemetry records, including tracking number, capture time, GPS coordinates, confidence score, upload latency, battery level, and image URL.
- **Quality analysis**: Review confidence, GPS accuracy, latency bands, and building detection performance.
- **Confusion matrix**: Evaluate building detection results against ground-truth labels.
- **Raw records table**: Browse and filter the underlying field-test dataset.
- **Sidebar filters**: Filter by captured date range, tracking number, status, upload result, building detection result, override records, and quality bands.

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── DESIGN.md
├── supabase_data/
│   └── field_test_records_rows.csv
└── .streamlit/
    └── config.toml
```

## Tech Stack

- **Python**
- **Streamlit** for the dashboard UI
- **Pandas** and **NumPy** for data processing
- **Folium** and **streamlit-folium** for interactive maps
- **Matplotlib** for charts and confusion matrix visualization

## Dataset

The dashboard loads field-test records from:

```text
supabase_data/field_test_records_rows.csv
```

Expected fields include telemetry and evaluation values such as:

- `captured_at`
- `tracking_number`
- `latitude`
- `longitude`
- `gps_accuracy_metres`
- `model_confidence`
- `building_detected`
- `ground_truth_is_building`
- `detection_overridden`
- `upload_success`
- `upload_latency_ms`
- `battery_level`
- `image_url`

## Evaluation Criteria

The app uses fixed thresholds for reproducible field-test analysis:

| Metric | Threshold |
|---|---:|
| Model confidence | `>= 0.80` |
| GPS accuracy | `<= 10 m` |
| Upload latency anomaly | `>= 1000 ms` |
| Map click tolerance | `12 m` |

## Local Setup

### 1. Clone or open the project

Open this project folder in your development environment.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python -m streamlit run app.py
```

The app will usually be available at:

```text
http://localhost:8501
```

## Deployment

This project is deployed on Streamlit Community Cloud:

[https://streamline-field-test-visualize.streamlit.app/](https://streamline-field-test-visualize.streamlit.app/)

For Streamlit Cloud deployment, ensure the repository includes:

- `app.py`
- `requirements.txt`
- `supabase_data/field_test_records_rows.csv`
- `.streamlit/config.toml`, if custom configuration is required

## Purpose

This dashboard was built to support academic field-test analysis for a Proof-of-Delivery verification workflow. It provides a visual and quantitative interface for reviewing delivery capture quality, telemetry reliability, and building detection behavior during real-world testing.
