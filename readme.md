# Sentinel — Behavior-Based Anomaly Tracker

## Overview

Sentinel is a lightweight cybersecurity-focused web application that monitors device behavior and detects anomalies based on deviations from normal usage patterns.

This project focuses on behavior analysis (not malware signatures), inspired by UEBA (User & Entity Behavior Analytics) systems.

---

## Current Status

🚧 In Development (Phase: UI + Data Collection)

* [x] Static dashboard UI
* [ ] Data collector (in progress)
* [ ] Backend API
* [ ] Anomaly detection engine

---

## Features (Planned)

* Track system behavior (process usage, activity patterns)
* Detect anomalies (new processes, unusual activity times)
* Visual dashboard with logs and alerts
* Basic reporting system

---

## Project Structure

sentinel/
├── frontend/        # UI (HTML, CSS, JS)
├── collector/       # Python data collection script
├── data/            # Future processed data
└── README.md

---

## How to Run

### 1. Frontend

Open:
frontend/index.html

---

### 2. Collector (in progress)

Will log system activity locally using Python.

Dependencies:
pip install psutil

Run:
python collector/collector.py

---

## Notes

* This system detects behavioral anomalies, not malware directly
* Current version uses static/mock data in UI
* Backend and real-time integration will be added next

---

## Next Steps

* Build and run data collector
* Store logs in structured format
* Implement basic anomaly detection rules
* Connect frontend to backend

---

## Author

Immanuel
