# SynthaResearch — Backend Server

The backend engine for the **Universal Synthetic User Research Platform**, an AI-driven simulation system that models human customer psychology, product sentiment, feature feedback, and willingness-to-pay across **any product or industry domain** (B2B SaaS, developer tools, fintech, healthtech, consumer apps, e-commerce, and more).

Powered by **OpenRouter LLM**, **FastAPI**, **MongoDB** with **Beanie ODM**, and **JWT Authentication**.

---

## Key Features

1. **Multi-Tenant Experiment Management**
   - Define custom product experiments (name, domain, value proposition, target audience, research goals) or pick from domain presets.
   - Experiments, personas, surveys, interviews, and reports are fully isolated per authenticated user in MongoDB.
   - Seamlessly switch active experiments or manage multiple research projects.

2. **OpenRouter Foundation Model Gateway**
   - Zero hardcoded models: Swap between OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, Meta Llama 3.3, Google Gemini 2.5 Flash, DeepSeek, etc. via `.env`.
   - Built-in graceful fallbacks and offline heuristics if LLM keys are absent.

3. **Domain-Tailored Persona Generation (`PersonaGenerationAgent`)**
   - Synthesizes diverse synthetic user personas tailored to the active product's target audience.
   - Includes full demographic details, current tool stacks, pain points, budget/willingness to pay, churn triggers, and MBTI psychological traits.

4. **Cognitive Persona Memory & Consistency (`PersonaMemoryModule`)**
   - Personas maintain consistent opinions and remember prior conversational context across turns.
   - Avoids cognitive drift during deep qualitative interrogations.

5. **Cross-Persona Survey Simulations (`SurveyAgent`)**
   - AI-suggested questions tailored to product goals or custom research inquiries.
   - Personas answer simultaneously in-character with automatic sentiment classification (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) and key takeaway extraction.
   - Generates side-by-side comparison matrices.

6. **Interactive Live 1-on-1 Qualitative Interviews (`InterviewAgent`)**
   - Real-time conversational interview with any synthetic persona.
   - Preserves multi-turn dialogue history and session transcripts in MongoDB.

7. **Insight Extraction & Strategic Reporting (`InsightExtractionAgent`)**
   - Aggregates empirical survey and interview data into executive findings.
   - Calculates the **Adoption Propensity Score (%)** ("Would use this product?") with behavioral segment breakdowns.
   - Exports both structured JSON summaries and styled, multi-page **PDF reports** via ReportLab.

8. **Secure Authentication & User Identity**
   - JWT access tokens and secure HttpOnly refresh token cookies.
   - Secure password hashing with `bcrypt`.
   - User profile management with customizable avatar seeds.

---

## Environment Configuration

Create a `.env` file in the `server/` directory (or copy from `.env.example`):

```env
# OpenRouter LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=syntharesearch

# Authentication Configuration (Generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_super_secret_jwt_key_here_change_for_production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration (Comma-separated origins for web clients)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Installation & Setup

### 1. Prerequisites
- **Python 3.10+**
- **MongoDB** running locally (`mongodb://localhost:27017`) or a MongoDB Atlas connection string.

### 2. Install Python Dependencies
```bash
# Navigate to server directory
cd server

# Recommended: activate virtual environment
# Windows:
..\venv\Scripts\activate
# Linux/macOS:
source ../venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

---

## Running the Backend

### Option A: FastAPI REST API Server (Recommended for Web Client)
```bash
uvicorn api:app --reload --port 8000
```
- **API Base URL**: `http://localhost:8000`
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Option B: Standalone Terminal CLI (`main.py`)
```bash
python main.py
```
Provides an interactive Rich terminal interface for setting up experiments, synthesizing personas, running surveys, interviewing personas, and exporting reports locally.

---

## API Endpoint Reference

### System & Health
* `GET /` — Service status and LLM configuration summary.
* `GET /api/llm-config` — Current active OpenRouter model and status.

### Authentication (`/auth`)
* `POST /auth/register` — Create a new user account with email, password, and avatar seed. Returns JWT tokens.
* `POST /auth/login` — Authenticate existing user. Returns access token and sets HttpOnly refresh cookie.
* `POST /auth/refresh` — Issue a new access token using a valid refresh token.
* `GET /auth/me` — Retrieve the authenticated user's profile.
* `PATCH /auth/profile` — Update user full name or avatar selection.
* `POST /auth/logout` — Invalidate user session and clear refresh cookies.

### Experiments (`/api`)
* `POST /api/setup-experiment` — Create and normalize a new product experiment workspace. Sets it as active.
* `GET /api/experiment` — Retrieve the currently active experiment for the user.
* `GET /api/experiments` — List all experiments created by the user.
* `POST /api/experiment/{experiment_id}/activate` — Switch the active experiment workspace.

### Personas (`/api`)
* `POST /api/generate-personas?count=5` — Synthesize synthetic personas for the active experiment and persist in MongoDB.
* `GET /api/personas` — List all personas generated for the active (or specified) experiment.

### Surveys (`/api`)
* `GET /api/suggest-questions?count=3` — Request AI-generated survey questions tailored to the active product.
* `POST /api/run-survey` — Run questions across all personas and persist results in MongoDB.
* `GET /api/survey-matrix` — Get side-by-side comparison matrix for the latest active survey.

### Interviews (`/api`)
* `POST /api/interview` — Execute a conversational turn with a specific persona; persists dialogue in MongoDB.
* `GET /api/interviews` — List summaries of all recorded interview sessions for the active experiment.
* `GET /api/interview/{session_id}` — Retrieve full transcript and details of an interview session.
* `POST /api/interview/reset` — Clear interview sessions for the active experiment.

### Reports & Analytics (`/api`)
* `GET /api/adoption-score` — Compute "Would use this product?" adoption propensity score (%) and sentiment breakdown.
* `POST /api/generate-report` (or `GET`) — Synthesize executive research report and store in MongoDB.
* `GET /api/reports/latest` — Retrieve data for the latest research report.
* `GET /api/reports/latest/pdf` — Stream and download the PDF report for the active experiment.
* `GET /api/reports/{report_id}/pdf` — Stream and download a specific report PDF by ID.
* `GET /api/reports` — List historical research reports.

---

## Testing & Validation Suites

The backend includes automated testing scripts to ensure consistency, diversity, and pipeline integrity:

```bash
# 1. End-to-end multi-domain test pipeline
python test_pipeline.py

# 2. Persona demographic, archetype, and trait diversity audit
python test_persona_diversity.py

# 3. Comprehensive multi-domain validation suite (Surveys, Memory, Scoring, Reporting)
python validation.py
```
