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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=8
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748")
    )
    bold_style = ParagraphStyle(
        'Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#2C5282")
    )
    quote_style = ParagraphStyle(
        'Quote_Custom',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=9.0,
        leading=12.5,
        textColor=colors.HexColor("#1A365D")
    )
    quote_author_style = ParagraphStyle(
        'QuoteAuthor_Custom',
        parent=body_style,
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#4A5568")
    )

    story = []

    # Title & Metadata
    product_name = report.get("product", "Synthetic User Research")
    report_date = report.get("report_date", "")
    story.append(Paragraph(f"Synthetic User Research Report: {product_name}", title_style))
    story.append(Paragraph(
        f"<b>Generated On:</b> {report_date} | "
        f"<b>Persona Sample Size:</b> {report.get('persona_count', 0)} synthetic profiles | "
        f"<b>Surveys Asked:</b> {report.get('survey_questions_asked', 0)} | "
        f"<b>Interviews:</b> {report.get('interview_sessions_count', 0)}",
        body_style
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    # Executive Summary (if present)
    exec_summary = report.get("executive_summary")
    if exec_summary:
        story.append(Paragraph("Executive Summary & Market Signal", h2_style))
        story.append(Paragraph(exec_summary, callout_style))
        story.append(Spacer(1, 10))

    # 1. 'Would Use This Product?' Adoption Propensity Scorecard
    would_use = report.get("would_use_score")
    if would_use:
        overall_score = would_use.get("overall_score", 0.0)
        story.append(Paragraph("1. 'Would Use This Product?' Adoption Propensity", h2_style))
        story.append(Paragraph(
            f"<b>Overall Target Market Adoption Score:</b> <font color='#2B6CB0'><b>{overall_score}%</b></font> — {would_use.get('score_label', '')}",
            body_style
        ))
        if would_use.get("summary_reasoning"):
            story.append(Spacer(1, 3))
            story.append(Paragraph(f"<i>Summary:</i> {would_use['summary_reasoning']}", body_style))
        story.append(Spacer(1, 6))

        # Segment breakdown table
        segments = would_use.get("segment_breakdown", [])
        if segments:
            seg_table_data = [[
                Paragraph("<b>Persona Segment / Archetype</b>", bold_style),
                Paragraph("<b>Score</b>", bold_style),
                Paragraph("<b>Stance</b>", bold_style),
                Paragraph("<b>Segment Reasoning</b>", bold_style)
            ]]
            for seg in segments:
                seg_table_data.append([
                    Paragraph(str(seg.get("segment", "Segment")), bold_style),
                    Paragraph(f"<b>{seg.get('score', 0)}%</b>", body_style),
                    Paragraph(str(seg.get("stance", "N/A")), body_style),
                    Paragraph(str(seg.get("reasoning", "N/A")), body_style)
                ])
            t_seg = Table(seg_table_data, colWidths=[130, 55, 105, 240])
            t_seg.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t_seg)
        story.append(Spacer(1, 10))

    # 2. Sentiment Distribution
    def _fmt_pct(v):
        if v is None:
            return "0.0%"
        try:
            val = float(v)
            if val <= 1.0:
                return f"{val * 100:.1f}%"
            return f"{val:.1f}%"
        except (ValueError, TypeError):
            return "0.0%"

    story.append(Paragraph("2. Sentiment & Response Distribution", h2_style))
    dist = report.get("sentiment_distribution", {})
    sentiment_data = [
        ["Sentiment Stance", "Percentage Share"],
        ["Positive Stance", _fmt_pct(dist.get('positive', 0))],
        ["Neutral Stance", _fmt_pct(dist.get('neutral', 0))],
        ["Negative / Critical Stance", _fmt_pct(dist.get('negative', 0))]
    ]
    t_sent = Table(sentiment_data, colWidths=[200, 150])
    t_sent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(t_sent)
    if report.get("sentiment_analysis"):
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<i>Analysis:</i> {report['sentiment_analysis']}", body_style))
    story.append(Spacer(1, 10))

    # 3. Emergent Theme Clusters
    story.append(Paragraph("3. Emergent Theme Clusters & Feedback Taxonomy", h2_style))
    clusters = report.get("theme_clusters", [])
    if clusters:
        cluster_table_data = [[
            Paragraph("<b>Category</b>", bold_style),
            Paragraph("<b>Theme Cluster</b>", bold_style),
            Paragraph("<b>Count</b>", bold_style),
            Paragraph("<b>Stance</b>", bold_style),
            Paragraph("<b>Cluster Synthesis</b>", bold_style)
        ]]
        for cl in clusters:
            cluster_table_data.append([
                Paragraph(str(cl.get("category", "General")), bold_style),
                Paragraph(str(cl.get("name", "Theme")), body_style),
                Paragraph(f"{cl.get('mention_count', 1)}", body_style),
                Paragraph(str(cl.get("sentiment", "neutral")).capitalize(), body_style),
                Paragraph(str(cl.get("summary", "")), body_style)
            ])
        t_cluster = Table(cluster_table_data, colWidths=[110, 140, 40, 50, 190])
        t_cluster.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_cluster)
    else:
        themes = report.get("themes", [])
        if themes:
            for i, th in enumerate(themes, 1):
                story.append(Paragraph(f"• <b>Theme {i}:</b> {th}", body_style))
        else:
            story.append(Paragraph("No significant themes extracted yet.", body_style))
    story.append(Spacer(1, 10))

    # 4. Agreement Patterns (Consensus vs Polarization)
    agreements = report.get("agreement_patterns")
    if agreements:
        story.append(Paragraph("4. Agreement Patterns & Stance Consistency", h2_style))
        for item in agreements.get("consensus", []):
            story.append(Paragraph(f"• <b>[Consensus]:</b> {item}", body_style))
            story.append(Spacer(1, 2))
        for item in agreements.get("polarization", []):
            story.append(Paragraph(f"• <b>[Polarization / Divergence]:</b> {item}", body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 8))

    # 5. Behavioral Trends
    story.append(Paragraph("5. Behavioral Cohort Trends", h2_style))
    trends = report.get("behavioral_trends", [])
    if trends:
        for trend in trends:
            grp = trend.get("group", "Cohort")
            finding = trend.get("finding", "")
            story.append(Paragraph(f"• <b>{grp}:</b> {finding}", body_style))
            story.append(Spacer(1, 3))
    story.append(Spacer(1, 8))

    # 6. Critical Objections
    objections = report.get("critical_objections", [])
    if objections:
        story.append(Paragraph("6. Critical Objections & Churn Risks", h2_style))
        for obj in objections:
            story.append(Paragraph(f"⚠ {obj}", body_style))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 8))

    # 7. Critical Insights & Recommendations
    story.append(Paragraph("7. Actionable Product Insights & Recommendations", h2_style))
    insights = report.get("top_insights", [])
    for ins in insights:
        story.append(Paragraph(f"✔ {ins}", body_style))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 8))

    # 8. Key Persona Quotes & Qualitative Voices
    quotes = report.get("key_persona_quotes", [])
    if quotes:
        story.append(Paragraph("8. Key Persona Quotes & Qualitative Voices", h2_style))
        quotes_table_data = [[
            Paragraph("<b>Persona & Archetype</b>", bold_style),
            Paragraph("<b>Verbatim Voice / Quote</b>", bold_style),
            Paragraph("<b>Topic & Sentiment</b>", bold_style)
        ]]
        for q in quotes:
            sent_str = str(q.get("sentiment", "neutral")).capitalize()
            p_header = f"<b>{q.get('persona_name', 'User')}</b><br/><i>{q.get('archetype', 'Participant')}</i>"
            q_text = f"\"{q.get('quote', '')}\""
            topic_str = f"<b>Topic:</b> {q.get('topic', 'General')}<br/><b>Stance:</b> {sent_str}"
            quotes_table_data.append([
                Paragraph(p_header, body_style),
                Paragraph(q_text, quote_style),
                Paragraph(topic_str, quote_author_style)
            ])
        t_quotes = Table(quotes_table_data, colWidths=[130, 275, 125])
        t_quotes.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_quotes)
        story.append(Spacer(1, 10))

    # 9. Curated Response Highlights
    highlights = report.get("response_highlights", [])
    if highlights:
        story.append(Paragraph("9. Curated Empirical Response Highlights", h2_style))
        high_table_data = [[
            Paragraph("<b>Source</b>", bold_style),
            Paragraph("<b>Topic / Query</b>", bold_style),
            Paragraph("<b>Empirical Highlight</b>", bold_style),
            Paragraph("<b>Respondent</b>", bold_style)
        ]]
        for h in highlights:
            high_table_data.append([
                Paragraph(str(h.get("source", "Simulation")), bold_style),
                Paragraph(str(h.get("topic", "Feedback")), body_style),
                Paragraph(str(h.get("highlight", "")), body_style),
                Paragraph(f"<b>{h.get('respondent_name', 'User')}</b><br/><i>{h.get('archetype', 'Cohort')}</i>", body_style)
            ])
        t_high = Table(high_table_data, colWidths=[80, 130, 210, 110])
        t_high.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_high)
        story.append(Spacer(1, 10))

    # 10. Comprehensive Persona Profiles Dossier
    story.append(Paragraph("10. Comprehensive Persona Profiles Dossier", h2_style))
    profiles = report.get("persona_profiles", [])
    if profiles:
        prof_table_data = [[
            Paragraph("<b>Persona & Demographics</b>", bold_style),
            Paragraph("<b>Archetype & Traits</b>", bold_style),
            Paragraph("<b>Primary Pain Points</b>", bold_style),
            Paragraph("<b>Willingness to Pay & Tools</b>", bold_style)
        ]]
        for prof in profiles:
            p_name_age = f"<b>{prof.get('name', 'Persona')}</b><br/>{prof.get('occupation', 'Professional')}<br/>{prof.get('location', '')} (Age {prof.get('age', 30)})"
            traits_str = ", ".join(prof.get("personality_traits", [])) if prof.get("personality_traits") else "Analytical"
            p_arch = f"<b>{prof.get('archetype', 'User')}</b><br/><i>Traits:</i> {traits_str}"
            p_pain = f"<b>Pain:</b> {prof.get('pain_points', 'Workflow delays')}<br/><b>Churn:</b> {prof.get('churn_triggers', 'High cost')}"
            p_wtp = f"<b>WTP:</b> {prof.get('willingness_to_pay', 'Standard')}<br/><b>Current:</b> {prof.get('current_tools', 'Legacy tools')}"
            prof_table_data.append([
                Paragraph(p_name_age, body_style),
                Paragraph(p_arch, body_style),
                Paragraph(p_pain, body_style),
                Paragraph(p_wtp, body_style)
            ])
        t_prof = Table(prof_table_data, colWidths=[125, 125, 140, 140])
        t_prof.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_prof)
    else:
        breakdown = report.get("per_persona_breakdown", [])
        for p in breakdown:
            p_name = p.get("name", "Unknown Persona")
            arch = p.get("archetype", "Archetype")
            summary = p.get("key_takeaway", "No summary")
            story.append(Paragraph(f"<b>{p_name} ({arch})</b>", bold_style))
            story.append(Paragraph(f"<i>Takeaway:</i> {summary}", body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    return output_path
