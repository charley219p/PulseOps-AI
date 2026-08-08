from schemas import HospitalRecommendation, DecisionLog
from state import HospitalState


def calculate_score(priority, hospital):
    """
    Calculate a patient-specific hospital score.

    First, hospitals that cannot satisfy mandatory requirements
    are eliminated. Then the remaining hospitals are scored based
    on clinical requirements, resources and travel time.
    """

    resources = hospital.resources

    # ---------------------------------------------------------
    # HARD REQUIREMENTS
    # ---------------------------------------------------------

    # ICU is mandatory for patients who need ICU
    if priority.needs_icu and resources.icu_beds <= 0:
        return None

    # CT scan is mandatory when required
    if priority.needs_ct_scan and not resources.ct_scan_available:
        return None

    # A hospital should have at least one doctor
    if resources.doctors <= 0:
        return None

    score = 0

    # ---------------------------------------------------------
    # CLINICAL REQUIREMENTS
    # ---------------------------------------------------------

    # Strong preference for ICU availability
    if priority.needs_icu:
        score += 100

    # Strong preference for CT availability
    if priority.needs_ct_scan:
        score += 80

    # ---------------------------------------------------------
    # HOSPITAL RESOURCES
    # ---------------------------------------------------------

    # Doctors matter, but should NOT dominate clinical requirements
    score += min(resources.doctors, 10) * 3

    # Ambulances are useful, but less important than patient needs
    score += min(resources.ambulances, 5) * 2

    # More ICU capacity is useful for critical patients
    if priority.needs_icu:
        score += min(resources.icu_beds, 10) * 5

    # ---------------------------------------------------------
    # DISTANCE / TRAVEL TIME
    # ---------------------------------------------------------

    score -= hospital.distance_km * 3
    score -= hospital.travel_time_min * 2

    return score


def hospital_selection_agent(state: HospitalState):

    recommendations = []
    logs = []

    # Track provisional resource usage while assigning
    # multiple patients in the same batch.
    remaining_icu = {
        h.hospital_id: h.resources.icu_beds
        for h in state["hospitals"]
    }

    remaining_doctors = {
        h.hospital_id: h.resources.doctors
        for h in state["hospitals"]
    }

    for priority in state["priorities"]:

        best_hospital = None
        best_score = float("-inf")

        for hospital in state["hospitals"]:

            resources = hospital.resources

            # -------------------------------------------------
            # Check current/provisional resources
            # -------------------------------------------------

            if remaining_doctors[hospital.hospital_id] <= 0:
                continue

            if (
                priority.needs_icu
                and remaining_icu[hospital.hospital_id] <= 0
            ):
                continue

            if (
                priority.needs_ct_scan
                and not resources.ct_scan_available
            ):
                continue

            # -------------------------------------------------
            # Calculate score
            # -------------------------------------------------

            score = calculate_score(priority, hospital)

            if score is None:
                continue

            # -------------------------------------------------
            # Prefer hospitals with more remaining capacity
            # -------------------------------------------------

            if priority.needs_icu:
                score += remaining_icu[hospital.hospital_id] * 10

            score += remaining_doctors[hospital.hospital_id] * 2

            # -------------------------------------------------
            # Select best hospital
            # -------------------------------------------------

            if score > best_score:
                best_score = score
                best_hospital = hospital

        # -----------------------------------------------------
        # No hospital can satisfy the patient
        # -----------------------------------------------------

        if best_hospital is None:

            recommendations.append(
                HospitalRecommendation(
                    patient_id=priority.patient_id,
                    hospital_id="NONE",
                    hospital_name="No Suitable Hospital",
                    score=-1,
                    estimated_travel_time=0,
                    reason="No hospital currently satisfies the patient's resource requirements."
                )
            )

            logs.append(
                DecisionLog(
                    agent="Hospital Selection Agent",
                    decision=f"{priority.patient_id} -> No suitable hospital",
                    reason="No hospital has sufficient resources for this patient.",
                    confidence=1.0
                )
            )

            continue

        hospital_id = best_hospital.hospital_id

        # -----------------------------------------------------
        # Reserve provisional resources
        # -----------------------------------------------------

        remaining_doctors[hospital_id] -= 1

        if priority.needs_icu:
            remaining_icu[hospital_id] -= 1

        # -----------------------------------------------------
        # Create recommendation
        # -----------------------------------------------------

        recommendation = HospitalRecommendation(
            patient_id=priority.patient_id,
            hospital_id=best_hospital.hospital_id,
            hospital_name=best_hospital.hospital_name,
            score=best_score,
            estimated_travel_time=best_hospital.travel_time_min,
            reason=(
                f"Selected based on patient requirements, "
                f"resource availability and travel time. "
                f"Operational score: {best_score:.1f}"
            )
        )

        recommendations.append(recommendation)

        logs.append(
            DecisionLog(
                agent="Hospital Selection Agent",
                decision=f"Selected {best_hospital.hospital_name}",
                reason=recommendation.reason,
                confidence=1.0
            )
        )

    return {
        "hospital_recommendations": recommendations,
        "logs": state["logs"] + logs
    }