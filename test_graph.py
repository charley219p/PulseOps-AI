from graph import graph

from utils.data_loader import (
    load_patients,
    load_hospitals,
)

state = {
    "patients": load_patients("data/patients.json"),
    "hospitals": load_hospitals("data/hospitals.json"),
    "priorities": [],
    "allocations": [],
    "logs": [],
    "scenario": "Heart Attack",
    "final_report": "",
}

result = graph.invoke(state)

print("\n===== PRIORITIES =====")
for priority in result["priorities"]:
    print(priority)

print("\n===== LOGS =====")
for log in result["logs"]:
    print(log)

print("\n===== RESOURCE STATUS =====")

for resource in result["resource_status"]:
    print(resource)

print("\n===== DECISIONS =====")

for decision in result["allocation_decisions"]:
    print(decision)
print("\n===== FINAL REPORT =====")
print(result["final_report"])