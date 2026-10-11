"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import { Experiment } from "@/types/api";
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Layers,
  Target,
  Loader2,
  RefreshCw,
  Plus,
  History,
  Check,
} from "lucide-react";
import Link from "next/link";

const DOMAIN_SUGGESTIONS = [
  "SaaS & Productivity",
  "FinTech & Payments",
  "Health & Wellness",
  "E-Commerce & Retail",
  "Food & Beverage",
  "Social Media & Community",
  "Developer Tools & AI",
  "EdTech & Learning",
  "Gaming & Entertainment",
  "Travel & Hospitality",
  "Media & Streaming",
  "Mobility & Logistics",
];

const PRESETS = [
  {
    name: "FocusFlow AI",
    domain: "SaaS & Productivity",
    desc: "An intelligent autonomous workspace tool that blocks digital distractions, batches async communication, and predicts burnout for engineering and remote knowledge teams.",
    audience: "Remote software engineers, tech managers, and neurodiverse knowledge workers aged 24-45.",
    objectives: [
      "Assess willingness to pay for autonomous calendar blocking",
      "Identify churn risks around privacy and background tracking",
      "Discover the most critical integrations required for daily adoption",
    ],
  },
  {
    name: "MealCraft AI",
    domain: "Food & Beverage",
    desc: "A smart culinary assistant that creates hyper-personalized weekly meal plans, tracks pantry ingredients, and coordinates automated grocery delivery with zero food waste.",
    audience: "Busy urban professionals, fitness enthusiasts, and dual-income households who value fresh home cooking.",
    objectives: [
      "Assess willingness to subscribe to automated weekly grocery basket checkouts",
      "Understand price tolerance for customized dietary optimization plans",
      "Identify churn risks related to ingredient substitution accuracy",
    ],
  },
  {
    name: "VibeCircle",
    domain: "Social Media & Community",
    desc: "An intentional micro-community network where verified interest groups share 60-second voice journals and coordinate curated real-world meetups without algorithmic ragebait.",
    audience: "Gen Z & Millennial creative hobbyists experiencing social feed burnout and seeking genuine affinity friendships.",
    objectives: [
      "Gauge willingness to engage in voice-first social interactions",
      "Uncover privacy comfort levels with local interest meetup discovery",
      "Identify engagement loops that prevent app abandonment",
    ],
  },
  {
    name: "AuraWealth",
    domain: "FinTech & Payments",
    desc: "Micro-investing and automated tax-loss harvesting app that translates complex financial goals into visual milestone gardens with real-time portfolio risk alerts.",
    audience: "Gen Z & Millennial retail investors with beginner-to-intermediate financial literacy.",
    objectives: [
      "Evaluate trust and security perception of automated investing",
      "Understand price tolerance for tiered subscription vs AUM fee",
      "Test reaction to visual gamified financial goals",
    ],
  },
  {
    name: "PulseClinic",
    domain: "Health & Wellness",
    desc: "A HIPAA-compliant asynchronous telehealth and preventative diagnostics hub bridging primary physicians and busy chronic care patients.",
    audience: "Working professionals managing chronic wellness conditions or busy families.",
    objectives: [
      "Measure willingness to switch from in-person visits to async chats",
      "Uncover fears regarding diagnostic accuracy and response latency",
    ],
  },
];

