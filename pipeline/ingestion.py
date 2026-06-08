import pandas as pd
import numpy as np
import os

def load_or_generate_raw_data() -> pd.DataFrame:
    """Loads raw dataset or generates a high-fidelity Kaggle manufacturing simulation."""
    target_path = "predictive_maintenance.csv"
    if os.path.exists(target_path):
        print(f"[INGESTION] Found local dataset file at {target_path}")
        return pd.read_csv(target_path)
    
    print("[INGESTION] Local dataset not found. Generating high-fidelity simulation...")
    np.random.seed(42)
    records = 10000
    
    types = np.random.choice(['L', 'M', 'H'], size=records, p=[0.6, 0.3, 0.1])
    air_temp = np.random.normal(300.0, 2.0, size=records)
    process_temp = air_temp + 10.0 + np.random.normal(0, 1.0, size=records)
    
    speed = np.random.normal(1500.0, 150.0, size=records)
    torque = (2860 * 60) / (2 * np.pi * speed) + np.random.normal(0, 5.0, size=records)
    tool_wear = np.random.uniform(0, 250, size=records)
    
    failures = np.zeros(records, dtype=int)
    fail_types = ["No Failure"] * records
    
    for i in range(records):
        if tool_wear[i] > 220 and np.random.rand() < 0.6:
            failures[i] = 1
            fail_types[i] = "Tool Wear Failure"
        elif (process_temp[i] - air_temp[i]) < 8.6 and speed[i] < 1380 and np.random.rand() < 0.5:
            failures[i] = 1
            fail_types[i] = "Heat Dissipation Failure"
        elif torque[i] * (speed[i] * 2 * np.pi / 60) > 9000 and np.random.rand() < 0.5:
            failures[i] = 1
            fail_types[i] = "Power Failure"
        elif tool_wear[i] * torque[i] > 11000 and np.random.rand() < 0.4:
            failures[i] = 1
            fail_types[i] = "Overstrain Failure"
        elif np.random.rand() < 0.002:
            failures[i] = 1
            fail_types[i] = "Random Failures"

    df = pd.DataFrame({
        'UDI': range(1, records + 1),
        'Product ID': [f"{t}{10000+i}" for i, t in enumerate(types)],
        'Type': types,
        'Air temperature [K]': air_temp,
        'Process temperature [K]': process_temp,
        'Rotational speed [rpm]': speed,
        'Torque [Nm]': torque,
        'Tool wear [min]': tool_wear,
        'Target': failures,
        'Failure Type': fail_types
    })
    
    df.to_csv(target_path, index=False)
    return df