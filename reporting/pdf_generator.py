import os
import matplotlib
matplotlib.use('Agg') # Runs headless without requiring UI thread window popup
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(oee_df: pd.DataFrame, spc_metrics: dict, output_path: str = "Daily_Quality_Performance_Report.pdf"):
    """Compiles analytical tables and custom Matplotlib SPC visual charts into a PDF summary report."""
    print(f"[REPORTING] Crafting automated PDF summary layout at {output_path}...")
    
    # 1. Generate PNG Trend Graph for the PDF report using Matplotlib
    chart_img = "temp_spc_chart.png"
    plt.figure(figsize=(6, 2.5))
    parameters = list(spc_metrics.keys())
    cpk_values = [spc_metrics[p]['cpk'] for p in parameters]
    
    colors_list = ['#2E75B6' if c >= 1.33 else '#C00000' for c in cpk_values]
    plt.barh(parameters, cpk_values, color=colors_list, height=0.4)
    plt.axvline(x=1.33, color='green', linestyle='--', label='Six Sigma Minimum (1.33)')
    plt.title("Process Capability Index (Cpk) Target Assessment")
    plt.xlabel("Cpk Value")
    plt.xlim(0, max(cpk_values) + 0.5)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(chart_img, dpi=200)
    plt.close()
    
    # 2. Setup ReportLab Document Elements
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ReportTitle', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#1F497D'), spaceAfter=15)
    body_style = ParagraphStyle('ReportBody', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=10)
    section_style = ParagraphStyle('SectionHeading', fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#1F497D'), spaceBefore=12, spaceAfter=8)
    
    # Write text paragraphs
    story.append(Paragraph("Manufacturing Execution System (MES) Analytics Report", title_style))
    story.append(Paragraph("This automated dashboard summarizes performance values, system run times, availability losses, and process control capabilities calculated from sensor array registers.", body_style))
    
    # Add OEE Table Section
    story.append(Paragraph("Overall Equipment Effectiveness Summary", section_style))
    oee_data = [["Machine ID", "Availability %", "Performance %", "Quality %", "OEE %"]]
    for _, row in oee_df.iterrows():
        oee_data.append([row['machine_id'], f"{row['availability']}%", f"{row['performance']}%", f"{row['quality']}%", f"{row['oee']}%"])
        
    t_oee = Table(oee_data, colWidths=[120, 100, 100, 100, 100])
    t_oee.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F2F2F2')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9)
    ]))
    story.append(t_oee)
    story.append(Spacer(1, 15))
    
    # Add Six Sigma Chart Section
    story.append(Paragraph("Six Sigma Quality Process Capability (SPC)", section_style))
    story.append(Image(chart_img, width=400, height=166))
    
    # Clean up document file
    doc.build(story)
    if os.path.exists(chart_img):
        os.remove(chart_img)
    print("[REPORTING] PDF presentation summary constructed successfully.")