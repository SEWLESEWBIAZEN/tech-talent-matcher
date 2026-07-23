import json
import os

DATA_FILE = "scenarios.json"

def load_scenarios():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_scenarios(scenarios):
    with open(DATA_FILE, "w") as f:
        json.dump(scenarios, f, indent=4)