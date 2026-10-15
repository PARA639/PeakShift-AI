# src/forecaster.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

class PeakForecaster:
    def __init__(self):
        # AI Algorithm: Random Forest Regressor as per handwritten technology stack note
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)

    def train_and_predict(self, df):
        df_feat = df.copy()
        df_feat["hour"] = df_feat["timestamp"].dt.hour
        df_feat["minute"] = df_feat["timestamp"].dt.minute
        df_feat["dayofweek"] = df_feat["timestamp"].dt.dayofweek
        
        features = ["hour", "minute", "dayofweek", "temperature_C", "humidity_pct", "solar_generation_kW"]
        X = df_feat[features]
        y = df_feat["net_demand_kW"]
        
        train_size = int(len(df_feat) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        # Fit Random Forest AI model
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_test)
        
        # Calculate same-hour baseline
        baseline = df_feat.groupby(["hour", "minute"])["net_demand_kW"].transform("mean").iloc[train_size:].values
        
        result_df = df_feat.iloc[train_size:].copy()
        result_df["forecast_RF"] = preds
        result_df["same_hour_baseline"] = baseline
        
        # Evaluate forecast accuracy against actual readings (Handwritten Point #3.iii)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        wape = np.sum(np.abs(y_test - preds)) / np.sum(y_test) * 100
        
        metrics = {
            "MAE_kW": round(mae, 2),
            "RMSE_kW": round(rmse, 2),
            "WAPE_pct": round(wape, 2)
        }
        
        return result_df, metrics
    