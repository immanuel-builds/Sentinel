# Sentinel — Behavior-Based Anomaly Tracker

## Overview
Sentinel is a minimal, rule-based security monitoring system designed to track local system behavior and flag irregularities. It provides a lightweight alternative to heavy monitoring suites, focusing on process execution patterns and resource utilization anomalies.

## Features
- **Hybrid Detection Engine**: Combines deterministic rules with statistical modeling for improved anomaly detection.
- **Behavioral Baselines**: Automatically establishes a baseline of "normal" activity hours to detect off-hours execution.
- **Statistical CPU Monitoring**: Uses mean and standard deviation to identify anomalous resource usage.
- **Process Frequency Analysis**: Detects rare processes that appear in less than 5% of logs.
- **Interactive Dashboard**: A real-time web interface for monitoring statistics, reviewing detailed logs, and managing anomaly states (Pending vs. Reviewed).
- **Persistent Management**: User-reviewed anomaly statuses are preserved across analysis cycles using stable MD5-based identifiers.

## Detection Methods

### 1. Rule-Based Detection
- **New Process Detection**: Flags any process not observed in the initial baseline period.
- **Time Anomalies**: Identifies system activity outside of established normal hours.
- **CPU Spike Thresholds**: Uses fixed multipliers against the session average.

### 2. Statistical Detection
- **CPU Deviation**: Flags usage that exceeds the mean by 2 or 3 standard deviations (Z-score analysis).
- **Rare Process Detection**: Identifies processes based on their occurrence frequency across all captured logs.

### 3. Machine Learning Detection
- **Isolation Forest**: Sentinel uses an unsupervised Isolation Forest model to detect global outliers in system behavior.
- **Pattern Matching**: It identifies unusual combinations of CPU usage and activity time that might not be caught by simple thresholds.
- **Explainability**: While powered by ML, results are interpreted and presented as explainable anomalies focusing on resource/time patterns.

"This ML layer complements rule-based and statistical detection. All results remain explainable."

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
