import json
from schemas import Patient, Hospital


def load_patients(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Patient(**patient) for patient in data]

def load_scenario(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_hospitals(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Change data["hospitals"] -> data
    return [Hospital(**hospital) for hospital in data]