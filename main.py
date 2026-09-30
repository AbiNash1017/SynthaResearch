import sys
import warnings
from pathlib import Path

# Ensure venv site-packages is discoverable if present
_venv_site = Path(__file__).resolve().parent / "venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

from datetime import datetime
from rich.console import Console

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")
from rich.panel import Panel
from rich.prompt import Prompt

from agents.persona_generator import PersonaGenerationAgent
from agents.survey_agent import SurveyAgent
from agents.interview_agent import InterviewAgent
from agents.insight_agent import InsightExtractionAgent
from config.settings import (
    is_openrouter_configured,
    OPENROUTER_MODEL,
    OPENROUTER_API_KEY
)
from utils.storage import load_json, save_json

console = Console()

def setup_experiment_cli():
    console.print(Panel("[bold cyan]Setup Product Research Workspace[/bold cyan]", border_style="cyan"))

    name = Prompt.ask("Product Name").strip()
    while not name:
        name = Prompt.ask("[red]Product Name cannot be empty. Please enter Product Name[/red]").strip()

    industry = Prompt.ask("Product Domain / Industry (e.g., B2B SaaS, Health & Wellness, FinTech, DevTools, E-Commerce)").strip()
    if not industry:
        industry = "General Technology"

    desc = Prompt.ask("Product Description & Core Value Proposition").strip()
    while not desc:
        desc = Prompt.ask("[red]Description cannot be empty. Please enter Product Description[/red]").strip()

    audience = Prompt.ask("Target Audience & User Demographics").strip()
    while not audience:
        audience = Prompt.ask("[red]Audience cannot be empty. Please enter Target Audience[/red]").strip()

    console.print("\nEnter Research Objectives (press Enter on empty line to finish):")
    objectives = []
    idx = 1
    while True:
        obj = Prompt.ask(f"Objective {idx} (or leave empty to finish)").strip()
        if not obj:
            if not objectives:
                console.print("[yellow]Please provide at least one research objective.[/yellow]")
                continue
            break
        objectives.append(obj)
        idx += 1

    raw_exp = {
        "product_name": name,
        "industry_domain": industry,
        "product_description": desc,
        "target_audience": audience,
        "research_objectives": objectives,
        "created_at": datetime.now().isoformat()
    }
    from utils.normalizer import normalize_experiment
    experiment = normalize_experiment(raw_exp)
    experiment.pop("_domain_profile", None)
    save_json("data/experiment.json", experiment)
    console.print(f"\n[bold green]✔ Workspace configured & normalized (typos auto-corrected):[/bold green]")
    console.print(f"  [cyan]Product:[/cyan] {experiment['product_name']}")
    console.print(f"  [cyan]Domain:[/cyan] {experiment['industry_domain']}")
    console.print(f"  [cyan]Target Audience:[/cyan] {experiment['target_audience']}")
    console.print(f"  [dim]Saved to data/experiment.json[/dim]\n")
    return experiment

def display_banner(exp):
    if exp:
        from utils.normalizer import normalize_experiment
        norm = normalize_experiment(exp)
        p_name = norm.get("product_name", "None (Setup Required)")
        domain = norm.get("industry_domain", "N/A")
    else:
        p_name = "None (Setup Required)"
        domain = "N/A"

    if is_openrouter_configured():
        llm_status = f"[green]Active ({OPENROUTER_MODEL})[/green]"
    else:
        llm_status = "[bold red]Not Configured — set OPENROUTER_API_KEY and OPENROUTER_MODEL in .env[/bold red]"

    banner_text = (
        f"[bold green]UNIVERSAL SYNTHETIC USER RESEARCH PLATFORM[/bold green]\n"
        f"[dim]AI-Powered Multi-Persona Simulation & Qualitative Discovery for Any Product[/dim]\n"
        f"[bold]Active Product:[/bold] [yellow]{p_name}[/yellow] [dim]({domain})[/dim]\n"
        f"[bold]OpenRouter LLM:[/bold] {llm_status}"
    )
    console.print(Panel(banner_text, border_style="green"))

MENU_CHOICES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

