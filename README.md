# Manufacturing KPI Dashboard

A real-time manufacturing line monitoring dashboard built with Python and Streamlit.

## Overview

This dashboard simulates a production monitoring system across multiple manufacturing lines. It tracks key performance indicators, detects anomalies, and surfaces alerts, providing shift managers and operations teams with actionable insights at a glance.

I built this as a personal project to explore data visualization and anomaly detection in a manufacturing context.

## Features

- **KPI Cards** — real-time output, efficiency, and downtime metrics with delta comparisons vs the previous 12-hour window
- **Anomaly Detection** — Z-score based detection that flags unusual output readings relative to each line's own historical behavior
- **Alerts Panel** — combines efficiency threshold alerts and anomaly alerts in one view
- **Interactive Filters** — filter by production line, adjust efficiency threshold, and tune anomaly sensitivity
- **Anomaly Log** — detailed table of flagged readings with Z-scores
- **Raw Data Table** — full view of all readings sorted by most recent

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Scipy

## Live Demo

[View the live dashboard](https://manufacturing-kpi-dashboard-app.streamlit.app/)

## Run Locally

## Run Locally

1. Clone the repo
```
git clone https://github.com/tariye-i/manufacturing-kpi-dashboard.git
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the app
```
streamlit run app.py
```