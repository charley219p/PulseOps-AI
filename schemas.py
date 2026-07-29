from pydantic import BaseModel, Field
from typing import List, Optional
#patient
class Patient(BaseModel):
    patient_id: str
    age: int
    symptoms: List[str]
    vitals: dict
    arrival_mode: str
#hospital resources
class HospitalResource(BaseModel):
    icu_beds: int
    doctors: int
    ambulances: int
    ventilators: int
    ct_scan_available: bool
#hospital
class Hospital(BaseModel):
    hospital_id: str
    hospital_name: str
    distance_km: float
    travel_time_min: int
    resources: HospitalResource
#climical priority
class ClinicalPriority(BaseModel):
    patient_id: str
    severity: str
    priority_score: int
    needs_icu: bool
    needs_ct_scan: bool
    reason: str
# resources allocation
class ResourceAllocation(BaseModel):
    patient_id: str
    assigned_hospital: str
    assigned_doctor: Optional[str] = None
    assigned_ambulance: Optional[str] = None
    assigned_icu: bool
    eta_minutes: int
class DecisionLog(BaseModel):
    agent: str
    decision: str
    reason: str
    confidence: float
class ResourceStatus(BaseModel):
    hospital_id: str
    hospital_name: str
    icu_available: bool
    available_doctors: int
    available_ambulances: int
    ct_scan_available: bool
    status: str
class AllocationDecision(BaseModel):
    patient_id: str
    hospital_id: str
    hospital_name: str
    decision: str
    assigned_icu: bool
    assigned_doctor: bool
    transfer_required: bool
    reason: str
class HospitalRecommendation(BaseModel):
    patient_id: str
    hospital_id: str
    hospital_name: str
    score: float
    reason: str
    