from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

prompt_text = Path(
    "prompts/clinical_priority.txt"
).read_text()

prompt = ChatPromptTemplate.from_messages(
[
("system", prompt_text),
("human","{patient}")
])

messages = prompt.invoke(
{
"patient":"Chest pain"
}
)

print(messages)