def _print_menu():
    console.print("\n[bold cyan]━━━  RESEARCH ACTIONS  ━━━[/bold cyan]")
    console.print(" [bold]1.[/bold]  Setup / Edit Experiment Workspace")
    console.print(" [bold]2.[/bold]  Generate Synthetic Personas")
    console.print("\n[bold cyan]━━━  SURVEY  ━━━[/bold cyan]")
    console.print(" [bold]3.[/bold]  Run Multi-Persona Survey  [dim](parallel execution, all personas)[/dim]")
    console.print(" [bold]4.[/bold]  View Survey Matrix  [dim](side-by-side comparison grid)[/dim]")
    console.print("\n[bold cyan]━━━  INTERVIEW  ━━━[/bold cyan]")
    console.print(" [bold]5.[/bold]  Start / Resume Interactive Interview with a Persona")
    console.print(" [bold]6.[/bold]  View All Interview Sessions  [dim](session history log)[/dim]")
    console.print("\n[bold cyan]━━━  INSIGHTS & SCORING  ━━━[/bold cyan]")
    console.print(" [bold]7.[/bold]  Generate Research & Insight Report  [dim](JSON + PDF export)[/dim]")
    console.print(" [bold]8.[/bold]  View Adoption Scorecard  [dim]('Would use this product?' by segment)[/dim]")
    console.print(" [bold]9.[/bold]  View Agreement & Polarization Patterns  [dim](consensus vs divergence)[/dim]")
    console.print("\n[bold cyan]━━━  VALIDATION  ━━━[/bold cyan]")
    console.print(" [bold]10.[/bold] Run Multi-Domain Validation Suite  [dim](persona consistency & theme quality)[/dim]")
    console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
    console.print(" [bold]11.[/bold] API Server Info  [dim](FastAPI endpoints reference)[/dim]")
    console.print(" [bold]12.[/bold] Exit\n")


def _display_adoption_scorecard(report: dict):
    from rich.table import Table
    # Insight agent stores under 'would_use_score' (not 'would_use_scoring')
    scoring = report.get("would_use_score", report.get("would_use_scoring", {}))
    if not scoring:
        console.print("[yellow]No adoption scoring data found. Generate a report first (Option 7).[/yellow]")
        return

    overall = scoring.get("overall_score", scoring.get("overall_adoption_score", "N/A"))
    summary = scoring.get("summary_reasoning", scoring.get("summary", scoring.get("interpretation", "")))
    console.print(Panel(
        f"[bold green]Overall Adoption Score: [yellow]{overall}%[/yellow][/bold green]\n"
        f"[dim]{summary}[/dim]",
        title="[bold]'Would Use This Product?' — Adoption Scorecard[/bold]",
        border_style="green"
    ))

    # Insight agent uses 'segment_breakdown' list with 'archetype', 'adoption_likelihood', 'reasoning'
    cohorts = scoring.get("segment_breakdown", scoring.get("cohort_breakdown", []))
    if cohorts:
        table = Table(title="Segment Breakdown", border_style="cyan", show_lines=True)
        table.add_column("Archetype / Segment", style="bold cyan")
        table.add_column("Adoption Score", justify="center")
        table.add_column("Reasoning", style="dim")
        for cohort in cohorts:
            seg = cohort.get("archetype", cohort.get("segment", "Unknown"))
            score = str(cohort.get("adoption_likelihood", cohort.get("adoption_score", cohort.get("score", "N/A"))))
            reason = cohort.get("reasoning", cohort.get("rationale", ""))[:120]
            table.add_row(seg, score, reason)
        console.print(table)


