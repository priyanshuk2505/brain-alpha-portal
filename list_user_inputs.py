import json

log_file = "/Users/priyanshukumar/.gemini/antigravity/brain/73ab022b-8892-4e1d-ad16-ee9b86041b37/.system_generated/logs/transcript.jsonl"
with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            step = json.loads(line)
            if step.get("type") == "USER_INPUT":
                print(f"Line {i}: content length: {len(step.get('content', ''))}, snippet: {step.get('content', '')[:100].replace(chr(10), ' ')}")
        except Exception as e:
            pass
