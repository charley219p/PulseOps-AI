

from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from models.llm import llm
from schemas import ClinicalPriority

prompt_text = Path(
    "prompts/clinical_priority.txt"
).read_text()

prompt = ChatPromptTemplate.from_messages(
[
("system",prompt_text),
("human","{patient}")
]
)

structured_llm = llm.with_structured_output(
ClinicalPriority
)

chain = prompt | structured_llm

response = chain.invoke(
{
"patient":"""
65 years old

Chest Pain

BP 80/60

HR 122

Ambulance
"""
}
)

print(response)