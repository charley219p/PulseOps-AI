
import json
import pandas as pd
import plotly.express as px  # pyright: ignore[reportMissingImports]
import streamlit as st

from graph import graph
from schemas import Patient, Hospital

st.set_page_config(
    page_title="PulseOps AI",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
.main {background:#f4f7fb;}
.block-container {padding-top:1.5rem;}
.metric-card{
background:white;padding:15px;border-radius:12px;
box-shadow:0px 3px 10px rgba(0,0,0,.1);
}
.report{
    background:#1f2937;
    color:white;
    padding:20px;
    border-radius:12px;
    border-left:6px solid #3b82f6;
    line-height:1.8;
    white-space:pre-wrap;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(90deg,#2563eb,#1e3a8a);
padding:25px;border-radius:15px;color:white;text-align:center;">
<h1>🏥 PulseOps AI</h1>
<h3>Autonomous Hospital Command Center</h3>
<p>LangGraph • Multi-Agent • AI Resource Allocation</p>
</div>
""", unsafe_allow_html=True)

st.write("")

import os

SCENARIO_PATH = "data/scenario.json"   # change if needed

if os.path.exists(SCENARIO_PATH):
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        scenario = json.load(f)
else:
    scenario_file = st.sidebar.file_uploader(
        "Upload Scenario JSON",
        type=["json"]
    )

    if scenario_file is None:
        st.info("Upload your scenario JSON from the sidebar.")
        st.stop()

    scenario = json.load(scenario_file)

patients = [Patient(**p) for p in scenario["patients"]]
hospitals = [Hospital(**h) for h in scenario["hospitals"]]

initial_state = {
    "patients": patients,
    "hospitals": hospitals,
    "priorities": [],
    "allocations": [],
    "logs": [],
    "resource_status": [],
    "allocation_decisions": [],
    "hospital_recommendations": [],
    "scenario": scenario["scenario"],
    "final_report": ""
}

st.error(f"🚨 ACTIVE EMERGENCY : {scenario['scenario']}")

if st.button("🚀 Run AI Command Center", use_container_width=True):

    progress = st.progress(0)

    for i in range(5):
        progress.progress((i+1)/5)

    result = graph.invoke(initial_state)

    critical = sum(p.severity=="Critical" for p in result["priorities"])
    medium = sum(p.severity=="Medium" for p in result["priorities"])
    low = sum(p.severity=="Low" for p in result["priorities"])
    icu = sum(d.assigned_icu for d in result["allocation_decisions"])
    transfers = sum(d.transfer_required for d in result["allocation_decisions"])

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Patients",len(result["patients"]))
    c2.metric("Critical",critical)
    c3.metric("Medium",medium)
    c4.metric("ICU Assigned",icu)
    c5.metric("Transfers",transfers)

    st.divider()

    st.subheader("🩺 Incoming Patients")
    for p in result["patients"]:
        st.markdown(
            f"""**{p.patient_id}** | Age: {p.age} | Arrival: {p.arrival_mode}<br>
            Symptoms: {", ".join(p.symptoms)}""",
            unsafe_allow_html=True
        )

    left,right=st.columns(2)

    with left:
        st.subheader("Clinical Priorities")
        pdf=pd.DataFrame([{
            "Patient":p.patient_id,
            "Severity":p.severity,
            "Priority":p.priority_score,
            "ICU":p.needs_icu,
            "CT":p.needs_ct_scan,
            "Reason":p.reason
        } for p in result["priorities"]])
        st.dataframe(pdf,use_container_width=True,hide_index=True)

    with right:
        st.subheader("Hospital Resources")
        rdf=pd.DataFrame([{
            "Hospital":h.hospital_name,
            "ICU Available":h.icu_available,
            "Doctors":h.available_doctors,
            "Ambulances":h.available_ambulances,
            "CT":h.ct_scan_available,
            "Status":h.status
        } for h in result["resource_status"]])
        st.dataframe(rdf,use_container_width=True,hide_index=True)

    st.subheader("🏥 Hospital Recommendations")
    hdf=pd.DataFrame([{
        "Patient":r.patient_id,
        "Hospital":r.hospital_name,
        "Score":round(r.score,2),
        "Reason":r.reason
    } for r in result["hospital_recommendations"]])
    st.dataframe(hdf,use_container_width=True,hide_index=True)

    st.subheader("🚑 Allocation Decisions")
    ddf=pd.DataFrame([{
        "Patient":d.patient_id,
        "Hospital":d.hospital_name,
        "Decision":d.decision,
        "ICU":d.assigned_icu,
        "Transfer":d.transfer_required,
        "Reason":d.reason
    } for d in result["allocation_decisions"]])
    st.dataframe(ddf,use_container_width=True,hide_index=True)

    a,b=st.columns(2)

    with a:
        fig=px.pie(
            names=["Critical","Medium","Low"],
            values=[critical,medium,low],
            title="Severity Distribution",
            hole=.45
        )
        st.plotly_chart(fig,use_container_width=True)

    with b:
        fig=px.bar(
            rdf,
            x="Hospital",
            y=["Doctors","Ambulances"],
            barmode="group",
            title="Hospital Resources"
        )
        st.plotly_chart(fig,use_container_width=True)

    fig=px.bar(
        x=["ICU","General Ward"],
        y=[icu,len(result["allocation_decisions"])-icu],
        labels={"x":"Allocation","y":"Patients"},
        title="Patient Allocation"
    )
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("🤖 AI Executive Summary")
    st.markdown(
        f"<div class='report'>{result['final_report']}</div>",
        unsafe_allow_html=True
    )

    st.subheader("📜 Workflow")
    st.markdown("""
Patient
⬇️
Clinical Priority Agent
⬇️
Resource Intelligence Agent
⬇️
Hospital Selection Agent
⬇️
Decision Engine
⬇️
Supervisor Agent
⬇️
Executive Report
""")

    with st.expander("Agent Logs"):
        for log in result["logs"]:
            st.write(f"### {log.agent}")
            st.write(log.decision)
            st.write(log.reason)
            st.progress(float(log.confidence))

    st.download_button(
        "📄 Download Report",
        result["final_report"],
        file_name="PulseOps_Report.txt",
        mime="text/plain"
    )

    st.divider()
    st.caption("Built with ❤️ Streamlit + LangGraph + Plotly")
