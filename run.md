# SynthaResearch — Run Instructions

Comprehensive instructions for starting both the backend (FastAPI) and frontend (Next.js) services for the Universal Synthetic User Research Platform.

---

## Prerequisites

1. **Python 3.10+** (with virtual environment recommended)
2. **Bun** or **Node.js (v18+)**
3. **OpenRouter API Key** configured in `server/.env`

---

## 1. Backend Server Setup (FastAPI)

### Step 1: Navigate to the server folder
```bash
cd server
```

### Step 2: Configure Environment Variables
Verify your `.env` file contains your OpenRouter API key and desired model:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### Step 3: Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### Step 4: Start the FastAPI Server
```bash
uvicorn api:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

---

## 2. Frontend Client Setup (Next.js)

### Step 1: Navigate to the client folder (in a new terminal)
```bash
cd client
```

### Step 2: Install Dependencies (if not already done)
```bash
bun install
# or: npm install
```

### Step 3: Start the Development Server
```bash
bun dev
# or: npm run dev
```

### Step 4: Open the Web UI
Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

---

## 3. Quick Simulation Workflow

1. **Workspace & Setup (`/`)**:
   - Choose a preset template (*FocusFlow AI*, *AuraWealth*, etc.) or enter your product details and research goals.
   - Click **Save & Normalize Experiment**.

2. **Synthetic Personas (`/personas`)**:
   - Select cohort size (e.g., 5 personas) and click **Generate New Cohort**.
   - Browse the generated user personas and click on any card to view their deep dossier (MBTI, churn triggers, price sensitivity).

3. **Surveys & Matrix (`/surveys`)**:
   - Use **AI Suggest Questions** or type custom research questions.
   - Click **Run Cohort Survey** to simulate answers across all personas.
   - Toggle between the **Matrix Grid View** and **Respondent Cards**.

4. **Live 1-on-1 Qualitative Interviews (`/interviews`)**:
   - Select any persona from the roster and ask questions in real-time.
   - Persona replies leverage continuous memory and behavioral traits.

5. **Analytics & Reports (`/reports`)**:
   - Review the **Adoption Propensity Score (%)** and sentiment breakdown.
   - Click **Generate Executive Report** to generate the executive synthesis and export the PDF report.


secret key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```