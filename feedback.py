import json
import os
from datetime import datetime

FEEDBACK_FILE = "feedback_log.json"

def log_feedback(question, answer, rating):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "rating": rating
    }
    logs = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE) as f:
            logs = json.load(f)
    logs.append(entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(logs, f, indent=2)