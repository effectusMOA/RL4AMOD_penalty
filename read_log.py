
import os

file_path = r"saved_files/sumo_output/scenario_lux/sumo_log_10.txt"
if os.path.exists(file_path):
    size = os.path.getsize(file_path)
    print(f"File size: {size} bytes")
    if size > 0:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    else:
        print("File is empty.")
else:
    print("File does not exist.")
