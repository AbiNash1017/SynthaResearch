# Synthetic User Generation Platform for Product Research

A platform that simulates human learner behavior, product opinions, and feature feedback to help edtech and product teams validate ideas without needing access to real users.

The behavioral models and personas in this project mirror user types from platforms like **Udemy** (course buying, completion drops, video length fatigue) and **Duolingo** (streaks, gamification loops, micro-lessons).

---

## Key Features

1. **Experiment Workspace**
   - Define your product name, product description, target audience, and research objectives.
   - Saved in `data/experiment.json`.

2. **Persona Generation Agent (`PersonaGenerationAgent`)**
   - Automatically generates diverse synthetic personas with complete demographic, behavioral, and psychological profiles.
   - Includes 5 archetypes:
     - **Impulse Buyer** (buys Udemy courses on sale, low completion rate, dislikes long theory).
     - **Streak Chaser** (Duolingo daily habit addict, motivated by XP, leaderboards, and streak freezes).
     - **Deep Learner** (completes comprehensive courses, analytical, disdains superficial badges).
     - **Career Switcher** (time-pressured, focuses on certificates, job outcomes, and resume items).
     - **Casual Browser** (recreational, low-commitment, prefers 3-minute lessons and ad-supported freemium).

3. **Persona Memory & Consistency Module (`PersonaMemoryModule`)**
   - Maintains consistent opinions across multi-turn interactions.
   - Locks in stances so a persona does not contradict themselves across different questions or interview turns.
   - Keeps conversation history for contextual responses.

4. **Survey Mode (`SurveyAgent`)**
   - Simultaneously asks questions to all synthetic personas.
   - Generates a side-by-side comparison matrix with sentiment tagging (`POSITIVE`, `NEUTRAL`, `NEGATIVE`).
   - Saved in `data/survey_responses.json`.

5. **Interview Mode (`InterviewAgent`)**
   - Real-time, multi-turn direct conversation with any selected persona.
   - Personas answer in-character, taking into account their traits, memory, and background story.
   - Appends session history to `data/interview_logs.json`.

6. **Insight Extraction Agent (`InsightExtractionAgent`)**
   - Aggregates all survey and interview data.
   - Extracts emergent themes using NLP (n-gram frequency).
   - Computes sentiment distribution and cross-archetype behavioral trends.
   - Generates a structured research report exported to **JSON** and **PDF** in the `reports/` folder.

---

## Project Structure

```
SyntheticUsersReserch/
├── agents/
│   ├── persona_generator.py      # Persona Generation Agent
│   ├── persona_memory.py         # Consistency & Memory Module
│   ├── survey_agent.py           # Survey Mode orchestration
│   ├── interview_agent.py        # Interactive 1-on-1 interview
│   └── insight_agent.py          # Insight extraction & report generation
├── config/
│   ├── archetype_map.py          # Learner archetypes & behavioral patterns
│   ├── topic_map.py              # Keyword to topic detection
│   └── settings.py               # Constants and configuration
├── data/
│   ├── experiment.json           # Active experiment setup
│   ├── persona_pool.json         # Generated synthetic personas
│   ├── survey_responses.json     # Survey answers and sentiment
│   └── interview_logs.json       # Multi-turn interview history
├── reports/
│   ├── report_<date>.json        # Machine-readable insight report
│   └── report_<date>.pdf         # Printable PDF research report
├── templates/
│   ├── name_bank.py              # Names, stories, demographics
│   └── response_templates.py     # Parameterized persona responses
├── utils/
│   ├── nlp_utils.py              # NLP tokenizer & theme extraction
│   ├── pdf_exporter.py           # ReportLab PDF generator
│   └── storage.py                # Safe JSON load/save operations
├── api.py                        # FastAPI REST backend
├── main.py                       # Rich CLI interface
├── test_pipeline.py              # Automated test suite
└── requirements.txt              # Project dependencies
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+ installed

### 1. Activate the Virtual Environment
If you are opening a new terminal in the project directory:

**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

*(If you ever need to recreate the environment: `python -m venv venv` and `pip install -r requirements.txt`)*

---

## How to Run

You can interact with the platform in two ways:

### Option A: Interactive Terminal CLI (`main.py`)
Run the terminal app:
```bash
python main.py
```

This presents a menu:
```
1. Setup Experiment Workspace
2. Generate Diverse Synthetic Personas
3. Run Multi-Persona Survey
4. Start Interactive Interview with a Persona
5. Generate Research & Insight Report (JSON + PDF)
6. Exit
```

**Walkthrough:**
1. **Option 1**: Enter your product name (e.g. *LearnFlow*), description, audience, and objectives.
2. **Option 2**: Generate 5 diverse personas and review their behavioral profile cards.
3. **Option 3**: Run the survey using the default study app questions or enter your own questions.
4. **Option 4**: Select a persona (e.g. `persona_001`) and chat with them in real-time. Type `exit` to end.
5. **Option 5**: Generate the research insight report. It creates both `reports/report_<date>.json` and a styled `reports/report_<date>.pdf`.

---

### Option B: FastAPI Backend Server (`api.py`)
Run the API server with hot-reload:
```bash
uvicorn api:app --reload --port 8000
```

Open your browser and navigate to:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Key Endpoints:
- `POST /api/setup-experiment`: Define product description & target audience.
- `GET /api/experiment`: View current experiment settings.
- `POST /api/generate-personas?count=5`: Generate synthetic personas.
- `GET /api/personas`: Retrieve all generated personas and their memory states.
- `POST /api/run-survey`: Send a list of questions to all personas simultaneously.
- `POST /api/interview`: Send a message to a specific persona (`{ "persona_id": "persona_001", "user_message": "..." }`).
- `GET /api/generate-report`: Extract insights and generate JSON + PDF reports.

---

