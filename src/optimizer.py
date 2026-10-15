import numpy as np
import pandas as pd

class LoadShiftOptimizer:
    def __init__(self, peak_start_hour=16, peak_end_hour=20):
        self.peak_start = peak_start_hour
        self.peak_end = peak_end_hour

    def optimize_schedule(self, df_day, load_registry, active_plan="ALL"):
        """
        Plans:
        - 'NONE': No shifting baseline
        - 'PUMPING': Water pumping shift only
        - 'ALL': All registered flexible loads shift
        - 'ALL_PRECOOL': All flexible loads + 10% thermal pre-cooling (1-4 PM)
        """
        df_sim = df_day.copy().reset_index(drop=True)
        df_sim["shifted_net_demand_kW"] = df_sim["net_demand_kW"]
        df_sim["demand_removed_kW"] = 0.0
        df_sim["demand_added_kW"] = 0.0

        if active_plan == "NONE":
            return df_sim, []

        applied_actions = []

        # Filter out locked or unclassified loads (FR5 constraint)
        flexible_loads = load_registry[load_registry["classification"] == "flexible"]

        for _, load in flexible_loads.iterrows():
            l_id = load["load_id"]
            kW = load["rated_kW"]

            if active_plan == "PUMPING" and "PUMP" not in l_id:
                continue
            if "COOLING" in l_id and active_plan != "ALL_PRECOOL":
                continue

            if "PUMP" in l_id:
                # Move 17:00-19:00 to 11:00-13:00
                orig_mask = (df_sim["timestamp"].dt.hour >= 17) & (df_sim["timestamp"].dt.hour < 19)
                target_mask = (df_sim["timestamp"].dt.hour >= 11) & (df_sim["timestamp"].dt.hour < 13)
                
                df_sim.loc[orig_mask, "shifted_net_demand_kW"] -= kW
                df_sim.loc[orig_mask, "demand_removed_kW"] += kW
                df_sim.loc[target_mask, "shifted_net_demand_kW"] += kW
                df_sim.loc[target_mask, "demand_added_kW"] += kW
                
                applied_actions.append({"load": load["load_name"], "class": "Flexible", "now": "17:00-19:00", "suggested": "11:00-13:00", "kW": kW})

            elif "EV" in l_id:
                # Move 17:00-20:00 to 22:00-01:00
                orig_mask = (df_sim["timestamp"].dt.hour >= 17) & (df_sim["timestamp"].dt.hour < 20)
                target_mask = (df_sim["timestamp"].dt.hour >= 22) | (df_sim["timestamp"].dt.hour < 1)
                
                df_sim.loc[orig_mask, "shifted_net_demand_kW"] -= kW
                df_sim.loc[orig_mask, "demand_removed_kW"] += kW
                df_sim.loc[target_mask, "shifted_net_demand_kW"] += kW
                df_sim.loc[target_mask, "demand_added_kW"] += kW
                
                applied_actions.append({"load": load["load_name"], "class": "Flexible", "now": "17:00-20:00", "suggested": "22:00-01:00", "kW": kW})

            elif "BATT" in l_id:
                # Move 17:30-19:30 to 13:00-15:00
                orig_mask = (df_sim["timestamp"].dt.hour == 17) & (df_sim["timestamp"].dt.minute >= 30) | (df_sim["timestamp"].dt.hour == 18) | (df_sim["timestamp"].dt.hour == 19) & (df_sim["timestamp"].dt.minute < 30)
                target_mask = (df_sim["timestamp"].dt.hour >= 13) & (df_sim["timestamp"].dt.hour < 15)
                
                df_sim.loc[orig_mask, "shifted_net_demand_kW"] -= kW
                df_sim.loc[orig_mask, "demand_removed_kW"] += kW
                df_sim.loc[target_mask, "shifted_net_demand_kW"] += kW
                df_sim.loc[target_mask, "demand_added_kW"] += kW
                
                applied_actions.append({"load": load["load_name"], "class": "Flexible", "now": "17:30-19:30", "suggested": "13:00-15:00", "kW": kW})

            elif "COOLING" in l_id and active_plan == "ALL_PRECOOL":
                # Pre-cooling: Cuts cooling by 10% during 4-8 PM, runs earlier 1-4 PM with 10% energy penalty
                orig_mask = (df_sim["timestamp"].dt.hour >= 16) & (df_sim["timestamp"].dt.hour < 20)
                target_mask = (df_sim["timestamp"].dt.hour >= 13) & (df_sim["timestamp"].dt.hour < 16)
                
                cool_shift_kW = kW * 0.15 # 15% comfort limit reduction
                penalty_kW = cool_shift_kW * 1.10 # 10% efficiency penalty for early running
                
                df_sim.loc[orig_mask, "shifted_net_demand_kW"] -= cool_shift_kW
                df_sim.loc[orig_mask, "demand_removed_kW"] += cool_shift_kW
                df_sim.loc[target_mask, "shifted_net_demand_kW"] += penalty_kW
                df_sim.loc[target_mask, "demand_added_kW"] += penalty_kW
                
                applied_actions.append({"load": load["load_name"], "class": "Thermal Pre-cool", "now": "16:00-20:00", "suggested": "13:00-16:00", "kW": round(cool_shift_kW, 1)})

        # Check for Rebound Peak Violation (FR6)
        peak_window_mask = (df_sim["timestamp"].dt.hour >= 16) & (df_sim["timestamp"].dt.hour < 20)
        off_peak_mask = ~peak_window_mask
        
        original_peak = df_sim["net_demand_kW"].max()
        max_offpeak_demand = df_sim.loc[off_peak_mask, "shifted_net_demand_kW"].max()

        df_sim["rebound_violation"] = max_offpeak_demand > original_peak

        return df_sim, applied_actions
    