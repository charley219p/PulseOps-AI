from models.llm import llm
from schemas import ClinicalPriority

structured_llm = llm.with_structured_output(
    ClinicalPriority
)

response = structured_llm.invoke(
"""
A 65-year-old patient has severe chest pain,
BP 80/60,
heart rate 125,
arrived by ambulance.
"""
)

print(response)
print(type(response))