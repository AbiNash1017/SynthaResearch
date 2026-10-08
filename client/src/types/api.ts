export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface LLMConfig {
  openrouter_configured: boolean;
  model: string;
  api_key_present: boolean;
}

export interface Experiment {
  product_name: string;
  product_description: string;
  target_audience: string;
  research_objectives: string[];
  industry_domain?: string;
  created_at?: string;
  _domain_profile?: any;
}

export interface Persona {
  id: string;
  name: string;
  age: number;
  gender: string;
  occupation: string;
  location: string;
  income_bracket?: string;
  education?: string;
  archetype: string;
  personality_traits: string[];
  behavioral_patterns: {
    current_tools: string;
    usage_frequency: string;
    primary_pain_points: string;
    willingness_to_pay: string;
    churn_triggers: string;
    feature_priorities: string;
  };
  psychological_profile: {
    mbti: string;
    risk_tolerance: string;
    motivation_type: string;
    decision_style: string;
  };
  background_story: string;
  opinion_seeds: {
    price_sensitivity: number;
    tech_comfort: number;
    openness_to_change: number;
    overall_sentiment_bias: number;
  };
  memory?: {
    conversation_history: any[];
    established_opinions: Record<string, any>;
    last_updated: string;
  };
}

export interface SurveyAnswer {
  question: string;
  answer: string;
  sentiment: "positive" | "neutral" | "negative";
  concerns?: string[];
  would_use?: boolean;
}

export interface PersonaSurveyResponse {
  persona_id: string;
  persona_name: string;
  archetype: string;
  answers: SurveyAnswer[];
  timestamp: string;
}

export interface SurveyMatrixRow {
  question_index: number;
  question: string;
  persona_responses: Record<
    string,
    {
      name: string;
      archetype: string;
      answer: string;
      sentiment: string;
    }
  >;
}

export interface SurveyResults {
  survey_id: string;
  product_name: string;
  questions: string[];
  responses: PersonaSurveyResponse[];
  created_at: string;
  matrix?: {
    questions: string[];
    personas: Array<{ id: string; name: string; archetype: string }>;
    rows: SurveyMatrixRow[];
  };
}

export interface InterviewTurn {
  turn: number;
  user_message: string;
  persona_response: string;
  timestamp: string;
}

export interface InterviewSessionSummary {
  session_id: string;
  persona_id: string;
  persona_name: string;
  archetype: string;
  turns_count: number;
  session_started: string;
}

export interface InterviewSessionDetail {
  session_id: string;
  product_name: string;
  persona_id: string;
  persona_name: string;
  archetype: string;
  turns: InterviewTurn[];
  session_started: string;
}

export interface AdoptionScoreData {
  product_name: string;
  adoption_score: number;
  sentiment_label: string;
  total_personas: number;
  breakdown: {
    would_use_count: number;
    would_not_use_count: number;
    positive_sentiment_count: number;
    neutral_sentiment_count: number;
    negative_sentiment_count: number;
  };
  segment_breakdown: Record<
    string,
    {
      total: number;
      positive: number;
      negative: number;
      percentage: number;
    }
  >;
}

export interface ResearchReport {
  report_date: string;
  product: string;
  persona_count: number;
  survey_questions_asked: number;
  interview_sessions_count: number;
  executive_summary?: string;
  key_findings?: string[];
  sentiment_breakdown?: {
    positive: number;
    neutral: number;
    negative: number;
  };
  pain_points?: string[];
  feature_requests?: string[];
  churn_risks?: string[];
  would_use_propensity_score?: number;
  pricing_insights?: string;
  nlp_thematic_patterns?: string[];
  consensus_areas?: string[];
  divergence_areas?: string[];
  recommendations?: string[];
}
