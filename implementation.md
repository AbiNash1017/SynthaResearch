# Synthetic User Generation Platform — Implementation Plan (Milestone 2, Task 2)

## 1. Overview

**Product (being researched):** A new online learning platform — a direct competitor to Udemy/Duolingo combining structured course delivery (Udemy-style) with gamified daily habits (Duolingo-style).

**Platform Purpose:** Product teams define their learning app, target learner audience, and research objectives. The system automatically generates diverse synthetic learner personas that simulate real online-learning user behavior — completion rates, motivation drops, subscription decisions, feature reactions — without needing real participants.

**Target Users of this tool:** Student project teams and early-stage edtech startups validating a new learning product idea.

**Features (this milestone — backend only):**
1. Experiment Workspace — define product description, target learner audience, research objectives (CLI / JSON input)
2. Persona Generation Agent — generates diverse synthetic learner personas with demographics, learning style, behavioral patterns, and psychological profile
3. Persona Memory & Consistency Module — each persona maintains consistent opinions and prior conversation context across multi-turn interactions
4. Survey Mode — all personas answer defined questions simultaneously; results saved to JSON for side-by-side comparison
5. Interview Mode — multi-turn conversation with a selected persona; persona stays in character using memory
6. Insight Extraction Agent — analyzes all responses, extracts themes, sentiment, behavioral trends, generates a structured report (JSON + PDF)

## 2. Scope & Constraints for This Milestone

- **No LLM / external API calls.** All agent logic is deterministic and rule-based — persona responses come from structured templates parameterized by persona attributes. This proves the full pipeline before AI complexity is added.
- **Backend only.** Interaction via Python CLI (`python main.py`) and direct JSON file inspection. No web UI, no HTML/CSS/JS.
- **No database.** Flat JSON files under `data/` serve as the persistence layer.
- **Single experiment session.** No auth, no multi-user support at this stage.
- **Modular agent design.** Each agent is a self-contained class with a clean interface — LLM backends can be dropped in later without restructuring the pipeline.

## 3. System Architecture

```
  CLI Entry (main.py)
       |
       |-- [1] Setup Experiment
       |         -> prompts for product name, description, target audience, objectives
       |         -> writes data/experiment.json
       |
       |-- [2] Generate Personas
       |         -> PersonaGenerationAgent reads experiment.json
       |         -> writes data/persona_pool.json
       |         -> prints persona summary cards to terminal
       |
       |-- [3] Run Survey
       |         -> SurveyAgent reads persona_pool.json + user-entered questions
       |         -> PersonaMemoryModule.generate_response() per persona per question
       |         -> writes data/survey_responses.json
       |         -> prints side-by-side table via rich
       |
       |-- [4] Start Interview
       |         -> user picks a persona by ID
       |         -> InterviewAgent: multi-turn loop
       |         -> each turn: PersonaMemoryModule.generate_response()
       |         -> appends to data/interview_logs.json
       |
       |-- [5] Generate Report
                 -> InsightAgent reads survey_responses.json + interview_logs.json
                 -> computes themes, sentiment, behavioral trends
                 -> writes reports/report_<date>.json
                 -> writes reports/report_<date>.pdf  (via reportlab)
                 -> prints summary to terminal
```

## 4. Data Model

### `data/experiment.json`
Defines the product being researched and the research context.
```json
{
  "product_name": "LearnFlow",
  "product_description": "A mobile-first learning platform combining Udemy-style structured courses with Duolingo-style daily streaks, XP points, and bite-sized lessons to improve course completion rates.",
  "target_audience": "Working professionals aged 22-40 who start online courses but rarely finish them; motivated by career growth; familiar with Udemy, Coursera, or Duolingo",
  "research_objectives": [
    "Understand why learners abandon courses after the first week",
    "Identify which gamification elements (streaks, badges, leaderboards) actually improve retention",
    "Gauge willingness to pay for a premium subscription vs one-time course purchase",
    "Find the ideal daily lesson length for busy professionals"
  ],
  "created_at": "2026-09-16T00:00:00"
}
```

