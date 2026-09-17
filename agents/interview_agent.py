from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel

from agents.persona_memory import PersonaMemoryModule
from utils.storage import load_json, save_json

console = Console()

class InterviewAgent:
    def __init__(self, persona_path: str = "data/persona_pool.json", logs_path: str = "data/interview_logs.json"):
        self.persona_path = persona_path
        self.logs_path = logs_path

    def start_interview_session(self, persona_id: str):
        personas = load_json(self.persona_path, [])
        persona = next((p for p in personas if p["id"] == persona_id), None)
        if not persona:
            console.print(f"[bold red]Persona {persona_id} not found![/bold red]")
            return

        header = (
            f"[bold cyan]{persona['name']}[/bold cyan] | [yellow]{persona['archetype']}[/yellow] | {persona['occupation']}\n"
            f"[dim]Traits: {', '.join(persona['personality_traits'])} | Location: {persona['location']}[/dim]\n"
            f"[italic]{persona['background_story']}[/italic]"
        )
        console.print(Panel(header, title="Live Persona Interview", border_style="green"))
        console.print("[dim]Type your message to the persona. Enter 'exit', 'quit', or 'end' to complete session.[/dim]\n")

        session_id = f"session_{int(datetime.now().timestamp())}"
        session_turns = []
        turn_num = 1

        while True:
            try:
                user_msg = console.input("[bold green]You:[/bold green] ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_msg:
                continue

            if user_msg.lower() in ["exit", "quit", "end"]:
                console.print("[dim]Interview session ended.[/dim]")
                break

            response = PersonaMemoryModule.generate_response(persona, user_msg, mode="interview")
            console.print(f"[bold cyan]{persona['name']}:[/bold cyan] {response}\n")

            session_turns.append({
                "turn": turn_num,
                "user_message": user_msg,
                "persona_response": response,
                "timestamp": datetime.now().isoformat()
            })
            turn_num += 1

            PersonaMemoryModule.update_persona_pool(persona, self.persona_path)

        if session_turns:
            all_logs = load_json(self.logs_path, [])
            all_logs.append({
                "session_id": session_id,
                "persona_id": persona["id"],
                "persona_name": persona["name"],
                "archetype": persona["archetype"],
                "turns": session_turns,
                "session_started": session_turns[0]["timestamp"]
            })
            save_json(self.logs_path, all_logs)
            console.print(f"[bold green]Saved {len(session_turns)} interview turns to {self.logs_path}[/bold green]")
