from schemas import AllocationDecision, DecisionLog
from state import HospitalState


def decision_engine(state: HospitalState):

    decisions = []
    logs = []

    
   
    for priority in state["priorities"]:
        recommendation = next(
            r for r in state["hospital_recommendations"]
            if r.patient_id == priority.patient_id
        )

        hospital = next(
            h for h in state["hospitals"]
            if h.hospital_id == recommendation.hospital_id
        )

        resources = hospital.resources
        

        if priority.needs_icu:

            if resources.icu_beds > 0:

                decision = AllocationDecision(
                    patient_id=priority.patient_id,
                    hospital_id=hospital.hospital_id,
                    hospital_name=hospital.hospital_name,
                    decision="Allocate ICU",
                    assigned_icu=True,
                    assigned_doctor=True,
                    transfer_required=False,
                    reason="ICU bed available."
                )

            else:

                decision = AllocationDecision(
                    patient_id=priority.patient_id,
                    hospital_id=hospital.hospital_id,
                    hospital_name=hospital.hospital_name,
                    decision="Transfer Patient",
                    assigned_icu=False,
                    assigned_doctor=False,
                    transfer_required=True,
                    reason="No ICU bed available."
                )

        else:

            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id=hospital.hospital_id,
                hospital_name=hospital.hospital_name,
                decision="General Ward",
                assigned_icu=False,
                assigned_doctor=True,
                transfer_required=False,
                reason="Patient does not require ICU."
            )

        decisions.append(decision)

        logs.append(
            DecisionLog(
                agent="Decision Engine",
                decision=decision.decision,
                reason=decision.reason,
                confidence=1.0
            )
        )

    return {
        "allocation_decisions": decisions,
        "logs": state["logs"] + logs
    }