### `data/persona_pool.json`
Each persona is a synthetic learner whose behavior mirrors real Udemy/Duolingo user archetypes.
```json
[
  {
    "id": "persona_001",
    "name": "Rohan Mehta",
    "age": 27,
    "gender": "Male",
    "occupation": "Junior Software Engineer",
    "location": "Bengaluru, India",
    "income_bracket": "lower-middle",
    "education": "B.Tech in CS",

    "personality_traits": ["ambitious", "easily distracted", "competitive"],

    "learning_behavioral_patterns": {
      "platform_familiarity": ["Udemy", "YouTube tutorials"],
      "course_completion_rate": "low",
      "preferred_lesson_length": "under 10 minutes",
      "learning_time": "late night (10pm-12am)",
      "motivation_trigger": "job promotion / salary hike",
      "dropout_trigger": "lessons feel too theoretical, no practice",
      "gamification_response": "high — responds well to streaks and leaderboards",
      "subscription_preference": "one-time course purchase",
      "device": "mobile"
    },

    "psychological_profile": {
      "mbti": "ESTP",
      "risk_tolerance": "low",
      "motivation_type": "extrinsic",
      "decision_style": "impulsive",
      "attention_span": "short"
    },

    "background_story": "Rohan bought 12 courses on Udemy over 2 years but finished only one. He starts with enthusiasm but drops off after day 3 when content gets dense. He loves the idea of streaks but forgets to open the app after a busy day at work.",

    "opinion_seeds": {
      "price_sensitivity": 0.85,
      "gamification_appeal": 0.90,
      "long_video_tolerance": 0.20,
      "social_learning_interest": 0.70,
      "certificate_value": 0.75,
      "overall_sentiment_bias": 0.55
    },

    "memory": {
      "conversation_history": [],
      "established_opinions": {},
      "last_updated": "2026-09-16T00:00:00"
    }
  }
]
```

**Learner behavioral archetypes represented across the persona pool (one per persona):**

| Archetype | Udemy/Duolingo Parallel | Key Trait |
|---|---|---|
| The Impulse Buyer | Buys Udemy courses on sale, never finishes | High price sensitivity, low completion |
| The Streak Chaser | Duolingo daily streak addict | Gamification-driven, surface-level learning |
| The Deep Learner | Finishes Udemy courses, takes notes | Intrinsic motivation, long attention span |
| The Career Switcher | Uses Coursera/Udemy for role transition | High urgency, certificate-focused |
| The Casual Browser | Opens Duolingo once a week | Low commitment, entertainment-driven |

### `data/survey_responses.json`
```json
{
  "survey_id": "survey_001",
  "questions": [
    "Why did you stop using your last online learning platform?",
    "Would a daily 5-minute lesson reminder improve your consistency?",
    "How much would you pay per month for unlimited course access?"
  ],
  "responses": [
    {
      "persona_id": "persona_001",
      "persona_name": "Rohan Mehta",
      "archetype": "Impulse Buyer",
      "answers": [
        {
          "question": "Why did you stop using your last online learning platform?",
          "answer": "Honestly, the videos just got really long and I felt like I wasn't making progress. I couldn't see the finish line.",
          "sentiment": "negative",
          "key_phrase": "too long, no progress visibility",
          "confidence": 0.82
        }
      ]
    }
  ],
  "created_at": "2026-09-16T00:00:00"
}
```

