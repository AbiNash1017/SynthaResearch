from datetime import datetime
from typing import Dict, Any, List
from config.topic_map import detect_topic
from templates.response_templates import (
    detect_question_type,
    get_varied_response,
    apply_tone,
    extract_stance
)
from utils.storage import load_json, save_json

class PersonaMemoryModule:
    @staticmethod
    def generate_response(persona: Dict[str, Any], question: str, mode: str = "interview") -> str:
        arch = persona.get("archetype", "Impulse Buyer")
        traits = persona.get("personality_traits", [])
        q_type = detect_question_type(question)
        topic = detect_topic(question)

        # Fallback question type matching
        if q_type == "open" and topic != "general":
            q_type = topic

        memory = persona.setdefault("memory", {
            "conversation_history": [],
            "established_opinions": {},
            "used_template_indices": {},
            "last_updated": datetime.now().isoformat()
        })
        opinions = memory.setdefault("established_opinions", {})
        history = memory.setdefault("conversation_history", [])
        used_indices = memory.setdefault("used_template_indices", {}).setdefault(q_type, [])

        # Check if an opinion is already established on this topic
        # Only repeat/reiterate if the question is directly re-asking the exact same question or topic
        # and not a conversational acknowledgement
        if topic in opinions and q_type not in ["acknowledgement", "greeting"] and len(history) >= 4:
            # Subtle variation rather than blunt robotic repetition
            base_template = get_varied_response(arch, q_type, used_indices)
            response = f"Building on what I said earlier, {base_template[0].lower() + base_template[1:]}"
        else:
            base_template = get_varied_response(arch, q_type, used_indices)
            response = base_template
            stance = extract_stance(response)
            if topic != "general":
                opinions[topic] = stance

        # Apply tone based on traits
        final_response = apply_tone(response, traits)

        # Append turn to persona memory
        history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        history.append({
            "role": "persona",
            "content": final_response,
            "timestamp": datetime.now().isoformat()
        })

        # Keep last 12 turns (6 complete exchanges)
        if len(history) > 12:
            memory["conversation_history"] = history[-12:]

        memory["last_updated"] = datetime.now().isoformat()
        return final_response

    @staticmethod
    def update_persona_pool(persona: Dict[str, Any], pool_path: str = "data/persona_pool.json"):
        pool = load_json(pool_path, [])
        for i, p in enumerate(pool):
            if p["id"] == persona["id"]:
                pool[i] = persona
                break
        save_json(pool_path, pool)