def _display_agreement_patterns(report: dict):
    from rich.table import Table
    patterns = report.get("agreement_patterns", {})
    if not patterns:
        console.print("[yellow]No agreement pattern data found. Generate a report first (Option 7).[/yellow]")
        return

    console.print(Panel(
        "[bold]Consensus & Polarization Analysis[/bold]\n"
        "[dim]Topics where personas agree (consensus) vs sharply diverge (polarization)[/dim]",
        border_style="magenta"
    ))

    consensus = patterns.get("consensus_items", patterns.get("consensus", []))
    polarized = patterns.get("polarization_items", patterns.get("polarization", []))

    if consensus:
        table = Table(title="[green]Consensus Topics[/green]  (≥65% agreement)", border_style="green", show_lines=True)
        table.add_column("Topic", style="bold")
        table.add_column("Shared Stance", justify="center")
        table.add_column("Agreement %", justify="center", style="green")
        table.add_column("Notes", style="dim")
        for item in consensus:
            table.add_row(
                str(item.get("topic", item.get("item", ""))),
                str(item.get("stance", item.get("shared_stance", ""))),
                str(item.get("agreement_pct", item.get("percentage", ""))),
                str(item.get("notes", item.get("summary", "")))[:100],
            )
        console.print(table)

    if polarized:
        table = Table(title="[red]Polarization Topics[/red]  (sharp divergence)", border_style="red", show_lines=True)
        table.add_column("Topic", style="bold")
        table.add_column("Divide", justify="center")
        table.add_column("Notes", style="dim")
        for item in polarized:
            table.add_row(
                str(item.get("topic", item.get("item", ""))),
                str(item.get("divide", item.get("split", ""))),
                str(item.get("notes", item.get("summary", "")))[:100],
            )
        console.print(table)


def _display_survey_matrix(survey_data):
    """survey_data may be a dict (top-level survey JSON) or a list of response dicts."""
    from rich.table import Table
    if not survey_data:
        console.print("[yellow]No survey data found. Run a survey first (Option 3).[/yellow]")
        return

    # survey_responses.json is a dict with 'responses' list; unwrap if needed
    if isinstance(survey_data, dict):
        responses = survey_data.get("responses", [])
        product = survey_data.get("product_name", "Product")
    else:
        responses = survey_data
        product = "Product"

    if not responses:
        console.print("[yellow]No survey responses found in data. Run a survey first (Option 3).[/yellow]")
        return

    # Build question → persona map
    q_map: dict = {}
    persona_ids: list = []
    for entry in responses:
        pid = entry.get("persona_id", "?")
        if pid not in persona_ids:
            persona_ids.append(pid)
        for ans in entry.get("answers", []):
            q = ans.get("question", "")
            if q not in q_map:
                q_map[q] = {}
            sentiment = ans.get("sentiment", "neutral")
            color = {"positive": "green", "negative": "red"}.get(sentiment, "white")
            q_map[q][pid] = f"[{color}]{ans.get('answer', '')[:80]}[/{color}]"

    table = Table(title=f"Survey Matrix — {product} — Side-by-Side Comparison", border_style="cyan", show_lines=True)
    table.add_column("Question", style="bold", width=30)
    for pid in persona_ids:
        pname = next((r.get("persona_name", pid) for r in responses if r.get("persona_id") == pid), pid)
        table.add_column(f"{pid}\n{pname}", width=25)

    for question, answers in q_map.items():
        row = [question[:80]] + [answers.get(pid, "[dim]—[/dim]") for pid in persona_ids]
        table.add_row(*row)

    console.print(table)


def _display_interview_sessions():
    from rich.table import Table
    logs = load_json("data/interview_logs.json", [])
    if not logs:
        console.print("[yellow]No interview sessions found. Start an interview first (Option 5).[/yellow]")
        return

    table = Table(title="Interview Session Log", border_style="cyan", show_lines=True)
    table.add_column("Session ID", style="cyan")
    table.add_column("Persona ID", style="bold")
    table.add_column("Persona Name")
    table.add_column("Turns", justify="center")
    table.add_column("Started At", style="dim")

    for s in logs:
        # interview_agent saves as 'session_started', not 'started_at'/'created_at'
        started = s.get("session_started", s.get("started_at", s.get("created_at", "?")))
        table.add_row(
            s.get("session_id", s.get("id", "N/A")),
            s.get("persona_id", "?"),
            s.get("persona_name", s.get("name", "?")),
            str(len(s.get("turns", []))),
            started,
        )
    console.print(table)

    # Allow drilling into a session
    session_ids = [s.get("session_id", s.get("id", "")) for s in logs]
    view = Prompt.ask("\nView session turns? Enter Session ID (or press Enter to skip)", default="")
    if view and view in session_ids:
        session = next(s for s in logs if s.get("session_id", s.get("id", "")) == view)
        for i, turn in enumerate(session.get("turns", []), 1):
            console.print(f"\n[bold cyan]Turn {i}[/bold cyan]")
            # interview_agent saves turns as {'turn': N, 'user_message': ..., 'persona_response': ...}
            console.print(f"  [bold]You:[/bold] {turn.get('user_message', turn.get('user', ''))}")
            console.print(f"  [bold yellow]{session.get('persona_name', 'Persona')}:[/bold yellow] {turn.get('persona_response', turn.get('persona', ''))[:300]}")


