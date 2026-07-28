from schemas import ResourceStatus
from state import HospitalState


def resource_intelligence_agent(state: HospitalState):

    resources = []

    for hospital in state["hospitals"]:

        status = ResourceStatus(
            hospital_id=hospital.hospital_id,
            hospital_name=hospital.hospital_name,
            icu_available=hospital.resources.icu_beds > 0,
            available_doctors=hospital.resources.doctors,
            available_ambulances=hospital.resources.ambulances,
            ct_scan_available=hospital.resources.ct_scan_available,
            status="Available" if hospital.resources.icu_beds > 0 else "Full",
        )

        resources.append(status)

    return {
        "resource_status": resources
    }