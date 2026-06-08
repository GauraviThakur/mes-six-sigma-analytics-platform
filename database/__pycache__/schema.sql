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