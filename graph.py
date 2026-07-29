from langgraph.graph import START, END, StateGraph

from state import HospitalState
from nodes.clinical_priority import clinical_priority_agent
from nodes.resource_intelligence import resource_intelligence_agent
from nodes.decision_engine import decision_engine

builder = StateGraph(HospitalState)

builder.add_node(
    "clinical_priority",
    clinical_priority_agent
)

builder.add_edge(
    START,
    "clinical_priority"
)

builder.add_edge(
    "clinical_priority",
    END
)

builder.add_node(
    "resource_intelligence",
    resource_intelligence_agent
)

builder.add_edge(
    "clinical_priority",
    "resource_intelligence"
)

builder.add_edge(
    "resource_intelligence",
    END
)

builder.add_node(
    "decision_engine",
    decision_engine
)



builder.add_edge(
    "decision_engine",
    END
)

from nodes.hospital_selection import hospital_selection_agent

builder.add_node(
    "hospital_selection",
    hospital_selection_agent
)

builder.add_edge(
    "resource_intelligence",
    "hospital_selection"
)

builder.add_edge(
    "hospital_selection",
    "decision_engine"
)
from nodes.supervisor import supervisor_agent

builder.add_node(
    "supervisor",
    supervisor_agent
)

builder.add_edge(
    "decision_engine",
    "supervisor"
)

builder.add_edge(
    "supervisor",
    END
)
graph = builder.compile()