### `data/interview_logs.json`
```json
[
  {
    "session_id": "session_001",
    "persona_id": "persona_001",
    "persona_name": "Rohan Mehta",
    "archetype": "Impulse Buyer",
    "turns": [
      {
        "turn": 1,
        "user_message": "Tell me about your experience with Udemy.",
        "persona_response": "Yeah I've bought a ton of courses there. Mostly during sales — you know, 499 rupees for a 40-hour course feels like a steal. But I've only actually finished maybe one of them. The rest are just sitting in my library.",
        "timestamp": "2026-09-16T10:00:00"
      },
      {
        "turn": 2,
        "user_message": "What made you stop watching them?",
        "persona_response": "The videos are just too long. Like hour-long lectures. After work I barely have 20 minutes and I don't even know where to start. Duolingo is better for that — short lessons, I can finish one before bed. But I don't feel like I'm actually learning anything deep.",
        "timestamp": "2026-09-16T10:01:30"
      }
    ],
    "session_started": "2026-09-16T10:00:00"
  }
]
```

### `reports/report_<YYYY-MM-DD>.json`
```json
{
  "report_date": "2026-09-16",
  "product": "LearnFlow",
  "persona_count": 5,
  "survey_questions_asked": 3,
  "interview_turns_total": 12,
  "themes": [
    "Course abandonment after day 3-7",
    "Lesson length as dropout factor",
    "Gamification drives surface engagement not deep learning",
    "Certificate value for career switchers",
    "Price sensitivity on subscription model"
  ],
  "sentiment_distribution": {
    "positive": 0.38,
    "neutral": 0.30,
    "negative": 0.32
  },
  "behavioral_trends": [
    {
      "group": "Extrinsic-motivated personas (Impulse Buyer, Streak Chaser)",
      "finding": "80% negative sentiment toward long-form video content; 90% positive toward bite-sized gamified lessons"
    },
    {
      "group": "Intrinsic-motivated personas (Deep Learner, Career Switcher)",
      "finding": "Willing to pay 2x more; care more about curriculum depth than gamification"
    }
  ],
  "top_insights": [
    "CRITICAL PAIN POINT: 4/5 personas cited lesson length >15 min as primary dropout trigger",
    "POLARIZING FEATURE: Leaderboards — loved by competitive personas, alienating to introverts",
    "CONSENSUS: Progress visualization (% complete, XP bar) valued across all archetypes"
  ],
  "per_persona_breakdown": []
}
```

**Key schema notes:**
- `learning_behavioral_patterns` — mirrors real Udemy/Duolingo behavioral data (completion rates, session timing, device preferences, dropout triggers).
- `opinion_seeds` — float biases (0.0–1.0) per feature axis; deterministically steer template-based response generation.
- `memory.established_opinions` — prevents contradiction; if persona said "I hate subscriptions" in turn 1, that stance is locked for all future turns.
- `memory.conversation_history` — last 5 turns used as context window for Interview Mode coherence.

## 5. Core Modules & Algorithms

### 5.1 Persona Generation Agent (`agents/persona_generator.py`)

**Input:** `experiment.json`  
**Output:** `persona_pool.json` (N diverse personas, default N=5)

```
parse experiment.target_audience:
  extract: age_range, platform_familiarity cues, motivation cues

archetypes = [
  "Impulse Buyer", "Streak Chaser", "Deep Learner",
  "Career Switcher", "Casual Browser"
]

for i, archetype in enumerate(archetypes):
  persona = {}
  persona.id          = f"persona_{i+1:03d}"
  persona.name        = name_bank.pick(gender=cycle_gender(i), culture=infer_culture(target_audience))
  persona.age         = age_bank.pick(archetype)
  persona.occupation  = occupation_bank.pick(archetype)
  persona.personality_traits = trait_map[archetype]   # 3 fixed traits per archetype
  persona.learning_behavioral_patterns = behavior_map[archetype]
  persona.psychological_profile = psych_map[archetype]
  persona.background_story = story_template[archetype].format(name=persona.name, ...)
  persona.opinion_seeds = seed_map[archetype]         # deterministic floats per archetype
  persona.memory = { conversation_history: [], established_opinions: {} }

validate diversity: assert all personas have different archetypes + different trait sets
save to data/persona_pool.json
print persona summary cards to terminal (via rich)
```

