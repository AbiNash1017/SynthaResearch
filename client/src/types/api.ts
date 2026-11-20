import { API_BASE } from "@/config/env";
export { API_BASE };

export interface LLMConfig {
  configured: boolean;
  model: string | null;
  has_api_key: boolean;
  base_url?: string;
  // Backward compatibility aliases
  openrouter_configured?: boolean;
  api_key_present?: boolean;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_seed?: string;
  avatar_gender?: string;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Experiment {
  id?: string;
  product_name: string;
  product_description: string;
  target_audience: string;
  research_objectives: string[];
  industry_domain?: string;
  is_active?: boolean;
  created_at?: string;
  _domain_profile?: Record<string, unknown>;
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
    conversation_history: Record<string, unknown>[];
    established_opinions: Record<string, unknown>;
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

export interface SurveyMatrix {
  questions: string[];
  personas: Array<{ id: string; name: string; archetype: string }>;
  rows: SurveyMatrixRow[];
  total_respondents?: number;
}

export interface SurveyResults {
  survey_id: string;
  product_name: string;
  questions: string[];
  responses: PersonaSurveyResponse[];
  created_at: string;
  matrix?: SurveyMatrix;
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

export interface SegmentAdoptionBreakdown {
  segment: string;
  score: number;
  stance: string;
  sample_size?: number;
  reasoning: string;
}

export interface WouldUseScore {
  overall_score: number;
  score_label: string;
  summary_reasoning?: string;
  segment_breakdown: SegmentAdoptionBreakdown[];
}

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
}

export interface AgreementPatterns {
  consensus: string[];
  polarization: string[];
}

export interface BehavioralTrend {
  group: string;
  finding: string;
}

export interface ThemeCluster {
  name: string;
  category: string;
  mention_count: number;
  sentiment: "positive" | "neutral" | "negative" | string;
  summary?: string;
  keywords?: string[];
}

export interface KeyPersonaQuote {
  quote: string;
  persona_name: string;
  archetype: string;
  topic?: string;
  sentiment: "positive" | "neutral" | "negative" | string;
}

export interface ResponseHighlight {
  topic: string;
  highlight: string;
  respondent_name: string;
  archetype: string;
  source: string;
  sentiment: "positive" | "neutral" | "negative" | string;
}

export interface PersonaProfile {
  id?: string;
  name: string;
  archetype: string;
  age?: number;
  gender?: string;
  occupation?: string;
  location?: string;
  personality_traits?: string[];
  pain_points?: string;
  willingness_to_pay?: string;
  current_tools?: string;
  churn_triggers?: string;
}

export interface PersonaBreakdownItem {
  id?: string;
  name: string;
  archetype: string;
  key_takeaway: string;
}

export interface AdoptionScoreData {
  product_name?: string;
  overall_score?: number;
  score_label?: string;
  summary_reasoning?: string;
  adoption_score?: number;
  sentiment_label?: string;
  total_personas?: number;
  breakdown?: {
    would_use_count?: number;
    would_not_use_count?: number;
    positive_sentiment_count?: number;
    neutral_sentiment_count?: number;
    negative_sentiment_count?: number;
    total_responses?: number;
  };
  segment_breakdown?: SegmentAdoptionBreakdown[] | Record<
    string,
    {
      total?: number;
      positive?: number;
      negative?: number;
      percentage?: number;
    }
  >;
}

export interface ResearchReport {
  id?: string;
  report_date: string;
  product: string;
  persona_count: number;
  survey_questions_asked: number;
  interview_sessions_count: number;
  executive_summary?: string;

  // Rich OpenRouter synthesis schema
  would_use_score?: WouldUseScore;
  themes?: string[];
  theme_clusters?: ThemeCluster[];
  key_persona_quotes?: KeyPersonaQuote[];
  response_highlights?: ResponseHighlight[];
  persona_profiles?: PersonaProfile[];
  agreement_patterns?: AgreementPatterns;
  sentiment_distribution?: SentimentDistribution;
  sentiment_analysis?: string;
  behavioral_trends?: BehavioralTrend[];
  critical_objections?: string[];
  top_insights?: string[];
  per_persona_breakdown?: PersonaBreakdownItem[];

  // Legacy fields
  key_findings?: string[];
  sentiment_breakdown?: SentimentDistribution;
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