export default function WorkspacePage() {
  const [loading, setLoading] = useState(false);
  const [fetchingExp, setFetchingExp] = useState(true);
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [allExperiments, setAllExperiments] = useState<Experiment[]>([]);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [switchingId, setSwitchingId] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Form states
  const [productName, setProductName] = useState("");
  const [productDesc, setProductDesc] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [domain, setDomain] = useState("SaaS & Productivity");
  const [objectives, setObjectives] = useState<string[]>([
    "Evaluate core value proposition and initial reaction",
    "Identify price sensitivity and willingness to pay",
    "Discover dealbreaker churn risks and missing capabilities",
  ]);
  const [newObj, setNewObj] = useState("");

  useEffect(() => {
    loadExperiment();
  }, []);

  async function loadExperiment() {
    setFetchingExp(true);
    try {
      const [exp, listRes] = await Promise.all([
        api.getExperiment().catch(() => null),
        api.listExperiments().catch(() => ({ count: 0, experiments: [] })),
      ]);

      if (listRes?.experiments) {
        setAllExperiments(listRes.experiments);
      }

      if (exp) {
        setActiveExp(exp);
        if (!isCreatingNew) {
          setProductName(exp.product_name || "");
          setProductDesc(exp.product_description || "");
          setTargetAudience(exp.target_audience || "");
          setDomain(exp.industry_domain || "SaaS & Productivity");
          if (exp.research_objectives && exp.research_objectives.length > 0) {
            setObjectives(exp.research_objectives);
          }
        }
      } else {
        applyPreset(PRESETS[0]);
      }
    } finally {
      setFetchingExp(false);
    }
  }

  function startNewProduct() {
    setIsCreatingNew(true);
    setProductName("");
    setProductDesc("");
    setTargetAudience("");
    setDomain("SaaS & Productivity");
    setObjectives([
      "Evaluate core value proposition and initial reaction",
      "Identify price sensitivity and willingness to pay",
      "Discover dealbreaker churn risks and missing capabilities",
    ]);
    setStatusMsg({
      type: "success",
      text: "Form cleared! Enter your new product details or pick a template, then save to initialize a fresh workspace.",
    });
  }

  async function switchToExperiment(exp: Experiment) {
    if (!exp.id) return;
    setSwitchingId(exp.id);
    setStatusMsg(null);
    try {
      await api.activateExperiment(exp.id);
      setIsCreatingNew(false);
      setActiveExp(exp);
      setProductName(exp.product_name || "");
      setProductDesc(exp.product_description || "");
      setTargetAudience(exp.target_audience || "");
      setDomain(exp.industry_domain || "SaaS & Productivity");
      if (exp.research_objectives && exp.research_objectives.length > 0) {
        setObjectives(exp.research_objectives);
      }
      // Refresh experiments list to update active badges
      const listRes = await api.listExperiments().catch(() => null);
      if (listRes?.experiments) setAllExperiments(listRes.experiments);

      setStatusMsg({
        type: "success",
        text: `Switched active product to "${exp.product_name}". All its personas, surveys, and interviews are now loaded!`,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to switch active product.";
      setStatusMsg({ type: "error", text: msg });
    } finally {
      setSwitchingId(null);
    }
  }

  function applyPreset(p: (typeof PRESETS)[0]) {
    setProductName(p.name);
    setDomain(p.domain);
    setProductDesc(p.desc);
    setTargetAudience(p.audience);
    setObjectives(p.objectives);
    setStatusMsg({
      type: "success",
      text: `Loaded "${p.name}" preset template!`,
    });
  }

  function addObjective() {
    if (!newObj.trim()) return;
    setObjectives([...objectives, newObj.trim()]);
    setNewObj("");
  }

  function removeObjective(idx: number) {
    setObjectives(objectives.filter((_, i) => i !== idx));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!productName.trim() || !productDesc.trim() || !targetAudience.trim()) {
      setStatusMsg({
        type: "error",
        text: "Please provide product name, description, and target audience.",
      });
      return;
    }

    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await api.setupExperiment({
        product_name: productName.trim(),
        product_description: productDesc.trim(),
        target_audience: targetAudience.trim(),
        research_objectives: objectives.filter((o) => o.trim().length > 0),
        industry_domain: domain,
      });
      setIsCreatingNew(false);
      setActiveExp(res.experiment);
      const listRes = await api.listExperiments().catch(() => null);
      if (listRes?.experiments) setAllExperiments(listRes.experiments);

      setStatusMsg({
        type: "success",
        text: `Product workspace "${res.experiment.product_name}" configured! Personas, surveys, and chats for this product start fresh.`,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to configure experiment workspace.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        title="Workspace & Experiment Setup"
        subtitle="Define your product specifications and research goals to anchor synthetic simulations"
        actions={
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={startNewProduct}
              className="px-3.5 py-2 bg-[#E7F5DC] hover:bg-[#CFE1B9] text-[#465135] text-xs font-bold rounded-xl transition-all flex items-center gap-1.5 cursor-pointer shadow-2xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create New Product</span>
            </button>
            {activeExp && (
              <Link
                href="/personas"
                className="px-4 py-2 bg-[#728156] hover:bg-[#5B6845] text-white text-sm font-semibold rounded-xl shadow-xs flex items-center gap-2 transition-all"
              >
                <span>Next: Persona Pool</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        }
      />

      <main className="p-8 max-w-6xl w-full mx-auto space-y-8">
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

        {/* Presets Bar */}
        <section className="bg-white/80 rounded-3xl p-6 border border-[#CFE1B9]/60 shadow-xs backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#728156]" />
              <h2 className="text-sm font-bold uppercase tracking-wider text-[#465135]">
                Quick-Start Research Templates
              </h2>
            </div>
            <span className="text-xs text-[#88976C]">Click to auto-populate research specs</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PRESETS.map((p) => (
              <button
                key={p.name}
                type="button"
                onClick={() => applyPreset(p)}
                className="text-left p-4 rounded-2xl bg-[#F8FAF7] hover:bg-[#E7F5DC]/60 border border-[#CFE1B9]/70 hover:border-[#98A77C] transition-all group"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-sm text-[#2D3522] group-hover:text-[#465135]">
                    {p.name}
                  </span>
                  <span className="text-[10px] font-semibold bg-[#E7F5DC] text-[#728156] px-2 py-0.5 rounded-full">
                    {p.domain}
                  </span>
                </div>
                <p className="text-xs text-[#647460] line-clamp-2 leading-relaxed">
                  {p.desc}
                </p>
              </button>
            ))}
          </div>
        </section>

        {/* Experiment Configuration Form */}
        <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Specs Column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/60 shadow-xs space-y-6">
              <div className="flex items-center justify-between pb-2 border-b border-[#F4F7F4]">
                <div className="flex items-center gap-2.5">
                  <Layers className="w-5 h-5 text-[#728156]" />
                  <h3 className="font-bold text-lg text-[#2D3522]">Product Parameters</h3>
                </div>
                {isCreatingNew ? (
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#E7F5DC] text-[#465135] border border-[#CFE1B9]">
                    ✨ New Product Workspace
                  </span>
                ) : activeExp ? (
                  <span className="text-xs text-[#88976C]">
                    Current: <strong className="text-[#465135]">{activeExp.product_name}</strong>
                  </span>
                ) : null}
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5B6845] uppercase tracking-wider mb-2">
                  Product Name
                </label>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  placeholder="e.g. FocusFlow AI, Notion, Figma"
                  required
                  className="w-full px-4 py-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522] font-medium placeholder:text-[#98A77C]/60"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5B6845] uppercase tracking-wider mb-2">
                  Industry / Domain
                </label>
                <div className="flex flex-wrap gap-2">
                  {DOMAIN_SUGGESTIONS.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDomain(d)}
                      className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all cursor-pointer ${
                        domain === d
                          ? "bg-[#728156] text-white border-[#728156] shadow-xs"
                          : "bg-[#F8FAF7] text-[#5B6845] border-[#CFE1B9] hover:bg-[#E7F5DC]"
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5B6845] uppercase tracking-wider mb-2">
                  Product Description & Value Proposition
                </label>
                <textarea
                  rows={4}
                  value={productDesc}
                  onChange={(e) => setProductDesc(e.target.value)}
                  placeholder="Describe key features, core workflow, value proposition, and problems it solves..."
                  required
                  className="w-full px-4 py-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522] leading-relaxed placeholder:text-[#98A77C]/60"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5B6845] uppercase tracking-wider mb-2">
                  Target Customer & Audience
                </label>
                <textarea
                  rows={3}
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  placeholder="Demographics, jobs to be done, technical experience level, habits..."
                  required
                  className="w-full px-4 py-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522] leading-relaxed placeholder:text-[#98A77C]/60"
                />
              </div>
            </div>

            {/* Research Objectives */}
            <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/60 shadow-xs space-y-5">
              <div className="flex items-center justify-between pb-2 border-b border-[#F4F7F4]">
                <div className="flex items-center gap-2.5">
                  <Target className="w-5 h-5 text-[#728156]" />
                  <h3 className="font-bold text-lg text-[#2D3522]">Research Objectives</h3>
                </div>
                <span className="text-xs text-[#88976C] font-mono">
                  {objectives.length} defined
                </span>
              </div>

              <div className="space-y-2.5">
                {objectives.map((obj, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between gap-3 p-3.5 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/70 group"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-lg bg-[#E7F5DC] text-[#728156] text-xs font-bold flex items-center justify-center shrink-0 font-mono">
                        {i + 1}
                      </span>
                      <span className="text-sm text-[#2D3522] font-medium">{obj}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeObjective(i)}
                      className="text-xs text-[#88976C] hover:text-rose-600 transition-colors p-1"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>

              <div className="flex gap-2 pt-2">
                <input
                  type="text"
                  value={newObj}
                  onChange={(e) => setNewObj(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addObjective();
                    }
                  }}
                  placeholder="Add another research goal or focus area..."
                  className="flex-1 px-4 py-2.5 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522]"
                />
                <button
                  type="button"
                  onClick={addObjective}
                  className="px-4 py-2.5 bg-[#E7F5DC] hover:bg-[#CFE1B9] text-[#465135] font-semibold text-sm rounded-xl transition-all"
                >
                  Add Goal
                </button>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3.5 bg-[#728156] hover:bg-[#5B6845] text-white text-sm font-bold rounded-2xl shadow-sm hover:shadow-md transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Configuring Workspace...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#E7F5DC]" />
                    <span>Save & Normalize Experiment</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Active Experiment Sidebar Preview */}
          <div className="space-y-6">
            <div className="bg-gradient-to-b from-[#E7F5DC]/40 to-white rounded-3xl p-6 border border-[#CFE1B9] shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#728156] uppercase tracking-wider">
                  Active Workspace Status
                </span>
                <button
                  type="button"
                  onClick={loadExperiment}
                  className="p-1.5 rounded-lg text-[#728156] hover:bg-[#E7F5DC] transition-colors"
                  title="Reload current experiment"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
              </div>

              {fetchingExp ? (
                <div className="py-8 flex flex-col items-center justify-center text-[#728156] gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="text-xs">Checking workspace...</span>
                </div>
              ) : activeExp ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-lg font-bold text-[#2D3522]">
                      {activeExp.product_name}
                    </h4>
                    <span className="inline-block mt-1 text-[11px] font-semibold bg-[#CFE1B9] text-[#2D3522] px-2.5 py-0.5 rounded-full">
                      {activeExp.industry_domain || "Technology"}
                    </span>
                  </div>

                  <div className="text-xs text-[#5B6845] space-y-2">
                    <p className="line-clamp-3 leading-relaxed">
                      {activeExp.product_description}
                    </p>
                    <div className="pt-2 border-t border-[#CFE1B9]/50">
                      <span className="font-semibold text-[#465135]">Target Audience:</span>
                      <p className="mt-0.5 line-clamp-2 text-[#647460]">
                        {activeExp.target_audience}
                      </p>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-[#CFE1B9]/50">
                    <Link
                      href="/personas"
                      className="w-full py-2.5 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-xs"
                    >
                      <span>Proceed to Persona Generation</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-[#88976C]">
                  No active experiment configured yet. Fill out the form or choose a template to begin.
                </div>
              )}
            </div>

            {/* Product Switcher & History */}
            <div className="bg-white rounded-3xl p-6 border border-[#CFE1B9]/60 shadow-xs space-y-3.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="w-4 h-4 text-[#728156]" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#2D3522]">
                    Your Products ({allExperiments.length})
                  </h4>
                </div>
                <button
                  type="button"
                  onClick={startNewProduct}
                  className="text-[11px] font-bold text-[#728156] hover:text-[#5B6845] flex items-center gap-1 cursor-pointer"
                >
                  <Plus className="w-3 h-3" />
                  <span>New</span>
                </button>
              </div>

              <p className="text-[11px] text-[#88976C]">
                Switch between products anytime to view and resume each product&apos;s isolated personas, surveys, and chats.
              </p>

              {allExperiments.length === 0 ? (
                <div className="text-center py-4 text-xs text-[#88976C]">
                  No saved products yet.
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {allExperiments.map((exp) => {
                    const isActive = exp.id === activeExp?.id;
                    const isSwitching = switchingId === exp.id;
                    return (
                      <div
                        key={exp.id || exp.product_name}
                        className={`p-3 rounded-2xl border transition-all ${
                          isActive
                            ? "bg-[#E7F5DC]/70 border-[#728156] shadow-2xs"
                            : "bg-[#F8FAF7] border-[#CFE1B9]/60 hover:bg-[#F4F7F4]"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="min-w-0">
                            <h5 className="font-bold text-xs text-[#2D3522] truncate">
                              {exp.product_name}
                            </h5>
                            <span className="text-[10px] text-[#728156] font-medium">
                              {exp.industry_domain || "General"}
                            </span>
                          </div>

                          {isActive ? (
                            <span className="px-2 py-0.5 rounded-full bg-[#728156] text-white text-[10px] font-bold flex items-center gap-1 shrink-0">
                              <Check className="w-2.5 h-2.5" />
                              <span>Active</span>
                            </span>
                          ) : (
                            <button
                              type="button"
                              onClick={() => switchToExperiment(exp)}
                              disabled={isSwitching}
                              className="px-2.5 py-1 rounded-lg bg-white hover:bg-[#E7F5DC] text-[#465135] text-[10px] font-bold border border-[#CFE1B9] transition-all shrink-0 cursor-pointer disabled:opacity-50"
                            >
                              {isSwitching ? (
                                <Loader2 className="w-3 h-3 animate-spin text-[#728156]" />
                              ) : (
                                "Switch"
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-white rounded-3xl p-6 border border-[#CFE1B9]/60 shadow-xs space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156]">
                Pipeline Checklist
              </h4>
              <ul className="text-xs space-y-2.5">
                <li className="flex items-center gap-2 text-[#2D3522]">
                  <CheckCircle2 className="w-4 h-4 text-[#728156] shrink-0" />
                  <span>Step 1: Product Workspace Defined</span>
                </li>
                <li className="flex items-center gap-2 text-[#88976C]">
                  <div className="w-4 h-4 rounded-full border-2 border-[#CFE1B9] shrink-0" />
                  <span>Step 2: Generate Diverse Persona Pool</span>
                </li>
                <li className="flex items-center gap-2 text-[#88976C]">
                  <div className="w-4 h-4 rounded-full border-2 border-[#CFE1B9] shrink-0" />
                  <span>Step 3: Run Multi-Persona Structured Survey</span>
                </li>
                <li className="flex items-center gap-2 text-[#88976C]">
                  <div className="w-4 h-4 rounded-full border-2 border-[#CFE1B9] shrink-0" />
                  <span>Step 4: Conduct Live 1-on-1 Qualitative Chat</span>
                </li>
                <li className="flex items-center gap-2 text-[#88976C]">
                  <div className="w-4 h-4 rounded-full border-2 border-[#CFE1B9] shrink-0" />
                  <span>Step 5: Synthesize Adoption Scores & PDF Report</span>
                </li>
              </ul>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
}