**Archetype-to-behavior mapping (config/archetype_map.py):**
```
"Impulse Buyer"   -> completion_rate: low,  gamification_appeal: high, price_sensitivity: high
"Streak Chaser"   -> completion_rate: medium, gamification_appeal: very high, social_interest: medium
"Deep Learner"    -> completion_rate: high, gamification_appeal: low,  price_sensitivity: low
"Career Switcher" -> completion_rate: high, certificate_value: very high, urgency: high
"Casual Browser"  -> completion_rate: very low, commitment: low, motivation: entertainment
```

### 5.2 Persona Memory & Consistency Module (`agents/persona_memory.py`)

Rules enforced on every response generation call:

**Rule 1 — Opinion lock-in:**
```
if question_topic in persona.memory.established_opinions:
    force response to align with stored stance
else:
    generate response; extract stance; store in established_opinions[topic]
```

**Rule 2 — History context window:**
```
context = persona.memory.conversation_history[-5:]
# context is passed to fill_template() to avoid repetition and maintain thread
```

**Rule 3 — Trait-consistent tone:**
```
trait_tone_map = {
  "ambitious"         : verbose, goal-referencing language
  "easily distracted" : short answers, goes off-topic occasionally
  "competitive"       : compares self to others
  "detail-oriented"   : cites specifics, uses numbers
  "casual"            : informal, uses hedging ("I guess", "kinda")
}
apply tone modifiers to filled template before returning response
```

**Core function:**
```python
def generate_response(persona: dict, question: str, mode: str) -> str:
    topic        = detect_topic(question)        # keyword matching against topic_map
    q_type       = detect_question_type(question) # open, likert, feature-rank, price, pain-point
    history      = persona["memory"]["conversation_history"][-5:]
    opinions     = persona["memory"]["established_opinions"]
    seeds        = persona["opinion_seeds"]
    traits       = persona["personality_traits"]
    archetype    = persona["archetype"]

    # select base template
    template = RESPONSE_TEMPLATES[archetype][q_type]

    # fill placeholders using seeds + persona fields
    response = fill_template(template, persona, seeds, opinions, history)

    # apply trait-based tone modifiers
    response = apply_tone(response, traits)

    # lock-in opinion if new topic
    if topic and topic not in opinions:
        opinions[topic] = extract_stance(response)  # "positive"/"negative"/"neutral"

    # update conversation history
    persona["memory"]["conversation_history"].append({
        "role": "user",    "content": question,
    })
    persona["memory"]["conversation_history"].append({
        "role": "persona", "content": response,
    })
    persona["memory"]["last_updated"] = datetime.now().isoformat()

    save_persona(persona)
    return response
```

### 5.3 Survey Mode (`agents/survey_agent.py`)

**Input:** list of questions (CLI prompt), `persona_pool.json`  
**Output:** `survey_responses.json`, rich table printed to terminal

```python
def run_survey(questions: list[str]) -> dict:
    personas = load_json("data/persona_pool.json")
    results  = []

    for persona in personas:
        answers = []
        for question in questions:
            answer   = PersonaMemoryModule.generate_response(persona, question, mode="survey")
            sentiment = score_sentiment(persona["opinion_seeds"]["overall_sentiment_bias"])
            answers.append({
                "question":   question,
                "answer":     answer,
                "sentiment":  sentiment,
                "key_phrase": extract_key_phrase(answer)
            })
        results.append({
            "persona_id":   persona["id"],
            "persona_name": persona["name"],
            "archetype":    persona["archetype"],
            "answers":      answers
        })

    survey_data = {
        "survey_id":  f"survey_{timestamp()}",
        "questions":  questions,
        "responses":  results,
        "created_at": datetime.now().isoformat()
    }
    save_json("data/survey_responses.json", survey_data)
    print_survey_table(survey_data)   # rich table: rows=questions, columns=personas
    return survey_data
```

