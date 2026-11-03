"""
FireCast AI — PDF & CSV Prediction Report Generation
"""

import os
import io
import datetime
from typing import Dict, Any, Optional
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from src.utils import logger, load_config


def generate_pdf_report(pred_result: Dict[str, Any], filepath: Optional[str] = None) -> bytes:
    """
    Generates a professional executive PDF report summarizing the wildfire burned-area
    prediction, input parameters, severity band, and scientific disclaimer.
    """
    config = load_config()
    buffer = io.BytesIO() if filepath is None else open(filepath, "wb")
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#FF6B35")
    c_dark = colors.HexColor("#0D121A")
    c_text = colors.HexColor("#1A2530")
    c_subtext = colors.HexColor("#5A6A7E")
    c_border = colors.HexColor("#D8E0E8")
    
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=c_primary
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=c_subtext
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=c_dark,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=c_subtext
    )
    
    story = []
    
    # Brand Header
    story.append(Paragraph("FIRECAST AI — PREDICTION INTELLIGENCE REPORT", title_style))
    story.append(Paragraph(
        f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC | "
        f"Platform Version: {config['app']['version']} | Model: {pred_result['model_used']}",
        subtitle_style
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=14))
    
    # Executive Summary Card
    ha_val = pred_result["burned_area_ha"]
    sev_name = pred_result["severity"]["name"]
    sev_desc = pred_result["severity"]["summary"]
    
    summary_data = [
        [
            Paragraph("<b>PREDICTED BURNED AREA</b>", subtitle_style),
            Paragraph("<b>SEVERITY CLASSIFICATION</b>", subtitle_style)
        ],
        [
            Paragraph(f"<font size=20 color='#FF6B35'><b>{ha_val:,.2f} hectares</b></font>", body_style),
            Paragraph(f"<font size=14 color='#111923'><b>{sev_name}</b></font><br/>{sev_desc}", body_style)
        ],
        [
            Paragraph(f"<b>Inference Latency:</b> {pred_result['inference_time_ms']} ms", subtitle_style),
            Paragraph(f"<b>Percentile Ref:</b> {pred_result['severity']['percentile_ref']}", subtitle_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[240, 290])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))
    
    # Input Telemetry Table
    story.append(Paragraph("Meteorological & Fuel Moisture Inputs", section_style))
    inputs = pred_result["input_summary"]
    
    input_rows = [
        ["Parameter", "Input Value", "Parameter", "Input Value"],
        ["Month", inputs["month"].upper(), "Fine Fuel Moisture (FFMC)", f"{inputs['FFMC']:.1f}"],
        ["Day of Week", inputs["day"].upper(), "Duff Moisture Code (DMC)", f"{inputs['DMC']:.1f}"],
        ["Air Temperature", f"{inputs['temp']} °C", "Drought Code (DC)", f"{inputs['DC']:.1f}"],
        ["Relative Humidity", f"{inputs['RH']} %", "Initial Spread Index (ISI)", f"{inputs['ISI']:.1f}"],
        ["Wind Velocity", f"{inputs['wind']} km/h", "Antecedent Rain", f"{inputs['rain']} mm"]
    ]
    input_table = Table(input_rows, colWidths=[135, 130, 135, 130])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_dark),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 14))
    
    # Major Contributing Drivers (SHAP)
    story.append(Paragraph("Primary Explanatory Factors (SHAP Attribution)", section_style))
    shap_info = pred_result.get("shap_explanation")
    if shap_info and "contributions" in shap_info:
        top_c = shap_info["contributions"][:5]
        driver_rows = [["Feature", "Direction", "Impact on log(Area)", "Interpretation"]]
        for c in top_c:
            direction_str = "Upward" if c["shap_value"] > 0 else "Downward"
            interp = "Elevates estimated fire perimeter" if c["shap_value"] > 0 else "Suppresses estimated fire growth"
            driver_rows.append([
                c["feature"],
                direction_str,
                f"{c['shap_value']:+.3f}",
                interp
            ])
        driver_table = Table(driver_rows, colWidths=[150, 75, 110, 195])
        driver_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#24303D")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(driver_table)
    else:
        story.append(Paragraph("Local feature contribution analysis not requested or unavailable.", body_style))
        
    story.append(Spacer(1, 16))
    
    # Boundary Warnings
    if pred_result.get("warnings"):
        story.append(Paragraph("Extrapolation & Boundary Advisories", section_style))
        for w in pred_result["warnings"]:
            clean_w = w.replace("**", "")
            story.append(Paragraph(f"• {clean_w}", body_style))
        story.append(Spacer(1, 10))

    # Mandatory Scientific Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceBefore=8, spaceAfter=8))
    story.append(Paragraph("<b>MANDATORY SCIENTIFIC DISCLAIMER & LIMITATIONS:</b>", disclaimer_style))
    story.append(Paragraph(
        "FireCast AI is a research-grade regression platform trained on 517 historical fire events from Montesinho Natural Park, "
        "Portugal (UCI Machine Learning Repository, Cortez & Morais 2007). The platform estimates potential conditional burned area "
        "in hectares IF a fire occurs. It does NOT predict whether a wildfire will ignite, guarantee fire prevention, or replace "
        "official emergency dispatch and civil protection warnings. Meteorological parameters explain only a portion of fire growth; "
        "topography, fuel loads, and suppression responses remain unmodeled.",
        disclaimer_style
    ))
    
    doc.build(story)
    
    if filepath is None:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    else:
        buffer.close()
        logger.info(f"Saved PDF report to {filepath}")
        return b""
