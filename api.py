from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

from src.ingestion import DataIngestionEngine
from src.optimizer import LoadShiftOptimizer

app = FastAPI(title="PeakShift AI API", version="1.0.0")

ingestion = DataIngestionEngine(data_path="data/raw")
grid_df, registry_df, _ = ingestion.load_and_clean_data()
optimizer = LoadShiftOptimizer()

class ScheduleRequest(BaseModel):
    plan_type: str = "ALL_PRECOOL" # "NONE", "PUMPING", "ALL", "ALL_PRECOOL"
    user_role: str = "Facilities Engineer"
    action: str = "SIMULATION_REQUEST"

class ApprovalRequest(BaseModel):
    proposal_id: str
    approved_by: str
    decision: str # "APPROVE", "REJECT", "MODIFY"
    reason: str

audit_logs = []

@app.get("/")
def read_root():
    return {"status": "Online", "system": "PeakShift AI Load Management Engine"}

@app.get("/api/v1/forecast/peak")
def get_peak_forecast():
    day_df = grid_df.iloc[:96]
    peak_row = day_df.loc[day_df["net_demand_kW"].idxmax()]
    return {
        "timestamp": peak_row["timestamp"].strftime("%Y-%m-%d %H:%M"),
        "peak_net_demand_kW": float(peak_row["net_demand_kW"]),
        "solar_generation_kW": float(peak_row["solar_generation_kW"]),
        "confidence": "HIGH"
    }

@app.post("/api/v1/schedule/optimize")
def generate_schedule(req: ScheduleRequest):
    day_df = grid_df.iloc[:96]
    sim_df, actions = optimizer.optimize_schedule(day_df, registry_df, active_plan=req.plan_type)
    
    peak_before = float(sim_df["net_demand_kW"].max())
    peak_after = float(sim_df["shifted_net_demand_kW"].max())
    reduction_pct = float(((peak_before - peak_after) / peak_before) * 100)
    
    return {
        "plan_type": req.plan_type,
        "peak_without_shifting_kW": round(peak_before, 1),
        "peak_with_plan_kW": round(peak_after, 1),
        "change_pct": round(-reduction_pct, 1),
        "actions": actions,
        "rebound_violation": bool(sim_df["rebound_violation"].iloc[0]),
        "status": "SIMULATION_LABELLED"
    }

@app.post("/api/v1/schedule/approve")
def approve_schedule(req: ApprovalRequest):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "proposal_id": req.proposal_id,
        "approved_by": req.approved_by,
        "decision": req.decision,
        "reason": req.reason,
        "execution_type": "SIMULATION_ONLY"
    }
    audit_logs.append(log_entry)
    return {"message": "Decision logged successfully", "log": log_entry}

@app.get("/api/v1/audit/logs")
def get_audit_logs():
    return {"audit_logs": audit_logs}
