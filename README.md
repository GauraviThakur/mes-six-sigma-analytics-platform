# Manufacturing Execution System (MES) & Six Sigma Analytics Platform

An end-to-end data engineering pipeline that ingests industrial manufacturing sensor logs, stores them in a relational database, calculates core performance metrics, and generates automated enterprise executive reports.

## 🚀 Key Features
* **ETL Ingestion Pipeline:** Automated data pipeline to download, unpack, and stream 10,000 factory production records into a structured PostgreSQL database.
* **Analytics Engine:** Programs high-fidelity calculations for Operational Equipment Effectiveness (OEE) components (Availability, Performance, Quality).
* **Six Sigma SPC Analysis:** Evaluates process capability indicators ($C_{pk}$) to detect statistical quality drifts across distinct manufacturing work centers.
* **Automated Reporting:** Programmatically generates professional, custom-styled Excel dashboards (OpenPyXL) and production-grade PDF summaries (ReportLab).

## 🛠️ Tech Stack
* **Language:** Python 3
* **Database:** PostgreSQL / SQLAlchemy Object-Relational Mapper (ORM)
* **Libraries:** Pandas, NumPy, ReportLab, OpenPyXL