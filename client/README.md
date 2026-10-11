# SynthaResearch — Next.js Web Client

The modern frontend application for the **Universal Synthetic User Research Platform** (SynthaResearch), built with **Next.js 16 (App Router)**, **React 19**, **TypeScript**, and **Tailwind CSS v4**.

Provides an intuitive, high-fidelity user interface for configuring product research workspaces, generating diverse synthetic personas, executing batch surveys, conducting live 1-on-1 interviews, and exporting executive research reports.

---

## Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org/) (App Router architecture)
- **UI Library**: [React 19](https://react.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Language**: TypeScript 5
- **Package Manager**: [Bun](https://bun.sh/) (or Node.js / npm)

---

## Application Structure & Views

### 1. Authentication (`/login` & `/register`)
- Clean user registration and sign-in interface.
- Built-in **DiceBear Avatar Picker** allowing users to select seeds and styles for their profile.
- Token management: Bearer token authorization in API requests, with automatic refresh token handling via HttpOnly cookies and response interceptors.

### 2. Workspace & Experiment Hub (`/`)
- Configure product parameters: Product Name, Description, Target Audience, and Research Objectives.
- One-click template presets (*FocusFlow AI*, *AuraWealth*, *NexusDev*, etc.) across varied domains (B2B SaaS, FinTech, HealthTech, Developer Tools, E-Commerce).
- Multi-experiment management: list all created experiments and switch the active workspace on the fly.

### 3. Synthetic Personas Roster (`/personas`)
- Generate customizable cohorts (e.g. 5 diverse personas) tailored to the active product.
- Rich persona dossiers displaying:
  - Demographics (age, gender, location, occupation, education, income)
  - Archetype and psychographic profile (MBTI, risk tolerance)
  - Current tool stack and primary pain points
  - Budget / Willingness-to-Pay and Churn triggers
  - Background narrative story

### 4. Survey Simulation & Matrix (`/surveys`)
- **AI-Suggested Questions**: Generate domain-relevant survey questions with one click.
- **Custom Question Builder**: Enter custom prompts and hypothesis tests.
- **Simultaneous Cohort Execution**: Watch all personas answer concurrently.
- Sentiment tags (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) and extracted key takeaways.
- **Matrix Grid View**: Toggle side-by-side comparison across personas and questions.

### 5. Live 1-on-1 Qualitative Interviews (`/interviews`)
- Select any persona to open a live conversational interview session.
- Real-time multi-turn chat powered by the backend `PersonaMemoryModule`.
- Persistent interview history and transcript inspection.

### 6. Executive Insights & PDF Reports (`/reports`)
- **Adoption Propensity Score (%)**: Visual score gauge measuring "Would use this product?".
- Sentiment breakdown (Positive, Neutral, Negative counts).
- Behavioral trends, cross-persona consensus, and polarization patterns.
- AI-synthesized executive summary and prioritized strategic recommendations.
- **Instant PDF Download & Inline Preview**: Streams generated PDF reports directly from the backend.

---

## Directory Reference

```text
client/
├── public/                 # Static assets and icons
├── src/
│   ├── app/                # Next.js App Router pages
│   │   ├── layout.tsx      # Root layout with AuthProvider & AppShell
│   │   ├── page.tsx        # Product Workspace & Setup
│   │   ├── login/          # User login page
│   │   ├── register/       # User registration page
│   │   ├── personas/       # Synthetic personas cohort page
│   │   ├── surveys/        # Multi-persona surveys & matrix page
│   │   ├── interviews/     # 1-on-1 live interview interface
│   │   ├── reports/        # Analytics, executive insights & PDF export
│   │   └── globals.css     # Tailwind CSS styles and custom styling
│   ├── components/         # Shared UI components
│   │   ├── AppShell.tsx    # Header, navigation container & auth guard
│   │   ├── Navigation.tsx  # Top navigation bar with active indicators
│   │   ├── Avatar.tsx      # SVG avatar renderer
│   │   └── AvatarPicker.tsx# Interactive avatar customizer modal
│   ├── config/             # Client configuration
│   │   └── env.ts          # Environment variables & API base URL
│   ├── lib/                # Core client utilities
│   │   ├── api.ts          # Typed REST API client with auto-refresh
│   │   ├── auth.ts         # Local storage token utilities
│   │   └── authContext.tsx # React Context provider for user state
│   └── types/              # TypeScript interfaces
│       └── api.ts          # Data models for personas, surveys, reports, auth
├── package.json            # Dependencies and scripts
└── tsconfig.json           # TypeScript configuration
```

---

## Environment Setup

Create `.env.local` in the `client/` directory (or copy from `.env.example`):

```env
# Backend FastAPI Server URL
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SERVER_URL=http://localhost:8000

# API Request Timeout (in milliseconds)
NEXT_PUBLIC_API_TIMEOUT_MS=120000

# Application Configuration
NEXT_PUBLIC_APP_NAME=SynthaResearch
NEXT_PUBLIC_APP_ENV=development
```

---

## Getting Started

### 1. Install Dependencies
```bash
bun install
# or
npm install
```

### 2. Run the Development Server
```bash
bun dev
# or
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Production Build
```bash
bun run build
bun start
# or
npm run build
npm start
```
