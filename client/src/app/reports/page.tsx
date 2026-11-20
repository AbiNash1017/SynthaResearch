"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import {
  AdoptionScoreData,
  ResearchReport,
  Experiment,
  SegmentAdoptionBreakdown,
  PersonaProfile,
} from "@/types/api";
import {
  BarChart3,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  ShieldAlert,
  FileCheck,
  Award,
  Download,
  Eye,
  X,
  ExternalLink,
  Layers,
  Scale,
  Users,
  Quote,
  MessageSquare,
  Tag,
} from "lucide-react";

export default function ReportsPage() {
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [adoptionData, setAdoptionData] = useState<AdoptionScoreData | null>(null);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [pdfPreviewOpen, setPdfPreviewOpen] = useState(false);
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const [themeCategoryFilter, setThemeCategoryFilter] = useState<string>("All");
  const [quoteSentimentFilter, setQuoteSentimentFilter] = useState<string>("All");

  useEffect(() => {
    let ignore = false;
    Promise.allSettled([
      api.getExperiment(),
      api.getAdoptionScore(),
      api.getLatestReport(),
    ]).then(([expRes, adoptRes, latestReportRes]) => {
      if (ignore) return;
      if (expRes.status === "fulfilled") setActiveExp(expRes.value);
      if (adoptRes.status === "fulfilled") setAdoptionData(adoptRes.value);
      if (
        latestReportRes.status === "fulfilled" &&
        latestReportRes.value?.report
      ) {
        setReport(latestReportRes.value.report);
      }
      setLoading(false);
    });
    return () => {
      ignore = true;
    };
  }, []);

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => {
      if (pdfBlobUrl) {
        URL.revokeObjectURL(pdfBlobUrl);
      }
    };
  }, [pdfBlobUrl]);

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
        text: `Full research report generated and synthesized! PDF exported and ready for preview or download.`,
      });
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to generate research report. Check if personas and survey responses exist.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setGeneratingReport(false);
    }
  }

  async function handleDownloadPdf() {
    setDownloadingPdf(true);
    try {
      const blob = await api.downloadReportPdfBlob(report?.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName =
        (report?.product || activeExp?.product_name || "Research")
          .replace(/\s+/g, "_")
          .replace(/[^a-zA-Z0-9_-]/g, "");
      a.download = `${safeName}_Research_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to download PDF report.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setDownloadingPdf(false);
    }
  }

  async function handleOpenPdfPreview() {
    setPreviewLoading(true);
    try {
      if (!pdfBlobUrl) {
        const blob = await api.downloadReportPdfBlob(report?.id);
        const url = URL.createObjectURL(blob);
        setPdfBlobUrl(url);
      }
      setPdfPreviewOpen(true);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to load PDF preview.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setPreviewLoading(false);
    }
  }

  function handleClosePdfPreview() {
    setPdfPreviewOpen(false);
  }

  // --- Derive Headline Metrics ---
  const rawScore =
    report?.would_use_score?.overall_score ??
    adoptionData?.overall_score ??
    (adoptionData?.adoption_score ? adoptionData.adoption_score * 100 : 0);
  const scorePercent = Number(rawScore).toFixed(1);

  const scoreLabel =
    report?.would_use_score?.score_label ??
    adoptionData?.score_label ??
    adoptionData?.sentiment_label ??
    "Evaluated";

  // Derive sentiment distribution
  const sentDist = report?.sentiment_distribution;
  const posPct = sentDist
    ? Math.round(
        Number(sentDist.positive) <= 1
          ? Number(sentDist.positive) * 100
          : Number(sentDist.positive)
      )
    : Math.round(
        ((adoptionData?.breakdown?.positive_sentiment_count ?? 0) /
          Math.max(1, adoptionData?.breakdown?.total_responses ?? 1)) *
          100
      );
  const neuPct = sentDist
    ? Math.round(
        Number(sentDist.neutral) <= 1
          ? Number(sentDist.neutral) * 100
          : Number(sentDist.neutral)
      )
    : Math.round(
        ((adoptionData?.breakdown?.neutral_sentiment_count ?? 0) /
          Math.max(1, adoptionData?.breakdown?.total_responses ?? 1)) *
          100
      );
  const negPct = sentDist
    ? Math.round(
        Number(sentDist.negative) <= 1
          ? Number(sentDist.negative) * 100
          : Number(sentDist.negative)
      )
    : Math.round(
        ((adoptionData?.breakdown?.negative_sentiment_count ?? 0) /
          Math.max(1, adoptionData?.breakdown?.total_responses ?? 1)) *
          100
      );

  // Derive segment breakdown list
  const segmentList: SegmentAdoptionBreakdown[] = (() => {
    if (
      report?.would_use_score?.segment_breakdown &&
      Array.isArray(report.would_use_score.segment_breakdown)
    ) {
      return report.would_use_score.segment_breakdown;
    }
    if (
      adoptionData?.segment_breakdown &&
      Array.isArray(adoptionData.segment_breakdown)
    ) {
      return adoptionData.segment_breakdown;
    }
    if (
      adoptionData?.segment_breakdown &&
      typeof adoptionData.segment_breakdown === "object"
    ) {
      return Object.entries(adoptionData.segment_breakdown).map(
        ([seg, data]) => ({
          segment: seg,
          score: data.percentage ?? 0,
          stance: "Evaluated",
          reasoning: "",
        })
      );
    }
    return [];
  })();

  // Derive persona profiles dossier
  const personaDossierList: PersonaProfile[] = (() => {
    if (report?.persona_profiles && report.persona_profiles.length > 0) {
      return report.persona_profiles;
    }
    if (report?.per_persona_breakdown && report.per_persona_breakdown.length > 0) {
      return report.per_persona_breakdown.map((p) => ({
        id: p.id,
        name: p.name,
        archetype: p.archetype,
        pain_points: p.key_takeaway,
        occupation: undefined,
        location: undefined,
        age: undefined,
        personality_traits: [],
        willingness_to_pay: undefined,
        current_tools: undefined,
        churn_triggers: undefined,
      }));
    }
    return [];
  })();

  const hasAnyReport = Boolean(report);

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAF7]">
      <Header
        title="Analytics & Executive Synthesis"
        subtitle={
          activeExp
            ? `Deep propensity scoring, segment breakdown, and strategic insights for "${activeExp.product_name}"`
            : "Propensity scoring and executive summary report generation"
        }
        actions={
          <div className="flex items-center gap-2">
            {hasAnyReport && (
              <>
                <button
                  onClick={handleOpenPdfPreview}
                  disabled={previewLoading}
                  className="px-4 py-2.5 bg-white hover:bg-[#F4F7F4] text-[#465135] border border-[#CFE1B9] rounded-xl text-xs font-bold shadow-2xs hover:shadow-xs transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                  title="Preview PDF directly in app"
                >
                  {previewLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin text-[#728156]" />
                  ) : (
                    <Eye className="w-4 h-4 text-[#728156]" />
                  )}
                  <span>Preview PDF</span>
                </button>
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="px-4 py-2.5 bg-white hover:bg-[#F4F7F4] text-[#465135] border border-[#CFE1B9] rounded-xl text-xs font-bold shadow-2xs hover:shadow-xs transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                  title="Download exported PDF report"
                >
                  {downloadingPdf ? (
                    <Loader2 className="w-4 h-4 animate-spin text-[#728156]" />
                  ) : (
                    <Download className="w-4 h-4 text-[#728156]" />
                  )}
                  <span>Download PDF</span>
                </button>
              </>
            )}

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
                  <span>{hasAnyReport ? "Re-Synthesize Report" : "Generate Executive Report"}</span>
                </>
              )}
            </button>
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
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-white/80 text-[#465135] shadow-xs">
                {scoreLabel}
              </span>
            </div>

            <div className="space-y-1.5">
              <div className="w-full bg-white/70 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-[#728156] h-full transition-all duration-700"
                  style={{
                    width: `${Math.min(100, Math.max(0, Number(scorePercent)))}%`,
                  }}
                />
              </div>
              <p className="text-[11px] text-[#5B6845] font-medium leading-snug">
                {report?.would_use_score?.summary_reasoning ||
                  (adoptionData?.total_personas
                    ? `Calculated from ${adoptionData.total_personas} synthetic persona sentiment distributions`
                    : "Empirical market signal calculation")}
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
                <span className="text-[10px] uppercase font-bold text-emerald-800">
                  Positive
                </span>
                <p className="text-xl font-bold text-emerald-700 mt-1">
                  {posPct}%
                </p>
              </div>
              <div className="p-3 rounded-2xl bg-amber-50 border border-amber-100">
                <span className="text-[10px] uppercase font-bold text-amber-800">
                  Neutral
                </span>
                <p className="text-xl font-bold text-amber-700 mt-1">
                  {neuPct}%
                </p>
              </div>
              <div className="p-3 rounded-2xl bg-rose-50 border border-rose-100">
                <span className="text-[10px] uppercase font-bold text-rose-800">
                  Negative
                </span>
                <p className="text-xl font-bold text-rose-700 mt-1">
                  {negPct}%
                </p>
              </div>
            </div>

            <p className="text-[11px] text-[#88976C] leading-snug">
              {report?.sentiment_analysis ||
                (adoptionData?.breakdown?.would_use_count !== undefined
                  ? `${adoptionData.breakdown.would_use_count} respondents declared clear intent to adopt.`
                  : "Response sentiment distribution across synthetic survey & interview turns.")}
            </p>
          </div>

          {/* Archetype Breakdown Card */}
          <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/70 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#728156]">
                Archetype Breakdown
              </span>
              <BarChart3 className="w-4 h-4 text-[#728156]" />
            </div>

            <div className="my-2 space-y-2.5 overflow-y-auto max-h-36 pr-1">
              {segmentList.length > 0 ? (
                segmentList.map((seg, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs items-center">
                      <span className="font-semibold text-[#2D3522] truncate max-w-[170px]" title={seg.segment}>
                        {seg.segment}
                      </span>
                      <span className="font-mono text-[#728156] font-bold">
                        {seg.score}%
                      </span>
                    </div>
                    <div className="w-full bg-[#F4F7F4] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#98A77C] h-full transition-all duration-500"
                        style={{
                          width: `${Math.min(100, Math.max(0, seg.score))}%`,
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-6 text-center text-xs text-[#88976C]">
                  Run surveys to analyze archetype affinity
                </div>
              )}
            </div>

            <p className="text-[11px] text-[#88976C]">
              Affinity segmented across occupational and psychographic cohorts
            </p>
          </div>
        </section>

        {/* Detailed Synthesized Report View */}
        {report ? (
          <section className="bg-white rounded-3xl p-8 border border-[#CFE1B9]/70 shadow-xs space-y-8">
            {/* Header info & PDF Action Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[#F4F7F4]">
              <div>
                <span className="text-[10px] font-bold text-[#728156] uppercase tracking-wider">
                  Universal Synthesis Dossier • {report.report_date}
                </span>
                <h3 className="text-2xl font-bold text-[#2D3522] mt-0.5">
                  Executive Intelligence Report: {report.product}
                </h3>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs px-3 py-1.5 rounded-xl bg-[#E7F5DC] text-[#465135] font-semibold border border-[#CFE1B9]">
                  {report.persona_count} Synthetic Respondents
                </span>
                <span className="text-xs px-3 py-1.5 rounded-xl bg-[#F8FAF7] text-[#5B6845] font-semibold border border-[#CFE1B9]">
                  {report.interview_sessions_count} Interviews Analyzed
                </span>
                <button
                  onClick={handleOpenPdfPreview}
                  disabled={previewLoading}
                  className="px-3.5 py-1.5 bg-[#F8FAF7] hover:bg-[#E7F5DC] text-[#465135] border border-[#CFE1B9] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Eye className="w-3.5 h-3.5 text-[#728156]" />
                  <span>Preview PDF</span>
                </button>
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="px-3.5 py-1.5 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </button>
              </div>
            </div>

            {/* Executive Summary */}
            {report.executive_summary && (
              <div className="bg-[#FAFDF7] p-6 rounded-2xl border border-[#CFE1B9]/70 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                  <FileCheck className="w-4 h-4" />
                  Executive Summary
                </h4>
                <p className="text-sm text-[#2D3522] leading-relaxed font-normal">
                  {report.executive_summary}
                </p>
              </div>
            )}

            {/* 1. Adoption Propensity Scorecard & Segment Deep-Dive */}
            {report.would_use_score && (
              <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                      <Award className="w-4 h-4 text-[#728156]" />
                      Adoption Propensity & Archetype Scorecard
                    </h4>
                    <p className="text-xs text-[#5B6845] mt-0.5">
                      {report.would_use_score.summary_reasoning}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-black text-[#2D3522]">
                      {report.would_use_score.overall_score}%
                    </span>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#E7F5DC] text-[#465135] border border-[#CFE1B9]">
                      {report.would_use_score.score_label}
                    </span>
                  </div>
                </div>

                {report.would_use_score.segment_breakdown &&
                  report.would_use_score.segment_breakdown.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                      {report.would_use_score.segment_breakdown.map((seg, i) => (
                        <div
                          key={i}
                          className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 shadow-2xs space-y-2 flex flex-col justify-between"
                        >
                          <div>
                            <div className="flex justify-between items-start gap-2">
                              <h5 className="font-bold text-xs text-[#2D3522]">
                                {seg.segment}
                              </h5>
                              <span className="text-xs font-mono font-bold text-[#728156]">
                                {seg.score}%
                              </span>
                            </div>
                            <span
                              className={`inline-block mt-1 text-[10px] font-semibold px-2 py-0.5 rounded-md ${
                                seg.score >= 70
                                  ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                  : seg.score >= 45
                                  ? "bg-amber-50 text-amber-800 border border-amber-200"
                                  : "bg-rose-50 text-rose-800 border border-rose-200"
                              }`}
                            >
                              {seg.stance}
                            </span>
                          </div>
                          <p className="text-xs text-[#5B6845] leading-relaxed pt-2 border-t border-[#F4F7F4]">
                            {seg.reasoning}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
              </div>
            )}

            {/* 2. Theme Clusters & Feedback Taxonomy */}
            {((report.theme_clusters && report.theme_clusters.length > 0) ||
              (report.themes && report.themes.length > 0)) && (
              <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                      <Layers className="w-4 h-4 text-[#728156]" />
                      Theme Clusters & Feedback Taxonomy
                    </h4>
                    <p className="text-xs text-[#5B6845] mt-0.5">
                      Semantic aggregation of persona feedback grouped by feedback domain and sentiment stance
                    </p>
                  </div>

                  {report.theme_clusters && report.theme_clusters.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5">
                      {["All", ...Array.from(new Set(report.theme_clusters.map((c) => c.category)))].map(
                        (cat) => (
                          <button
                            key={cat}
                            onClick={() => setThemeCategoryFilter(cat)}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                              themeCategoryFilter === cat
                                ? "bg-[#728156] text-white shadow-2xs"
                                : "bg-white text-[#465135] border border-[#CFE1B9]/70 hover:bg-[#E7F5DC]/60"
                            }`}
                          >
                            {cat}
                          </button>
                        )
                      )}
                    </div>
                  )}
                </div>

                {report.theme_clusters && report.theme_clusters.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                    {report.theme_clusters
                      .filter(
                        (c) =>
                          themeCategoryFilter === "All" ||
                          c.category === themeCategoryFilter
                      )
                      .map((cluster, idx) => {
                        const isPos = String(cluster.sentiment).toLowerCase() === "positive";
                        const isNeg = String(cluster.sentiment).toLowerCase() === "negative";
                        return (
                          <div
                            key={idx}
                            className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 shadow-2xs hover:shadow-xs transition-shadow space-y-2.5 flex flex-col justify-between"
                          >
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-md bg-[#FAFDF7] border border-[#CFE1B9] text-[#465135]">
                                  {cluster.category}
                                </span>
                                <div className="flex items-center gap-1.5">
                                  <span
                                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                      isPos
                                        ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                        : isNeg
                                        ? "bg-rose-50 text-rose-800 border border-rose-200"
                                        : "bg-amber-50 text-amber-800 border border-amber-200"
                                    }`}
                                  >
                                    {String(cluster.sentiment).toUpperCase()}
                                  </span>
                                  <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-700">
                                    {cluster.mention_count} mentions
                                  </span>
                                </div>
                              </div>
                              <h5 className="font-bold text-sm text-[#2D3522]">
                                {cluster.name}
                              </h5>
                              {cluster.summary && (
                                <p className="text-xs text-[#5B6845] leading-relaxed">
                                  {cluster.summary}
                                </p>
                              )}
                            </div>

                            {cluster.keywords && cluster.keywords.length > 0 && (
                              <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[#F4F7F4]">
                                {cluster.keywords.map((kw, kIdx) => (
                                  <span
                                    key={kIdx}
                                    className="text-[10px] px-2 py-0.5 rounded-md bg-[#F8FAF7] text-[#5B6845] border border-[#CFE1B9]/50"
                                  >
                                    #{kw}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {report.themes?.map((theme, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-white border border-[#CFE1B9]/70 flex items-start gap-3 shadow-2xs"
                      >
                        <span className="w-6 h-6 rounded-lg bg-[#E7F5DC] text-[#728156] text-xs font-bold flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <p className="text-xs text-[#2D3522] leading-relaxed font-medium">
                          {theme}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 3. Agreement Patterns: Consensus vs Polarization */}
            {report.agreement_patterns && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Consensus */}
                <div className="p-6 rounded-2xl bg-emerald-50/40 border border-emerald-200/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Empirical Consensus Points
                  </h4>
                  <ul className="space-y-2.5 text-xs text-[#2D3522]">
                    {report.agreement_patterns.consensus &&
                    report.agreement_patterns.consensus.length > 0 ? (
                      report.agreement_patterns.consensus.map((c, i) => (
                        <li key={i} className="flex items-start gap-2.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                          <span className="leading-relaxed">{c}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs text-gray-500">
                        General alignment on core product utility observed.
                      </li>
                    )}
                  </ul>
                </div>

                {/* Polarization */}
                <div className="p-6 rounded-2xl bg-amber-50/40 border border-amber-200/60 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-amber-800 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-amber-600" />
                    Polarization & Divergent Points
                  </h4>
                  <ul className="space-y-2.5 text-xs text-[#2D3522]">
                    {report.agreement_patterns.polarization &&
                    report.agreement_patterns.polarization.length > 0 ? (
                      report.agreement_patterns.polarization.map((p, i) => (
                        <li key={i} className="flex items-start gap-2.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-600 mt-1.5 shrink-0" />
                          <span className="leading-relaxed">{p}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs text-gray-500">
                        No critical divergence identified across personas.
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            )}

            {/* 4. Behavioral Cohort Trends */}
            {report.behavioral_trends && report.behavioral_trends.length > 0 && (
              <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#728156]" />
                  Behavioral Cohort Trends & Dynamics
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {report.behavioral_trends.map((trend, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 shadow-2xs space-y-2"
                    >
                      <span className="text-xs font-bold text-[#465135] block border-b border-[#F4F7F4] pb-1.5">
                        {trend.group}
                      </span>
                      <p className="text-xs text-[#2D3522] leading-relaxed">
                        {trend.finding}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 5. Critical Objections & Churn Risks */}
            {report.critical_objections && report.critical_objections.length > 0 && (
              <div className="p-6 rounded-2xl bg-rose-50/50 border border-rose-200/60 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-rose-600" />
                  Critical Objections & Dealbreaker Risks
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {report.critical_objections.map((obj, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-xl bg-white border border-rose-200 flex items-start gap-2.5 shadow-2xs"
                    >
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <p className="text-xs text-rose-950 leading-relaxed font-medium">
                        {obj}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 6. Strategic Recommendations & Actionable Insights */}
            {((report.top_insights && report.top_insights.length > 0) ||
              (report.recommendations && report.recommendations.length > 0)) && (
              <div className="p-6 rounded-2xl bg-gradient-to-r from-[#E7F5DC]/60 via-[#F8FAF7] to-white border border-[#CFE1B9] space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#465135] flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-[#728156]" />
                  Actionable Strategic Product Insights
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {(report.top_insights || report.recommendations || []).map(
                    (item, i) => (
                      <div
                        key={i}
                        className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 flex items-start gap-3 shadow-2xs hover:shadow-xs transition-shadow"
                      >
                        <span className="w-6 h-6 rounded-lg bg-[#E7F5DC] text-[#728156] text-xs font-bold flex items-center justify-center shrink-0">
                          {i + 1}
                        </span>
                        <p className="text-xs text-[#2D3522] leading-relaxed font-medium">
                          {item}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* 7. Key Persona Quotes & Qualitative Voices */}
            {report.key_persona_quotes && report.key_persona_quotes.length > 0 && (
              <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                      <Quote className="w-4 h-4 text-[#728156]" />
                      Key Persona Quotes & Qualitative Voices
                    </h4>
                    <p className="text-xs text-[#5B6845] mt-0.5">
                      Verbatim feedback expressions captured during multi-persona surveys and 1-on-1 qualitative interviews
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {["All", "positive", "neutral", "negative"].map((st) => (
                      <button
                        key={st}
                        onClick={() => setQuoteSentimentFilter(st)}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer capitalize ${
                          quoteSentimentFilter === st
                            ? "bg-[#728156] text-white shadow-2xs"
                            : "bg-white text-[#465135] border border-[#CFE1B9]/70 hover:bg-[#E7F5DC]/60"
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                  {report.key_persona_quotes
                    .filter(
                      (q) =>
                        quoteSentimentFilter === "All" ||
                        String(q.sentiment).toLowerCase() === quoteSentimentFilter.toLowerCase()
                    )
                    .map((quoteObj, qIdx) => {
                      const isPos = String(quoteObj.sentiment).toLowerCase() === "positive";
                      const isNeg = String(quoteObj.sentiment).toLowerCase() === "negative";
                      return (
                        <div
                          key={qIdx}
                          className={`p-4 rounded-xl bg-white border shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between space-y-3 ${
                            isPos
                              ? "border-emerald-200/80 border-l-4 border-l-emerald-500"
                              : isNeg
                              ? "border-rose-200/80 border-l-4 border-l-rose-500"
                              : "border-[#CFE1B9] border-l-4 border-l-amber-500"
                          }`}
                        >
                          <div className="space-y-2">
                            <Quote className="w-4 h-4 text-[#728156]/40" />
                            <p className="text-xs text-[#2D3522] italic font-medium leading-relaxed">
                              &ldquo;{quoteObj.quote}&rdquo;
                            </p>
                          </div>

                          <div className="pt-2 border-t border-[#F4F7F4] flex flex-wrap items-center justify-between gap-2">
                            <div>
                              <span className="font-bold text-xs text-[#2D3522] block">
                                {quoteObj.persona_name}
                              </span>
                              <span className="text-[10px] text-[#728156] font-medium">
                                {quoteObj.archetype}
                              </span>
                            </div>

                            <div className="flex items-center gap-1.5">
                              {quoteObj.topic && (
                                <span className="text-[10px] px-2 py-0.5 rounded-md bg-[#FAFDF7] text-[#5B6845] border border-[#CFE1B9]/60 truncate max-w-[140px]" title={quoteObj.topic}>
                                  {quoteObj.topic}
                                </span>
                              )}
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  isPos
                                    ? "bg-emerald-50 text-emerald-800"
                                    : isNeg
                                    ? "bg-rose-50 text-rose-800"
                                    : "bg-amber-50 text-amber-800"
                                }`}
                              >
                                {String(quoteObj.sentiment).toUpperCase()}
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* 8. Curated Empirical Response Highlights */}
            {report.response_highlights && report.response_highlights.length > 0 && (
              <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-[#728156]" />
                  Curated Empirical Response Highlights
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                  {report.response_highlights.map((high, hIdx) => (
                    <div
                      key={hIdx}
                      className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 shadow-2xs space-y-2 flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#E7F5DC] text-[#465135]">
                            {high.source}
                          </span>
                          <span className="text-[10px] text-[#88976C] font-semibold truncate max-w-[120px]">
                            {high.topic}
                          </span>
                        </div>
                        <p className="text-xs text-[#2D3522] leading-relaxed">
                          {high.highlight}
                        </p>
                      </div>

                      <div className="pt-2 border-t border-[#F4F7F4] flex items-center justify-between text-[11px]">
                        <span className="font-semibold text-[#465135]">
                          {high.respondent_name}
                        </span>
                        <span className="text-[10px] text-[#728156]">
                          {high.archetype}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 9. Comprehensive Synthetic Persona Profiles Dossier */}
            <div className="p-6 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/60 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] flex items-center gap-2">
                <Users className="w-4 h-4 text-[#728156]" />
                Synthetic Persona Profiles Dossier
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {personaDossierList.map((prof, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-white border border-[#CFE1B9]/70 shadow-2xs space-y-2.5 flex flex-col justify-between"
                  >
                    <div className="space-y-1.5">
                      <div className="flex justify-between items-start gap-2">
                        <div>
                          <h5 className="font-bold text-xs text-[#2D3522]">
                            {prof.name}
                          </h5>
                          {prof.occupation && (
                            <span className="text-[11px] text-[#5B6845] block">
                              {prof.occupation}
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#E7F5DC] text-[#465135] shrink-0">
                          {prof.archetype}
                        </span>
                      </div>

                      {prof.location && (
                        <p className="text-[10px] text-[#88976C]">
                          📍 {prof.location} {prof.age ? `• ${prof.age} yrs` : ""}
                        </p>
                      )}

                      {prof.personality_traits && prof.personality_traits.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {prof.personality_traits.map((tr, tIdx) => (
                            <span
                              key={tIdx}
                              className="text-[9px] px-1.5 py-0.5 rounded bg-gray-50 border border-gray-200 text-gray-700"
                            >
                              {tr}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="space-y-1.5 pt-2 border-t border-[#F4F7F4] text-xs">
                      {prof.pain_points && (
                        <div>
                          <span className="text-[10px] font-bold text-[#728156] uppercase block">
                            Key Pain Points
                          </span>
                          <p className="text-[#2D3522] leading-snug">
                            {prof.pain_points}
                          </p>
                        </div>
                      )}
                      {prof.willingness_to_pay && (
                        <div>
                          <span className="text-[10px] font-bold text-[#728156] uppercase block">
                            Willingness To Pay
                          </span>
                          <p className="text-[#5B6845] leading-snug">
                            {prof.willingness_to_pay}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        ) : !loading ? (
          <div className="bg-white rounded-3xl p-16 text-center border border-[#CFE1B9]/70 space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center mx-auto shadow-xs">
              <BarChart3 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#2D3522]">
                Generate Comprehensive Executive Intelligence
              </h3>
              <p className="text-xs text-[#647460] max-w-md mx-auto mt-1 leading-relaxed">
                Click the button below to trigger full cross-synthesis across all personas, survey matrix responses, and 1-on-1 qualitative interview transcripts.
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
        ) : (
          <div className="p-16 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-[#728156] mx-auto" />
            <p className="text-xs text-[#728156] font-semibold mt-3">
              Loading synthesized intelligence...
            </p>
          </div>
        )}
      </main>

      {/* In-App PDF Preview Modal */}
      {pdfPreviewOpen && pdfBlobUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 sm:p-6 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-5xl h-[90vh] rounded-3xl shadow-2xl border border-[#CFE1B9] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-[#F4F7F4] bg-[#FAFDF7] flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center font-bold">
                  PDF
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#2D3522]">
                    Research Intelligence Dossier — {report?.product || activeExp?.product_name || "Vibecircle"}
                  </h3>
                  <p className="text-[11px] text-[#728156]">
                    Official exported document • {report?.report_date || "Current"}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href={pdfBlobUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-white hover:bg-[#F4F7F4] text-[#465135] border border-[#CFE1B9] rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all"
                  title="Open in new window"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">New Tab</span>
                </a>
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="px-3 py-1.5 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </button>
                <button
                  onClick={handleClosePdfPreview}
                  className="w-8 h-8 rounded-xl bg-white hover:bg-rose-50 text-[#728156] hover:text-rose-600 border border-[#CFE1B9] hover:border-rose-200 flex items-center justify-center transition-all cursor-pointer ml-1"
                  aria-label="Close PDF Preview"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Iframe Body */}
            <div className="flex-1 w-full h-full bg-[#525659] p-2">
              <iframe
                src={pdfBlobUrl}
                title="PDF Report Preview"
                className="w-full h-full rounded-xl border-0 shadow-inner bg-white"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
