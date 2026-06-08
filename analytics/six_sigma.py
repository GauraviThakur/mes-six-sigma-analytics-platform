import pandas as pd
import numpy as np
from database.connection import get_db

def calculate_process_capability() -> dict:
    """Computes Mean, Sigma, Control Limits, Cp, and Cpk for critical parameters."""
    print("[ANALYTICS] Running Six Sigma Statistical Process Control (SPC)...")
    db = get_db()
    
    query = """
    SELECT p.torque_nm, p.process_temp_k, pr.usl_torque, pr.lsl_torque, pr.usl_temp, pr.lsl_temp 
    FROM fact_production_records p
    JOIN dim_products pr ON p.product_id = pr.product_id;
    """
    df = pd.read_sql(query, db.bind)
    db.close()
    
    if df.empty:
        return {}
        
    metrics = {}
    # Analyze variables: Torque and Temperature
    for var, usl_col, lsl_col, label in [('torque_nm', 'usl_torque', 'lsl_torque', 'Torque'),
                                         ('process_temp_k', 'usl_temp', 'lsl_temp', 'Temperature')]:
        data = df[var].dropna().values
        mean = np.mean(data)
        sigma = np.std(data, ddof=1) if len(data) > 1 else 0.001
        if sigma == 0: sigma = 0.001
        
        usl = df[usl_col].iloc[0]
        lsl = df[lsl_col].iloc[0]
        
        # Six Sigma Formula calculations
        ucl = mean + (3 * sigma)
        lcl = mean - (3 * sigma)
        
        cp = (usl - lsl) / (6 * sigma)
        cpk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
        
        metrics[label] = {
            "mean": round(float(mean), 2),
            "sigma": round(float(sigma), 2),
            "ucl": round(float(ucl), 2),
            "lcl": round(float(lcl), 2),
            "usl": float(usl),
            "lsl": float(lsl),
            "cp": round(float(cp), 2),
            "cpk": round(float(cpk), 2)
        }
        
    return metrics