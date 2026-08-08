from schemas import ResourceStatus
from state import HospitalState


def resource_intelligence_agent(state: HospitalState):

    resources = []

    for hospital in state["hospitals"]:

        hospital_resources = hospital.resources

        # Hospital is considered available if it has
        # at least one doctor. ICU availability is tracked
        # separately.
        if hospital_resources.doctors > 0:
            status = "Available"
        else:
            status = "Full"

        resource_status = ResourceStatus(
            hospital_id=hospital.hospital_id,
            hospital_name=hospital.hospital_name,
            icu_available=hospital_resources.icu_beds > 0,
            available_doctors=hospital_resources.doctors,
            available_ambulances=hospital_resources.ambulances,
            ct_scan_available=hospital_resources.ct_scan_available,
            status=status
        )

        resources.append(resource_status)

    return {
        "resource_status": resources
    }