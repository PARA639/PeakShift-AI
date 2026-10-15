import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"

def test_peak_forecast():
    response = client.get("/api/v1/forecast/peak")
    assert response.status_code == 200
    assert "peak_net_demand_kW" in response.json()

def test_optimize_schedule():
    payload = {"plan_type": "ALL_PRECOOL", "user_role": "Facilities Engineer", "action": "SIMULATION_REQUEST"}
    response = client.post("/api/v1/schedule/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SIMULATION_LABELLED"
    assert data["peak_with_plan_kW"] <= data["peak_without_shifting_kW"]

def test_human_approval_flow():
    payload = {
        "proposal_id": "PROP_2026_001",
        "approved_by": "Chief Engineer",
        "decision": "APPROVE",
        "reason": "Safe peak reduction confirmed"
    }
    response = client.post("/api/v1/schedule/approve", json=payload)
    assert response.status_code == 200
    assert response.json()["log"]["decision"] == "APPROVE"
    