**Sentiment scoring (deterministic):**
```
score = persona.opinion_seeds["overall_sentiment_bias"]
      + topic_seed_adjustment(topic)      # e.g., if topic=="price", add price_sensitivity offset
sentiment = "positive" if score > 0.60 else
            "neutral"  if score > 0.35 else "negative"
```

### 5.4 Interview Mode (`agents/interview_agent.py`)

**Input:** persona_id (selected via CLI), multi-turn user messages  
**Output:** persona responses printed to terminal; turns appended to `interview_logs.json`

```python
def start_interview(persona_id: str):
    persona = load_persona(persona_id)
    print_persona_header(persona)   # name, archetype, key traits — printed once at session start
    session = {
        "session_id":     f"session_{timestamp()}",
        "persona_id":     persona_id,
        "persona_name":   persona["name"],
        "archetype":      persona["archetype"],
        "turns":          [],
        "session_started": datetime.now().isoformat()
    }

    turn = 1
    while True:
        user_msg = input("You: ").strip()
        if user_msg.lower() in ("exit", "quit", "end"):
            break

        response = PersonaMemoryModule.generate_response(persona, user_msg, mode="interview")
        print(f"{persona['name']}: {response}\n")

        session["turns"].append({
            "turn":             turn,
            "user_message":     user_msg,
            "persona_response": response,
            "timestamp":        datetime.now().isoformat()
        })
        turn += 1

    append_session(session)   # appends to interview_logs.json
```

### 5.5 Insight Extraction Agent (`agents/insight_agent.py`)

**Input:** `survey_responses.json`, `interview_logs.json`, `persona_pool.json`  
**Output:** `reports/report_<date>.json`, `reports/report_<date>.pdf`

```python
def generate_report() -> dict:
    survey   = load_json("data/survey_responses.json")
    logs     = load_json("data/interview_logs.json")
    personas = load_json("data/persona_pool.json")

    all_texts = collect_all_response_texts(survey, logs)

    # 1. Theme extraction (rule-based NLP)
    tokens    = tokenize_and_clean(all_texts)          # re.findall + stopword removal
    bigrams   = count_bigrams(tokens)                  # collections.Counter
    themes    = [phrase for phrase, _ in bigrams.most_common(5)]

    # 2. Sentiment distribution
    sentiments = [ans["sentiment"]
                  for r in survey["responses"]
                  for ans in r["answers"]]
    dist = {
        "positive": sentiments.count("positive") / len(sentiments),
        "neutral":  sentiments.count("neutral")  / len(sentiments),
        "negative": sentiments.count("negative") / len(sentiments)
    }

    # 3. Behavioral trends — group by motivation_type
    trends = compute_behavioral_trends(personas, survey)
    # Rule: group extrinsic vs intrinsic personas; compare mean sentiment per group

    # 4. Top insights — heuristic rules
    insights = []
    pain_points = [a["key_phrase"] for r in survey["responses"]
                   for a in r["answers"] if a["sentiment"] == "negative"]
    pain_freq = Counter(pain_points)
    for phrase, count in pain_freq.items():
        if count / len(personas) >= 0.60:
            insights.append(f"CRITICAL PAIN POINT: '{phrase}' raised by {count}/{len(personas)} personas")

    # 5. Per-persona breakdown
    breakdown = build_persona_breakdown(survey, logs, personas)

    report = {
        "report_date":           date.today().isoformat(),
        "product":               load_json("data/experiment.json")["product_name"],
        "persona_count":         len(personas),
        "themes":                themes,
        "sentiment_distribution": dist,
        "behavioral_trends":     trends,
        "top_insights":          insights,
        "per_persona_breakdown": breakdown
    }

    save_json(f"reports/report_{date.today()}.json", report)
    export_pdf(report, f"reports/report_{date.today()}.pdf")
    print_report_summary(report)
    return report
```

