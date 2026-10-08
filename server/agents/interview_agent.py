import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Ensure venv site-packages is discoverable if present
_venv_site = Path(__file__).resolve().parent.parent / "venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

from agents.persona_memory import PersonaMemoryModule
from utils.storage import load_json, save_json

def _print_msg(msg: str):
    if HAS_RICH and console:
        console.print(msg)
    else:
        import re
        clean_msg = re.sub(r"\[/?(?:bold|dim|italic|yellow|cyan|green|red|blue|magenta)[^\]]*\]", "", msg)
        print(clean_msg)

class InterviewAgent:
    def __init__(
        self,
        persona_path: str = "data/persona_pool.json",
        logs_path: str = "data/interview_logs.json",
        experiment_path: str = "data/experiment.json"
    ):
        self.persona_path = persona_path
        self.logs_path = logs_path
        self.experiment_path = experiment_path

    def start_interview_session(self, persona_id: str):
        personas = load_json(self.persona_path, [])
        persona = next((p for p in personas if p["id"] == persona_id), None)
        if not persona:
            _print_msg(f"[bold red]Persona {persona_id} not found![/bold red]")
            return

        experiment = load_json(self.experiment_path, {})
        p_name = experiment.get("product_name", "Product Under Research")

        traits_str = ", ".join(persona.get("personality_traits", []))

        if HAS_RICH and console:
            header = (
                f"[bold cyan]{persona['name']}[/bold cyan] | [yellow]{persona.get('archetype', 'User')}[/yellow] | {persona.get('occupation', '')}\n"
                f"[dim]Traits: {traits_str} | Location: {persona.get('location', '')}[/dim]\n"
                f"[dim]Product: [bold]{p_name}[/bold][/dim]\n"
                f"[italic]{persona.get('background_story', '')}[/italic]"
            )
            console.print(Panel(header, title="Live Persona Interview", border_style="green"))
            console.print("[dim]Type your message to the persona. Enter 'exit', 'quit', or 'end' to complete session.[/dim]\n")
        else:
            print(f"\n=== Live Persona Interview: {persona['name']} ({persona.get('archetype', 'User')}) ===")
            print(f"Role: {persona.get('occupation', '')} in {persona.get('location', '')}")
            print(f"Traits: {traits_str} | Product: {p_name}")
            print(f"Background: {persona.get('background_story', '')}")
            print("Type your message to the persona. Enter 'exit', 'quit', or 'end' to complete session.\n")

        session_id = f"session_{int(datetime.now().timestamp())}"
        session_turns = []
        turn_num = 1

        try:
            while True:
                try:
                    if HAS_RICH and console:
                        user_msg = console.input("[bold green]You:[/bold green] ").strip()
                    else:
                        user_msg = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not user_msg:
                    continue

                if user_msg.lower() in ["exit", "quit", "end"]:
                    _print_msg("[dim]Interview session ended.[/dim]")
                    break

                response = PersonaMemoryModule.generate_response(
                    persona=persona,
                    question=user_msg,
                    experiment=experiment,
                    mode="interview"
                )

                if HAS_RICH and console:
                    console.print(f"[bold cyan]{persona['name']}:[/bold cyan] {response}\n")
                else:
                    print(f"{persona['name']}: {response}\n")

                session_turns.append({
                    "turn": turn_num,
                    "user_message": user_msg,
                    "persona_response": response,
                    "timestamp": datetime.now().isoformat()
                })
                turn_num += 1

                PersonaMemoryModule.update_persona_pool(persona, self.persona_path)

        finally:
            if session_turns:
                all_logs = load_json(self.logs_path, [])
                all_logs.append({
                    "session_id": session_id,
                    "product_name": p_name,
                    "persona_id": persona["id"],
                    "persona_name": persona["name"],
                    "archetype": persona.get("archetype", "User"),
                    "turns": session_turns,
                    "session_started": session_turns[0]["timestamp"]
                })
                save_json(self.logs_path, all_logs)
                _print_msg(f"[bold green]Saved {len(session_turns)} interview turns to {self.logs_path}[/bold green]")
        return session_id
