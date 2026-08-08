from schemas import AllocationDecision, DecisionLog
from state import HospitalState


def decision_engine(state: HospitalState):

    decisions = []
    logs = []

    # ---------------------------------------------------------
    # Track resources during this execution
    # ---------------------------------------------------------

    remaining_icu = {
        h.hospital_id: h.resources.icu_beds
        for h in state["hospitals"]
    }

    remaining_doctors = {
        h.hospital_id: h.resources.doctors
        for h in state["hospitals"]
    }

    for priority in state["priorities"]:

        recommendation = next(
            (
                r
                for r in state["hospital_recommendations"]
                if r.patient_id == priority.patient_id
            ),
            None
        )

        # -----------------------------------------------------
        # No hospital found
        # -----------------------------------------------------

        if recommendation is None:
            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id="NONE",
                hospital_name="No Suitable Hospital",
                decision="Transfer Patient",
                assigned_icu=False,
                assigned_doctor=False,
                transfer_required=True,
                reason="No hospital recommendation available."
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

            continue

        if recommendation.hospital_id == "NONE":

            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id="NONE",
                hospital_name="No Suitable Hospital",
                decision="Transfer Patient",
                assigned_icu=False,
                assigned_doctor=False,
                transfer_required=True,
                reason="No hospital currently satisfies the patient's requirements."
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

            continue

        # -----------------------------------------------------
        # Find selected hospital
        # -----------------------------------------------------

        hospital = next(
            (
                h
                for h in state["hospitals"]
                if h.hospital_id == recommendation.hospital_id
            ),
            None
        )

        if hospital is None:

            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id="NONE",
                hospital_name="Unknown Hospital",
                decision="Transfer Patient",
                assigned_icu=False,
                assigned_doctor=False,
                transfer_required=True,
                reason="Recommended hospital could not be found."
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

            continue

        hospital_id = hospital.hospital_id

        # -----------------------------------------------------
        # Check doctor availability
        # -----------------------------------------------------

        if remaining_doctors[hospital_id] <= 0:

            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id=hospital_id,
                hospital_name=hospital.hospital_name,
                decision="Transfer Patient",
                assigned_icu=False,
                assigned_doctor=False,
                transfer_required=True,
                reason="No doctor currently available at selected hospital."
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

            continue

        # -----------------------------------------------------
        # ICU patient
        # -----------------------------------------------------

        if priority.needs_icu:

            if remaining_icu[hospital_id] > 0:

                remaining_icu[hospital_id] -= 1
                remaining_doctors[hospital_id] -= 1

                decision = AllocationDecision(
                    patient_id=priority.patient_id,
                    hospital_id=hospital_id,
                    hospital_name=hospital.hospital_name,
                    decision="Allocate ICU",
                    assigned_icu=True,
                    assigned_doctor=True,
                    transfer_required=False,
                    reason=(
                        f"ICU allocated at {hospital.hospital_name}. "
                        f"Remaining ICU beds: "
                        f"{remaining_icu[hospital_id]}"
                    )
                )

            else:

                decision = AllocationDecision(
                    patient_id=priority.patient_id,
                    hospital_id=hospital_id,
                    hospital_name=hospital.hospital_name,
                    decision="Transfer Patient",
                    assigned_icu=False,
                    assigned_doctor=False,
                    transfer_required=True,
                    reason="No ICU bed available."
                )

        # -----------------------------------------------------
        # Non-ICU patient
        # -----------------------------------------------------

        else:

            remaining_doctors[hospital_id] -= 1

            decision = AllocationDecision(
                patient_id=priority.patient_id,
                hospital_id=hospital_id,
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