**NLP utilities (stdlib only, `utils/nlp_utils.py`):**
```python
STOPWORDS = {"i", "the", "a", "and", "to", "it", "is", "of", "my", "in",
             "that", "just", "me", "you", "we", "they", "was", "are", ...}

def tokenize_and_clean(texts: list[str]) -> list[str]:
    combined = " ".join(texts).lower()
    words    = re.findall(r"[a-z]+", combined)
    return [w for w in words if w not in STOPWORDS and len(w) > 3]

def count_bigrams(tokens: list[str]) -> Counter:
    return Counter(zip(tokens, tokens[1:]))
```

## 6. Folder Structure

```
synthetic-users-research/
├── venv/                              (not committed)
├── requirements.txt
├── implementation.md                  (this file)
├── main.py                            # CLI entry point + menu loop
├── config/
│   ├── __init__.py
│   ├── archetype_map.py               # archetype -> behavior/seed/trait mappings
│   ├── topic_map.py                   # keyword -> topic label mappings for opinion lock-in
│   └── settings.py                    # DEFAULT_N=5, sentiment thresholds, revision intervals
├── agents/
│   ├── __init__.py
│   ├── persona_generator.py           # Persona Generation Agent
│   ├── persona_memory.py              # Persona Memory & Consistency Module
│   ├── survey_agent.py                # Survey Mode
│   ├── interview_agent.py             # Interview Mode
│   └── insight_agent.py               # Insight Extraction + Report
├── templates/
│   ├── __init__.py
│   ├── response_templates.py          # RESPONSE_TEMPLATES[archetype][question_type] = template string
│   └── name_bank.py                   # name pools, occupation pools, background story templates
├── utils/
│   ├── __init__.py
│   ├── storage.py                     # load_json / save_json with safe defaults
│   ├── nlp_utils.py                   # tokenizer, stopword filter, bigram counter (stdlib only)
│   └── pdf_exporter.py                # report dict -> PDF via reportlab
├── data/
│   ├── experiment.json                # written by Setup step
│   ├── persona_pool.json              # written by PersonaGenerationAgent
│   ├── survey_responses.json          # written by SurveyAgent
│   └── interview_logs.json            # appended by InterviewAgent
└── reports/
    └── report_<date>.json / .pdf      # written by InsightAgent
```

## 7. CLI Menu (`main.py`)

```
=== Synthetic Users Research Platform ===
Product: [product_name from experiment.json, or "Not set"]

1. Setup experiment (product + audience + objectives)
2. Generate personas
3. Run survey
4. Start interview
5. Generate research report
6. Exit

Select option:
```

On first run (no `experiment.json`), route directly to option 1 before showing the menu.  
Menus 2–5 require experiment.json to exist and will prompt accordingly if missing.

## 8. Response Template Design (`templates/response_templates.py`)

Templates are parameterized strings with placeholders filled from persona fields and opinion_seeds.

```python
RESPONSE_TEMPLATES = {
  "Impulse Buyer": {
    "open":        "Honestly, {frustration_example}. I bought {platform} courses but {completion_reason}.",
    "likert":      "{agree_phrase} — but only if {condition_from_seeds}.",
    "price":       "I'd pay max {price_ceiling} rupees/month. More than that and I'd just wait for a sale.",
    "pain_point":  "The biggest problem is {top_frustration}. I always end up {dropout_behavior}.",
    "feature_rank":"I'd want {top_feature} first, then maybe {second_feature}. {gamification_feature} is cool too."
  },
  "Deep Learner": {
    "open":        "What matters to me is {quality_signal}. I finished {completion_example} because {intrinsic_reason}.",
    "likert":      "Absolutely — {specific_reason_with_data}.",
    "price":       "I'm fine paying {price_ceiling} if the content quality justifies it. Cheap courses often cut corners.",
    "pain_point":  "My frustration is usually {quality_frustration}, not the interface.",
    "feature_rank":"Curriculum depth is non-negotiable. After that: {second_feature}, then {third_feature}."
  }
  # ... Streak Chaser, Career Switcher, Casual Browser follow same pattern
}
```

