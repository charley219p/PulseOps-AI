"""
PulseOps AI — HTTP intake API

This sits in front of your existing LangGraph pipeline (graph.py) and gives
the field-intake webpage something real to POST to. Streamlit itself can't
receive HTTP requests, so this runs as a separate small FastAPI service —
you can run it alongside app.py in the same Repl.

It accepts EITHER shape the intake form produces:
  - medic/nurse:      {"scenario": "...", "patients": [{"patient_id", "age",
                        "symptoms", "vitals", "arrival_mode"}, ...]}
  - bystander/caller:  {"incident_type", "location", "vehicles_involved",
                        "patients": [{"condition","severity","age_group"}],
                        "traffic", "ambulance_present", "incident_time"}

...converts whichever one arrives into your existing Patient objects, loads
a hospital directory, runs graph.invoke() exactly like app.py does, and
returns triage priorities + hospital recommendations as JSON.

Run it:
    pip install fastapi uvicorn
    uvicorn api:app --host 0.0.0.0 --port 8000

Then point the intake page's "PulseOps API endpoint" field at:
    https://<your-repl-url>:8000/api/intake
"""

import json
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph import graph
from schemas import Patient, Hospital

app = FastAPI(title="PulseOps AI Intake API")

# Wide open for now so the intake page (hosted anywhere) can reach this.
# Restrict allow_origins to your real frontend domain before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HOSPITALS_PATH = os.environ.get("PULSEOPS_HOSPITALS_PATH", "data/hospitals_default.json")

# A bystander gives us an age GROUP, not an age — your Patient model needs
# a number. These are rough midpoints, only used until a real age arrives.
AGE_GROUP_MIDPOINT = {"Child": 8, "Adult": 35, "Elderly": 72}


def load_hospitals() -> List[Hospital]:
    if not os.path.exists(HOSPITALS_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"No hospital directory at {HOSPITALS_PATH}. "
                   f"Add one (see data/hospitals_default.json) with real, "
                   f"current capacity — the sample file is placeholder data only.",
        )
    with open(HOSPITALS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Hospital(**h) for h in raw]


def bystander_to_patients(payload: dict) -> List[Patient]:
    """
    Converts a scene report into Patient objects.

    IMPORTANT: a bystander has no vitals to give, so `vitals` comes through
    empty. Your Clinical Priority Agent was designed around real vitals —
    treat anything triaged from a bystander report as provisional until a
    paramedic on scene overwrites it with a proper medic submission.
    """
    patients = []
    for i, p in enumerate(payload.get("patients", [])):
        if not p.get("condition"):
            continue
        age = AGE_GROUP_MIDPOINT.get(p.get("age_group"), 35)
        symptoms = [p["condition"], f"Bystander-reported severity: {p.get('severity', 'Unknown')}"]
        arrival_mode = "Ambulance" if payload.get("ambulance_present") else "Pending / self-arranged"
        patients.append(Patient(
            patient_id=f"B{i + 1:03d}",
            age=age,
            symptoms=symptoms,
            vitals={},
            arrival_mode=arrival_mode,
        ))
    return patients


def medic_to_patients(payload: dict) -> List[Patient]:
    return [Patient(**p) for p in payload.get("patients", [])]


def is_medic_payload(payload: dict) -> bool:
    if "scenario" not in payload or not payload.get("patients"):
        return False
    return "patient_id" in payload["patients"][0]


@app.post("/api/intake")
async def intake(payload: dict):
    medic = is_medic_payload(payload)

    try:
        if medic:
            patients = medic_to_patients(payload)
            scenario_name = payload["scenario"]
        else:
            patients = bystander_to_patients(payload)
            addr = (payload.get("location") or {}).get("address", "location unknown")
            scenario_name = f"{payload.get('incident_type', 'Incident')} — {addr}"
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read patients from payload: {e}")

    if not patients:
        raise HTTPException(status_code=422, detail="No patients were included in the report.")

    hospitals = load_hospitals()

    initial_state = {
        "patients": patients,
        "hospitals": hospitals,
        "priorities": [],
        "allocations": [],
        "logs": [],
        "resource_status": [],
        "allocation_decisions": [],
        "hospital_recommendations": [],
        "scenario": scenario_name,
        "final_report": "",
    }

    result = graph.invoke(initial_state)

    return {
        "scenario": scenario_name,
        "source": "medic" if medic else "bystander",
        "priorities": [p.dict() for p in result["priorities"]],
        "hospital_recommendations": [r.dict() for r in result["hospital_recommendations"]],
        "allocation_decisions": [d.dict() for d in result["allocation_decisions"]],
        "final_report": result["final_report"],
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
