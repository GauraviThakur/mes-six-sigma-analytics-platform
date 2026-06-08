from config.settings import SMTP_SERVER, SMTP_PORT, SMTP_USER, REPORT_RECIPIENTS

def dispatch_production_reports(excel_path: str, pdf_path: str):
    """Mocks operational email routing. Prevents authentic authentication crashes during local runs."""
    print("[EMAIL] Initializing SMTP pipeline transmission block...")
    print(f"[EMAIL] Targeting Gateway: {SMTP_SERVER}:{SMTP_PORT} via Account: {SMTP_USER}")
    print(f"[EMAIL] Attaching Asset 1: {excel_path}")
    print(f"[EMAIL] Attaching Asset 2: {pdf_path}")
    print(f"[EMAIL] Delivering data package to Operations Distribution List: {REPORT_RECIPIENTS}")
    print("[EMAIL] Status: Outbound transfer simulation completed successfully. 0 packets dropped.")