from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from models.llm import llm
from schemas import ClinicalPriority, DecisionLog
from state import HospitalState
from utils.prompt_loader import load_prompt
# Load Prompt
prompt_text = load_prompt("clinical_priority.txt")

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_text),
        ("human", "{patient}")
    ]
)

# Structured Output
structured_llm = llm.with_structured_output(ClinicalPriority)

# Build Chain
chain = prompt | structured_llm


def clinical_priority_agent(state: HospitalState):

    patients = state["patients"]

    priorities = []
    logs = []

    for patient in patients:

        result = chain.invoke(
            {
                "patient": patient.model_dump_json(indent=2)
            }
        )

        priorities.append(result)

        logs.append(
            DecisionLog(
                agent="Clinical Priority Agent",
                decision=f"{patient.patient_id} -> {result.severity}",
                reason=result.reason,
                confidence=result.priority_score / 100,
            )
        )

    return {
        "priorities": priorities,
        "logs": logs,
    }