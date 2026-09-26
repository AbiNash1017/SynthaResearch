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

    experiment = {
        "product_name": name,
        "industry_domain": industry,
        "product_description": desc,
        "target_audience": audience,
        "research_objectives": objectives,
        "created_at": datetime.now().isoformat()
    }
    save_json("data/experiment.json", experiment)
    console.print(f"\n[bold green]✔ Experiment configured and saved to data/experiment.json![/bold green]\n")
    return experiment

def display_banner(exp):
    p_name = exp.get("product_name", "None (Setup Required)") if exp else "None (Setup Required)"
    domain = exp.get("industry_domain", "N/A") if exp else "N/A"

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

def main():
    persona_agent = PersonaGenerationAgent()
    survey_agent = SurveyAgent()
    interview_agent = InterviewAgent()
    insight_agent = InsightExtractionAgent()

    while True:
        exp = load_json("data/experiment.json", None)
        display_banner(exp)

        console.print("[bold]1.[/bold] Setup / Edit Experiment Workspace")
        console.print("[bold]2.[/bold] Generate Synthetic Personas")
        console.print("[bold]3.[/bold] Run Multi-Persona Survey")
        console.print("[bold]4.[/bold] Start Interactive Interview with a Persona")
        console.print("[bold]5.[/bold] Generate Research & Insight Report (JSON + PDF)")
        console.print("[bold]6.[/bold] Exit")

        choice = Prompt.ask("\nSelect an action", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            setup_experiment_cli()

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
                console.print("[yellow]Simulating survey responses across all synthetic personas...[/yellow]\n")
                results = survey_agent.run_survey(questions, experiment=exp)
                survey_agent.print_survey_table(results)

        elif choice == "4":
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
            interview_agent.start_interview_session(p_id)

        elif choice == "5":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[yellow]Synthesizing empirical responses, behavioral profiles, and sentiment metrics...[/yellow]")
            report = insight_agent.generate_report()
            insight_agent.print_report_summary(report)
            console.print(f"\n[bold green]Report exported as JSON and PDF in reports/ directory![/bold green]\n")

        elif choice == "6":
            console.print("[dim]Goodbye![/dim]")
            sys.exit(0)

if __name__ == "__main__":
    main()
