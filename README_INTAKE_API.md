# Wiring the intake page to real hospital recommendations

Your Replit app is Streamlit — it renders a page but can't receive an HTTP
POST from another webpage. `api.py` fixes that: it's a small FastAPI service
that reuses your existing `graph.py` pipeline and gives the intake form
something real to call.

## 1. Add these files to your repo
- `api.py` → repo root (same folder as `app.py`, `graph.py`, `schemas.py`)
- `data/hospitals_default.json` → your existing `data/` folder

**Replace the hospital data first.** The included file is placeholder —
made-up hospital names and bed counts so nothing looks like real, current
capacity for a real facility. Swap in your actual hospital directory (or
wire `load_hospitals()` in `api.py` to a live source) before this goes near
a real incident.

## 2. Install and run
```
pip install fastapi uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000
```
On Replit, you'll likely want this as a second running process alongside
`streamlit run app.py` — check your `.replit` file's run configuration, or
run the two in separate Repls if that's simpler.

## 3. Point the intake page at it
In the intake page's review screen, set **PulseOps API endpoint** to:
```
https://<your-repl-url>/api/intake
```
Hit **Send to PulseOps** — the page will show the recommended hospital per
patient, why the AI picked it, and the executive summary, straight from
your `graph.invoke()` run.

## Known gaps worth knowing about
- **Bystander reports carry no vitals.** The converter in `api.py` passes
  an empty `vitals` dict for anyone triaged from a scene report. Whatever
  your Clinical Priority Agent does with missing vitals, treat bystander
  triage as provisional — a medic submission for the same patient should
  take priority once one exists.
- **Age groups, not ages.** Bystanders pick "Child / Adult / Elderly"; the
  API maps that to a rough midpoint age (8 / 35 / 72) since `Patient.age`
  needs a number. Adjust `AGE_GROUP_MIDPOINT` if you want different values.
- **CORS is wide open** (`allow_origins=["*"]`) so the intake page can call
  it from anywhere during testing. Lock this to your real frontend's origin
  before this is exposed publicly.
