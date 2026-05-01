import psutil
import time
import json
import os
from datetime import datetime

def run_collector():
    """
    Main loop to collect system activity data and log it to a JSON file.
    """
    log_filename = "activity_log.json"

    print("Starting activity collector... Press Ctrl+C to stop.")

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
                    # Skip processes that disappear or are inaccessible
                    pass

            # 3. Get current CPU usage percentage
            # interval=1 means it will sample CPU usage over 1 second
            cpu_usage = psutil.cpu_percent(interval=1)

            # 4. Prepare the log entry
            entry = {
                "timestamp": timestamp,
                "processes": processes,
                "cpu": cpu_usage
            }

            # 5. Data storage: Handle file creation and appending safely
            # To keep the JSON file a valid list of objects, we read the existing list,
            # append the new entry, and write it back.
            if os.path.exists(log_filename):
                try:
                    with open(log_filename, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    # If the file is empty or corrupted, start with an empty list
                    data = []
            else:
                data = []

            data.append(entry)

            # 6. Write back to file safely using a temporary file to avoid corruption
            temp_filename = log_filename + ".tmp"
            with open(temp_filename, 'w') as f:
                json.dump(data, f, indent=4)

            os.replace(temp_filename, log_filename)

            print(f"[{timestamp}] Logged {len(processes)} processes, CPU: {cpu_usage}%")

            # 7. Execute every 5-10 seconds.
            # Since cpu_percent(interval=1) already took 1 second, we sleep for 5 more.
            time.sleep(5)

        except KeyboardInterrupt:
            print("\nCollector stopped manually.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_collector()
