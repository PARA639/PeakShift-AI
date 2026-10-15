PeakShift-AI

A problem-first approach to "The 4 PM Spike" AI Synergy Hackathon 2026 · Case 05 · Track: AI for Energy & Environment

PeakShift AI helps facilities staff answer three questions before any optimization happens: which loads drive the peak, which of them can move, and did our intervention actually work?

Status

Round 1: Problem Discovery & Technical Feasibility Proof. This repository is a feasibility proof, not a finished product. All demonstrations use synthetic data unless stated otherwise. Nothing here should be read as a validated result on real facility data.

1. Problem Framing

We selected Framing P1: Flexibility and attribution gap.

Facilities staff can see that demand spikes around 4 PM, but across uneven meters they cannot identify which loads drive the peak, cannot tell which loads are movable, and cannot verify whether an intervention worked. A forecasting model or scheduler built on top of that gap would produce confident recommendations that no one can check. P1 keeps the problem definition upstream of the technology: establish attribution, flexibility and verifiability first, then let forecasting and scheduling serve that loop.

Framings considered
#	Framing	Decision
P1	Flexibility and attribution gap	Selected. Addresses the root uncertainty the others depend on
P2	Forecasting gap	Used as a component. A forecast of an unattributed peak is hard to act on
P3	Tariff / cost optimization	Not selected. Assumes cost is the binding pain point
P4	Automated control / scheduling	Used as a component. Automating unattributed loads risks operational harm
P5	Metering / data infrastructure	Not selected. A capital project; P1 works around uneven metering

Note: P2 to P5 labels should be aligned with the official Case 05 wording before submission. [verify]

2. Evidence Map
Tag	Item
[CASE]	Demand peaks around 4 PM
[CASE]	Meter coverage is uneven across the facility
[CASE]	Staff cannot attribute the peak to specific loads
[CASE]	Staff cannot verify intervention results
[ASSUMPTION]	The peak is driven by a small set of recurring loads (e.g. HVAC, pumps, EV charging)
[ASSUMPTION]	Some of those loads can shift by 30 to 90 minutes without harming operations
[ASSUMPTION]	Peak reduction carries a real cost (demand charge or capacity penalty)
[ASSUMPTION]	Staff will act on recommendations they can inspect and trust
[UNKNOWN]	Meter granularity, sampling interval and data quality
[UNKNOWN]	Which loads are truly movable, and their operational constraints
[UNKNOWN]	A credible "before vs. after" baseline (weather, occupancy, seasonality)
[UNKNOWN]	Whether the 4 PM peak is the true cost driver or one of several

Full version: docs/evidence_map.md

[CASE] rows must be traceable to the official case sheet. Anything that is not traceable belongs under [ASSUMPTION]. [verify] against the context sheet before submission.

3. Approach

peakshift AI is a loop, not a single model. Forecasting and scheduling are modules inside it.

Uneven meters +sub-meters
Attribution: which loadsdrive the 4 PM peak
Flexibility scoring: whichloads are movable, withstaff input
Forecast + schedulesuggestions
Staff approve / override
Verification: baseline vs.actual
Stage	Purpose	Human role
Attribution	Estimate each load's contribution to the peak, with uncertainty	Review where uncertainty is high
Flexibility scoring	Rank loads by how movable they are	Confirm operational constraints
Forecast + schedule	Suggest shifts that reduce the peak	Approve or override
Verification	Compare outcome to a no-intervention baseline	Decide whether the result is credible
4. Technical Feasibility Proof

The goal is to show that P1 is testable, not that a product exists.

4.1 Attribution on uneven meters (notebook)

notebooks/01_attribution_feasibility.ipynb

Generates synthetic load profiles for 4 to 5 loads with a 4 PM peak
Hides some sub-meters so only a main meter and partial sub-meters remain
Estimates each load's share of the peak and reports uncertainty
Documents where attribution degrades as meter coverage drops
4.2 Verification logic (pseudocode)

pseudocode.md

baseline   = predict_load(weather, occupancy, day_type)   # no-intervention counterfactual
actual     = measured_load_after_shift
savings    = baseline_peak - actual_peak
band       = baseline_error_band
if savings <= band:
    report "not verifiable"
else:
    report savings with confidence

The key design choice: a savings claim is only reported if it exceeds the baseline's own error.

4.3 Architecture

docs/architecture.md contains the diagram above and module responsibilities.

5. PeakShift-AI/
├── .gitignore               # Ignores virtual environments, caches, and DB files
├── README.md                # System documentation, Architecture Diagram, Wireframe & Pseudocode
├── requirements.txt         # Production Python package dependencies
├── db.py                    # SQLite Database Manager (peakshift.db)
├── data_generator.py        # 15-minute synthetic data engine & SQLite DB populator
├── app.py                   # Streamlit Centralised Dashboard UI (7-Point Solution)
├── api.py                   # FastAPI Backend REST Server
├── test_api.py              # Pytest Automated Test Suite (AT1–AT6 Verification)
│
├── notebooks/
│   └── 01_peakshift_analysis.py  # Data exploration, Random Forest training & evaluation
│
├── src/                     # Core Business Logic & AI Engines
│   ├── __init__.py          # Python package marker
│   ├── ingestion.py         # Timestamp grid alignment, cleaning & data reliability scoring
│   ├── spike_detector.py    # Electricity spike & unusual consumption anomaly detector
│   ├── forecaster.py        # Random Forest Regressor AI demand forecasting model
│   ├── optimizer.py         # 4–8 PM Peak shift optimizer with rebound peak prevention
│   └── evaluator.py         # Acceptance test evaluator module (AT1–AT6)
│
└── data/
    └── raw/                 # Generated 15-minute interval datasets
        ├── environment_data.csv     # Weather & Rooftop Solar kW generation (15-min)
        ├── smart_meters_15min.csv   # Active demand kW across campus buildings
        ├── monthly_buildings.csv    # Low-confidence monthly aggregate buildings
        └── load_registry.csv        # Staff load classification (flexible vs protected)

Files are added as they are completed. Anything not yet present is planned, not claimed.

6. What This Proves and What It Does Not

It shows:

The P1 loop is well-defined and can be decomposed into testable steps
Attribution is feasible in principle on synthetic data with partial metering
Verification can be made conservative by design

It does not show:

Performance on real facility data
That loads are actually movable in practice (needs staff input)
Real savings or cost impact
7. Limitations and Open Questions
Synthetic data reflects our assumptions, so results will look cleaner than reality
Attribution quality depends on meter coverage; this is characterised, not solved
Flexibility cannot be inferred from meter data alone and requires operator knowledge
The baseline model must be validated against real weather and occupancy variation
8. Use of AI and Human Judgment

(Disclosure required by the hackathon.)

Task	AI contribution	Human decision
Framing comparison	Drafted candidate framings	Chose P1 and justified it
Evidence map	Suggested candidate items	Moved untraceable items from [CASE] to [ASSUMPTION]
Synthetic data and notebook	Generated starter code	Set the assumptions and checked outputs
Verification logic	Proposed structure	Added the "report only if savings exceed baseline error" rule

Tools and models used: list here [fill in]

9. Dependencies

Open-source libraries and pre-trained models are disclosed here as required by the hackathon rules.

python >= 3.10
numpy
pandas
scikit-learn
matplotlib
jupyter
10. Team
Name	Role
[Neural Minds]	[Hackathon]

License
Participants shall retain full ownership and all intellectual property (IP) rights in and to any code, applications, designs, concepts, or other materials (collectively, the "Submission") 
created during the Hackathon. The Organizer claims no ownership rights over your Submission.
