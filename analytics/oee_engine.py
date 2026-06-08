import pandas as pd
from database.connection import engine

def calculate_oee_metrics():
    print("[ANALYTICS] Computing high-fidelity OEE metrics across work centers...")
    
    # 1. Fetch real production tracking metrics from PostgreSQL
    prod_df = pd.read_sql("SELECT * FROM fact_production_records", engine)
    qual_df = pd.read_sql("SELECT * FROM fact_quality_inspections", engine)
    down_df = pd.read_sql("SELECT * FROM fact_downtime_logs", engine)
    
    metrics = []
    
    # Standardize reading columns regardless of lowercase/uppercase defaults
    machine_col = 'machine_id' if 'machine_id' in prod_df.columns else prod_df.columns[2]
    
    for machine in prod_df[machine_col].unique():
        m_prod = prod_df[prod_df[machine_col] == machine]
        m_qual = qual_df[qual_df['production_id'].isin(m_prod['production_id'])]
        m_down = down_df[down_df['machine_id'] == machine] if not down_df.empty else pd.DataFrame()
        
        # Calculate real factory time metrics (1 row = 1 minute format)
        total_observed_mins = len(m_prod)
        total_downtime_mins = m_down['downtime_mins'].sum() if not m_down.empty else 0
        
        # 1. Availability Component
        operating_time = max(0, total_observed_mins - total_downtime_mins)
        availability = (operating_time / total_observed_mins) if total_observed_mins > 0 else 0
        
        # 2. Performance Component (Mean RPM vs 1500 RPM Baseline Design Limit)
        speed_col = 'rotational_speed_rpm'
        performance = min(1.0, (m_prod[speed_col].mean() / 1500.0)) if not m_prod.empty else 0
        
        # 3. Quality Component (Good Pieces / Total Inspected Pieces)
        total_checked = m_qual['units_checked'].sum() if not m_qual.empty else 0
        total_defective = m_qual['units_defective'].sum() if not m_qual.empty else 0
        good_units = total_checked - total_defective
        quality = (good_units / total_checked) if total_checked > 0 else 1.0
        
        # Combined OEE Metric
        oee = availability * performance * quality
        
        # Formatting decimals correctly to clean percentage representations
        metrics.append({
            "Machine ID": machine,
            "machine_id": machine,
            "Availability %": f"{availability * 100:.2f}%",
            "Performance %": f"{performance * 100:.2f}%",
            "Quality %": f"{quality * 100:.2f}%",
            "OEE %": f"{oee * 100:.2f}%",
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee
        })
        
    return pd.DataFrame(metrics)