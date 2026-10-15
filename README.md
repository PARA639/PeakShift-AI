# PeakShift-AI ⚡
> **Intelligent Load Scheduling and Demand Response for Campus Energy Management**  
> *A Problem-First Approach to "The 4 PM Spike"*  
> **AI Synergy Hackathon 2026 · Case 05 · Track: AI for Energy & Environment**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B.svg)](https://streamlit.io/)
[![Backend Engine](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/SQLite3-peakshift.db-003B57.svg)](https://www.sqlite.org/)
[![ML Model](https://img.shields.io/badge/AI--Model-Random--Forest--Regressor-green.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](#12-team--intellectual-property)

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
1. [Problem Discovery & Framing (Framing P1)](#1-problem-discovery--framing)
2. [Evidence Map (Case Evidence vs Assumptions)](#2-evidence-map)
3. [End-to-End System Workflow](#3-end-to-end-system-workflow)
4. [Technical System Architecture](#4-technical-system-architecture)
5. [Streamlit UI Wireframe & Dashboard Layout](#5-streamlit-ui-wireframe--dashboard-layout)
6. [Core Algorithm Pseudocode](#6-core-algorithm-pseudocode)
7. [Dataset Exploration & Data Schemas](#7-dataset-exploration--data-schemas)
8. [Repository Directory Structure](#8-repository-directory-structure)
9. [API Specifications & Verification Tests](#9-api-specifications--verification-tests)
10. [Limitations & Open Questions](#10-limitations--open-questions)
11. [Disclosures & Human-AI Collaboration](#11-disclosures--human-ai-collaboration)
12. [Quickstart & Local Setup Guide](#12-quickstart--local-setup-guide)
13. [Team & Intellectual Property](#13-team--intellectual-property)

---

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
| **P4** | Automated Equipment Control | Component | Used strictly in human-gated simulation mode. Direct automation risks operational & research harm. |
| **P5** | Metering Infrastructure Project | Excluded | A capital hardware project; P1 works software-side around uneven metering realities. |

---

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
