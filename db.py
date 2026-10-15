# db.py
import sqlite3
import pandas as pd

DB_NAME = "peakshift.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Meter readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meter_readings (
            timestamp TEXT,
            building_id TEXT,
            demand_kW REAL,
            quality_flag TEXT
        )
    ''')
    
    # Environment & Solar table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment_data (
            timestamp TEXT PRIMARY KEY,
            temperature_C REAL,
            humidity_pct REAL,
            solar_generation_kW REAL,
            is_weekday INTEGER
        )
    ''')
    
    # Audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            proposal_id TEXT,
            approved_by TEXT,
            decision TEXT,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_df_to_sqlite(df, table_name):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def query_db(query):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db()
    print("SQLite database initialized successfully.")
    