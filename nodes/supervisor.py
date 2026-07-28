from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from models.llm import llm
from state import HospitalState

prompt_text = Path("prompts/supervisor.txt").read_text()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_text),
        ("human", "{context}")
    ]
)

chain = prompt | llm


def supervisor_agent(state: HospitalState):

    context = f"""
Scenario:
{state['scenario']}

Clinical Priorities:
{state['priorities']}

Hospital Recommendations:
{state['hospital_recommendations']}

Allocation Decisions:
{state['allocation_decisions']}
"""

    response = chain.invoke(
        {
            "context": context
        }
    )

    return {
        "final_report": response.content
    }