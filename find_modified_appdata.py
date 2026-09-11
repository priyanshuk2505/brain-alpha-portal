import os
import time

paths = [
    "/Users/priyanshukumar/.gemini/antigravity/scratch",
    "/Users/priyanshukumar/.gemini/antigravity/brain/73ab022b-8892-4e1d-ad16-ee9b86041b37"
]

now = time.time()
print("Checking for recently modified files under allowed paths:")
for path in paths:
    if not os.path.exists(path):
        continue
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                age_minutes = (now - mtime) / 60.0
                if age_minutes < 60.0:
                    print(f"  {file_path} - Age: {age_minutes:.1f} minutes, Size: {os.path.getsize(file_path)} bytes")
            except Exception as e:
                pass
