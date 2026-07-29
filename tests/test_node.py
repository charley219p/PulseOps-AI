from nodes.clinical_priority import clinical_priority_agent

from schemas import Patient

state = {

"patients":[

Patient(

patient_id="P001",

age=67,

symptoms=[
"Chest Pain",
"Sweating"
],

vitals={
"bp":"80/60",
"hr":122
},

arrival_mode="Ambulance"

)

]

}

result = clinical_priority_agent(state)

print(result)