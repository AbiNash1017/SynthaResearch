import re
from datetime import datetime
from typing import Dict, Any, Optional
from config.settings import is_openrouter_configured
from config.topic_map import detect_topic
from utils.llm_client import llm_client
from utils.storage import load_json, save_json

class PersonaMemoryModule:
    @staticmethod
    def generate_response(
        persona: Dict[str, Any],
        question: str,
        experiment: Optional[Dict[str, Any]] = None,
        mode: str = "interview"
    ) -> str:
        """
        Generates an authentic in-character response from the persona using OpenRouter LLM.
        Maintains memory, conversation history, and stance consistency across turns.
        """
        if experiment is None:
            experiment = load_json("data/experiment.json", {})

        topic = detect_topic(question)
        memory = persona.setdefault("memory", {
            "conversation_history": [],
            "established_opinions": {},
            "last_updated": datetime.now().isoformat()
        })
        opinions = memory.setdefault("established_opinions", {})
        history = memory.setdefault("conversation_history", [])

        response = None
        if is_openrouter_configured():
            try:
                response = PersonaMemoryModule._generate_with_llm(
                    persona=persona,
                    question=question,
                    experiment=experiment,
                    mode=mode,
                    topic=topic
                )
                # Check for garbage/safety outputs
                if not response or response.strip().startswith("User Safety:") or "Response Safety:" in response or len(response.strip()) < 10:
                    response = None
            except Exception:
                response = None

        if not response:
            response = PersonaMemoryModule._generate_fallback(persona, question, experiment, topic)

        # Detect sentiment/stance from the generated response
        stance = PersonaMemoryModule.extract_stance(response)
        if topic != "general" and topic not in ["greeting", "acknowledgement"]:
            opinions[topic] = {
                "stance": stance,
                "last_question": question,
                "recorded_at": datetime.now().isoformat()
            }

        # Record conversation turns in persona memory
        history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        history.append({
            "role": "persona",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # Keep last 12 turns (6 full exchanges)
        if len(history) > 12:
            memory["conversation_history"] = history[-12:]

        memory["last_updated"] = datetime.now().isoformat()
        return response

    @staticmethod
    def _generate_with_llm(
        persona: Dict[str, Any],
        question: str,
        experiment: Dict[str, Any],
        mode: str,
        topic: str
    ) -> str:
        """Roleplays as the persona using OpenRouter LLM with established memory."""
        name = persona.get("name", "User")
        archetype = persona.get("archetype", "General Consumer")
        traits = ", ".join(persona.get("personality_traits", []))
        bg = persona.get("background_story", "")
        bp = persona.get("behavioral_patterns", {})
        psych = persona.get("psychological_profile", {})
        established = persona.get("memory", {}).get("established_opinions", {})

        p_name = experiment.get("product_name", "the product")
        p_desc = experiment.get("product_description", "")
        p_audience = experiment.get("target_audience", "")

        system_prompt = f"""You are roleplaying in a live product research interview as:
- Name: {name}
- Age: {persona.get('age', 28)}, Gender: {persona.get('gender', 'unspecified')}
- Occupation: {persona.get('occupation', 'Professional')} in {persona.get('location', 'Global')}
- Archetype: {archetype}
- Personality Traits: {traits}
- Personal Background: {bg}
- Your Daily Habits & Current Tools: {bp.get('current_tools', 'Standard everyday solutions')}
- Your Biggest Pain Points: {bp.get('primary_pain_points', 'Wasted time and friction')}
- Your Spending & Budget Attitude: {bp.get('willingness_to_pay', 'Carefully evaluate before paying')}
- What Makes You Quit an App / Dealbreakers: {bp.get('churn_triggers', 'Annoyance, bugs, or high prices')}

Product Under Research:
- Name: {p_name}
- Description: {p_desc}
- Target Audience: {p_audience}

Prior Opinions You Expressed In This Chat:
{established if established else "This is the start of the interview."}

CONVERSATIONAL RULES:
1. Speak completely in character as {name} in the first person ("I", "my", "me").
2. DO NOT sound like an AI assistant or a robot. NEVER say "As a synthetic user", "As an AI", or "Glad to share my feedback on this product."
3. Be natural, spoken, and candid. Share your real thoughts, gut reactions, doubts, or excitement.
4. Reference your real life, your job as a {persona.get('occupation')}, your age ({persona.get('age')}), and where you live ({persona.get('location')}).
5. Directly address what the researcher just asked. If they ask for your thoughts, insights, or remarks on {p_name} and its target demographic, give a thoughtful, realistic opinion based on who you are.
6. {'Provide a conversational spoken reply (2 to 4 natural sentences).' if mode == 'interview' else 'Provide a clear, succinct survey answer (1 to 2 sentences).'}
7. Your response MUST be distinctly shaped by your specific archetype ({archetype}), your occupation, your location, and your age. Do NOT give a generic answer that any user could give.
"""


        messages = [{"role": "system", "content": system_prompt}]

        for turn in persona.get("memory", {}).get("conversation_history", [])[-6:]:
            role = "assistant" if turn.get("role") == "persona" else "user"
            messages.append({"role": role, "content": turn.get("content", "")})

        messages.append({"role": "user", "content": question})

        return llm_client.chat_completion(messages, temperature=0.75, max_tokens=400)

    @staticmethod
    def _generate_fallback(persona: Dict[str, Any], question: str, experiment: Dict[str, Any], topic: str) -> str:
        """Dynamic conversational fallback that responds authentically to the question context."""
        name = persona.get("name", "Alex")
        age = persona.get("age", 27)
        occ = persona.get("occupation", "Specialist")
        loc = persona.get("location", "the city")
        arch = persona.get("archetype", "Consumer")
        traits = persona.get("personality_traits", ["practical", "observant"])
        bp = persona.get("behavioral_patterns", {})
        pain = bp.get("primary_pain_points", "friction in day-to-day use")
        current_tools = bp.get("current_tools", "traditional apps")
        wtp = bp.get("willingness_to_pay", "strict value-for-money")
        churn = bp.get("churn_triggers", "unreliable performance")

        p_name = experiment.get("product_name", "this product")
        p_desc = experiment.get("product_description", "the app")
        p_audience = experiment.get("target_audience", "users")

        q_lower = question.lower()

        # 1. Questions asking for insights, thoughts, remarks, demographic feedback
        if any(k in q_lower for k in ["insight", "remark", "demographic", "thought", "opinion", "feedback", "what do you think", "how do you feel", "perspective"]):
            return (
                f"Honestly, speaking as a {age}-year-old {occ} living in {loc}, looking at {p_name} gives me mixed feelings. "
                f"On paper, targeting {p_audience} makes sense, but in reality, different age brackets use apps for totally different reasons. "
                f"My main concern as a {arch} is whether it actually solves my daily headache with {pain}. "
                f"If the app ends up feeling chaotic or triggers {churn}, people in my social circle will abandon it within a week, "
                f"so it really needs to prove it's safer and more reliable than sticking with {current_tools}."
            )

        # 2. Questions about pricing, cost, subscription
        elif any(k in q_lower for k in ["price", "cost", "pay", "subscription", "pricing", "dollar", "rupee", "money", "afford", "expensive", "fee"]):
            return (
                f"When it comes to my wallet, I'm pretty straightforward: {wtp}. "
                f"I'm already paying for several essentials, so unless {p_name} provides undeniable daily utility that saves me time, "
                f"I wouldn't be comfortable with a recurring fee. A fair free tier or a very low, transparent cost is the only way I'd consider it."
            )

        # 3. Questions about privacy, safety, anonymity, moderation
        elif any(k in q_lower for k in ["privacy", "safe", "safety", "anonym", "secure", "security", "data", "trust", "moderation", "harass"]):
            return (
                f"Safety and data privacy are non-negotiable for me. If {p_name} is dealing with {p_desc[:50]}, "
                f"there has to be ironclad moderation and zero sketchy tracking. "
                f"The moment an app feels compromised or allows toxic behavior, that's an instant dealbreaker ({churn}) for me."
            )

        # 4. Questions about switching, alternatives, current habits
        elif any(k in q_lower for k in ["switch", "competitor", "alternative", "replace", "current", "habit", "migrate"]):
            return (
                f"Right now, my default routine revolves around {current_tools}. "
                f"Switching to {p_name} would require a noticeable improvement in convenience, because changing habits is friction-heavy. "
                f"It would have to make communicating with {p_audience} radically smoother before I'd make the jump."
            )

        # 5. Greetings
        elif any(k in q_lower for k in ["hello", "hi", "hey", "good morning", "good evening", "how are you", "who are you"]):
            return (
                f"Hey! Great to connect. I'm {name}, a {age}-year-old {occ} here in {loc}. "
                f"Glad to share my honest take on {p_name}."
            )

        # 6. Acknowledgement
        elif any(k in q_lower for k in ["ok", "okay", "cool", "understood", "got it", "makes sense", "sure"]):
            return f"Exactly. That's why from my viewpoint as a {arch}, execution is going to be everything for {p_name}."

        # 7. General fallback
        else:
            return (
                f"From my point of view as someone who's generally {traits[0]} and {traits[1] if len(traits)>1 else 'practical'}, "
                f"my reaction to {p_name} comes down to daily friction. "
                f"I deal with {pain} regularly, and if this app can genuinely make that easier without {churn}, "
                f"I'd be interested—otherwise, I'll probably just stick to {current_tools}."
            )

    @staticmethod
    def extract_stance(text: str) -> str:
        """Classifies text into positive, negative, or neutral stance."""
        lower = text.lower()
        pos_words = ["love", "great", "excellent", "excited", "happy", "yes", "definitely", "willing", "useful", "valuable", "seamless", "fantastic", "effective", "worth it", "appreciate"]
        neg_words = ["hate", "dislike", "terrible", "frustrat", "annoy", "no", "never", "unwilling", "expensive", "waste", "complicat", "skeptical", "refuse", "hesitate", "overpriced", "clunky", "dealbreaker"]

        pos_count = sum(1 for w in pos_words if w in lower)
        neg_count = sum(1 for w in neg_words if w in lower)

        if pos_count > neg_count and pos_count >= 1:
            return "positive"
        elif neg_count > pos_count and neg_count >= 1:
            return "negative"
        return "neutral"

    @staticmethod
    def update_persona_pool(persona: Dict[str, Any], pool_path: str = "data/persona_pool.json"):
        pool = load_json(pool_path, [])
        for i, p in enumerate(pool):
            if p.get("id") == persona.get("id"):
                pool[i] = persona
                break
        save_json(pool_path, pool)
