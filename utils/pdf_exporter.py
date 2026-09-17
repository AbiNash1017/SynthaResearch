import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def export_pdf(report: Dict[str, Any], output_path: str) -> str:
    """Generates a structured multi-page PDF research report from report dict."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748")
    )
    bold_style = ParagraphStyle(
        'Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Title & Metadata
    product_name = report.get("product", "Synthetic User Research")
    report_date = report.get("report_date", "")
    story.append(Paragraph(f"Synthetic User Research Report: {product_name}", title_style))
    story.append(Paragraph(f"<b>Generated On:</b> {report_date} | <b>Persona Sample Size:</b> {report.get('persona_count', 0)} synthetic profiles", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E0"), spaceAfter=15))
    
    # 1. Executive Summary & Sentiment Distribution
    story.append(Paragraph("1. Sentiment & Response Distribution", h2_style))
    dist = report.get("sentiment_distribution", {})
    sentiment_data = [
        ["Sentiment Stance", "Percentage Share"],
        ["Positive Stance", f"{dist.get('positive', 0)*100:.1f}%"],
        ["Neutral Stance", f"{dist.get('neutral', 0)*100:.1f}%"],
        ["Negative / Critical Stance", f"{dist.get('negative', 0)*100:.1f}%"]
    ]
    t_sent = Table(sentiment_data, colWidths=[200, 150])
    t_sent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(t_sent)
    story.append(Spacer(1, 12))
    
    # 2. Key Emergent Themes
    story.append(Paragraph("2. Top Emergent Themes", h2_style))
    themes = report.get("themes", [])
    if themes:
        for i, th in enumerate(themes, 1):
            story.append(Paragraph(f"• <b>Theme {i}:</b> {th.capitalize()}", body_style))
    else:
        story.append(Paragraph("No significant themes extracted yet.", body_style))
    story.append(Spacer(1, 12))
    
    # 3. Behavioral Trends
    story.append(Paragraph("3. Behavioral Cohort Trends", h2_style))
    trends = report.get("behavioral_trends", [])
    if trends:
        for trend in trends:
            grp = trend.get("group", "Cohort")
            finding = trend.get("finding", "")
            story.append(Paragraph(f"• <b>{grp}:</b> {finding}", body_style))
            story.append(Spacer(1, 4))
    story.append(Spacer(1, 10))
    
    # 4. Critical Insights
    story.append(Paragraph("4. Actionable Product Insights", h2_style))
    insights = report.get("top_insights", [])
    for ins in insights:
        story.append(Paragraph(f"✔ {ins}", body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 10))
    
    # 5. Persona Profiles Breakdown
    story.append(Paragraph("5. Synthetic Persona Cohort Breakdown", h2_style))
    breakdown = report.get("per_persona_breakdown", [])
    for p in breakdown:
        p_name = p.get("name", "Unknown Persona")
        arch = p.get("archetype", "Archetype")
        summary = p.get("key_takeaway", "No summary")
        story.append(Paragraph(f"<b>{p_name} ({arch})</b>", bold_style))
        story.append(Paragraph(f"<i>Takeaway:</i> {summary}", body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    return output_path
