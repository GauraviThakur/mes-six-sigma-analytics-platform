import pandas as pd
from datetime import datetime, timedelta
from database.connection import engine
from sqlalchemy import text

def run_etl():
    print("[ETL] Starting production execution pipeline with real dataset...")
    
    # 1. Clear out any leftover data safely
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_downtime_logs, fact_quality_inspections, fact_production_records, dim_shifts, dim_machines, dim_products CASCADE;"))

    # 2. Ingest real dataset
    csv_path = "predictive_maintenance.csv"
    raw_df = pd.read_csv(csv_path)
    
    # 3. Seed Dimension Tables
    products_data = [
        {"product_id": "L", "product_name": "Light Component", "product_type": "L", "target_torque": 40.0, "usl_torque": 55.0, "lsl_torque": 25.0, "target_temp": 300.0, "usl_temp": 305.0, "lsl_temp": 295.0},
        {"product_id": "M", "product_name": "Medium Component", "product_type": "M", "target_torque": 45.0, "usl_torque": 60.0, "lsl_torque": 30.0, "target_temp": 301.0, "usl_temp": 306.0, "lsl_temp": 296.0},
        {"product_id": "H", "product_name": "Heavy Component", "product_type": "H", "target_torque": 50.0, "usl_torque": 65.0, "lsl_torque": 35.0, "target_temp": 302.0, "usl_temp": 307.0, "lsl_temp": 297.0}
    ]
    pd.DataFrame(products_data).to_sql("dim_products", engine, if_exists="append", index=False)

    machines_data = [
        {"machine_id": "MCH_01", "machine_name": "CNC Milling Station 1", "work_center": "Milling_WC", "design_speed_rpm": 1500.0},
        {"machine_id": "MCH_02", "machine_name": "CNC Milling Station 2", "work_center": "Milling_WC", "design_speed_rpm": 1500.0}
    ]
    pd.DataFrame(machines_data).to_sql("dim_machines", engine, if_exists="append", index=False)

    shifts_data = [
        {"shift_id": "SH_01", "shift_name": "Day Shift", "start_time": "06:00:00", "end_time": "14:00:00", "planned_runtime_mins": 480.0},
        {"shift_id": "SH_02", "shift_name": "Evening Shift", "start_time": "14:00:00", "end_time": "22:00:00", "planned_runtime_mins": 480.0}
    ]
    pd.DataFrame(shifts_data).to_sql("dim_shifts", engine, if_exists="append", index=False)

    # 4. Process and Load Fact Tables
    base_time = datetime.now() - timedelta(days=7)
    
    prod_records = []
    qual_records = []
    down_records = []
    
    # Map the real UCI columns cleanly to your SQL database fields
    for idx, row in raw_df.iterrows():
        current_time = base_time + timedelta(minutes=idx)
        
        m_id = "MCH_01" if idx % 2 == 0 else "MCH_02"
        s_id = "SH_01" if idx % 1440 < 480 else "SH_02"
        p_type = row['Type']
        
        prod_records.append({
            "production_id": idx + 1,
            "timestamp": current_time,
            "machine_id": m_id,
            "product_id": p_type,
            "shift_id": s_id,
            "rotational_speed_rpm": row['Rotational speed [rpm]'],
            "torque_nm": row['Torque [Nm]'],
            "tool_wear_mins": row['Tool wear [min]'],
            "air_temp_k": row['Air temperature [K]'],
            "process_temp_k": row['Process temperature [K]'],
            "total_pieces_produced": 1,
            "cycle_time_secs": 60.0
        })
        
        # UCI raw uses 'Machine failure' column instead of 'Target'
        is_fail = int(row['Machine failure']) == 1
        
        # Determine specific failure reason from the separate boolean columns in the raw data
        fail_type = "Mechanical Error"
        if is_fail:
            if 'TWF' in row and row['TWF'] == 1: fail_type = "Tool Wear Failure"
            elif 'HDF' in row and row['HDF'] == 1: fail_type = "Heat Dissipation Failure"
            elif 'PWF' in row and row['PWF'] == 1: fail_type = "Power Failure"
            elif 'OSF' in row and row['OSF'] == 1: fail_type = "Overstrain Failure"
            elif 'RNF' in row and row['RNF'] == 1: fail_type = "Random Failure"
        else:
            fail_type = None
        
        qual_records.append({
            "production_id": idx + 1,
            "timestamp": current_time,
            "measured_torque": row['Torque [Nm]'],
            "measured_temp": row['Process temperature [K]'],
            "is_defect": is_fail,
            "defect_type": fail_type,
            "units_checked": 1,
            "units_defective": 1 if is_fail else 0
        })
        
        if is_fail:
            down_records.append({
                "timestamp": current_time,
                "machine_id": m_id,
                "shift_id": s_id,
                "downtime_mins": 15.0,
                "reason_code": fail_type,
                "is_planned": False
            })

    # Bulk upload everything straight to PostgreSQL
    pd.DataFrame(prod_records).to_sql("fact_production_records", engine, if_exists="append", index=False)
    pd.DataFrame(qual_records).to_sql("fact_quality_inspections", engine, if_exists="append", index=False)
    if down_records:
        pd.DataFrame(down_records).to_sql("fact_downtime_logs", engine, if_exists="append", index=False)
        
    print(f"[ETL] Database loaded flawlessly. Processed {len(raw_df)} true factory records.")