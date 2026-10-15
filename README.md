# PeakShift-AI ⚡
> **Intelligent Load Scheduling and Demand Response for Campus Energy Management**  
> *A Problem-First Approach to "The 4 PM Spike"*  
> **AI Synergy Hackathon 2026 · Case 05 · Track: AI for Energy & Environment**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B.svg)](https://streamlit.io/)
[![Backend Engine](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/SQLite3-peakshift.db-003B57.svg)](https://www.sqlite.org/)
[![ML Model](https://img.shields.io/badge/AI--Model-Random--Forest--Regressor-green.svg)](https://scikit-learn.org/)

---

## 📌 Executive Summary

**PeakShift-AI** is an intelligent, software-only campus energy advisory and demand-response system designed to flatten the weekday **4:00 PM – 8:00 PM net grid peak ("The 4 PM Spike")**.

Instead of acting as an uninspectable "black-box" control model, PeakShift-AI empowers campus facilities engineers by systematically answering three core operational questions *before* any optimization takes place:
1. **Which loads drive the peak?** (Attribution across uneven 15-minute smart meters & monthly aggregates)
2. **Which of them can safely move?** (Staff-confirmed flexibility windows with strict safety hard-locks)
3. **Did our intervention actually work?** (Counterfactual verification measured against forecast error bounds)

---

## 🚦 Round 1 Status & Prototype Scope

* **Status**: Round 1 — Problem Discovery, Technical Feasibility Proof & Working Prototype.
* **Data Resolution**: All datasets operate on a **15-minute interval grid (96 slots/day)** across 120 synthetic evaluation days.
* **Safety Boundary**: Version 1 provides **zero direct physical control** over campus electrical infrastructure. Every proposed schedule is labelled as a **SIMULATION** and blocked until an authorized human engineer logs approval inside the audit trail.
* **Critical Protection**: Laboratory equipment, server rooms, and student welfare loads are hard-locked (`PROTECTED`) and excluded from any load shifting.

---

## 📄 Table of Contents
1. [Problem Discovery & Framing](#section-1)
2. [Evidence Map](#section-2)
3. [End-to-End System Workflow](#section-3)
4. [Technical System Architecture](#section-4)
5. [Streamlit UI Wireframe & Dashboard Layout](#section-5)
6. [Core Algorithm Pseudocode](#section-6)
7. [Dataset Exploration & Data Schemas](#section-7)
8. [Repository Directory Structure](#section-8)
9. [API Specifications & Verification Tests](#section-9)
10. [Limitations & Open Questions](#section-10)
11. [Disclosures & Human-AI Collaboration](#section-11)
12. [Quickstart & Local Setup Guide](#section-12)
13. [Team & Intellectual Property](#section-13)

---

<a id="section-1"></a>
## 1. Problem Discovery & Framing

We selected **Framing P1: Flexibility and Attribution Gap**.

Facilities staff can observe that campus electrical demand spikes sharply between 4 PM and 8 PM, but across uneven metering (some buildings have continuous 15-minute smart meters, while others have only monthly utility bills), they cannot identify which specific loads drive the spike, cannot tell which loads are safely movable, and cannot verify whether an intervention produced genuine energy savings.

Building a complex AI forecasting or automated control model on top of that gap produces confident recommendations that operators cannot inspect or trust. **Framing P1 keeps the problem definition upstream of technology:** establish attribution, load flexibility, and verifiable baselines first—then deploy machine learning forecasting and optimization to serve that human decision loop.

### Framings Comparison Matrix

| ID | Problem Framing | Decision | Rationale & Scope Boundary |
| :--- | :--- | :--- | :--- |
| **P1** | **Flexibility & Attribution Gap** | **SELECTED** | Addresses the root operational uncertainty that all downstream scheduling relies upon. |
| **P2** | Forecasting Gap | Component | Embedded as a module inside P1. Forecasting an unattributed peak cannot be acted upon safely. |
| **P3** | Tariff & Cost Optimization | Excluded | Assumes financial tariff structure is the primary pain point rather than electrical capacity limits. |
| **P4** | Automated Equipment Control | Component | Used strictly in human-gated simulation mode. Direct automation risks operational harm. |
| **P5** | Metering Infrastructure Project | Excluded | A capital hardware project; P1 works software-side around uneven metering realities. |

---

<a id="section-2"></a>
## 2. Evidence Map

To maintain strict scientific hygiene during Round 1, facts derived from the case brief (`[CASE]`), unverified working hypotheses (`[ASSUMPTION]`), and operational unknowns (`[UNKNOWN]`) are categorized separately:

| Tag | Item / Signal | Operational Handling in PeakShift-AI |
| :--- | :--- | :--- |
| `[CASE]` | Demand spikes sharply weekday 4:00 – 8:00 PM | Targeted via Net Demand optimization (`Campus Load - Solar Output`). |
| `[CASE]` | Metering coverage is uneven across campus | Solved via 15-min interpolation and confidence flags (`HIGH` vs `LOW`). |
| `[CASE]` | Staff cannot attribute peak to specific loads | Solved by load registry mapping and rolling statistical anomaly detection. |
| `[CASE]` | Past awareness campaigns had short-lived impact | Replaced with specific, owner-confirmed, actionable load shift schedules. |
| `[ASSUMPTION]` | Evening peak is driven by a small set of loads | Modeled on HVAC pre-cooling, water pumping, EV charging, and battery storage. |
| `[ASSUMPTION]` | Loads can shift by 30–90 mins without harm | Requires staff confirmation step in registry; strict shift windows enforced. |
| `[ASSUMPTION]` | Peak reduction carries real demand charge savings | Assumes 10–15% peak shave lowers campus monthly maximum capacity penalties. |
| `[ASSUMPTION]` | Staff will act on recommendations they can inspect | Solved using interactive Streamlit plan toggles and explanation panels. |
| `[UNKNOWN]` | Real meter noise, granularity, and sampling gaps | Characterized via synthetic holdout testing; needs real field meter audit. |
| `[UNKNOWN]` | True movable fraction of HVAC vs lab loads | Lab & server loads are hard-locked as `PROTECTED` (target zero interruption). |
| `[UNKNOWN]` | Credible baseline accounting for weather/occupancy | Addressed by Same-Hour Baseline forecast in counterfactual verification logic. |

---

<a id="section-3"></a>
## 3. End-to-End System Workflow

PeakShift-AI operates as an interactive **human-in-the-loop decision loop**:

```mermaid
flowchart TD
    Start([Start 15-Min Execution Cycle]) --> Step1[1. Ingest Smart Meter, Solar, Weather & Registry Data]
    Step1 --> Step2[2. Align Timestamps to Common 15-Min Grid & Score Quality]
    Step2 --> Step3[3. Run Rolling Std Spike Detector for Anomalies]
    Step3 --> Step4[4. Train Random Forest AI Model & Predict Net Demand]
    Step4 --> Step5[5. Attribute 4-8 PM Peak to Buildings & Loads]
    Step5 --> Step6[6. Filter Load Registry: Exclude Protected & Unregistered Loads]
    Step6 --> Step7[7. MILP Optimization: Compute Shift Window & Check Rebound Limits]
    Step7 --> Step8{Safe Schedule Found?}
    
    Step8 -- No --> SafeExit[Safe Exit: Log Reason, Issue 'No Action Needed']
    Step8 -- Yes --> Step9[8. Present Proposal on Streamlit Dashboard UI]
    
    Step9 --> Step10{Human Staff Approval Gate}
    Step10 -- Reject / Modify --> LogReject[Log Rejection Reason to SQLite Audit DB]
    Step10 -- Approve --> LogApprove[Log Approval to SQLite Audit DB & Trigger Simulation]
    
    LogApprove --> Step11[9. Execute Shifted Schedule in Labelled Simulation Mode]
    Step11 --> Step12[10. Performance Check: Compare vs Forecast Baseline Error Margin]
    Step12 --> End([Cycle Complete - Await Next 15-Min Reading])
<a id="section-4"></a>
## 4. Technical System Architecture
 +-----------------------------------------------------------------------------------+
 |                                DATA LAYER                                         |
 |  [15-min Smart Meters]    [Rooftop PV Feeds]    [Weather API]   [Staff Registry]  |
 +-----------------------------------------------------------------------------------+
                                       │
                                       ▼
 +-----------------------------------------------------------------------------------+
 |                        INGESTION & STORAGE ENGINE (db.py)                         |
 |     - SQLite Database (`peakshift.db`) & CSV File Persistence                     |
 |     - Timestamp Alignment (96 Slots/Day: 00:00 to 23:45)                         |
 |     - Data Quality Scoring & Missing Value Forward-Fill                           |
 +-----------------------------------------------------------------------------------+
                                       │
                                       ▼
 +-----------------------------------------------------------------------------------+
 |                   AI FORECASTING & SPIKE DETECTION (src/)                         |
 |     - Random Forest Regressor (`src/forecaster.py`)                               |
 |     - Net Demand Calculation = Campus Load - Rooftop Solar Output                 |
 |     - Rolling Std Spike & Anomaly Detector (`src/spike_detector.py`)              |
 +-----------------------------------------------------------------------------------+
                                       │
                                       ▼
 +-----------------------------------------------------------------------------------+
 |                      OPTIMIZATION & SAFETY ENGINE (src/)                          |
 |     - MILP / Rule-Based Load Shift Scheduler (`src/optimizer.py`)                 |
 |     - Rebound Peak Violation Prevention Engine                                   |
 |     - Safety Hard-Lock: Protected & Unregistered Loads Blocked                   |
 +-----------------------------------------------------------------------------------+
                                       │
                                       ▼
 +-----------------------------------------------------------------------------------+
 |                     PRESENTATION & API LAYER (app.py, api.py)                     |
 |     - Centralised Streamlit Web Dashboard UI (`app.py`)                           |
 |     - FastAPI REST Service (`api.py`)                                             |
 |     - Human Approval Gate & Audit Trail SQLite Logger                             |
 +-----------------------------------------------------------------------------------+
<a id="section-5"></a>
## 5. Streamlit UI Wireframe & Dashboard Layout

+-----------------------------------------------------------------------------------+
|  PeakShift-AI: Centralised Campus Energy Management Dashboard                     |
|  Theme 5: "The 4 PM Spike Focus" | 15-Minute Meter Resolution                     |
+-----------------------------------------------------------------------------------+
| ⚠️ WARNING: Simulation on synthetic data. Real equipment control is disabled.     |
+-----------------------------------------------------------------------------------+
|  1. REAL-TIME ENERGY & SOLAR MONITORING (KPI CARDS)                               |
|  +-----------------------+ +-----------------------+ +-------------------------+  |
|  | Latest Campus Demand  | | Rooftop Solar Output  | | Net Grid Demand         |  |
|  | 1,215.4 kW            | | 234.8 kW             | | 980.6 kW                |  |
|  +-----------------------+ +-----------------------+ +-------------------------+  |
+-----------------------------------------------------------------------------------+
|  2. ELECTRICITY SPIKE & ANOMALY ALERTS                                            |
|  ⚠️ Sudden Spike Detected: 1,350.2 kW at 16:45 | Action: Review Building Load     |
+-----------------------------------------------------------------------------------+
|  3. BUILD THE PLAN (RECOMMENDATION TOGGLES)                                       |
|  [ A. No Shifting ]   [ B. Pumping Only ]   [ C. All Flexible ]   [ D. C + Pre-Cool]|
|                                                                                   |
|  KPI SUMMARY FOR SELECTED PLAN:                                                   |
|  * Peak Without Shifting: 1,107 kW                                                |
|  * Peak With AI Plan:     981 kW                                                  |
|  * Peak Reduction:        -11.4% (-126 kW lower)                                  |
+-----------------------------------------------------------------------------------+
|  4. INTERACTIVE DEMAND & SOLAR TREND CHART (Plotly Graph)                         |
|  1,200 kW |                   --- Target Peak Window 16:00-20:00 ---              |
|  1,000 kW |                .-'  \                                                 |
|    800 kW |             .-'      \____ Red Dash: Original Net Demand              |
|    600 kW |         _.-'              \___ Green Line: AI Shifted Demand          |
|    400 kW |       -'                      \__ Yellow Line: Rooftop Solar          |
|      0 kW +-------+--------+--------+--------+--------+--------+--------+         |
|           00:00   04:00    08:00    12:00    16:00    20:00    23:45              |
+-----------------------------------------------------------------------------------+
|  5. ACTIONABLE LOAD SCHEDULE TABLE                                                |
|  Load Name                 Class     Allowed Window   Shift Action       kW Shift |
|  Hostel Water Pumping      Flexible  10:00 - 16:00    17:00 -> 11:00      45 kW    |
|  Fleet EV Charging         Flexible  22:00 - 06:00    17:00 -> 22:00      60 kW    |
|  Battery Storage           Flexible  10:00 - 15:00    17:30 -> 13:00      35 kW    |
+-----------------------------------------------------------------------------------+
|  6. LOCKED INFRASTRUCTURE & SAFETY CHECKS                                         |
|  🔒 Lab Equipment & Server Rooms: Critical (230 kW) -> [LOCKED / NOT SHIFTABLE]   |
|  ❓ Unclassified Loads: Unknown Status (70 kW)      -> [LOCKED / EXCLUDED]        |
|  ✓ Critical loads untouched  |  ✓ No new rebound peak  |  ✓ Comfort limits ok     |
+-----------------------------------------------------------------------------------+
|  7. HUMAN APPROVAL GATE (ACTION PERMISSION & AUDIT LOGGING)                       |
|  Authorized Staff ID / Name: [ Facilities Engineer #01              ]             |
|  Approval Comments / Notes:  [ Schedule verified for 4-8 PM campus peak. ]        |
|  [ BUTTON: Approve Plan (Simulation Mode) ]                                       |
+-----------------------------------------------------------------------------------+

<a id="section-6"></a>
**## 6. Core Algorithm Pseudocode**
6.1  Data Ingestion & Quality Scoring
ALGORITHM IngestAndCleanData(meter_csv, solar_csv, weather_csv, monthly_csv):
    CREATE common_grid = Timestamps(start="2025-09-01 00:00", step="15min")
    PIVOT meter_csv ON timestamp TO CREATE meter_matrix
    FILL missing_values IN meter_matrix USING ForwardFill (.ffill)
    
    FOR EACH building IN meter_matrix.columns:
        missing_count = COUNT(where demand is NULL)
        stuck_count = COUNT(where demand[t] == demand[t-1])
        quality_score = MAX(0, 100 - (missing_count * 2 + stuck_count * 0.1))
        
        IF quality_score >= 80 THEN
            confidence[building] = "HIGH CONFIDENCE"
        ELSE
            confidence[building] = "MEDIUM CONFIDENCE"
            
    net_demand = (meter_matrix.SUM(axis=1) + coarse_kw) - solar_csv.generation_kW
    RETURN net_demand, confidence_scores

6.2 Sudden Electricity Spike Detection
ALGORITHM DetectElectricitySpikes(net_demand_series, threshold_std=2.2):
    INITIALIZE alerts_list = []
    FOR EACH interval t IN net_demand_series:
        window = net_demand_series[t-8 : t]
        mean_val = MEAN(window)
        std_val = STD_DEV(window)
        threshold = mean_val + (threshold_std * std_val)
        
        IF net_demand_series[t] > threshold THEN
            CREATE alert = "Unusual Consumption Spike Detected"
            APPEND alert TO alerts_list
            
    RETURN alerts_list

6.3 Random Forest AI Demand Forecasting
ALGORITHM TrainRandomForestForecaster(dataset):
    EXTRACT features = [hour, minute, dayofweek, temperature_C, humidity_pct, solar_generation_kW]
    SET target = net_demand_kW
    SPLIT dataset INTO X_train, X_test, y_train, y_test (80/20 split)
    
    INITIALIZE model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    FIT model USING (X_train, y_train)
    predictions = model.PREDICT(X_test)
    
    RETURN predictions, metrics

6.4 MILP Load Shift Optimization & Rebound Guard
ALGORITHM OptimizePeakShift(day_data, load_registry, selected_plan):
    CREATE shifted_demand = COPY(day_data.net_demand_kW)
    FILTER loads = load_registry WHERE classification == "flexible"
    
    FOR EACH load IN loads:
        IF load.id MATCHES selected_plan THEN
            shifted_demand[orig_slots] -= load.rated_kW
            shifted_demand[target_slots] += load.rated_kW
            
    original_peak = MAX(day_data.net_demand_kW[peak_window])
    offpeak_shifted_max = MAX(shifted_demand[offpeak_window])
    
    IF offpeak_shifted_max > original_peak THEN
        REJECT candidate (Rebound Violation)
    ELSE
        ACCEPT candidate
<a id="section-7"></a>
## 7. Dataset Exploration & Data Schemas
7.1 meter_readings Table (SQLite / CSV)

Column Name	 Data Type	Constraint	     Description	                   Example
timestamp	 DATETIME	NOT NULL	15-minute interval timestamp	   2025-09-01 16:15:00
building_id	 STRING	   NOT NULL	    Building ID (BLDG_001 to BLDG_007)	   BLDG_001
demand_kW	 FLOAT	     ≥0.0	    Active power demand in kW	            125.40
quality_fla STRING	     ENUM	   Data quality label (GOOD, INCONSISTENT)	 GOOD

7.2 environment_data Table (SQLite / CSV)
Column Name 	   Data Type	         Description	                Example
timestamp	        DATETIME	       Primary Key (15-min step) 	 2025-09-01 12:00:00
temperature_C	     FLOAT	          Ambient outdoor temperature in °C	 32.5
humidity_pct	     FLOAT	          Relative humidity percentage	     55.0
solar_generation_kW	 FLOAT	          Rooftop PV output in kW	        240.8
is_weekday	        INTEGER	        1 = Weekday (Mon-Fri), 0 = Weekend	  1

7.3 load_registry Table (CSV)

Column Name	       Data Type	       Description	                           Example
load_id	            STRING	     Unique load asset identifier	            LOAD_PUMP_01
load_name	        STRING	     Description of electrical equipment	    Hostel Water Pumping
rated_kW	        FLOAT	     Nominal power rating in kW                     45.0
classification	    STRING	     flexible, protected, or unregistered	      flexible
allowed_start	    TIME	     Start of allowed shift window              	10:00
allowed_end      	TIME	     End of allowed shift window	                16:00

<a id="section-8"></a>
**## 8. Repository Directory Structure**
PeakShift-AI/
├── .gitignore               # Ignores virtual environments, caches, and DB files
├── README.md                # Master system documentation & specifications
├── WORKFLOW.md              # Detailed step-by-step pipeline specification
├── ARCHITECTURE.md          # Technical architecture & module interaction
├── WIREFRAME.md             # Dashboard UI layout documentation
├── PSEUDOCODE.md            # Complete algorithm pseudocode
├── DATASET_EXPLORATION.md   # Data schema & quality scoring rules
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
│   ├── ingestion.py         # Timestamp grid alignment, cleaning & quality scoring
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

<a id="section-9"></a>
**## 9. API Specifications & Verification Tests**
REST API Endpoints (api.py)

Method	     Endpoint	                    Description	                                          Sample Output
GET	            /	                        Healthcheck endpoint                                  {"status": "Online", "system":"PeakShift AI"}
GET	           /api/v1/forecast/peak	    Returns day-ahead 4-8 PM peak net load                {"peak_net_demand_kW": 1107.0, "confidence": "HIGH"}
POST	      /api/v1/schedule/optimize	    Generates candidate shift schedule	                  {"peak_with_plan_kW": 981.0, "change_pct": -11.4}
POST	     /api/v1/schedule/approve	    Logs human approval to SQLite audit DB	              {"message": "Decision logged", "status": "APPROVED"}

<a id="section-10"></a>
##10 . Limitations & Open Questions

1) Synthetic Regularity: Generated load curves are smoother than real power grids.
2) Sub-metering Limits: Attribution confidence drops when building sub-metering falls below 60%.
3) Operator Knowledge Dependency: Load flexibility windows cannot be inferred purely from time-series data; human confirmation is mandatory.

<a id="section-11"></a>
## 11. Disclosures & Human-AI Collaboration

Task / Component	      AI / Software Contribution	         Human Decision & Authority
Problem Framing	          Drafted candidate framing options	     Selected Framing P1 (Flexibility & Attribution) based on operational risk.
Evidence Mapping	      Suggested evidence tags and signals	 Traceability check against official Case 05 sheet.
Model & Code Setup	      Generated initial code structure	     Defined physical constraints, 15-minute grids, and validated outputs.

**Tools Used**: Python 3.11, Scikit-learn (Random Forest Regressor), Streamlit, FastAPI, SQLite3, Pytest, Plotly, Pandas, NumPy.

<a id="section-12"></a>
## 12. Quickstart & Local Setup Guide

# 1. Clone Repository
git clone https://github.com/PARA639/PeakShift-AI.git
cd PeakShift-AI

# 2. Activate Virtual Environment
.\venv\Scripts\Activate.ps1  # On Mac/Linux: source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Generate 15-Min Synthetic Data & SQLite DB
python data_generator.py

# 5. Run Automated Tests
pytest test_api.py -v

# 6. Launch Web Dashboard UI
streamlit run app.py

<a id="section-13"></a>
## 13. Team & Intellectual Property
Team Name: Neural Minds
Track: AI for Energy & Environment (Case 05: "The 4 PM Spike")
Hackathon: AI Synergy Hackathon 2026

**##License & Intellectual Property**
Participants shall retain full ownership and all intellectual property (IP) rights in and to any code, applications, designs, concepts, or other materials created during the AI Synergy Hackathon 2026.


