# SynthaResearch — Run Instructions

Step-by-step guide for starting both the backend (FastAPI + MongoDB) and frontend (Next.js) services for the Universal Synthetic User Research Platform.

---

## Prerequisites

1. **Python 3.10+** (with virtual environment recommended)
2. **MongoDB** installed and running locally (`mongodb://localhost:27017`) or a free [MongoDB Atlas](https://www.mongodb.com/atlas) cloud connection string.
3. **Bun** (recommended) or **Node.js (v18+)**
4. **OpenRouter API Key** (from [openrouter.ai](https://openrouter.ai/keys))

---

## 1. Database Setup (MongoDB)

Ensure MongoDB is running prior to starting the FastAPI backend:

- **Local Windows Service**: Check that MongoDB is started in Windows Services or run:
  ```powershell
  net start MongoDB
  ```
- **Local Docker (alternative)**:
  ```bash
  docker run -d -p 27017:27017 --name mongodb mongo:latest
  ```
- **MongoDB Atlas**: Use your connection string directly in `server/.env`.

---

## 2. Backend Server Setup (FastAPI)

### Step 1: Navigate to the server folder
```bash
cd server
```

### Step 2: Configure Environment Variables
Create or verify your `server/.env` file:
```env
# OpenRouter LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=syntharesearch

# JWT Secret Key (generate one using the command below)
SECRET_KEY=your_super_secret_jwt_key_here_change_for_production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

> [!TIP]
> To generate a secure random `SECRET_KEY`, run:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### Step 3: Install Dependencies
```bash
# Recommended: activate virtual environment
# Windows:
..\venv\Scripts\activate
# Linux/macOS:
source ../venv/bin/activate

pip install -r requirements.txt
```

### Step 4: Start the FastAPI Server
```bash
uvicorn api:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 3. Frontend Client Setup (Next.js)

### Step 1: Navigate to the client folder (in a new terminal)
```bash
cd client
```

### Step 2: Verify Environment Variables
Verify or create `client/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SERVER_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT_MS=120000
NEXT_PUBLIC_APP_NAME=SynthaResearch
NEXT_PUBLIC_APP_ENV=development
```

### Step 3: Install Dependencies
```bash
bun install
# or: npm install
```

### Step 4: Start the Development Server
```bash
bun dev
# or: npm run dev
```

### Step 5: Open the Web UI
Navigate to [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 4. End-to-End User Research Simulation Workflow

1. **Authentication (`/register` & `/login`)**:
   - Create an account or sign in.
   - Choose a unique avatar seed and gender styling from the interactive avatar selector.
   - Sessions are secured with JWT access tokens and HttpOnly refresh cookies.

2. **Workspace & Experiment Setup (`/`)**:
   - Choose a preset template (*FocusFlow AI*, *AuraWealth*, *NexusDev*, etc.) or enter custom product details:
     - Product Name & Domain (B2B SaaS, FinTech, HealthTech, etc.)
     - Core Value Proposition & Description
     - Target Audience & Research Objectives
   - Click **Save & Normalize Experiment** to activate the workspace.

3. **Synthetic Persona Cohort (`/personas`)**:
   - Select desired cohort size (e.g. 5 personas) and click **Generate New Cohort**.
   - Browse synthetic user cards and click to view rich dossiers (demographics, tool stacks, pain points, willingness-to-pay, churn triggers, and MBTI traits).

4. **Surveys & Sentiment Matrix (`/surveys`)**:
   - Click **AI Suggest Questions** to auto-generate questions tailored to your research objectives, or type custom questions.
   - Click **Run Cohort Survey** to simulate answers across all personas simultaneously.
   - Inspect persona responses, sentiments (`POSITIVE`, `NEUTRAL`, `NEGATIVE`), key takeaways, and toggle the **Matrix Comparison View**.

5. **Live 1-on-1 Qualitative Interviews (`/interviews`)**:
   - Pick any persona from your roster to launch an interactive interview session.
   - Ask clarifying follow-ups, challenge their feedback, or probe pricing thresholds.
   - Personas answer in-character with persistent conversational memory across turns.

6. **Analytics & Executive Report (`/reports`)**:
   - Review the **Adoption Propensity Score (%)** ("Would use this product?") and sentiment distribution.
   - Click **Generate Executive Report** to synthesize themes, objections, and prioritized product recommendations.
   - Click **Download PDF** to export a multi-page, formatted executive summary document.

---

## 5. Alternative: Terminal CLI Mode

For headless or terminal-only usage, run the standalone CLI tool from `server/`:
```bash
cd server
python main.py
```
This presents an interactive menu to set up experiments, generate personas, run surveys, interview users, and export reports directly to `reports/` and `data/`.