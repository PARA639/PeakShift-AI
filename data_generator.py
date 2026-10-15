# data_generator.py
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from db import init_db, save_df_to_sqlite

def generate_data(output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    init_db()
    np.random.seed(42)
    
    # 120 days of 15-minute intervals (96 intervals/day)
    start_date = datetime(2025, 9, 1, 0, 0)
    timestamps = [start_date + timedelta(minutes=15 * i) for i in range(120 * 96)]
    
    df_env = pd.DataFrame({"timestamp": [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps]})
    dt_series = pd.to_datetime(df_env["timestamp"])
    
    df_env["hour"] = dt_series.dt.hour
    df_env["minute"] = dt_series.dt.minute
    df_env["day_of_week"] = dt_series.dt.dayofweek
    df_env["is_weekday"] = df_env["day_of_week"].apply(lambda x: 1 if x < 5 else 0)
    
    # Weather
    temp_base = 28 + 6 * np.sin((df_env["hour"] - 9) * np.pi / 12)
    df_env["temperature_C"] = np.round(temp_base + np.random.normal(0, 1.5, len(df_env)), 2)
    df_env["humidity_pct"] = np.round(np.clip(60 - 20 * np.sin((df_env["hour"] - 9) * np.pi / 12) + np.random.normal(0, 3, len(df_env)), 20, 95), 2)
    
    # Solar Generation (kW)
    solar_curve = np.maximum(0, np.sin((df_env["hour"] + df_env["minute"]/60 - 6) * np.pi / 12))
    solar_curve[(df_env["hour"] < 6) | (df_env["hour"] >= 18)] = 0
    df_env["solar_generation_kW"] = np.round(np.maximum(0, solar_curve * 280 + np.random.normal(0, 8, len(df_env))), 2)
    
    # Meter Readings (7 15-min Buildings, 3 Monthly Aggregate)
    meter_records = []
    for b_idx in range(1, 8):
        building_id = f"BLDG_{b_idx:03d}"
        base_load = 60 + b_idx * 15
        for idx, row in df_env.iterrows():
            hr = row["hour"] + row["minute"]/60.0
            peak_factor = 1.0
            if row["is_weekday"] and 16 <= hr <= 20:
                peak_factor = 1.65 + 0.2 * np.sin((hr - 16) * np.pi / 4)
            elif row["is_weekday"] and 9 <= hr < 16:
                peak_factor = 1.3
            
            # Simulate occasional sudden spike (Unusual Consumption)
            spike = 0.0
            if np.random.rand() < 0.005:  # 0.5% chance of unusual spike
                spike = np.random.uniform(50, 100)
                
            load = base_load * peak_factor + np.random.normal(0, 5) + spike
            quality = "GOOD" if np.random.rand() > 0.02 else "INCONSISTENT"
            
            meter_records.append({
                "timestamp": row["timestamp"],
                "building_id": building_id,
                "demand_kW": round(max(5.0, load), 2),
                "quality_flag": quality
            })
            
    df_meters = pd.DataFrame(meter_records)
    
    # Monthly Buildings (BLDG_008 to BLDG_010)
    monthly_records = []
    for b_idx in range(8, 11):
        building_id = f"BLDG_{b_idx:03d}"
        monthly_records.append({"building_id": building_id, "month": "2025-09", "total_kWh": 45000 + b_idx * 2000})
        monthly_records.append({"building_id": building_id, "month": "2025-10", "total_kWh": 43000 + b_idx * 2100})
    df_monthly = pd.DataFrame(monthly_records)

    # Load Registry
    registry_data = [
        {"load_id": "LOAD_PUMP_01", "building_id": "BLDG_001", "load_name": "Hostel Water Pumping", "rated_kW": 45.0, "classification": "flexible", "allowed_start": "10:00", "allowed_end": "16:00", "current_start": "17:00", "current_end": "19:00", "max_comfort_impact_pct": 10.0},
        {"load_id": "LOAD_EV_01", "building_id": "BLDG_002", "load_name": "Fleet EV Charging", "rated_kW": 60.0, "classification": "flexible", "allowed_start": "22:00", "allowed_end": "06:00", "current_start": "17:00", "current_end": "20:00", "max_comfort_impact_pct": 0.0},
        {"load_id": "LOAD_BATT_01", "building_id": "BLDG_003", "load_name": "Non-urgent Battery Storage", "rated_kW": 35.0, "classification": "flexible", "allowed_start": "10:00", "allowed_end": "15:00", "current_start": "17:30", "current_end": "19:30", "max_comfort_impact_pct": 0.0},
        {"load_id": "LOAD_LAB_01", "building_id": "BLDG_004", "load_name": "Lab Equipment & Server Rooms", "rated_kW": 230.0, "classification": "protected", "allowed_start": "N/A", "allowed_end": "N/A", "current_start": "00:00", "current_end": "23:45", "max_comfort_impact_pct": 0.0},
        {"load_id": "LOAD_UNCLASS_01", "building_id": "BLDG_005", "load_name": "Unclassified Loads", "rated_kW": 70.0, "classification": "unregistered", "allowed_start": "N/A", "allowed_end": "N/A", "current_start": "00:00", "current_end": "23:45", "max_comfort_impact_pct": 0.0},
        {"load_id": "LOAD_COOLING_01", "building_id": "BLDG_001", "load_name": "Pre-cooling HVAC Thermal Shift", "rated_kW": 120.0, "classification": "flexible", "allowed_start": "13:00", "allowed_end": "16:00", "current_start": "16:00", "current_end": "20:00", "max_comfort_impact_pct": 15.0}
    ]
    df_registry = pd.DataFrame(registry_data)

    # Save to CSV and SQLite
    df_env.to_csv(f"{output_dir}/environment_data.csv", index=False)
    df_meters.to_csv(f"{output_dir}/smart_meters_15min.csv", index=False)
    df_monthly.to_csv(f"{output_dir}/monthly_buildings.csv", index=False)
    df_registry.to_csv(f"{output_dir}/load_registry.csv", index=False)
    
    save_df_to_sqlite(df_env, "environment_data")
    save_df_to_sqlite(df_meters, "meter_readings")
    
    print("Dataset generated & SQLite database populated successfully.")

if __name__ == "__main__":
    generate_data()
    