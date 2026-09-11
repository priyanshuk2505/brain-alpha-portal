import json

log_file = "/Users/priyanshukumar/.gemini/antigravity/brain/73ab022b-8892-4e1d-ad16-ee9b86041b37/.system_generated/logs/transcript.jsonl"
last_user_idx = -1
last_user_step = None

with open(log_file, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        try:
            step = json.loads(line)
            if step.get("type") == "USER_INPUT":
                last_user_idx = idx
                last_user_step = step
        except:
            pass

if last_user_step:
    print(f"Last USER_INPUT is at Line {last_user_idx}")
    print("Content length:", len(last_user_step.get("content", "")))
    print("Snippet of content:", repr(last_user_step.get("content", "")[:300]))
    print("End snippet of content:", repr(last_user_step.get("content", "")[-300:]))
else:
    print("No USER_INPUT found.")
