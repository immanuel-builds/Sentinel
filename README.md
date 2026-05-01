# Sentinel — Behavior-Based Anomaly Tracker

## Overview
Sentinel is a minimal, rule-based security monitoring system designed to track local system behavior and flag irregularities. It provides a lightweight alternative to heavy monitoring suites, focusing on process execution patterns and resource utilization anomalies.

## Features
- **Behavioral Baselines**: Automatically establishes a baseline of "normal" activity hours to detect off-hours execution.
- **CPU Spike Detection**: Monitors system-wide CPU usage and flags spikes that deviate significantly from the session average.
- **Process Tracking**: Identifies and alerts on the appearance of new processes not observed during the initial baseline period.
- **Interactive Dashboard**: A real-time web interface for monitoring statistics, reviewing detailed logs, and managing anomaly states (Pending vs. Reviewed).
- **Persistent Management**: User-reviewed anomaly statuses are preserved across analysis cycles using stable MD5-based identifiers.

## Architecture
- **Collector**: A background utility using `psutil` to sample system processes and CPU usage at regular intervals.
- **Analyzer**: A heuristic-driven engine that processes raw logs, builds behavioral baselines, and generates structured anomalies.
- **Backend**: A FastAPI-based REST layer that serves JSON data from local storage and handles state updates for anomalies.
- **Frontend**: A clean, vanilla JavaScript dashboard featuring real-time data fetching, advanced filtering, and search capabilities.

## Setup Instructions

### 1. Install dependencies
Ensure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Run backend
Start the API server to serve logs and anomalies:
```bash
uvicorn backend.main:app --reload
```

### 3. Run collector/analyzer loop
Start the automated data collection and analysis pipeline in a separate terminal:
```bash
python runner.py
```

### 4. Open frontend
Simply open the dashboard in your web browser:
```text
frontend/index.html
```

## Example Anomalies

**New Process Detection**
```json
{
    "id": "2802d8f75486c5dde80e9a746b2ade3e",
    "type": "new_process",
    "process": "systemd",
    "reason": "New process 'systemd' detected during normal hours. This process was not observed in the baseline period.",
    "risk": "low",
    "status": "pending"
}
```

**Resource Usage Spike**
```json
{
    "id": "2acbc76b92d57765aa93926b2de84929",
    "type": "cpu_spike",
    "process": "System Wide",
    "reason": "CPU usage spike: 25.4% is 5.8x the session average of 4.4%.",
    "risk": "high",
    "status": "pending"
}
```

## Limitations
- **Rule-Based Heuristics**: Detection is based on fixed rules (CPU limits, time ranges) and lacks advanced machine learning or behavioral modeling.
- **Interval-Based**: The system captures snapshots of activity rather than high-frequency real-time event streaming.
- **Local Scope**: Monitoring is restricted to process execution and CPU utilization; it does not perform deep network packet inspection or file integrity monitoring.
