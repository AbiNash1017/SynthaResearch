# Universal Synthetic User Research Platform

An AI-powered synthetic user research platform that simulates human customer behavior, product opinions, friction points, and feature feedback across **any product or industry domain** (B2B SaaS, developer tools, fintech, health & wellness, e-commerce, consumer apps, edtech, hardware, and more).

Powered by **OpenRouter LLM**, allowing you to use any foundation model (OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, Meta Llama 3.3, DeepSeek, etc.) with both API key and model selection fully controlled via `.env`.

---

## Key Features

1. **Universal Product Experiment Workspace**
   - Define any product name, industry domain, product description, target audience, and research objectives.
   - Dynamic validation and storage in `data/experiment.json`.

2. **OpenRouter LLM Integration**
   - **Zero Hardcoded Models or Keys**: Both `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` are read directly from your `.env` file.
   - Works with any model available on OpenRouter (e.g. `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.3-70b-instruct`, `deepseek/deepseek-chat`, etc.).
   - Transparent configuration status and graceful fallback if keys are missing.

3. **Domain-Tailored Persona Generation (`PersonaGenerationAgent`)**
   - Dynamically creates diverse synthetic user personas specifically tailored to the active product and target market.
   - Each persona contains realistic demographics, custom archetypes, current tool stack, primary pain points, budget/willingness to pay, churn triggers, MBTI/psychological traits, and background narratives.

4. **Persona Memory & Consistency Module (`PersonaMemoryModule`)**
   - Personas maintain consistent opinions and remember prior conversation context across multi-turn interactions.
   - Inhabits the persona's traits, budget constraints, and skepticism/enthusiasm authentically.

5. **Dynamic Survey Mode (`SurveyAgent`)**
   - Suggests product-specific survey questions using OpenRouter LLM or accepts custom research questions.
   - Personas answer simultaneously in-character with sentiment classification (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) and key takeaway extraction.
   - Generates side-by-side comparison matrices in CLI and API.

6. **Interactive Live Interview Mode (`InterviewAgent`)**
   - Real-time, multi-turn 1-on-1 interview with any selected persona.
   - Personas give candid, nuanced feedback reflecting their background and product domain constraints.
   - Logs saved to `data/interview_logs.json`.

7. **Insight Extraction & Report Synthesis (`InsightExtractionAgent`)**
   - Synthesizes all empirical survey and interview data using OpenRouter LLM.
   - Produces executive summaries, product-market validation signals, emergent themes, behavioral cohort breakdowns, critical objections, and actionable product recommendations.
   - Exports reports to both structured **JSON** and multi-page **PDF** in `reports/`.

---

## Environment Setup

### 1. Configure OpenRouter in `.env`
Copy `.env.example` to `.env` (or edit `.env` directly) and specify your credentials:

```env
# OpenRouter LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

> [!NOTE]
> You can swap the model at any time simply by changing `OPENROUTER_MODEL` in `.env` (e.g., to `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.3-70b-instruct`, etc.). Neither the API key nor the model name is hardcoded.

### 2. Install Dependencies
```bash
# Windows
.\venv\Scripts\pip install -r requirements.txt

# Linux / macOS
pip install -r requirements.txt
```

---

## How to Run

### Option A: Interactive Terminal CLI (`main.py`)
```bash
python main.py
```
Menu options:
1. **Setup / Edit Experiment Workspace**: Define any product, audience, and objectives.
2. **Generate Synthetic Personas**: Generates personas tailored for your product.
3. **Run Multi-Persona Survey**: Get AI-suggested or custom questions answered by all personas.
4. **Start Interactive Interview**: Live chat with an individual persona.
5. **Generate Research & Insight Report**: Creates JSON and PDF research reports in `reports/`.
6. **Exit**.

### Option B: FastAPI Backend Server (`api.py`)
Run the server:
```bash
uvicorn api:app --reload --port 8000
```
Visit interactive API documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Key Endpoints:
- `GET /api/llm-config`: Check OpenRouter configuration status and active model.
- `POST /api/setup-experiment`: Define product, domain, audience, and objectives.
- `GET /api/experiment`: Retrieve current active experiment.
- `GET /api/suggest-questions`: AI-suggested survey questions for the active product.
- `POST /api/generate-personas`: Generate synthetic personas.
- `GET /api/personas`: Retrieve all generated personas and memory states.
- `POST /api/run-survey`: Run questions across all personas.
- `POST /api/interview`: 1-on-1 turn with a specific persona.
- `GET /api/generate-report`: Generate research insight JSON + PDF reports.

---

## Running Automated Tests

Run the end-to-end test suite across multiple product categories (B2B SaaS DevTools and IoT Consumer Tech):
```bash
python test_pipeline.py
```
