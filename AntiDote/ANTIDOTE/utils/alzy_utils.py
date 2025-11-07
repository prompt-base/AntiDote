import json, os, datetime

DATA_FILE = "alzy_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"reminders": [], "logs": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_reminder(task, time):
    data = load_data()
    data["reminders"].append({"task": task, "time": time})
    save_data(data)

def get_due_reminders():
    data = load_data()
    now = datetime.datetime.now().strftime("%H:%M")
    return [r for r in data["reminders"] if r["time"] == now]
