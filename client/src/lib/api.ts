import {
  API_BASE,
  LLMConfig,
  Experiment,
  Persona,
  SurveyResults,
  SurveyMatrix,
  InterviewSessionSummary,
  InterviewSessionDetail,
  AdoptionScoreData,
  ResearchReport,
  AuthResponse,
  User,
} from "@/types/api";
import { ENV } from "@/config/env";
import { getStoredToken, setStoredToken, clearStoredAuth } from "./auth";

const DEFAULT_TIMEOUT_MS = ENV.API_TIMEOUT_MS;

interface FetchOptions extends RequestInit {
  timeoutMs?: number;
  skipAuth?: boolean;
}

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

async function fetchJson<T>(url: string, options?: FetchOptions): Promise<T> {
  const timeoutMs = options?.timeoutMs || DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options?.headers as Record<string, string>) || {}),
  };

  if (!options?.skipAuth) {
    const token = getStoredToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  try {
    const res = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
      signal: controller.signal,
      credentials: "include", // Send HttpOnly refresh_token cookie
    });

    clearTimeout(timeoutId);

    // If 401 Unauthorized and not already an auth route
    if (res.status === 401 && !url.startsWith("/auth/")) {
      const refreshedToken = await handleTokenRefresh();
      if (refreshedToken) {
        // Retry original request with fresh token
        headers["Authorization"] = `Bearer ${refreshedToken}`;
        const retryRes = await fetch(`${API_BASE}${url}`, {
          ...options,
          headers,
          credentials: "include",
        });
        if (retryRes.ok) {
          return retryRes.json() as Promise<T>;
        }
      } else {
        clearStoredAuth();
        if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
          // eslint-disable-next-line @next/next/no-location-assign-relative-destination
          window.location.href = "/login";
        }
      }
    }

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
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`Request timed out after ${timeoutMs / 1000} seconds. Please try again.`);
    }
    throw error;
  }
}

async function handleTokenRefresh(): Promise<string | null> {
  if (isRefreshing) {
    return new Promise((resolve) => {
      subscribeTokenRefresh((token) => resolve(token));
    });
  }

  isRefreshing = true;

  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    if (!res.ok) {
      isRefreshing = false;
      return null;
    }

    const data = await res.json();
    const newToken = data.access_token;
    if (newToken) {
      setStoredToken(newToken);
      onRefreshed(newToken);
      isRefreshing = false;
      return newToken;
    }
    isRefreshing = false;
    return null;
  } catch {
    isRefreshing = false;
    return null;
  }
}

export const api = {
  // Auth Services
  auth: {
    login: (credentials: { email: string; password: string }) =>
      fetchJson<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
        skipAuth: true,
      }),
    register: (data: { email: string; password: string; full_name?: string }) =>
      fetchJson<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
        skipAuth: true,
      }),
    getMe: () => fetchJson<User>("/auth/me"),
    logout: () =>
      fetchJson<{ message: string }>("/auth/logout", {
        method: "POST",
      }),
  },

  // System & Health
  checkHealth: () =>
    fetchJson<{ status: string; system: string; llm_config: LLMConfig }>("/", {
      skipAuth: true,
      timeoutMs: 8000,
    }),
  getLLMConfig: () =>
    fetchJson<LLMConfig>("/api/llm-config", {
      skipAuth: true,
      timeoutMs: 8000,
    }),

  // Experiment Workspace
  getExperiment: () => fetchJson<Experiment>("/api/experiment"),
  listExperiments: () =>
    fetchJson<{ count: number; experiments: Experiment[] }>("/api/experiments"),
  activateExperiment: (experimentId: string) =>
    fetchJson<{ message: string }>(`/api/experiment/${experimentId}/activate`, {
      method: "POST",
    }),
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
      timeoutMs: 120000,
    }),

  // Personas
  listPersonas: (experimentId?: string) =>
    fetchJson<{ count: number; personas: Persona[] }>(
      experimentId
        ? `/api/personas?experiment_id=${encodeURIComponent(experimentId)}`
        : "/api/personas"
    ),
  generatePersonas: (count: number = 5) =>
    fetchJson<{ count: number; product: string; personas: Persona[] }>(
      `/api/generate-personas?count=${count}`,
      { method: "POST", timeoutMs: 300000 }
    ),

  // Surveys
  suggestQuestions: (count: number = 3) =>
    fetchJson<{ product_name: string; suggested_questions: string[] }>(
      `/api/suggest-questions?count=${count}`,
      { timeoutMs: 90000 }
    ),
  runSurvey: (questions: string[]) =>
    fetchJson<SurveyResults>("/api/run-survey", {
      method: "POST",
      body: JSON.stringify({ questions }),
      timeoutMs: 300000,
    }),
  getSurveyMatrix: () => fetchJson<SurveyMatrix>("/api/survey-matrix"),

  // 1-on-1 Interactive Interviews
  listInterviews: (experimentId?: string) =>
    fetchJson<{ count: number; sessions: InterviewSessionSummary[] }>(
      experimentId
        ? `/api/interviews?experiment_id=${encodeURIComponent(experimentId)}`
        : "/api/interviews"
    ),
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
      timeoutMs: 120000,
    }),
  resetInterviews: () =>
    fetchJson<{ message: string }>("/api/interview/reset", {
      method: "POST",
    }),

  // Analytics & Reports
  getAdoptionScore: () => fetchJson<AdoptionScoreData>("/api/adoption-score"),
  generateReport: () =>
    fetchJson<ResearchReport>("/api/generate-report", {
      timeoutMs: 300000,
    }),
  getLatestReport: () =>
    fetchJson<{ report: ResearchReport | null }>("/api/reports/latest"),
  listReports: (experimentId?: string) =>
    fetchJson<{ count: number; reports: ResearchReport[] }>(
      experimentId
        ? `/api/reports?experiment_id=${encodeURIComponent(experimentId)}`
        : "/api/reports"
    ),
  downloadReportPdfBlob: async (reportId?: string): Promise<Blob> => {
    const token = getStoredToken();
    const endpoint = reportId ? `/api/reports/${reportId}/pdf` : "/api/reports/latest/pdf";
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
    if (!res.ok) {
      let errText = "Failed to load PDF report";
      try {
        const data = await res.json();
        errText = data.detail || errText;
      } catch {
        // use default
      }
      throw new Error(errText);
    }
    return res.blob();
  },
  getReportPdfDirectUrl: (reportId?: string): string => {
    const token = getStoredToken();
    const endpoint = reportId ? `/api/reports/${reportId}/pdf` : "/api/reports/latest/pdf";
    return token ? `${API_BASE}${endpoint}?token=${encodeURIComponent(token)}` : `${API_BASE}${endpoint}`;
  },
};
