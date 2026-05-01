# Cybersecurity Behavior Tracking System

A minimal, proactive security monitoring system that tracks system activity, detects anomalies (CPU spikes, off-hours activity), and provides an interactive dashboard.

## Structure

- `backend/`: FastAPI server and Rule-Based Analyzer.
- `collector/`: System activity logger (psutil).
- `data/`: JSON storage for logs and anomalies.
- `frontend/`: Vanilla JS dashboard with real-time updates.
- `runner.py`: Automation script to run the collection/analysis pipeline.

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
   In a separate terminal:
   ```bash
   python runner.py
   ```

4. **View the Dashboard:**
   Open `frontend/index.html` in your browser.

## Features

- **Proactive Detection:** Identifies CPU spikes relative to session averages.
- **Persistent Interaction:** Mark anomalies as "reviewed" in the UI; status persists across analysis cycles.
- **Live Updates:** Dashboard auto-refreshes every 7 seconds.
- **Robustness:** Atomic JSON writes and error-resistant data handling.
