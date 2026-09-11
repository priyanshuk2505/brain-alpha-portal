import json
import os

log_file = "/Users/priyanshukumar/.gemini/antigravity/brain/73ab022b-8892-4e1d-ad16-ee9b86041b37/.system_generated/logs/transcript.jsonl"
if not os.path.exists(log_file):
    print("Log file not found.")
    exit(1)

with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "snt_social_value" in line:
            try:
                step = json.loads(line)
                source = step.get("source")
                stype = step.get("type")
                print(f"Line {i}: source={source}, type={stype}, content_len={len(line)}")
            except Exception as e:
                print(f"Line {i} loads error: {e}")
