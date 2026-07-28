from schemas import HospitalRecommendation, DecisionLog
from state import HospitalState


def calculate_score(priority, hospital):
    score = 0

    if priority.needs_icu:
        if hospital.resources.icu_beds > 0:
            score += 50
        else:
            score -= 100

    score += hospital.resources.doctors * 5
    score += hospital.resources.ambulances * 3
    score -= hospital.distance_km * 2
    score -= hospital.travel_time_min

    return score


def hospital_selection_agent(state: HospitalState):

    recommendations = []
    logs = []

    for priority in state["priorities"]:

        best_hospital = None
        best_score = float("-inf")

        for hospital in state["hospitals"]:

            score = calculate_score(priority, hospital)

            if score > best_score:
                best_score = score
                best_hospital = hospital

        recommendation = HospitalRecommendation(
            patient_id=priority.patient_id,
            hospital_id=best_hospital.hospital_id,
            hospital_name=best_hospital.hospital_name,
            score=best_score,
            estimated_travel_time=best_hospital.travel_time_min,
            reason=f"Highest operational score ({best_score:.1f})"
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