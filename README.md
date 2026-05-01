# Cybersecurity Behavior Tracking System

A minimal, proactive security monitoring system that tracks system activity, detects anomalies (CPU spikes, off-hours activity), and provides an interactive dashboard.

## Project Structure

- `backend/`: FastAPI server and Rule-Based Analyzer.
- `collector/`: System activity logger using `psutil`.
- `data/`: Centralized JSON storage for activity logs and detected anomalies.
- `frontend/`: Vanilla JavaScript dashboard with real-time updates and interactive controls.
- `runner.py`: Root-level automation script orchestrating the collection and analysis pipeline.

## Getting Started

1. **Install Dependencies:**
   ```bash
   pip install fastapi uvicorn psutil
   ```

2. **Start the Backend:**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Run the Automation Pipeline:**
   In a separate terminal, start the continuous monitoring cycle:
   ```bash
   python runner.py
   ```

4. **View the Dashboard:**
   Open `frontend/index.html` in your web browser.

## API Endpoints

- `GET /logs`: Returns full list of raw system logs.
- `GET /anomalies`: Returns full list of detected anomalies.
- `GET /summary`: Returns high-level statistics (total events, anomaly count, unique processes).
- `PATCH /anomalies/{id}`: Updates an anomaly's status. Accepts JSON: `{"status": "reviewed"}`.

## Anomaly Data Structure

Each anomaly entry in `data/anomalies.json` follows this schema:
```json
{
    "id": "md5_hash_string",
    "timestamp": "ISO-8601-string",
    "type": "cpu_spike | new_process | time_anomaly",
    "process": "process_name | System Wide",
    "reason": "Human-readable explanation of the alert",
    "risk": "low | medium | high",
    "status": "pending | reviewed"
}
```

## Anomaly Lifecycle

1. **Detection**: The `analyzer.py` script identifies unusual patterns and flags them as anomalies with a default status of `pending`.
2. **Review**: Security analysts use the dashboard to inspect alerts. Clicking "Mark as Reviewed" sends a `PATCH` request to the backend.
3. **Persistence**: The updated status is saved to disk. Subsequent analysis runs match existing anomalies by their unique `id` and preserve their reviewed status, ensuring work is not lost.

## Core Features

- **Heuristic Analysis**: Detects CPU spikes relative to session averages and identifies off-hours activity based on automated baselining.
- **State Management**: Persistent anomaly statuses that survive system restarts and analysis cycles.
- **Real-time Visualization**: Dashboard auto-refreshes every 7 seconds to display the latest system state.
- **Data Integrity**: Uses atomic JSON writes with temporary files to prevent data corruption during simultaneous read/write operations.
