# src/spike_detector.py
import pandas as pd
import numpy as np

class SpikeDetector:
    def __init__(self, threshold_std=2.2):
        self.threshold_std = threshold_std

    def detect_spikes(self, df):
        df_analysis = df.copy()
        rolling_mean = df_analysis["net_demand_kW"].rolling(window=8, min_periods=1).mean()
        rolling_std = df_analysis["net_demand_kW"].rolling(window=8, min_periods=1).std().fillna(1.0)
        
        # Spike condition: Net demand > Mean + threshold * Std
        df_analysis["is_spike"] = df_analysis["net_demand_kW"] > (rolling_mean + self.threshold_std * rolling_std)
        
        spikes = df_analysis[df_analysis["is_spike"]][["timestamp", "net_demand_kW", "solar_generation_kW"]]
        alerts = []
        for _, row in spikes.iterrows():
            alerts.append({
                "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "demand_kW": row["net_demand_kW"],
                "message": f"⚠️ Sudden Spike Detected: {row['net_demand_kW']:.1f} kW at {row['timestamp'].strftime('%H:%M')}"
            })
        return alerts
    