# Sentinel — Behavior-Based Anomaly Tracker

## Overview

Sentinel is a lightweight cybersecurity-focused web application that monitors device behavior and detects anomalies based on deviations from normal usage patterns.

---

## Project Structure

sentinel/
│
├── frontend/        # User Interface
│   ├── index.html   # Main dashboard
│   ├── style.css    # Dashboard styling
│   └── script.js    # Data fetching & UI logic
│
├── backend/         # Logic & API
│   ├── main.py      # FastAPI application
│   ├── analyzer.py  # Anomaly detection logic
│   └── utils.py     # Shared JSON utilities
│
├── collector/       # Data Collection
│   └── collector.py # System activity logger
│
├── data/            # Local Storage
│   ├── activity_log.json
│   └── anomalies.json
│
├── runner.py        # Pipeline automation
└── README.md

---

## How to Run

### 1. Install Dependencies

```bash
pip install psutil fastapi uvicorn
```

### 2. Start the Backend API

```bash
uvicorn backend.main:app --reload
```

### 3. Run the Automation Pipeline

This script runs the collector and analyzer in a continuous loop.

```bash
python runner.py
```

### 4. Open the Dashboard

Open `frontend/index.html` in your browser.

---

## Folder Explanations

- **frontend/**: The user interface built with vanilla HTML/CSS/JS. Supports real-time monitoring with auto-refresh and interactive anomaly management.
- **backend/**: Contains the FastAPI server, the analysis engine, and common utilities.
- **collector/**: Scripts to gather raw system activity like running processes and CPU usage.
- **data/**: Central storage for logs and detected anomalies in JSON format.
- **runner.py**: The orchestrator that automates the data collection and analysis lifecycle.

---

## Author

Sentinel Team