def _api_info():
    console.print(Panel(
        "[bold cyan]FastAPI Server Endpoints[/bold cyan]\n\n"
        "[bold]Survey[/bold]\n"
        "  POST  /api/run-survey           — Run survey with user-defined questions\n"
        "  GET   /api/survey-matrix        — Side-by-side matrix view of responses\n\n"
        "[bold]Interview[/bold]\n"
        "  POST  /api/interview            — Send message to persona (session-aware)\n"
        "  GET   /api/interviews           — List all interview sessions\n"
        "  GET   /api/interview/{id}       — Get session history for a session ID\n"
        "  POST  /api/interview/reset      — Reset / clear interview session\n\n"
        "[bold]Insights & Scoring[/bold]\n"
        "  POST  /api/generate-report      — Generate full insight report\n"
        "  GET   /api/adoption-score       — 'Would use this product?' scorecard\n"
        "  GET   /api/agreement-patterns   — Consensus vs polarization analysis\n\n"
        "[dim]Start server with: uvicorn api:app --reload[/dim]",
        border_style="blue"
    ))




def _get_latest_report() -> dict:
    """Load the most recent report JSON from the reports/ directory."""
    import json as _json
    reports_dir = Path(__file__).resolve().parent / "reports"
    report_files = sorted(reports_dir.glob("report_*.json"), reverse=True)
    if not report_files:
        return {}
    try:
        with open(report_files[0], "r", encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return {}


def main():

    persona_agent = PersonaGenerationAgent()
    survey_agent = SurveyAgent()
    interview_agent = InterviewAgent()
    insight_agent = InsightExtractionAgent()

    while True:
        exp = load_json("data/experiment.json", None)
        display_banner(exp)
        _print_menu()

        choice = Prompt.ask("Select an action", choices=MENU_CHOICES, default="1")

        # ── 1. Setup ──────────────────────────────────────────────────────────
        if choice == "1":
            setup_experiment_cli()

        # ── 2. Generate Personas ──────────────────────────────────────────────
        elif choice == "2":
            exp = load_json("data/experiment.json", None)
            if not exp:
                console.print("[yellow]No active experiment detected. Setting up first...[/yellow]")
                exp = setup_experiment_cli()

            count_str = Prompt.ask("Number of personas to generate", default="5")
            try:
                count = int(count_str)
            except ValueError:
                count = 5

            console.print(f"\n[bold cyan]Generating {count} synthetic user personas tailored for '{exp.get('product_name')}'...[/bold cyan]")
            personas = persona_agent.generate_personas(exp, count=count)
            console.print(f"[bold green]Generated {len(personas)} personas successfully![/bold green]\n")
            persona_agent.print_persona_cards(personas)

        # ── 3. Run Survey ────────────────────────────────────────────────────
        elif choice == "3":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            exp = load_json("data/experiment.json", {})
            suggested_q = survey_agent.suggest_questions(exp, count=3)

            console.print("\n[bold cyan]Targeted Survey Questions for Active Product:[/bold cyan]")
            for i, q in enumerate(suggested_q, 1):
                console.print(f"  {i}. {q}")

            use_suggested = Prompt.ask("\nUse these questions?", choices=["y", "n"], default="y")
            if use_suggested == "y":
                questions = suggested_q
            else:
                questions = []
                while True:
                    q = Prompt.ask(f"Enter Question {len(questions)+1} (or press Enter to finish)").strip()
                    if not q:
                        break
                    questions.append(q)

            if questions:
                console.print("[yellow]Simulating survey responses simultaneously across all synthetic personas...[/yellow]\n")
                results = survey_agent.run_survey(questions, experiment=exp, simultaneous=True)
                survey_agent.print_survey_table(results)
                console.print("\n[dim]Tip: Use Option 4 to view the full side-by-side Survey Matrix.[/dim]")

        # ── 4. View Survey Matrix ────────────────────────────────────────────
        elif choice == "4":
            survey_data = load_json("data/survey_responses.json", [])
            _display_survey_matrix(survey_data)

        # ── 5. Interview / Resume Session ────────────────────────────────────
        elif choice == "5":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[bold]Select a Persona to Interview:[/bold]")
            for p in personas:
                arch = p.get("archetype", "User")
                occ = p.get("occupation", "Professional")
                console.print(f"  [cyan]{p['id']}[/cyan] - {p['name']} ([yellow]{arch}[/yellow]) - {occ}")

            p_id = Prompt.ask("\nEnter Persona ID", default=personas[0]["id"])

            # Check for existing sessions to allow resumption
            logs = load_json("data/interview_logs.json", [])
            existing = [s for s in logs if s.get("persona_id") == p_id]
            if existing:
                console.print(f"[dim]Found {len(existing)} existing session(s) for this persona.[/dim]")
                resume = Prompt.ask("Resume latest session or start fresh?", choices=["resume", "fresh"], default="resume")
                if resume == "fresh":
                    # InterviewAgent always starts a new timestamped session; inform user
                    console.print("[dim]Starting a fresh session (previous sessions are preserved in the log).[/dim]")
                interview_agent.start_interview_session(p_id)
            else:
                interview_agent.start_interview_session(p_id)

        # ── 6. View Interview Sessions ───────────────────────────────────────
        elif choice == "6":
            _display_interview_sessions()

        # ── 7. Generate Report ───────────────────────────────────────────────
        elif choice == "7":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[yellow]Synthesizing empirical responses, behavioral profiles, and sentiment metrics...[/yellow]")
            report = insight_agent.generate_report()
            insight_agent.print_report_summary(report)

            # Key Highlights
            console.print("\n[bold magenta]── Key Highlights ──[/bold magenta]")
            _display_adoption_scorecard(report)
            _display_agreement_patterns(report)

            console.print(f"\n[bold green]Report exported as JSON and PDF in reports/ directory![/bold green]\n")

        # ── 8. Adoption Scorecard ────────────────────────────────────────────
        elif choice == "8":
            latest = _get_latest_report()
            if latest:
                _display_adoption_scorecard(latest)
            else:
                console.print("[yellow]No report found. Generate a report first (Option 7).[/yellow]")

        # ── 9. Agreement & Polarization Patterns ─────────────────────────────
        elif choice == "9":
            latest = _get_latest_report()
            if latest:
                _display_agreement_patterns(latest)
            else:
                console.print("[yellow]No report found. Generate a report first (Option 7).[/yellow]")

        # ── 10. Run Validation Suite ─────────────────────────────────────────
        elif choice == "10":
            console.print(Panel(
                "[bold cyan]Multi-Domain Validation Suite[/bold cyan]\n"
                "[dim]Validates persona consistency, theme relevance, and adoption score discrimination\n"
                "across 5 product categories (B2B SaaS, Health/IoT, FinTech, EdTech, E-Commerce)[/dim]",
                border_style="cyan"
            ))
            import subprocess
            confirm = Prompt.ask("Run validation suite now? (may take several minutes)", choices=["y", "n"], default="y")
            if confirm == "y":
                console.print("[yellow]Running test_milestone3_validation.py...[/yellow]\n")
                result = subprocess.run(
                    [sys.executable, "test_milestone3_validation.py"],
                    capture_output=False,
                    text=True
                )
                if result.returncode == 0:
                    console.print("[bold green]✔ Validation suite completed successfully![/bold green]")
                else:
                    console.print(f"[bold red]✘ Validation suite finished with errors (exit code {result.returncode}).[/bold red]")

        # ── 11. API Server Info ───────────────────────────────────────────────
        elif choice == "11":
            _api_info()

        # ── 12. Exit ──────────────────────────────────────────────────────────
        elif choice == "12":
            console.print("[dim]Goodbye![/dim]")
            sys.exit(0)

if __name__ == "__main__":
    main()
