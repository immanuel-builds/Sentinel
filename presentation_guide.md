# Sentinel: Project Presentation Guide

## 1. Project Pitch (30–45 Seconds)
"Sentinel is a behavior-based anomaly detection system designed to monitor local system activity. Unlike traditional security tools that only look for known 'bad' files, Sentinel tracks how your computer is actually behaving—like which processes are running and how much CPU they use. It’s useful because it can spot 'silent' threats, such as crypto-miners or unauthorized background tasks, that don't have a signature yet. What makes Sentinel different is its multi-layer detection engine: it combines simple rules with statistical baselining and machine learning to provide a detection system that is both reliable and intelligent."

---

## 2. Technical Explanation (2–3 Minutes)

### A. Data Flow
The system follows a linear pipeline:
1. **Collector**: A Python script runs in the background, using the `psutil` library to snapshot running processes and CPU usage every few seconds.
2. **Logs**: This raw data is stored in `activity_log.json`.
3. **Analyzer**: The heart of the system. It reads the logs and applies three layers of logic to identify anomalies.
4. **Anomalies**: Flagged events are saved in `anomalies.json` with unique IDs and risk scores.
5. **Backend**: A FastAPI server provides a RESTful interface to access these logs and anomalies.
6. **Frontend**: A vanilla JavaScript dashboard fetches this data in real-time, allowing a security analyst to search, filter, and review alerts.

### B. Detection Layers
1. **Rule-Based**: This is our foundation. It checks for specific things we know are unusual, like a process starting for the first time or activity happening during off-hours.
2. **Statistical**: This layer calculates a 'normal' baseline for your specific session using mean and standard deviation. It flags anything that deviates significantly from that average.
3. **Machine Learning**: We use an **Isolation Forest** model. Instead of looking at single values, it looks at the *relationship* between CPU usage and time to find global outliers that rules might miss.

### C. Why a Hybrid Approach?
We chose a hybrid model for three reasons:
- **Reliability**: Rules always work, even if you only have 1 minute of data.
- **Adaptability**: Statistical detection adjusts to how you are using your computer *right now*.
- **Intelligence**: ML finds complex patterns that are too difficult to write manually as rules.

---

## 3. Detection Types (Simple Language)

- **Rule-Based (Deterministic Checks)**:
  "Think of this like a security guard with a list of rules. If a process starts at 3 AM when the office is closed, it rings the bell. It's simple, fast, and never misses the obvious."

- **Statistical (Deviation Analysis)**:
  "This is like knowing your friend usually speaks at a certain volume. If they suddenly start shouting, you notice it's unusual. The system calculates the 'average' behavior and alerts us when things get too loud."

- **Machine Learning (Pattern Recognition)**:
  "This doesn't use any rules or averages. It's like a computer looking at a big crowd and pointing out the one person walking in the opposite direction. it finds things that just 'don't fit' the overall pattern."

---

## 4. Defense Questions & Answers

**Q1: Why not only use machine learning for detection?**
*   **Answer**: Machine learning is powerful but "hungry"—it needs a lot of data to be accurate. If we only used ML, the system would be useless for the first 20 minutes of starting up. By using a hybrid approach, our **Rule-Based** layer protects the system immediately, while the **ML** layer adds intelligence once enough data is collected.

**Q2: what are the main limitations of your system?**
*   **Answer**: Currently, Sentinel is a **local-only** tool focusing on CPU and process lists. It does not monitor network traffic or deep file contents (like antivirus). Also, because it's **interval-based** (sampling every few seconds), it might miss an anomaly that starts and ends very quickly between those samples.

**Q3: How is this different from a standard antivirus software?**
*   **Answer**: Traditional antivirus uses **Signatures** (a database of known bad files). If a virus is brand new (Zero-day), the antivirus might miss it. Sentinel uses **Behavioral Analysis**. We don't care what the file name is; we care if it's acting weirdly—like hogging CPU at midnight or starting without permission.

**Q4: What happens if the collected data is insufficient or corrupted?**
*   **Answer**: I implemented a **Robustness Layer**. If the log file is missing or corrupted, the system returns a safe empty list instead of crashing. If there are fewer than 10 entries, the Statistical layer skips processing, and if there are fewer than 20, the ML layer skips. The Rule-Based layer always acts as our reliable safety net.

**Q5: Why did you not implement a user authentication system?**
*   **Answer**: For this phase of the project, I focused on the **detection engine** and the **real-time data pipeline**. Adding authentication would have shifted the focus toward web development rather than cybersecurity analysis. In a production version, this would be the first thing added to the backend using OAuth or JWT.

---

## 5. Slide Structure (8–10 Slides)

1.  **Title Slide**:
    *   Project Name: Sentinel
    *   Sub-title: Behavior-Based Anomaly Detection System
    *   Presented by: [Your Name]
2.  **Problem Statement**:
    *   Threats are evolving beyond file signatures.
    *   Traditional tools miss "zero-day" behavioral threats (e.g., miners).
    *   Need for lightweight, behavior-based monitoring.
3.  **Solution Overview**:
    *   Real-time system activity tracking.
    *   Three-layer hybrid detection engine.
    *   Interactive dashboard for forensic review.
4.  **System Architecture**:
    *   Backend: FastAPI (Python)
    *   Automation: Continuous Runner loop
    *   Storage: Atomic JSON flat-files
    *   Frontend: Vanilla HTML/CSS/JavaScript
5.  **Data Flow**:
    *   Show the path: Collector → Activity Logs → Analyzer → Anomaly DB → API → UI.
6.  **Detection Methods**:
    *   Rule-Based: Off-hours, new processes.
    *   Statistical: Z-score analysis for CPU spikes.
    *   Machine Learning: Isolation Forest pattern matching.
7.  **System Robustness**:
    *   Atomic writes to prevent corruption.
    *   Tiered fallback (degrades gracefully if ML/Stats layers fail).
8.  **Demo Screenshots**:
    *   Show the Dashboard, Filtered Logs, and Detected Anomalies.
9.  **Limitations & Future Scope**:
    *   Limitations: Local-only, interval-based sampling.
    *   Future: Real-time streaming (WebSockets), Network monitoring.
10. **Conclusion**:
    *   Sentinel provides a functional, explainable, and multi-layered approach to security monitoring.

---

## 6. Future Improvements

*   **Real-time Streaming**: Migrate from interval-based polling to real-time event streaming using **WebSockets** for instant dashboard updates.
*   **Multi-Node Monitoring**: Expand the system to monitor multiple computers from a single central dashboard (Enterprise support).
*   **Network Inspection**: Integrate packet capture (e.g., using `scapy`) to detect anomalous outbound network traffic or data exfiltration.
*   **Advanced ML Models**: Experiment with **Autoencoders** (Deep Learning) for even more sensitive behavioral anomaly detection as the dataset grows.
*   **Response Actions**: Implement automated responses, such as killing a process or isolating the machine when a 'Critical' risk anomaly is detected.
