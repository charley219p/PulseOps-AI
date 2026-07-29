from typing import TypedDict
from schemas import ResourceStatus
from schemas import AllocationDecision
from schemas import HospitalRecommendation
from schemas import (
    Patient,
    Hospital,
    ClinicalPriority,
    ResourceAllocation,
    DecisionLog
)
class HospitalState(TypedDict):

    patients: list[Patient]

    hospitals: list[Hospital]

    priorities: list[ClinicalPriority]

    allocations: list[ResourceAllocation]

    logs: list[DecisionLog]

    resource_status: list[ResourceStatus]

    allocation_decisions: list[AllocationDecision]

    hospital_recommendations: list[HospitalRecommendation]

    scenario: str

    final_report: str