import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from beanie import PydanticObjectId

from db.models import User, Experiment, Persona, SurveySession, InterviewSession, ResearchReport
from auth.dependencies import get_current_user, get_user_from_auth_or_query
from services import insight_agent
from utils.pdf_exporter import export_pdf

router = APIRouter(prefix="/api", tags=["Reports & Analytics"])


@router.get("/adoption-score")
async def get_adoption_score(current_user: User = Depends(get_current_user)):
    """Calculates and returns the 'Would use this product?' adoption propensity score."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found.")

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    persona_docs = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == str(exp.id)
    ).to_list()

    if not persona_docs:
        raise HTTPException(status_code=400, detail="No personas found for active product. Generate personas first.")

    personas_dicts = [
        {
            "id": p.persona_id,
            "name": p.name,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "opinion_seeds": p.opinion_seeds
        }
        for p in persona_docs
    ]

    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str,
        SurveySession.experiment_id == str(exp.id)
    ).sort(-SurveySession.created_at).first_or_none()

    survey_data = {
        "questions": latest_survey.questions if latest_survey else [],
        "responses": latest_survey.responses if latest_survey else []
    }

    score_data = insight_agent.calculate_would_use_score(exp_dict, personas_dicts, survey_data)
    
    # Calculate response sentiment counts
    pos_count = 0
    neu_count = 0
    neg_count = 0
    total_answers = 0
    for resp in survey_data.get("responses", []):
        for ans in resp.get("answers", []):
            total_answers += 1
            s = str(ans.get("sentiment", "neutral")).lower()
            if s == "positive":
                pos_count += 1
            elif s == "negative":
                neg_count += 1
            else:
                neu_count += 1

    score_data["total_personas"] = len(persona_docs)
    score_data["breakdown"] = {
        "positive_sentiment_count": pos_count,
        "neutral_sentiment_count": neu_count,
        "negative_sentiment_count": neg_count,
        "total_responses": total_answers,
        "would_use_count": sum(1 for s in score_data.get("segment_breakdown", []) if s.get("score", 0) >= 50)
    }
    score_data["adoption_score"] = round(score_data.get("overall_score", 0) / 100.0, 3)
    score_data["sentiment_label"] = score_data.get("score_label", "Evaluated")
    score_data["product_name"] = exp.product_name
    return score_data


@router.api_route("/generate-report", methods=["GET", "POST"])
async def generate_report(current_user: User = Depends(get_current_user)):
    """Generates an executive research synthesis report and stores it in MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found.")

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    persona_docs = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == str(exp.id)
    ).to_list()
    if not persona_docs:
        raise HTTPException(status_code=400, detail="No personas found for active product. Generate personas first.")

    personas_dicts = [
        {
            "id": p.persona_id,
            "name": p.name,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "opinion_seeds": p.opinion_seeds
        }
        for p in persona_docs
    ]

    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str,
        SurveySession.experiment_id == str(exp.id)
    ).sort(-SurveySession.created_at).first_or_none()

    survey_data = {
        "questions": latest_survey.questions if latest_survey else [],
        "responses": latest_survey.responses if latest_survey else []
    }

    interview_sessions = await InterviewSession.find(
        InterviewSession.user_id == user_id_str,
        InterviewSession.experiment_id == str(exp.id)
    ).to_list()

    interview_logs = [
        {
            "session_id": s.session_id,
            "persona_id": s.persona_id,
            "persona_name": s.persona_name,
            "archetype": s.archetype,
            "turns": s.turns
        }
        for s in interview_sessions
    ]

    try:
        report = insight_agent.generate_report(
            experiment=exp_dict,
            personas=personas_dicts,
            survey_data=survey_data,
            interview_logs=interview_logs,
            save_to_file=True
        )

        # Store in MongoDB
        doc = ResearchReport(
            user_id=user_id_str,
            experiment_id=str(exp.id),
            timestamp=datetime.utcnow().isoformat(),
            date_str=report.get("report_date", datetime.utcnow().strftime("%Y-%m-%d")),
            product_name=exp.product_name,
            executive_summary=report.get("executive_summary", ""),
            findings=report.get("findings", []),
            sentiment_analysis=report.get("sentiment_distribution", {}),
            behavioral_themes=report.get("behavioral_trends", []),
            adoption_score=report.get("would_use_score", {}),
            strategic_recommendations=report.get("top_insights", []),
            domain_context=report.get("domain_context", {}),
            raw_data=report
        )
        await doc.insert()
        report["id"] = str(doc.id)

        # Export report with doc.id for stable ID retrieval
        try:
            os.makedirs("reports", exist_ok=True)
            export_pdf(report, f"reports/report_{doc.id}.pdf")
        except Exception as pdf_err:
            print(f"Notice: Non-critical PDF export error: {pdf_err}")

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/latest")
async def get_latest_report(current_user: User = Depends(get_current_user)):
    """Returns the most recent research report generated for the active product."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        return {"report": None}

    doc = await ResearchReport.find(
        ResearchReport.user_id == user_id_str,
        ResearchReport.experiment_id == str(exp.id)
    ).sort(-ResearchReport.created_at).first_or_none()

    if not doc:
        return {"report": None}

    report_data = doc.raw_data or {}
    if not report_data:
        report_data = {
            "id": str(doc.id),
            "product": doc.product_name,
            "report_date": doc.date_str,
            "executive_summary": doc.executive_summary,
            "would_use_score": doc.adoption_score,
            "sentiment_distribution": doc.sentiment_analysis,
            "behavioral_trends": doc.behavioral_themes,
            "top_insights": doc.strategic_recommendations,
        }
    report_data["id"] = str(doc.id)
    return {"report": report_data}


@router.get("/reports/latest/pdf")
async def get_latest_report_pdf(
    user: User = Depends(get_user_from_auth_or_query)
):
    """Streams the PDF file for the most recent research report of the active product."""
    user_id_str = str(user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=404, detail="No active product found.")

    doc = await ResearchReport.find(
        ResearchReport.user_id == user_id_str,
        ResearchReport.experiment_id == str(exp.id)
    ).sort(-ResearchReport.created_at).first_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="No generated reports found for active product.")

    doc_id_str = str(doc.id)
    pdf_path = f"reports/report_{doc_id_str}.pdf"
    date_pdf_path = f"reports/report_{doc.date_str}.pdf"

    if not os.path.exists(pdf_path):
        if os.path.exists(date_pdf_path):
            pdf_path = date_pdf_path
        elif doc.raw_data:
            os.makedirs("reports", exist_ok=True)
            export_pdf(doc.raw_data, pdf_path)
        else:
            raise HTTPException(status_code=404, detail="PDF report file not found on disk.")

    safe_name = "".join(c for c in doc.product_name if c.isalnum() or c in (" ", "_", "-")).strip() or "Research"
    safe_name = safe_name.replace(" ", "_")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{safe_name}_Research_Report.pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}_Research_Report.pdf"'
        }
    )


@router.get("/reports/{report_id}/pdf")
async def get_report_pdf_by_id(
    report_id: str,
    user: User = Depends(get_user_from_auth_or_query)
):
    """Streams the PDF file for a specific research report by ID."""
    user_id_str = str(user.id)

    try:
        obj_id = PydanticObjectId(report_id)
        doc = await ResearchReport.get(obj_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report ID format.")

    if not doc or doc.user_id != user_id_str:
        raise HTTPException(status_code=404, detail="Report not found.")

    pdf_path = f"reports/report_{report_id}.pdf"
    date_pdf_path = f"reports/report_{doc.date_str}.pdf"

    if not os.path.exists(pdf_path):
        if os.path.exists(date_pdf_path):
            pdf_path = date_pdf_path
        elif doc.raw_data:
            os.makedirs("reports", exist_ok=True)
            export_pdf(doc.raw_data, pdf_path)
        else:
            raise HTTPException(status_code=404, detail="PDF report file not found.")

    safe_name = "".join(c for c in doc.product_name if c.isalnum() or c in (" ", "_", "-")).strip() or "Research"
    safe_name = safe_name.replace(" ", "_")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{safe_name}_Research_Report.pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}_Research_Report.pdf"'
        }
    )


@router.get("/reports")
async def list_reports(
    experiment_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Lists past research reports generated for the user."""
    user_id_str = str(current_user.id)
    exp_id = experiment_id
    if not exp_id:
        exp = await Experiment.find_one(
            Experiment.user_id == user_id_str,
            Experiment.is_active == True
        )
        if exp:
            exp_id = str(exp.id)

    if exp_id:
        reports = await ResearchReport.find(
            ResearchReport.user_id == user_id_str,
            ResearchReport.experiment_id == exp_id
        ).sort(-ResearchReport.created_at).to_list()
    else:
        reports = await ResearchReport.find(
            ResearchReport.user_id == user_id_str
        ).sort(-ResearchReport.created_at).to_list()

    return {
        "count": len(reports),
        "reports": [
            {
                "id": str(r.id),
                "product_name": r.product_name,
                "date_str": r.date_str,
                "executive_summary": r.executive_summary[:200] if r.executive_summary else "",
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]
    }
