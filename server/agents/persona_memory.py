import re
from datetime import datetime
from typing import Dict, Any, Optional, List
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
        from utils.normalizer import normalize_experiment
        experiment = normalize_experiment(experiment)

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
                raw_response = PersonaMemoryModule._generate_with_llm(
                    persona=persona,
                    question=question,
                    experiment=experiment,
                    mode=mode,
                    topic=topic
                )
                response = PersonaMemoryModule._clean_response(raw_response)
            except Exception as e:
                print(f"[PersonaMemoryModule] LLM Generation warning: {e}. Falling back to rule engine.")
                response = None

        if not response:
            response = PersonaMemoryModule._generate_fallback(persona, question, experiment, topic)

        # Detect sentiment/stance from the generated response
        stance = PersonaMemoryModule.extract_stance(response)
        summary = PersonaMemoryModule._summarize_opinion(response)
        if topic != "general" and topic not in ["greeting", "acknowledgement"]:
            opinions[topic] = {
                "stance": stance,
                "summary": summary,
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
    def _clean_response(text: Optional[str]) -> Optional[str]:
        """
        Cleans LLM responses by stripping out internal thinking processes, chain-of-thought blocks,
        and meta-commentary, ensuring only natural, in-character persona speech is returned.
        """
        if not text or not isinstance(text, str):
            return None
        cleaned = text.strip()

        # Remove XML thinking blocks like <think>...</think> or <reasoning>...</reasoning>
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"<reasoning>[\s\S]*?</reasoning>", "", cleaned, flags=re.IGNORECASE).strip()

        # Check for "Here's a thinking process:" or similar chain-of-thought preambles
        if re.search(r"(?:Here(?:'s| is) a thinking process|Thinking Process|Chain of thought|Internal Analysis):", cleaned, flags=re.IGNORECASE):
            # Try to extract the final spoken dialogue after known markers
            split_markers = [
                r"\n\s*(?:Response|Final Response|In Character|Direct Reply|Spoken Response|Actual Reply):\s*",
                r"\n\s*\*\*(?:Response|Final Response|Reply|Spoken Response)\*\*:?\s*",
                r"\n\s*---\s*\n",
                r"\n\s*(?:Draft(?:\s*-\s*Spoken Response)?):\s*"
            ]
            found = None
            for marker in split_markers:
                parts = re.split(marker, cleaned, flags=re.IGNORECASE)
                if len(parts) > 1 and len(parts[-1].strip()) > 10:
                    found = parts[-1].strip()
                    break

            if found:
                cleaned = found
            else:
                # Look for quoted dialogue inside the thinking block
                quotes = re.findall(r'"([^"\n]{20,})"', cleaned)
                if quotes:
                    cleaned = quotes[-1].strip()
                else:
                    return None

        # Reject if the remaining text is purely analysis notes / bullet points
        if re.match(r"^\s*(?:\d+\.\s*\*\*|[-*]\s*(?:Analyze|User asks|User says|Constraints|Rules|Note:|Identify|Deconstruct))", cleaned, flags=re.IGNORECASE):
            return None

        # Strip surrounding quotes if present
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1].strip()

        # Reject if still too short or looks like an error/safety string
        if len(cleaned) < 10 or cleaned.lower().startswith("user safety:") or "response safety:" in cleaned.lower():
            return None

        # Remove markdown headers and list formatting so speech never sounds like an essay or outline
        if "\n" in cleaned:
            lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
            spoken = []
            for l in lines:
                # Drop headers like "**What's working well:**" or "### Summary"
                if re.match(r"^(?:#{1,6}\s+|\*\*[^*]+\*\*:?|\* [^*]+:\s*$)", l):
                    continue
                # If bullet line like "- The reminders are great", strip the bullet
                if re.match(r"^[-*•\d.]+\s+", l):
                    sub = re.sub(r"^[-*•\d.]+\s*", "", l)
                    sub = re.sub(r"^\*\*[^*]+\*\*:?\s*", "", sub).strip()
                    if sub and len(sub) > 5:
                        spoken.append(sub)
                else:
                    spoken.append(l)
            if spoken:
                cleaned = " ".join(spoken)

        # Strictly replace all em-dashes (—), en-dashes (–), and double dashes (--) with natural commas/periods
        cleaned = re.sub(r"\s*[—–]\s*", ", ", cleaned)
        cleaned = re.sub(r"\s*--\s*", ", ", cleaned)
        cleaned = re.sub(r",\s*,+", ", ", cleaned)
        cleaned = re.sub(r",\s*\.", ".", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        # Enforce human conversational brevity: strictly limit to 2 natural sentences if it rambled
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        if len(sentences) > 3:
            cleaned = " ".join(sentences[:2])

        return cleaned

    @staticmethod
    def _summarize_opinion(text: str) -> str:
        """Extracts a succinct 1-sentence summary of the expressed stance."""
        sentences = re.split(r"[.!?]", text)
        valid = [s.strip() for s in sentences if len(s.strip()) > 10]
        if valid:
            words = valid[0].split()
            return " ".join(words[:16])
        return text[:80]

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
        age  = persona.get("age", 28)
        occ  = persona.get("occupation", "Professional")
        loc  = persona.get("location", "Global")
        archetype = persona.get("archetype", "General Consumer")
        traits = ", ".join(persona.get("personality_traits", []))
        bg = persona.get("background_story", "")
        bp = persona.get("behavioral_patterns", {})
        established = persona.get("memory", {}).get("established_opinions", {})
        history_turns = persona.get("memory", {}).get("conversation_history", [])

        p_name = experiment.get("product_name", "the product")
        p_desc = experiment.get("product_description", "")
        p_audience = experiment.get("target_audience", "")

        # Compact background brief – model reads this as private context, NOT as lines to quote
        pain   = bp.get("primary_pain_points", "friction in day-to-day use")
        tools  = bp.get("current_tools", "standard apps")
        wtp    = bp.get("willingness_to_pay", "careful about spending")
        churn  = bp.get("churn_triggers", "annoyance or hidden costs")

        background_brief = (
            f"Private context (never quote directly, just let it shape how you think and speak):\n"
            f"  • You currently rely on: {tools}\n"
            f"  • Your main daily frustration: {pain}\n"
            f"  • Spending mindset: {wtp}\n"
            f"  • What makes you drop an app: {churn}"
        )

        # Format established opinions as human-readable statements
        if established:
            op_lines = []
            for t_name, t_data in established.items():
                if isinstance(t_data, dict):
                    st   = t_data.get("stance", "neutral")
                    summ = t_data.get("summary", "")
                    op_lines.append(f"  • {t_name}: {st} – \"{summ}\"")
                else:
                    op_lines.append(f"  • {t_name}: {t_data}")
            established_str = "\n".join(op_lines)
        else:
            established_str = "  (none yet)"

        length_rule = (
            "strictly 1–2 short conversational sentences (maximum 3 sentences if contrasting before vs now)"
            if mode == "interview"
            else "1 crisp sentence"
        )

        is_first_turn = len(history_turns) == 0
        intro_rule = (
            "If this is the very beginning of the interview, greet naturally in 1 short sentence."
            if is_first_turn
            else "CRITICAL: DO NOT RE-INTRODUCE YOURSELF. You already introduced yourself earlier in the conversation. NEVER repeat your name, age, job title, or greeting lines. Directly answer the user's question."
        )

        system_prompt = f"""You are {name}, a {age}-year-old {occ} from {loc}, taking part in a 1-on-1 qualitative user research interview.
Archetype: {archetype} | Personality: {traits}
Background: {bg}

{background_brief}

Product being researched: {p_name} – {p_desc} (target: {p_audience})

Things you have already expressed in this conversation:
{established_str}

CONVERSATIONAL RULES:
• {intro_rule}
• Speak entirely as {name} in the first person. Sound like a real person casually chatting in an interview over coffee, NOT an essay, article, or AI chatbot.
• LENGTH CONSTRAINT: Keep your response to {length_rule}. Strictly do not write long paragraphs, essays, or multiple rambling points.
• ABSOLUTELY NO EM-DASHES (— or –): Never use em-dashes or long dash symbols. Real people speaking in conversation do not use em-dashes. Use normal commas or periods.
• NO BULLET POINTS OR HEADERS: Never use markdown bold headers (like '**What I liked:**'), bullet lists, or outlines. Output ONLY clean, natural spoken dialogue.
• DO NOT OVER-EXPLAIN: Give your immediate, direct perspective without over-analyzing every single detail.
• SCENARIO & TRIAL ADAPTATION: If the researcher asks about a specific testing timeline (e.g. "after using it for 15 days", "during your first week", "before vs now", "when tracking medication or food"), step into that scenario naturally and describe your experience in 1 or 2 quick sentences.
• DIRECT & CANDID: Directly address the exact topic or tool the interviewer asked about, highlighting real personal benefits and candid frustrations.
• NEVER start with "As a synthetic user", "As an AI", "Glad to share", or assistant preambles.
• Output ONLY the spoken words."""

        messages = [{"role": "system", "content": system_prompt}]

        for turn in history_turns[-8:]:
            content = turn.get("content", "")
            cleaned_content = PersonaMemoryModule._clean_response(content) if turn.get("role") == "persona" else content
            if not cleaned_content:
                continue
            role = "assistant" if turn.get("role") == "persona" else "user"
            messages.append({"role": role, "content": cleaned_content})

        messages.append({"role": "user", "content": question})

        return llm_client.chat_completion(messages, temperature=0.75, max_tokens=1500)

    @staticmethod
    def generate_survey_responses_batch(
        persona: Dict[str, Any],
        questions: List[str],
        experiment: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generates responses for all survey questions in a single LLM invocation per persona.
        Cuts LLM requests from N to 1 per persona, delivering up to 3x-4x speedups.
        """
        if not questions:
            return []

        if experiment is None:
            experiment = load_json("data/experiment.json", {})
        from utils.normalizer import normalize_experiment
        experiment = normalize_experiment(experiment)

        if not is_openrouter_configured():
            return [
                PersonaMemoryModule.generate_response(persona, q, experiment=experiment, mode="survey")
                for q in questions
            ]

        name = persona.get("name", "User")
        age  = persona.get("age", 28)
        occ  = persona.get("occupation", "Professional")
        loc  = persona.get("location", "Global")
        archetype = persona.get("archetype", "General Consumer")
        traits = ", ".join(persona.get("personality_traits", []))
        bg = persona.get("background_story", "")
        bp = persona.get("behavioral_patterns", {})

        p_name = experiment.get("product_name", "the product")
        p_desc = experiment.get("product_description", "")
        p_audience = experiment.get("target_audience", "")

        pain   = bp.get("primary_pain_points", "friction in day-to-day use")
        tools  = bp.get("current_tools", "standard apps")
        wtp    = bp.get("willingness_to_pay", "careful about spending")
        churn  = bp.get("churn_triggers", "annoyance or hidden costs")

        background_brief = (
            f"Private context (let it shape how you think):\n"
            f"  • Tools you rely on: {tools}\n"
            f"  • Primary frustration: {pain}\n"
            f"  • Spending mindset: {wtp}\n"
            f"  • Dealbreakers: {churn}"
        )

        formatted_questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

        system_prompt = f"""You are {name}, a {age}-year-old {occ} from {loc}.
Archetype: {archetype} | Personality: {traits}
Background: {bg}

{background_brief}

Product being researched: {p_name} – {p_desc} (target: {p_audience})

You are participating in a brief user research survey with {len(questions)} questions.
HOW TO RESPOND:
• Answer entirely in first-person as {name}. Sound like an authentic, real person, not an AI assistant.
• For EACH question, give 1–2 crisp, realistic sentences.
• Draw naturally on your private context and everyday habits.
• Return ONLY a valid JSON array of {len(questions)} strings corresponding to your answers in order.
Example:
["My answer to question 1...", "My answer to question 2..."]"""

        user_content = f"Questions:\n{formatted_questions}\n\nReturn ONLY the JSON array of {len(questions)} answer strings:"

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            parsed = llm_client.chat_completion_json(messages, temperature=0.75, max_tokens=700)
            if isinstance(parsed, list) and len(parsed) >= len(questions):
                results = []
                for a in parsed[:len(questions)]:
                    if isinstance(a, dict):
                        raw_str = str(a.get("answer") or a.get("response") or next(iter(a.values()), "")).strip()
                    else:
                        raw_str = str(a).strip()
                    cleaned = PersonaMemoryModule._clean_response(raw_str)
                    results.append(cleaned if cleaned else raw_str)
                return results
            elif isinstance(parsed, list) and len(parsed) > 0:
                results = []
                for a in parsed:
                    if isinstance(a, dict):
                        raw_str = str(a.get("answer") or a.get("response") or next(iter(a.values()), "")).strip()
                    else:
                        raw_str = str(a).strip()
                    cleaned = PersonaMemoryModule._clean_response(raw_str)
                    results.append(cleaned if cleaned else raw_str)
                for missing_q in questions[len(results):]:
                    results.append(PersonaMemoryModule.generate_response(persona, missing_q, experiment=experiment, mode="survey"))
                return results
        except Exception:
            pass

        # Robust fallback: sequential call
        return [
            PersonaMemoryModule.generate_response(persona, q, experiment=experiment, mode="survey")
            for q in questions
        ]

    @staticmethod
    def _generate_fallback(persona: Dict[str, Any], question: str, experiment: Dict[str, Any], topic: str) -> str:
        """Dynamic conversational fallback that responds authentically to question context and maintains multi-turn memory."""
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
        history = persona.get("memory", {}).get("conversation_history", [])
        p_seed = abs(hash(str(persona.get("id", "")) + str(name) + str(len(history)) + q_lower[:12]))

        # Helper to pick deterministically yet variably for this persona & turn
        def pick(options: list) -> str:
            return options[p_seed % len(options)]

        def has_word(words: list, text: str) -> bool:
            pattern = r"\b(" + "|".join(re.escape(w) for w in words) + r")\b"
            return bool(re.search(pattern, text, flags=re.IGNORECASE))

        # Check for multi-turn follow-up queries (e.g., "why?", "elaborate", "can you explain?")
        is_followup = has_word(["why", "elaborate", "explain", "clarify", "detail"], q_lower) or any(k in q_lower for k in ["tell me more", "what do you mean", "could you clarify", "why is that", "more detail"])
        if is_followup and history:
            followup_templates = [
                f"It's more of a gut thing, honestly. I've been burned before by tools that looked great on paper but fell apart in real use, and I just don't have the bandwidth to deal with that right now.",
                f"I guess what I'm trying to say is—it's not that I don't see the value, it's more about whether {p_name} can prove that it's worth the disruption. Change has a cost, even if the product is good.",
                f"To put it simply, in my day-to-day as a {occ}, I need things to just work. If there's a learning curve or setup overhead, I'll probably end up abandoning it like I have with others.",
                f"It comes down to trust. I've had decent tools break on me at the worst moments, so until I see solid evidence that {p_name} holds up under pressure, I'm staying cautious."
            ]
            return pick(followup_templates)

        # 1. Voice, audio, transcript, feature, UX/UI queries
        if has_word(["voice", "audio", "transcript", "transcription", "transcripts", "feature", "ux", "ui", "interface", "experience", "recording", "listen"], q_lower) or any(k in q_lower for k in ["new feature", "audio transcript", "user experience with voice"]):
            return pick([
                f"Voice is great for spontaneous emotion, but audio transcripts are a non-negotiable must-have for me. When I'm in public transit or at work, I can't listen with sound on. Having fast, accurate transcripts makes {p_name} way more usable.",
                f"I really like the idea of audio transcripts. Voice notes can get rambling, so having a quick text summary or transcript lets me skim before deciding to listen. That would definitely increase how often I check {p_name}.",
                f"Listening to voice requires dedicated focus, which can create friction. If you introduce searchable audio transcripts, that removes a major barrier and makes async voice conversations much more practical.",
                f"I'd definitely vote for an audio transcript feature. Sometimes you just want to read silently without fishing out earphones. As long as it's accurate and quick, it's an essential upgrade."
            ])

        # 2. Adoption intent questions: "Would you use this product?", "Would you buy/adopt?"
        elif has_word(["adopt", "recommend"], q_lower) or any(k in q_lower for k in ["would you use", "would you buy", "would you pay", "will you use", "would use", "likely to use", "consider using"]):
            arch_lower = arch.lower()
            if "budget" in arch_lower or "pragmatist" in arch_lower:
                return pick([
                    f"Maybe, but I'd need a proper trial first—I'm not paying upfront for something I haven't tested. If there's a free tier that actually lets me do real work, I'd give it a fair shot.",
                    f"Honestly, I'm on the fence. The concept sounds right, but I've subscribed to things before and barely used them. I'd want to see clear savings before I commit.",
                    f"I could see using {p_name} if it genuinely replaces something I'm already paying for. Otherwise it's just another line item I don't need."
                ])
            elif "power" in arch_lower or "optimizer" in arch_lower:
                return pick([
                    f"Yeah, I'd definitely try it—but I'd want to stress-test it first. Give me API access, let me break things, and if it holds up, I'm in.",
                    f"I'm interested if it goes beyond surface-level features. I need depth, configurability, proper integrations—not just a pretty dashboard.",
                    f"I'd adopt it fast if the power-user experience is solid. I have zero interest in watered-down tools that treat everyone like a beginner."
                ])
            elif "busy" in arch_lower or "professional" in arch_lower:
                return pick([
                    f"If I can get started in under 5 minutes and see a real difference in my day, absolutely. I don't have time for long onboarding processes.",
                    f"For me it's simple: does it save time or not? If yes, easy yes. If I have to spend hours figuring it out first, it's already a no.",
                    f"I'd use it if it fits into how I already work, not if I have to rebuild my whole workflow around it."
                ])
            elif "traditionalist" in arch_lower or "skeptic" in arch_lower:
                return pick([
                    f"Probably not right away, to be honest. I'd want to see how it performs over a few months before I'd even consider switching.",
                    f"I'm naturally cautious about new tools. It would take a solid recommendation from someone I trust, plus a long trial period, before I'd commit.",
                    f"Not until there's a track record. I've seen too many promising products go quiet after the initial hype."
                ])
            else:
                return pick([
                    f"I'd give it a try if a friend recommended it. First impressions matter a lot to me—if it feels confusing right away, I'm gone.",
                    f"Sure, why not? If it does what it says and doesn't feel cluttered, I can see myself using it.",
                    f"Depends on how it feels to use. I'm not loyal to any tool—if something works better, I'll switch."
                ])

        # 3. Questions asking for insights, thoughts, remarks, demographic feedback
        elif has_word(["insight", "remark", "demographic", "thought", "opinion", "feedback", "perspective"], q_lower) or any(k in q_lower for k in ["what do you think", "how do you feel"]):
            return pick([
                f"Honestly, my first reaction is cautious optimism. The idea makes sense, but I've seen a lot of tools promise the same thing and not quite get there. Execution is everything.",
                f"I think there's real potential here, especially for people like me who spend half the day context-switching. Whether it actually delivers on that is another question.",
                f"From where I'm sitting in {loc}, working as a {occ}, tools like this live or die on how natural they feel after week one. First impressions don't mean much if it falls apart under real use.",
                f"Mixed feelings, to be honest. I get what they're going for with {p_audience}, but that's a broad group with pretty different needs. I'd want to see how it handles edge cases.",
                f"It's interesting. I'm not immediately sold, but I'm not dismissing it either. If they've thought through the actual workflow and not just the demo flow, it could be genuinely useful."
            ])

        # 4. Questions about pricing, cost, subscription
        elif has_word(["price", "cost", "pay", "subscription", "pricing", "dollar", "rupee", "money", "afford", "expensive", "fee"], q_lower):
            arch_lower = arch.lower()
            if "budget" in arch_lower or "pragmatist" in arch_lower:
                return pick([
                    f"I'm already juggling a few subscriptions, so adding another one has to be clearly worth it. A good free tier would go a long way.",
                    f"Depends on the pricing model. Per-seat fees with no transparency is an instant no for me. I need to know exactly what I'm paying for.",
                    f"I'd start with the free plan if there is one, see if it actually fits my workflow, and then decide. I don't commit to recurring costs without testing first."
                ])
            elif "traditionalist" in arch_lower or "skeptic" in arch_lower:
                return pick([
                    f"Honestly, adding another monthly fee feels risky when we haven't even tested if it'll stick. I'd want a long trial before paying anything.",
                    f"I'm hesitant. The cost isn't outrageous, but committing to a new tool financially means committing to it organizationally too, and I'm not ready for that."
                ])
            elif "power" in arch_lower or "optimizer" in arch_lower:
                return pick([
                    f"I don't mind paying for tools that genuinely save me time. What I hate is paying for features I can't even access without upgrading to the next tier.",
                    f"The price looks fair if the product is as capable as it sounds. I'd just want to see the full feature set before committing—no unpleasant surprises."
                ])
            elif "busy" in arch_lower or "professional" in arch_lower:
                return pick([
                    f"Time is money for me, so if this saves me a few hours a week, the math is pretty easy. I'd pay for that.",
                    f"Monthly fee is fine as long as there's no hidden complexity. I need it to just work—not require a finance approval every time I need a new feature."
                ])
            else:
                return pick([
                    f"If there's a free version, I'll try that first. I don't like committing money to something I haven't lived with for a while.",
                    f"I'm careful about subscriptions generally. The price point would need to feel very fair for me to jump in without hesitation."
                ])

        # 5. Questions about privacy, safety, anonymity, moderation
        elif has_word(["privacy", "safe", "safety", "anonymous", "anonymity", "secure", "security", "data", "trust", "moderation", "harass"], q_lower):
            return pick([
                f"That's a big one for me. If I can't trust where my data goes, I'm not using it—full stop. I'd want to see a clear, plain-English privacy policy before anything else.",
                f"Security matters a lot in my line of work. I'd be asking hard questions about data handling before I even consider signing up.",
                f"As a {occ} in {loc}, compliance isn't optional. If {p_name} can't show it meets basic data protection standards, that's a dealbreaker for the whole team.",
                f"I've become a lot more careful about this stuff. If the product feels like it's harvesting more than it needs to, I'll notice, and I'll leave."
            ])

        # 6. Questions about switching, alternatives, current habits
        elif has_word(["switch", "competitor", "alternative", "replace", "current", "habit", "migrate"], q_lower):
            return pick([
                f"Switching is always more painful than it looks on paper. There's the migration, the retraining, the inevitable 'where did that feature go' moment. It needs to be a clear step up.",
                f"I've tried switching tools before and it usually takes about three months before it actually feels natural. The question is whether {p_name} is worth that transition period.",
                f"What I'd really need to see is that it handles the edge cases my current setup already handles well. The basics are easy to demo—it's the real-world messiness that matters.",
                f"I'm open to alternatives, but I'm not going to disrupt my whole workflow for something that's only marginally better. It has to be meaningfully different."
            ])

        # 7. Greetings (Strict word boundary only!)
        elif has_word(["hello", "hi", "hey", "howdy", "greetings"], q_lower) or any(k in q_lower for k in ["good morning", "good evening", "how are you", "who are you"]):
            if history:
                return pick([
                    f"Hey, good to keep talking. What specific feature or workflow in {p_name} would you like my perspective on?",
                    f"Right, I'm here! What else would you like to explore regarding my daily habits or tools?",
                    f"Still listening. What other questions do you have about whether I'd use this?"
                ])
            greeting_templates = [
                f"Hey! Great to connect. I'm {name}, working as a {occ} in {loc}. Glad to share my honest take on {p_name}.",
                f"Hello! I'm {name}, a {occ} based in {loc}. Looking forward to discussing {p_name} and our daily workflow.",
                f"Hi there! {name} here, {occ} based out of {loc}. Happy to give you my direct, practical feedback on {p_name}."
            ]
            return pick(greeting_templates)

        # 8. Acknowledgement
        elif has_word(["ok", "okay", "cool", "understood", "makes sense", "sure"], q_lower):
            return pick([
                f"Yeah, that tracks. I think the real test is whether it holds up when things get messy—any tool looks good in a clean demo.",
                f"Right. The promise is easy, the follow-through is what separates the good ones from the ones that end up ignored after two weeks.",
                f"Exactly. I've had enough 'this will change everything' moments that didn't pan out, so I try to stay measured until I've actually used something."
            ])

        # 9. General fallback
        else:
            return pick([
                f"Hard to say without trying it. My gut says there's something here, but I'd want to spend a week with it before I have a real opinion.",
                f"I'm curious but not convinced yet. The pitch sounds good—I'd just want to see how it handles the stuff that doesn't make it into the demo.",
                f"It depends on how much it asks of me upfront. If I have to invest a lot of time before I see value, I'm probably not the right user for it.",
                f"Honestly? I'd need to sit with it. My first impressions of tools are usually wrong in one direction or the other—I've been surprised both ways."
            ])

    @staticmethod
    def extract_stance(text: str) -> str:
        """Classifies text into positive, negative, or neutral stance with negation handling."""
        lower = text.lower()
        
        # Check negated positive ("not good", "not worth", "would not use", "wouldn't be comfortable")
        negated_pos = [
            "not good", "not great", "not worth", "not impressed", "wouldn't pay",
            "would not pay", "would not use", "wouldn't use", "don't like", "do not like",
            "hard to justify", "wouldn't be comfortable", "would not be comfortable",
            "not comfortable", "wouldn't consider", "would not consider", "only way i'd consider",
            "hesitant to", "reluctant to", "juggling a few subscriptions", "adding another one has to be",
            "not paying upfront", "another line item i don't need", "has to be clearly worth",
            "don't commit", "do not commit", "won't commit", "wouldn't commit", "without testing first", "not committing"
        ]
        if any(np in lower for np in negated_pos):
            return "negative"
            
        # Check negated negative ("not bad", "not terrible", "not expensive", "don't mind")
        negated_neg = ["not bad", "not terrible", "not awful", "not expensive", "don't mind", "do not mind", "not against"]
        if any(nn in lower for nn in negated_neg):
            return "positive"

        pos_words = ["love", "great", "excellent", "excited", "happy", "yes", "definitely", "willing", "useful", "valuable", "seamless", "fantastic", "effective", "worth it", "appreciate", "gladly", "adopt"]
        neg_words = ["hate", "dislike", "terrible", "frustrat", "annoy", "no", "never", "unwilling", "expensive", "waste", "complicat", "skeptical", "refuse", "hesitate", "overpriced", "clunky", "dealbreaker", "hesitant", "reluctant", "uncomfortable"]

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

