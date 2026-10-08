import {
  API_BASE,
  LLMConfig,
  Experiment,
  Persona,
  SurveyResults,
  InterviewSessionSummary,
  InterviewSessionDetail,
  AdoptionScoreData,
  ResearchReport,
} from "@/types/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    let errorDetail = "An error occurred";
    try {
      const errData = await res.json();
      errorDetail = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail || `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // System & Health
  checkHealth: () => fetchJson<{ status: string; system: string; llm_config: LLMConfig }>("/"),
  getLLMConfig: () => fetchJson<LLMConfig>("/api/llm-config"),

  // Experiment Workspace
  getExperiment: () => fetchJson<Experiment>("/api/experiment"),
  setupExperiment: (data: {
    product_name: string;
    product_description: string;
    target_audience: string;
    research_objectives: string[];
    industry_domain?: string;
  }) =>
    fetchJson<{ message: string; experiment: Experiment }>("/api/setup-experiment", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Personas
  listPersonas: () => fetchJson<{ count: number; personas: Persona[] }>("/api/personas"),
  generatePersonas: (count: number = 5) =>
    fetchJson<{ count: number; product: string; personas: Persona[] }>(
      `/api/generate-personas?count=${count}`,
      { method: "POST" }
    ),

  // Surveys
  suggestQuestions: (count: number = 3) =>
    fetchJson<{ product_name: string; suggested_questions: string[] }>(
      `/api/suggest-questions?count=${count}`
    ),
  runSurvey: (questions: string[]) =>
    fetchJson<SurveyResults>("/api/run-survey", {
      method: "POST",
      body: JSON.stringify({ questions }),
    }),
  getSurveyMatrix: () => fetchJson<any>("/api/survey-matrix"),

  // 1-on-1 Interactive Interviews
  listInterviews: () =>
    fetchJson<{ count: number; sessions: InterviewSessionSummary[] }>("/api/interviews"),
  getInterviewSession: (sessionId: string) =>
    fetchJson<InterviewSessionDetail>(`/api/interview/${sessionId}`),
  sendInterviewMessage: (data: {
    persona_id: string;
    user_message: string;
    session_id?: string;
  }) =>
    fetchJson<{
      session_id: string;
      persona_id: string;
      persona_name: string;
      archetype?: string;
      user_message: string;
      persona_response: string;
    }>("/api/interview", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  resetInterviews: () =>
    fetchJson<{ message: string }>("/api/interview/reset", {
      method: "POST",
    }),

  // Analytics & Reports
  getAdoptionScore: () => fetchJson<AdoptionScoreData>("/api/adoption-score"),
  generateReport: () => fetchJson<ResearchReport>("/api/generate-report"),
};
