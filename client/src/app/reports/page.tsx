"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import { AdoptionScoreData, ResearchReport, Experiment } from "@/types/api";
import {
  BarChart3,
  Sparkles,
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  ShieldAlert,
  Coins,
  RefreshCw,
  FileCheck,
  Award,
} from "lucide-react";

export default function ReportsPage() {
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [adoptionData, setAdoptionData] = useState<AdoptionScoreData | null>(null);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [expRes, adoptRes] = await Promise.allSettled([
        api.getExperiment(),
        api.getAdoptionScore(),
      ]);

      if (expRes.status === "fulfilled") setActiveExp(expRes.value);
      if (adoptRes.status === "fulfilled") setAdoptionData(adoptRes.value);
    } catch {
      // Continue
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateReport() {
    setGeneratingReport(true);
    setStatusMsg(null);
    try {
      const rep = await api.generateReport();
      setReport(rep);
      // Re-fetch adoption score as well
      const adopt = await api.getAdoptionScore().catch(() => null);
      if (adopt) setAdoptionData(adopt);

      setStatusMsg({
        type: "success",
        text: `Full research report generated and synthesized! PDF exported to backend reports directory.`,
      });
    } catch (err: any) {
      setStatusMsg({
        type: "error",
        text: err.message || "Failed to generate research report. Check if personas and survey responses exist.",
      });
    } finally {
      setGeneratingReport(false);
    }
  }

  const score = adoptionData?.adoption_score || 0;
  const scorePercent = Math.round(score * 100);

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        title="Analytics & Executive Synthesis"
        subtitle={
          activeExp
            ? `Deep propensity scoring, segment breakdown, and strategic insights for "${activeExp.product_name}"`
            : "Propensity scoring and executive summary report generation"
        }
        actions={
          <button
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="px-5 py-2.5 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-bold shadow-xs hover:shadow-md transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {generatingReport ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Synthesizing Deep Report...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-[#E7F5DC]" />
                <span>Generate Executive Report</span>
              </>
            )}
          </button>
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

        {/* Adoption Propensity Headline KPI Banner */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Score Dial Card */}
          <div className="bg-gradient-to-br from-[#E7F5DC] via-[#CFE1B9]/60 to-[#B6C99B]/40 rounded-3xl p-7 border border-[#CFE1B9] shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#465135]">
                Adoption Propensity Score
              </span>
              <Award className="w-5 h-5 text-[#728156]" />
            </div>

            <div className="my-4 flex items-baseline gap-3">
              <span className="text-5xl font-black text-[#2D3522] tracking-tight">
                {scorePercent}%
              </span>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-white/80 text-[#465135] shadow-xs capitalize">
                {adoptionData?.sentiment_label || "Evaluated"}
              </span>
            </div>

            <div className="space-y-1.5">
              <div className="w-full bg-white/70 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-[#728156] h-full transition-all duration-700"
                  style={{ width: `${scorePercent}%` }}
                />
              </div>
              <p className="text-[11px] text-[#5B6845] font-medium">
                Calculated from {adoptionData?.total_personas || 0} synthetic persona sentiment distributions
              </p>
            </div>
          </div>

          {/* Persona Sentiment Distribution */}
          <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/70 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#728156]">
                Response Sentiment Split
              </span>
              <TrendingUp className="w-4 h-4 text-[#728156]" />
            </div>

            <div className="grid grid-cols-3 gap-2 my-3 text-center">
              <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-100">
                <span className="text-[10px] uppercase font-bold text-emerald-800">Positive</span>
                <p className="text-xl font-bold text-emerald-700 mt-1">
                  {adoptionData?.breakdown?.positive_sentiment_count ?? 0}
                </p>
              </div>
              <div className="p-3 rounded-2xl bg-amber-50 border border-amber-100">
                <span className="text-[10px] uppercase font-bold text-amber-800">Neutral</span>
                <p className="text-xl font-bold text-amber-700 mt-1">
                  {adoptionData?.breakdown?.neutral_sentiment_count ?? 0}
                </p>
              </div>
              <div className="p-3 rounded-2xl bg-rose-50 border border-rose-100">
                <span className="text-[10px] uppercase font-bold text-rose-800">Negative</span>
                <p className="text-xl font-bold text-rose-700 mt-1">
                  {adoptionData?.breakdown?.negative_sentiment_count ?? 0}
                </p>
              </div>
            </div>

            <p className="text-[11px] text-[#88976C]">
              {adoptionData?.breakdown?.would_use_count ?? 0} respondents declared clear intent to adopt.
            </p>
          </div>

          {/* Segment Breakdown Card */}
          <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/70 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#728156]">
                Archetype Breakdown
              </span>
              <BarChart3 className="w-4 h-4 text-[#728156]" />
            </div>

            <div className="my-2 space-y-2 overflow-y-auto max-h-36 pr-1">
              {adoptionData?.segment_breakdown &&
                Object.entries(adoptionData.segment_breakdown).map(([seg, data]) => (
                  <div key={seg} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-[#2D3522] truncate max-w-[150px]">
                        {seg}
                      </span>
                      <span className="font-mono text-[#728156] font-bold">
                        {data.percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-[#F4F7F4] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#98A77C] h-full"
                        style={{ width: `${data.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>

            <p className="text-[11px] text-[#88976C]">
              Affinity segmented across occupational and psychographic cohorts
            </p>
          </div>
        </section>

        {/* Detailed Synthesized Report View */}
        {report ? (
          <section className="bg-white rounded-3xl p-8 border border-[#CFE1B9]/70 shadow-xs space-y-8">
            {/* Header info */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#F4F7F4]">
              <div>
                <span className="text-[10px] font-bold text-[#728156] uppercase tracking-wider">
                  Universal Synthesis Dossier • {report.report_date}
                </span>
                <h3 className="text-2xl font-bold text-[#2D3522] mt-0.5">
                  Executive Intelligence Report: {report.product}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-3 py-1 rounded-xl bg-[#E7F5DC] text-[#465135] font-semibold border border-[#CFE1B9]">
                  {report.persona_count} Synthetic Respondents
                </span>
                <span className="text-xs px-3 py-1 rounded-xl bg-[#F8FAF7] text-[#5B6845] font-semibold border border-[#CFE1B9]">
                  {report.interview_sessions_count} Interviews Analyzed
                </span>
              </div>
            </div>

            {/* Executive Summary */}
            {report.executive_summary && (
              <div className="bg-[#FAFDF7] p-6 rounded-2xl border border-[#CFE1B9]/70 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                  <FileCheck className="w-4 h-4" />
                  Executive Summary
                </h4>
                <p className="text-sm text-[#2D3522] leading-relaxed">
                  {report.executive_summary}
                </p>
              </div>
            )}

            {/* Findings and Insights Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Key Findings */}
              {report.key_findings && report.key_findings.length > 0 && (
                <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-[#728156]" />
                    Key Findings
                  </h4>
                  <ul className="space-y-2 text-xs text-[#2D3522]">
                    {report.key_findings.map((f, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#728156] mt-1.5 shrink-0" />
                        <span className="leading-relaxed">{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Top Pain Points */}
              {report.pain_points && report.pain_points.length > 0 && (
                <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    Critical Pain Points & Blockers
                  </h4>
                  <ul className="space-y-2 text-xs text-[#2D3522]">
                    {report.pain_points.map((p, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-600 mt-1.5 shrink-0" />
                        <span className="leading-relaxed">{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Churn Risks */}
              {report.churn_risks && report.churn_risks.length > 0 && (
                <div className="p-6 rounded-2xl bg-rose-50/50 border border-rose-200/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-rose-600" />
                    Dealbreaker Churn Triggers
                  </h4>
                  <ul className="space-y-2 text-xs text-rose-950">
                    {report.churn_risks.map((c, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-600 mt-1.5 shrink-0" />
                        <span className="leading-relaxed">{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Pricing Insights */}
              {report.pricing_insights && (
                <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                    <Coins className="w-4 h-4 text-[#728156]" />
                    Pricing & Elasticity Dynamics
                  </h4>
                  <p className="text-xs text-[#2D3522] leading-relaxed">
                    {report.pricing_insights}
                  </p>
                </div>
              )}
            </div>

            {/* Strategic Recommendations */}
            {report.recommendations && report.recommendations.length > 0 && (
              <div className="p-6 rounded-2xl bg-gradient-to-r from-[#E7F5DC]/60 via-[#F8FAF7] to-white border border-[#CFE1B9] space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#465135] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#728156]" />
                  Strategic Product Recommendations
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {report.recommendations.map((rec, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-xl bg-white border border-[#CFE1B9]/70 flex items-start gap-2.5 shadow-xs"
                    >
                      <span className="w-5 h-5 rounded-md bg-[#E7F5DC] text-[#728156] text-xs font-bold flex items-center justify-center shrink-0">
                        {i + 1}
                      </span>
                      <p className="text-xs text-[#2D3522] leading-relaxed font-medium">
                        {rec}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        ) : (
          <div className="bg-white rounded-3xl p-16 text-center border border-[#CFE1B9]/70 space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center mx-auto shadow-xs">
              <BarChart3 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#2D3522]">
                Generate Comprehensive Executive Intelligence
              </h3>
              <p className="text-xs text-[#647460] max-w-md mx-auto mt-1 leading-relaxed">
                Click the button at top right to trigger full OpenRouter LLM cross-synthesis across all personas, survey matrix rows, and 1-on-1 qualitative interview transcripts.
              </p>
            </div>
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="px-6 py-3 bg-[#728156] hover:bg-[#5B6845] text-white rounded-2xl text-xs font-bold shadow-xs hover:shadow-md transition-all inline-flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {generatingReport ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Deep Report...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-[#E7F5DC]" />
                  <span>Generate Report Now</span>
                </>
              )}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
