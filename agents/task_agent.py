import json
import os
from datetime import datetime

TASKS_FILE = "data/tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(text):
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "text": text,
        "done": False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    tasks.append(task)
    save_tasks(tasks)
    return f"✅ Task added: {text}"

def list_tasks():
    tasks = load_tasks()
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        return "🎉 No pending tasks! You're all clear."
    lines = ["📋 *Your pending tasks:*\n"]
    for t in pending:
        lines.append(f"{t['id']}. {t['text']}")
    return "\n".join(lines)

def complete_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            return f"✅ Marked done: {t['text']}"
    return "❌ Task not found."

def delete_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            tasks.remove(t)
            save_tasks(tasks)
            return f"🗑️ Deleted: {t['text']}"
    return "❌ Task not found."