# src/ingestion.py
import pandas as pd
import numpy as np
from db import query_db

class DataIngestionEngine:
    def __init__(self, data_path="data/raw"):
        self.data_path = data_path

    def load_and_clean_data(self):
        env_df = pd.read_csv(f"{self.data_path}/environment_data.csv")
        meters_df = pd.read_csv(f"{self.data_path}/smart_meters_15min.csv")
        monthly_df = pd.read_csv(f"{self.data_path}/monthly_buildings.csv")
        registry_df = pd.read_csv(f"{self.data_path}/load_registry.csv")

        env_df["timestamp"] = pd.to_datetime(env_df["timestamp"])
        meters_df["timestamp"] = pd.to_datetime(meters_df["timestamp"])

        # Detect and drop duplicates
        meters_df = meters_df.drop_duplicates(subset=["timestamp", "building_id"])

        # Pivot meters on common 15-min time grid
        meter_pivot = meters_df.pivot(index="timestamp", columns="building_id", values="demand_kW").ffill()

        grid_df = pd.merge(env_df, meter_pivot, on="timestamp", how="left")
        grid_df["metered_campus_demand_kW"] = meter_pivot.sum(axis=1).values

        # Monthly-only building coarse load estimation
        monthly_avg_kW = (monthly_df["total_kWh"].sum() / 2) / (30 * 24)
        grid_df["monthly_estimated_demand_kW"] = monthly_avg_kW
        grid_df["total_campus_demand_kW"] = grid_df["metered_campus_demand_kW"] + grid_df["monthly_estimated_demand_kW"]
        grid_df["net_demand_kW"] = grid_df["total_campus_demand_kW"] - grid_df["solar_generation_kW"]

        # Quality & Reliability scoring
        quality_scores = {}
        for col in meter_pivot.columns:
            stuck_count = (meter_pivot[col].diff() == 0).sum()
            missing_count = meter_pivot[col].isnull().sum()
            score = max(0, 100 - (missing_count * 2 + stuck_count * 0.1))
            quality_scores[col] = {"score": round(score, 1), "confidence": "HIGH" if score > 80 else "MEDIUM"}

        for b_id in monthly_df["building_id"].unique():
            quality_scores[b_id] = {"score": 35.0, "confidence": "LOW (Unreliable / Monthly Aggregate)"}

        return grid_df, registry_df, quality_scores
    