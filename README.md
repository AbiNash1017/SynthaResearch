# SynthaResearch

**AI-powered synthetic user research.** Describe a product, generate realistic AI personas, survey and interview them, and get an adoption report in minutes.

Real user interviews are slow and expensive, so early-stage teams often skip them. SynthaResearch gives you fast, directional feedback (objections, pricing reactions, feature priorities) before you talk to real users.

## Features

- **Experiments:** Set up a workspace per product with its domain, audience, value proposition and research goals.
- **Persona generation:** Diverse personas with demographics, tool stacks, pain points, budget, churn triggers and MBTI traits.
- **Surveys:** AI-suggested or custom questions, answered in character, with sentiment tagging and a comparison matrix.
- **Live interviews:** 1-on-1 chat with any persona. Personas remember prior turns and stay consistent with opinions they've already given.
- **Reports:** Adoption propensity score with segment breakdowns, key findings and recommendations, exported to PDF.
- **Auth:** JWT access tokens plus HttpOnly refresh cookies. All data is isolated per user.

## Tech Stack

| Layer    | Tech |
| -------- | ---- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| Backend  | FastAPI, Pydantic, Uvicorn |
| Database | MongoDB with Beanie ODM (Motor) |
| AI       | OpenRouter (model-agnostic, with automatic failover) |
| Other    | PyJWT, bcrypt, ReportLab (PDF), Rich (CLI) |

## Architecture

```
Next.js client  ──REST──▶  FastAPI  ──▶  Agents ──▶ LLM client ──▶ OpenRouter
                              │          (persona, survey, interview, insight)
                              ▼
                           MongoDB
```

The LLM client cycles through fallback models on errors (429/5xx/empty responses), strips leaked chain-of-thought, and drops to a rule-based responder if all models fail.

See [server/architecture.md](server/architecture.md) for the full breakdown.

## Getting Started

**Prerequisites:** Python 3.10+, Bun or Node 18+, MongoDB (local or Atlas), and an [OpenRouter API key](https://openrouter.ai/keys).

### 1. Backend

```bash
cd server
python -m venv ../venv
source ../venv/bin/activate        # Windows: ..\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # add OPENROUTER_API_KEY, MONGODB_URL, SECRET_KEY
uvicorn api:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd client
cp .env.example .env.local         # NEXT_PUBLIC_API_URL=http://localhost:8000
bun install                        # or npm install
bun dev                            # or npm run dev
```

App: http://localhost:3000

### Optional: CLI

```bash
cd server
python main.py
```

## Project Structure

```
client/              Next.js app (pages: personas, surveys, interviews, reports)
server/
  agents/            Persona, memory, survey, interview, and insight agents
  routers/           FastAPI route modules
  auth/              JWT auth
  db/                MongoDB connection and Beanie models
  utils/             LLM client, normalizer, NLP, PDF exporter
  config/            Settings, archetypes, topic maps
```

## Testing

```bash
cd server
python test_pipeline.py            # end-to-end pipeline across domains
python test_persona_diversity.py   # persona diversity audit
python validation.py               # full validation suite
```

## License

Copyright © 2026 Abinash Das. All rights reserved. This code is viewable for portfolio purposes only and may not be used, copied, or modified without permission. See [LICENSE](LICENSE).
