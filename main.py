import os
from sqlalchemy import text
from database.connection import engine
from pipeline.etl import run_etl
from analytics.oee_engine import calculate_oee_metrics
from analytics.six_sigma import calculate_process_capability
from reporting.excel_generator import generate_excel_report
from reporting.pdf_generator import generate_pdf_report
from reporting.email_client import dispatch_production_reports

def initialize_database():
    """Builds the database tables cleanly by executing the entire SQL script block in a single transaction."""
    print("[INIT] Building database schema tables...")
    
    sql_script = """
    DROP TABLE IF EXISTS fact_downtime_logs CASCADE;
    DROP TABLE IF EXISTS fact_quality_inspections CASCADE;
    DROP TABLE IF EXISTS fact_production_records CASCADE;
    DROP TABLE IF EXISTS dim_shifts CASCADE;
    DROP TABLE IF EXISTS dim_machines CASCADE;
    DROP TABLE IF EXISTS dim_products CASCADE;

    CREATE TABLE dim_products (
        product_id VARCHAR(50) PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        product_type VARCHAR(10) NOT NULL,
        target_torque NUMERIC(6,2),
        usl_torque NUMERIC(6,2),
        lsl_torque NUMERIC(6,2),
        target_temp NUMERIC(6,2),
        usl_temp NUMERIC(6,2),
        lsl_temp NUMERIC(6,2)
    );

    CREATE TABLE dim_machines (
        machine_id VARCHAR(50) PRIMARY KEY,
        machine_name VARCHAR(100) NOT NULL,
        work_center VARCHAR(50) NOT NULL,
        design_speed_rpm NUMERIC(6,2) NOT NULL
    );

    CREATE TABLE dim_shifts (
        shift_id VARCHAR(20) PRIMARY KEY,
        shift_name VARCHAR(50) NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        planned_runtime_mins NUMERIC(6,2) NOT NULL
    );

    CREATE TABLE fact_production_records (
        production_id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        machine_id VARCHAR(50) REFERENCES dim_machines(machine_id),
        product_id VARCHAR(50) REFERENCES dim_products(product_id),
        shift_id VARCHAR(20) REFERENCES dim_shifts(shift_id),
        rotational_speed_rpm NUMERIC(6,2),
        torque_nm NUMERIC(6,2),
        tool_wear_mins NUMERIC(6,2),
        air_temp_k NUMERIC(6,2),
        process_temp_k NUMERIC(6,2),
        total_pieces_produced INT NOT NULL,
        cycle_time_secs NUMERIC(6,2) NOT NULL
    );

    CREATE TABLE fact_quality_inspections (
        inspection_id SERIAL PRIMARY KEY,
        production_id INT REFERENCES fact_production_records(production_id),
        timestamp TIMESTAMP NOT NULL,
        measured_torque NUMERIC(6,2),
        measured_temp NUMERIC(6,2),
        is_defect BOOLEAN NOT NULL,
        defect_type VARCHAR(50),
        units_checked INT NOT NULL,
        units_defective INT NOT NULL
    );

    CREATE TABLE fact_downtime_logs (
        downtime_id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        machine_id VARCHAR(50) REFERENCES dim_machines(machine_id),
        shift_id VARCHAR(20) REFERENCES dim_shifts(shift_id),
        downtime_mins NUMERIC(6,2) NOT NULL,
        reason_code VARCHAR(100) NOT NULL,
        is_planned BOOLEAN NOT NULL
    );
    """
    
    # engine.begin() ensures ALL tables are created perfectly together or none at all
    with engine.begin() as conn:
        conn.execute(text(sql_script))
    print("[INIT] Database structure initialized successfully.")

if __name__ == "__main__":
    print("\n=== STARTING MANUFACTURING EXECUTION PLATFORM ===")
    
    try:
        # 1. Initialize the structure
        initialize_database()
        
        # 2. Run Data Stream & Engineering ETL
        run_etl()
        
        # 3. Process Advanced Manufacturing Analytics
        oee_df = calculate_oee_metrics()
        spc_metrics = calculate_process_capability()
        
        # 4. Generate Professional Business Documentation
        excel_name = "MES_Manufacturing_Performance_Report.xlsx"
        pdf_name = "Daily_Quality_Performance_Report.pdf"
        
        generate_excel_report(oee_df, spc_metrics, output_path=excel_name)
        generate_pdf_report(oee_df, spc_metrics, output_path=pdf_name)
        
        # 5. Route Automated Output Assets
        dispatch_production_reports(excel_path=excel_name, pdf_path=pdf_name)
        
        print("=== MES PLATFORM RUN COMPLETED SUCCESSFULLY WITHOUT ERRORS ===\n")
        
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Pipeline execution halted: {e}\n")