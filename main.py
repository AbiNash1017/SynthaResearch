import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from agents.persona_generator import PersonaGenerationAgent
from agents.survey_agent import SurveyAgent
from agents.interview_agent import InterviewAgent
from agents.insight_agent import InsightExtractionAgent
from utils.storage import load_json, save_json

console = Console()

def setup_experiment_cli():
    console.print(Panel("[bold cyan]Step 1: Setup Product Experiment Workspace[/bold cyan]", border_style="cyan"))
    name = Prompt.ask("Product Name", default="LearnFlow")
    desc = Prompt.ask("Product Description", default="A hybrid online learning app combining Udemy-style structured courses with Duolingo-style daily streak gamification to conquer student course dropouts.")
    audience = Prompt.ask("Target Audience", default="College students and working professionals aged 20-35 who enroll in online courses but fail to finish them.")
    console.print("\nEnter Research Objectives (leave empty to finish):")
    objectives = []
    default_objs = [
        "Discover why learners drop out of courses after the first week",
        "Test reaction to bite-sized 5-minute daily lessons vs 45-minute lectures",
        "Evaluate willingness to pay for subscriptions vs one-time course fees",
        "Identify if streaks and XP leaderboards create genuine motivation"
    ]
    for i, dobj in enumerate(default_objs, 1):
        obj = Prompt.ask(f"Objective {i}", default=dobj)
        if obj.strip():
            objectives.append(obj.strip())

    experiment = {
        "product_name": name,
        "product_description": desc,
        "target_audience": audience,
        "research_objectives": objectives,
        "created_at": datetime.now().isoformat()
    }
    save_json("data/experiment.json", experiment)
    console.print(f"\n[bold green]✔ Experiment configured and saved to data/experiment.json![/bold green]\n")
    return experiment

def main():
    persona_agent = PersonaGenerationAgent()
    survey_agent = SurveyAgent()
    interview_agent = InterviewAgent()
    insight_agent = InsightExtractionAgent()

    while True:
        exp = load_json("data/experiment.json", None)
        p_name = exp.get("product_name", "None (Setup Required)") if exp else "None (Setup Required)"

        console.print(Panel(
            f"[bold green]SYNTHETIC USER GENERATION PLATFORM[/bold green]\n"
            f"[dim]Study App & EdTech User Research Simulator (Udemy / Duolingo Behavior Model)[/dim]\n"
            f"[bold]Active Experiment:[/bold] [yellow]{p_name}[/yellow]",
            border_style="green"
        ))

        console.print("[bold]1.[/bold] Setup Experiment Workspace")
        console.print("[bold]2.[/bold] Generate Diverse Synthetic Personas")
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
            console.print("\n[bold cyan]Generating synthetic user personas with diverse behavioral patterns...[/bold cyan]")
            personas = persona_agent.generate_personas(exp, count=5)
            console.print(f"[bold green]Generated {len(personas)} personas successfully![/bold green]\n")
            persona_agent.print_persona_cards(personas)

        elif choice == "3":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[bold cyan]Default Survey Questions:[/bold cyan]")
            default_q = [
                "Why did you abandon or stop using your previous online course or study app?",
                "Would a 5-minute daily micro-lesson format keep you consistent compared to long video lectures?",
                "How much would you be willing to pay monthly for this learning platform?"
            ]
            for i, q in enumerate(default_q, 1):
                console.print(f"  {i}. {q}")

            use_default = Prompt.ask("\nUse these questions?", choices=["y", "n"], default="y")
            if use_default == "y":
                questions = default_q
            else:
                questions = []
                while True:
                    q = Prompt.ask(f"Enter Question {len(questions)+1} (or empty to finish)")
                    if not q.strip():
                        break
                    questions.append(q.strip())

            if questions:
                console.print("[yellow]Simulating survey responses across all synthetic personas...[/yellow]\n")
                results = survey_agent.run_survey(questions)
                survey_agent.print_survey_table(results)

        elif choice == "4":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[bold]Select a Persona to Interview:[/bold]")
            for p in personas:
                console.print(f"  [cyan]{p['id']}[/cyan] - {p['name']} ([yellow]{p['archetype']}[/yellow]) - {p['occupation']}")

            p_id = Prompt.ask("\nEnter Persona ID", default=personas[0]["id"])
            interview_agent.start_interview_session(p_id)

        elif choice == "5":
            personas = load_json("data/persona_pool.json", [])
            if not personas:
                console.print("[red]No personas found. Please generate personas (Option 2) first![/red]")
                continue

            console.print("\n[yellow]Aggregating response themes, behavioral profiles, and sentiment metrics...[/yellow]")
            report = insight_agent.generate_report()
            insight_agent.print_report_summary(report)
            console.print(f"\n[bold green]Report exported as JSON and PDF in reports/ folder![/bold green]\n")

        elif choice == "6":
            console.print("[dim]Goodbye![/dim]")
            sys.exit(0)

if __name__ == "__main__":
    main()
