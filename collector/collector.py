import psutil
import time
import os
import sys
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.utils import load_json, save_json

def run_collector():
    """
    Main loop to collect system activity data and log it to a JSON file.
    """
    data_dir = "data"
    log_filename = os.path.join(data_dir, "activity_log.json")

    print(f"Starting activity collector... Logging to {log_filename}")
    print("Press Ctrl+C to stop.")

    while True:
        try:
            # 1. Capture current timestamp in ISO format
            timestamp = datetime.now().isoformat()

            # 2. Get list of currently running process names
            processes = []
            for proc in psutil.process_iter(['name']):
                try:
                    processes.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # 3. Get current CPU usage percentage
            cpu_usage = psutil.cpu_percent(interval=1)

            # 4. Prepare the log entry
            entry = {
                "timestamp": timestamp,
                "processes": processes,
                "cpu": cpu_usage
            }

            # 5. Data storage: Use utils for safe appending
            data = load_json(log_filename, [])
            data.append(entry)
            save_json(log_filename, data)

            print(f"[{timestamp}] Logged {len(processes)} processes, CPU: {cpu_usage}%")

            # 6. Execute every 5 seconds.
            time.sleep(5)

        except KeyboardInterrupt:
            print("\nCollector stopped manually.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_collector()
