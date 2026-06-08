import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgress") # Replace with your real Postgres password if different!
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mes_analytics")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Setup placeholder credentials for the automated email system
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "analytics@factory.com"
SMTP_PASSWORD = "mock_secure_password"
REPORT_RECIPIENTS = ["operations_manager@factory.com"]