**Question type detection (`detect_question_type`):**
```
keywords("why", "tell me", "describe", "how do you") -> "open"
keywords("would you", "do you agree", "rate", "how likely") -> "likert"
keywords("pay", "price", "cost", "subscription", "rupees", "dollar") -> "price"
keywords("problem", "frustration", "pain", "annoying", "hate") -> "pain_point"
keywords("rank", "prefer", "feature", "important", "priority") -> "feature_rank"
```

## 9. Environment Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### `requirements.txt`
```
rich==13.7.1
reportlab==4.2.0
flask==3.0.3
```
- `rich` — terminal tables, colored persona cards, survey grids.
- `reportlab` — PDF generation for the research report.
- `flask` — reserved for a future lightweight API layer; not used in this milestone.
- No LLM SDK. When an LLM is added later, only `persona_generator.py`, `persona_memory.py`, and `insight_agent.py` internals change — no structural changes elsewhere.

## 10. Implementation Task List (in build order)

1. **Scaffold** — create folder structure above, `venv`, `requirements.txt`.
2. **`utils/storage.py`** — `load_json(path, default={})` / `save_json(path, data)` — safe handling of missing files.
3. **`config/settings.py`** — `DEFAULT_N=5`, sentiment thresholds (`POS=0.60`, `NEG=0.35`), history window size (`MEMORY_WINDOW=5`).
4. **`config/archetype_map.py`** — define the 5 archetype profiles: trait list, behavior dict, opinion_seeds dict, psych profile, background story template.
5. **`config/topic_map.py`** — keyword lists for each topic label (e.g., `"price"`, `"gamification"`, `"lesson_length"`, `"certification"`, `"social_features"`).
6. **`templates/name_bank.py`** — name pools (male/female/neutral × 3 cultures), occupation pools per archetype, background story f-string templates per archetype.
7. **`templates/response_templates.py`** — `RESPONSE_TEMPLATES[archetype][question_type]` fill-in templates, plus `fill_template()`, `apply_tone()`, `detect_topic()`, `detect_question_type()`, `extract_stance()` functions.
8. **`agents/persona_generator.py`** — `generate_personas(experiment: dict) -> list` per §5.1; print persona cards via `rich`.
9. **`agents/persona_memory.py`** — `generate_response(persona, question, mode)` per §5.2; `save_persona()` helper.
10. **`agents/survey_agent.py`** — `run_survey(questions: list) -> dict` per §5.3; `print_survey_table()` via `rich`.
11. **`agents/interview_agent.py`** — `start_interview(persona_id: str)` REPL loop per §5.4; `append_session()` helper.
12. **`utils/nlp_utils.py`** — `tokenize_and_clean()`, `count_bigrams()`, `extract_key_phrase()`, embedded `STOPWORDS` set.
13. **`utils/pdf_exporter.py`** — `export_pdf(report: dict, path: str)` using `reportlab`.
14. **`agents/insight_agent.py`** — `generate_report() -> dict` per §5.5; `compute_behavioral_trends()`, `build_persona_breakdown()`, `print_report_summary()`.
15. **`main.py`** — CLI menu loop; route options 1–5 to the correct agent; first-run guard.
16. **Manual test pass** — run with LearnFlow experiment: generate 5 personas, 3-question survey, 6-turn interview with "Impulse Buyer" persona, generate + inspect report PDF.

## 11. Future Extension Notes (not part of this milestone)

- Swap `persona_generator.py` rule-based archetype expansion for an LLM call generating richly varied personas beyond the 5 fixed archetypes.
- Swap `persona_memory.py` template responses for LLM inference conditioned on the persona dict + conversation history.
- Swap `insight_agent.py` bigram-frequency themes for semantic clustering using sentence embeddings.
- Add web frontend (Flask + HTML/CSS/JS): Experiment Workspace form, visual persona cards, Survey comparison grid, Interview chat UI, Report dashboard with charts.
- Real-time Interview Mode streaming via Server-Sent Events.
- Multi-experiment support: namespace `data/` per `experiment_id`.
