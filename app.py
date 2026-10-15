# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from src.ingestion import DataIngestionEngine
from src.forecaster import PeakForecaster
from src.spike_detector import SpikeDetector
from src.optimizer import LoadShiftOptimizer
from db import query_db, save_df_to_sqlite

st.set_page_config(page_title="PeakShift AI: Energy Management", layout="wide")

# 1. Load Data
@st.cache_data
def load_data():
    ingestion = DataIngestionEngine(data_path="data/raw")
    grid_df, registry_df, quality_scores = ingestion.load_and_clean_data()
    return grid_df, registry_df, quality_scores

grid_df, registry_df, quality_scores = load_data()

forecaster = PeakForecaster()
spike_detector = SpikeDetector()
optimizer = LoadShiftOptimizer()

# Title Header
st.title("Centralised Energy Dashboard — PeakShift AI")
st.caption("Intelligent Load Scheduling & Demand Response for Campus Energy Management (4–8 PM Spike Focus)")

# 2. Real-Time Energy Monitoring (Handwritten Point #1)
st.markdown("### 1. Real-Time Energy & Solar Monitoring")
day_df = grid_df.iloc[96:192].copy().reset_index(drop=True)  # Single day sample
latest_row = day_df.iloc[-1]

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Latest Campus Demand", f"{latest_row['total_campus_demand_kW']:.1f} kW")
with m_col2:
    st.metric("Rooftop Solar Generation", f"{latest_row['solar_generation_kW']:.1f} kW", delta="Solar Active")
with m_col3:
    st.metric("Net Grid Demand", f"{latest_row['net_demand_kW']:.1f} kW")
with m_col4:
    st.metric("Peak Window", "16:00 – 20:00 (4-8 PM)", delta="Target Peak")

st.markdown("---")

# 3. Electricity Spike Detection Alerts (Handwritten Point #4 & #5.iv)
st.markdown("### 2. Electricity Spike & Unusual Consumption Alerts")
alerts = spike_detector.detect_spikes(day_df)
if alerts:
    for alert in alerts[:2]:
        st.error(f"{alert['message']} | Action: Review building load contribution.")
else:
    st.success("✓ No unusual consumption spikes detected in current cycle.")

st.markdown("---")

# 4. Plan Selector & AI Optimization (Handwritten Point #5.v)
st.markdown("### 3. AI-Generated Recommendations & Load Scheduling")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)
with p_col1: btn_a = st.button("A. No shifting", use_container_width=True)
with p_col2: btn_b = st.button("B. Pumping only", use_container_width=True)
with p_col3: btn_c = st.button("C. All flexible loads", use_container_width=True)
with p_col4: btn_d = st.button("D. C plus pre-cooling", use_container_width=True)

if "plan" not in st.session_state: st.session_state.plan = "ALL_PRECOOL"
if btn_a: st.session_state.plan = "NONE"
if btn_b: st.session_state.plan = "PUMPING"
if btn_c: st.session_state.plan = "ALL"
if btn_d: st.session_state.plan = "ALL_PRECOOL"

sim_df, actions = optimizer.optimize_schedule(day_df, registry_df, active_plan=st.session_state.plan)

peak_before = int(sim_df["net_demand_kW"].max())
peak_after = int(sim_df["shifted_net_demand_kW"].max())
diff_kW = peak_before - peak_after
diff_pct = round((diff_kW / peak_before) * 100, 1)

# KPI Cards
k1, k2, k3 = st.columns(3)
with k1: st.metric("Peak Without Shifting", f"{peak_before} kW")
with k2: st.metric("Peak With Shifting", f"{peak_after} kW")
with k3: st.metric("Peak Reduction", f"-{diff_pct}% ({diff_kW} kW lower)", delta_color="inverse")

# 5. Solar Trends & Demand Peak Plot (Handwritten Point #5.ii & #5.iii)
fig = go.Figure()
time_str = sim_df["timestamp"].dt.strftime("%H:%M")

fig.add_trace(go.Scatter(x=time_str, y=sim_df["net_demand_kW"], mode='lines', name='Actual Grid Demand (No Shift)', line=dict(color='red', dash='dash')))
fig.add_trace(go.Scatter(x=time_str, y=sim_df["shifted_net_demand_kW"], mode='lines', name='AI Proposed Schedule Demand', line=dict(color='#00A896', width=3)))
fig.add_trace(go.Scatter(x=time_str, y=sim_df["solar_generation_kW"], mode='lines', name='Rooftop Solar Output', line=dict(color='orange', width=2)))

fig.add_vrect(x0="16:00", x1="20:00", fillcolor="rgba(255, 0, 0, 0.08)", line_width=0, annotation_text="Target 4-8 PM Peak Window")

fig.update_layout(xaxis_title="Time of Day (15-min Intervals)", yaxis_title="kW", height=400, margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig, use_container_width=True)

# 6. Safety & Critical Load Locks (Handwritten Point #6)
st.markdown("### 4. Locked Infrastructure & Safety Rules")
sc1, sc2 = st.columns(2)
with sc1: st.info("🔒 **Lab Equipment & Server Rooms**: Critical load (230 kW) — **LOCKED / Not Shiftable**")
with sc2: st.info("❓ **Unclassified Loads**: Unknown status (70 kW) — **LOCKED / Excluded**")

# 7. Human Approval Gate Permission (Handwritten Point #6)
st.markdown("---")
st.markdown("### 5. Safety & Human Approval Gate")

if "approved" not in st.session_state: st.session_state.approved = False

if not st.session_state.approved:
    st.warning("⏳ **Action Required**: Propose changes require human authorization before execution.")
    user_name = st.text_input("Authorized Staff ID / Name:", "Facilities Engineer #01")
    notes = st.text_area("Approval Comments:", "Schedule verified for 4-8 PM campus peak reduction.")
    
    if st.button("Approve Plan (Simulation Mode)", type="primary"):
        st.session_state.approved = True
        st.session_state.user = user_name
        st.session_state.notes = notes
        
        # Log to SQLite DB
        audit_df = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "proposal_id": "PROP_4PM_SPIKE",
            "approved_by": user_name,
            "decision": "APPROVED",
            "reason": notes
        }])
        save_df_to_sqlite(audit_df, "audit_logs")
        st.rerun()
else:
    st.success(f"✅ **Plan Authorized in Simulation** by **{st.session_state.user}**.")
    st.write(f"**Remarks**: {st.session_state.notes}")
    if st.button("Reset Permission State"):
        st.session_state.approved = False
        st.rerun()

# 8. Performance Evaluation (Handwritten Point #3.iii & #7)
st.markdown("---")
st.markdown("### 6. AI Forecast Performance Evaluation (Actual vs Predicted)")
forecast_res, metrics = forecaster.train_and_predict(grid_df)

ev1, ev2, ev3 = st.columns(3)
with ev1: st.metric("Model Algorithm", "Random Forest Regressor")
with ev2: st.metric("Forecast MAE", f"{metrics['MAE_kW']} kW")
with ev3: st.metric("Forecast WAPE Error", f"{metrics['WAPE_pct']}%")
