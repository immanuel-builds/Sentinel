import json
import os
from typing import Any

def load_json(file_path: str, default_value: Any = None) -> Any:
    """Safely load a JSON file, returning default_value if missing, empty, or malformed."""
    if default_value is None:
        default_value = []

    if not os.path.exists(file_path):
        return default_value

    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return default_value

def save_json(file_path: str, data: Any) -> bool:
    """Safely save data to a JSON file using a temporary file to avoid corruption."""
    try:
        # Ensure directory exists
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        temp_file = file_path + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, file_path)
        return True
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False
