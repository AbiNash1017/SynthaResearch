"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import { Experiment, SurveyResults, PersonaSurveyResponse } from "@/types/api";
import {
  ClipboardList,
  Sparkles,
  Play,
  ArrowRight,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Smile,
  Meh,
  Frown,
} from "lucide-react";
import Link from "next/link";

export default function SurveysPage() {
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [questions, setQuestions] = useState<string[]>([
    "Would you adopt this product into your daily routine? Why or why not?",
    "What is the single biggest friction or concern preventing you from paying?",
    "Which existing software or alternative would this most likely replace?",
  ]);
  const [newQuestion, setNewQuestion] = useState("");
  const [surveyResults, setSurveyResults] = useState<SurveyResults | null>(null);
  const [, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [viewMode, setViewMode] = useState<"matrix" | "cards">("cards");

  function formatAnswerText(text: string): string {
    if (!text) return "";
    let clean = text.trim();
    if (clean.startsWith("{") && clean.includes("answer")) {
      try {
        const match = clean.match(/['"]answer['"]\s*:\s*['"]([\s\S]*?)['"]\s*\}/);
        if (match && match[1]) {
          clean = match[1];
        }
      } catch {
        // fallback
      }
    }
    return clean;
  }

  useEffect(() => {
    let ignore = false;
    Promise.allSettled([
      api.getExperiment().catch(() => null),
      api.getSurveyMatrix().catch(() => null),
    ]).then(([expRes, matrixRes]) => {
      if (ignore) return;
      const exp = expRes.status === "fulfilled" ? expRes.value : null;
      if (exp) setActiveExp(exp);

      const matrix = matrixRes.status === "fulfilled" ? matrixRes.value : null;
      if (matrix && matrix.questions) {
        // Reconstruct respondent cards from matrix if available
        let reconstructedResponses: PersonaSurveyResponse[] = [];

        if (matrix.personas && matrix.personas.length > 0 && matrix.rows) {
          reconstructedResponses = matrix.personas.map((p) => {
            const answers = (matrix.rows || []).map((row) => {
              const resp = row.persona_responses?.[p.id];
              return {
                question: row.question,
                answer: resp?.answer || "",
                sentiment: (resp?.sentiment as "positive" | "neutral" | "negative") || "neutral",
              };
            });
            return {
              persona_id: p.id,
              persona_name: p.name,
              archetype: p.archetype,
              answers,
              timestamp: new Date().toISOString(),
            };
          });
        }

        setSurveyResults({
          survey_id: "active",
          product_name: exp?.product_name || "Active Product",
          questions: matrix.questions as string[],
          responses: reconstructedResponses,
          created_at: new Date().toISOString(),
          matrix: matrix,
        });
      }
      setLoading(false);
    });
    return () => {
      ignore = true;
    };
  }, []);

  async function handleSuggestQuestions() {
    setSuggesting(true);
    setStatusMsg(null);
    try {
      const res = await api.suggestQuestions(3);
      if (res.suggested_questions && res.suggested_questions.length > 0) {
        setQuestions((prev) => {
          const combined = [...prev, ...res.suggested_questions];
          return Array.from(new Set(combined));
        });
        setStatusMsg({
          type: "success",
          text: `Added ${res.suggested_questions.length} AI-suggested questions tailored to ${res.product_name}!`,
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to generate AI survey questions.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setSuggesting(false);
    }
  }

  function addQuestion() {
    if (!newQuestion.trim()) return;
    setQuestions([...questions, newQuestion.trim()]);
    setNewQuestion("");
  }

  function removeQuestion(idx: number) {
    setQuestions(questions.filter((_, i) => i !== idx));
  }

  async function handleRunSurvey() {
    if (questions.length === 0) {
      setStatusMsg({
        type: "error",
        text: "Please add at least one question before deploying the survey.",
      });
      return;
    }

    setRunning(true);
    setStatusMsg(null);
    try {
      const res = await api.runSurvey(questions);
      setSurveyResults(res);
      setStatusMsg({
        type: "success",
        text: `Survey completed! Gathered responses from ${res.responses?.length || 0} synthetic respondents across ${res.questions?.length || 0} questions.`,
      });
    } catch (err: unknown) {
      // Check if backend actually completed and saved survey matrix to MongoDB
      try {
        const matrix = await api.getSurveyMatrix();
        if (matrix && (matrix.total_respondents ?? matrix.rows?.length ?? 0) > 0) {
          const count = matrix.total_respondents ?? matrix.rows?.length ?? 0;
          setStatusMsg({
            type: "success",
            text: `Survey simulation completed and saved in database! (${count} respondents recorded)`,
          });
          return;
        }
      } catch {
        // Fall back to original error
      }
      const msg = err instanceof Error ? err.message : "Failed to execute survey simulation. Check if personas are generated.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setRunning(false);
    }
  }

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Smile className="w-3 h-3" /> Positive
          </span>
        );
      case "negative":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
            <Frown className="w-3 h-3" /> Negative
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
            <Meh className="w-3 h-3" /> Neutral
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        title="Surveys & Cross-Persona Matrix"
        subtitle={
          activeExp
            ? `Deploy structured questionnaires to all synthetic users for "${activeExp.product_name}"`
            : "Deploy multi-persona structured surveys and compare responses side-by-side"
        }
        actions={
          <div className="flex items-center gap-3">
            <Link
              href="/interviews"
              className="px-4 py-2 bg-[#728156] hover:bg-[#5B6845] text-white text-sm font-semibold rounded-xl shadow-xs flex items-center gap-2 transition-all"
            >
              <span>Next: 1-on-1 Interviews</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        }
      />

      <main className="p-8 max-w-7xl w-full mx-auto space-y-8">
        {/* Status notification */}
        {statusMsg && (
          <div
            className={`p-4 rounded-2xl flex items-center gap-3 transition-all ${
              statusMsg.type === "success"
                ? "bg-[#E7F5DC] text-[#2D3522] border border-[#CFE1B9]"
                : "bg-rose-50 text-rose-900 border border-rose-200"
            }`}
          >
            {statusMsg.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-[#728156] shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            )}
            <p className="text-sm font-medium">{statusMsg.text}</p>
          </div>
        )}

        {/* Survey Builder Card */}
        <section className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/60 shadow-xs space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-2 border-b border-[#F4F7F4]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center">
                <ClipboardList className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#2D3522]">
                  Survey Question Questionnaire ({questions.length})
                </h2>
                <p className="text-xs text-[#728156]">
                  Simulates full cohort answering simultaneously with individual personality bias.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleSuggestQuestions}
                disabled={suggesting}
                className="px-3.5 py-2 bg-[#E7F5DC] hover:bg-[#CFE1B9] text-[#465135] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {suggesting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-[#728156]" />
                )}
                <span>AI Suggest Questions</span>
              </button>

              <button
                onClick={handleRunSurvey}
                disabled={running}
                className="px-5 py-2 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-bold shadow-xs hover:shadow-md transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {running ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Surveying Personas...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run Cohort Survey</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Questions list */}
          <div className="space-y-2.5">
            {questions.map((q, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between gap-3 p-3.5 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/70 group hover:border-[#98A77C] transition-all"
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="w-6 h-6 rounded-lg bg-[#E7F5DC] text-[#728156] text-xs font-bold flex items-center justify-center shrink-0 font-mono">
                    Q{idx + 1}
                  </span>
                  <span className="text-sm text-[#2D3522] font-medium leading-relaxed">
                    {q}
                  </span>
                </div>
                <button
                  onClick={() => removeQuestion(idx)}
                  className="p-1.5 text-[#88976C] hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                  title="Remove question"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Add custom question */}
          <div className="flex gap-2">
            <input
              type="text"
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addQuestion();
                }
              }}
              placeholder="Type a research question to ask all personas (e.g., 'What would make you cancel after 1 month?')..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522]"
            />
            <button
              onClick={addQuestion}
              className="px-4 py-2.5 bg-[#728156] hover:bg-[#5B6845] text-white font-semibold text-xs rounded-xl flex items-center gap-1.5 transition-all shadow-xs"
            >
              <Plus className="w-4 h-4" />
              <span>Add Question</span>
            </button>
          </div>
        </section>

        {/* Results Section */}
        {surveyResults && (
          <section className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/60 shadow-xs space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-2 border-b border-[#F4F7F4]">
              <div>
                <h3 className="text-lg font-bold text-[#2D3522]">
                  Survey Results & Cross-Persona Matrix
                </h3>
                <p className="text-xs text-[#728156] mt-0.5">
                  Comparison matrix of all respondents side-by-side with automatic sentiment classification.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#728156] text-white shadow-xs">
                  Respondent Cards
                </span>
              </div>
            </div>

            {/* Matrix View (fallback if set) */}
            {viewMode === "matrix" && surveyResults.matrix && (
              <div className="overflow-x-auto rounded-2xl border border-[#CFE1B9]/70">
                <table className="w-full border-collapse text-left text-xs">
                  <thead>
                    <tr className="bg-[#E7F5DC] text-[#2D3522] border-b border-[#CFE1B9]">
                      <th className="p-4 font-bold w-64 min-w-[240px] sticky left-0 bg-[#E7F5DC] z-10 shadow-xs">
                        Survey Question
                      </th>
                      {surveyResults.matrix.personas?.map((p) => (
                        <th
                          key={p.id}
                          className="p-4 font-bold min-w-[260px] border-l border-[#CFE1B9]/60"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-[#2D3522]">{p.name}</span>
                            <span className="text-[10px] font-normal px-2 py-0.5 rounded-full bg-white text-[#728156]">
                              {p.archetype}
                            </span>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#CFE1B9]/50">
                    {surveyResults.matrix.rows?.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-[#F8FAF7]/80 transition-colors">
                        <td className="p-4 font-semibold text-[#2D3522] bg-[#FAFDF7] sticky left-0 z-10 border-r border-[#CFE1B9]/60 align-top shadow-xs">
                          <span className="text-[10px] font-mono text-[#728156] block mb-1">
                            Q{row.question_index + 1}
                          </span>
                          {row.question}
                        </td>
                        {surveyResults.matrix?.personas?.map((p) => {
                          const answerData = row.persona_responses?.[p.id];
                          return (
                            <td
                              key={p.id}
                              className="p-4 align-top border-l border-[#CFE1B9]/40 space-y-2 bg-white"
                            >
                              {answerData ? (
                                <>
                                  <div className="flex items-center justify-between">
                                    {getSentimentBadge(answerData.sentiment)}
                                  </div>
                                  <p className="text-xs text-[#2D3522] leading-relaxed">
                                    &ldquo;{formatAnswerText(answerData.answer)}&rdquo;
                                  </p>
                                </>
                              ) : (
                                <span className="text-[#88976C] italic text-[11px]">
                                  No response
                                </span>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Respondent Cards View */}
            {viewMode === "cards" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {surveyResults.responses?.map((resp) => (
                  <div
                    key={resp.persona_id}
                    className="p-5 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/70 space-y-4 hover:border-[#98A77C] transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-bold text-sm text-[#2D3522]">
                          {resp.persona_name}
                        </h4>
                        <span className="text-[11px] text-[#728156] font-medium">
                          {resp.archetype}
                        </span>
                      </div>
                      <Link
                        href={`/interviews?persona=${resp.persona_id}`}
                        className="text-[10px] font-bold text-[#728156] hover:text-[#465135] bg-[#E7F5DC] px-2 py-1 rounded-md flex items-center gap-1"
                      >
                        Interview <ArrowRight className="w-2.5 h-2.5" />
                      </Link>
                    </div>

                    <div className="space-y-3 pt-2 border-t border-[#CFE1B9]/50">
                      {resp.answers?.map((ans, aIdx) => (
                        <div key={aIdx} className="space-y-1">
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="font-semibold text-[#5B6845] line-clamp-1">
                              Q{aIdx + 1}: {ans.question}
                            </span>
                            {getSentimentBadge(ans.sentiment)}
                          </div>
                          <p className="text-xs text-[#2D3522] italic bg-white p-2.5 rounded-xl border border-[#CFE1B9]/40 leading-relaxed">
                            &ldquo;{formatAnswerText(ans.answer)}&rdquo;
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
