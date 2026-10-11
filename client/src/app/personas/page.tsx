"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import { Experiment, Persona } from "@/types/api";
import {
  Users,
  Sparkles,
  ArrowRight,
  Loader2,
  Briefcase,
  MapPin,
  AlertTriangle,
  Brain,
  Search,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import { Avatar } from "@/components/Avatar";

export default function PersonasPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [personaCount, setPersonaCount] = useState(5);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterArchetype, setFilterArchetype] = useState("all");
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    let ignore = false;
    Promise.allSettled([api.getExperiment(), api.listPersonas()]).then(
      ([expRes, personasRes]) => {
        if (ignore) return;
        if (expRes.status === "fulfilled") {
          setActiveExp(expRes.value);
        }
        if (personasRes.status === "fulfilled" && personasRes.value.personas) {
          setPersonas(personasRes.value.personas);
          if (personasRes.value.personas.length > 0) {
            setSelectedPersona(personasRes.value.personas[0]);
          }
        }
        setLoading(false);
      }
    );
    return () => {
      ignore = true;
    };
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    setStatusMsg(null);
    try {
      const res = await api.generatePersonas(personaCount);
      setPersonas(res.personas);
      if (res.personas.length > 0) {
        setSelectedPersona(res.personas[0]);
      }
      setStatusMsg({
        type: "success",
        text: `Successfully generated ${res.personas.length} synthetic user personas aligned with ${res.product}!`,
      });
    } catch (err: unknown) {
      // Check if backend actually finished and saved personas to MongoDB
      try {
        const checkRes = await api.listPersonas();
        if (checkRes && checkRes.personas && checkRes.personas.length > 0) {
          setPersonas(checkRes.personas);
          setSelectedPersona(checkRes.personas[0]);
          setStatusMsg({
            type: "success",
            text: `Personas generated and loaded successfully from database! (${checkRes.personas.length} personas)`,
          });
          return;
        }
      } catch {
        // Fall back to original error
      }
      const msg = err instanceof Error ? err.message : "Failed to generate personas. Ensure the backend and LLM are configured.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setGenerating(false);
    }
  }

  const archetypes = Array.from(new Set(personas.map((p) => p.archetype).filter(Boolean)));

  const filteredPersonas = personas.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.occupation?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.archetype?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.background_story?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesArchetype =
      filterArchetype === "all" || p.archetype === filterArchetype;

    return matchesSearch && matchesArchetype;
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        title="Synthetic Persona Pool"
        subtitle={
          activeExp
            ? `Demographically balanced virtual respondents calibrated for "${activeExp.product_name}"`
            : "Generate and inspect psychographic personas for research simulations"
        }
        actions={
          <div className="flex items-center gap-3">
            <Link
              href="/surveys"
              className="px-4 py-2 bg-[#728156] hover:bg-[#5B6845] text-white text-sm font-semibold rounded-xl shadow-xs flex items-center gap-2 transition-all"
            >
              <span>Next: Run Survey</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        }
      />

      <main className="p-8 max-w-7xl w-full mx-auto space-y-6">
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

        {/* Top Control Bar: Generation & Counts */}
        <section className="bg-white rounded-3xl p-6 border border-[#CFE1B9]/60 shadow-xs flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#2D3522]">
                Active Persona Pool ({personas.length})
              </h2>
              <p className="text-xs text-[#728156]">
                Each persona carries distinct behavioral memory, risk tolerances, and price elasticity.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-[#F8FAF7] border border-[#CFE1B9] px-3 py-1.5 rounded-xl">
              <span className="text-xs font-semibold text-[#5B6845]">Cohort Size:</span>
              <select
                value={personaCount}
                onChange={(e) => setPersonaCount(Number(e.target.value))}
                className="bg-transparent text-xs font-bold text-[#2D3522] focus:outline-none cursor-pointer"
              >
                <option value={3}>3 Personas</option>
                <option value={5}>5 Personas (Recommended)</option>
                <option value={8}>8 Personas (Broad)</option>
                <option value={10}>10 Personas (Deep Cohort)</option>
              </select>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-5 py-2.5 bg-[#728156] hover:bg-[#5B6845] text-white rounded-xl text-xs font-bold shadow-xs hover:shadow-md transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Cohort...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-[#E7F5DC]" />
                  <span>Generate New Cohort</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* Personas Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Persona List Column */}
          <div className="lg:col-span-5 space-y-4">
            {/* Search & Filter */}
            <div className="bg-white rounded-2xl p-3 border border-[#CFE1B9]/60 shadow-xs space-y-2">
              <div className="relative">
                <Search className="w-4 h-4 text-[#88976C] absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search personas by name, occupation, pain point..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-1 focus:ring-[#728156] text-[#2D3522]"
                />
              </div>

              {archetypes.length > 0 && (
                <div className="flex gap-1.5 overflow-x-auto pb-1">
                  <button
                    onClick={() => setFilterArchetype("all")}
                    className={`text-[11px] px-2.5 py-1 rounded-lg font-medium whitespace-nowrap transition-all ${
                      filterArchetype === "all"
                        ? "bg-[#728156] text-white"
                        : "bg-[#F8FAF7] text-[#5B6845] hover:bg-[#E7F5DC]"
                    }`}
                  >
                    All ({personas.length})
                  </button>
                  {archetypes.map((arch) => (
                    <button
                      key={arch}
                      onClick={() => setFilterArchetype(arch)}
                      className={`text-[11px] px-2.5 py-1 rounded-lg font-medium whitespace-nowrap transition-all ${
                        filterArchetype === arch
                          ? "bg-[#728156] text-white"
                          : "bg-[#F8FAF7] text-[#5B6845] hover:bg-[#E7F5DC]"
                      }`}
                    >
                      {arch}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Persona Cards List */}
            {loading ? (
              <div className="bg-white rounded-3xl p-12 text-center border border-[#CFE1B9]/60 flex flex-col items-center gap-3">
                <Loader2 className="w-6 h-6 animate-spin text-[#728156]" />
                <span className="text-xs text-[#5B6845]">Loading persona pool...</span>
              </div>
            ) : filteredPersonas.length === 0 ? (
              <div className="bg-white rounded-3xl p-12 text-center border border-[#CFE1B9]/60 space-y-3">
                <Users className="w-8 h-8 text-[#98A77C] mx-auto" />
                <h4 className="text-sm font-bold text-[#2D3522]">No Personas Available</h4>
                <p className="text-xs text-[#647460] max-w-xs mx-auto">
                  Generate your first synthetic cohort using the button above to begin research simulations.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
                {filteredPersonas.map((p) => {
                  const isSelected = selectedPersona?.id === p.id;
                  return (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPersona(p)}
                      className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                        isSelected
                          ? "bg-[#E7F5DC]/60 border-[#728156] shadow-xs ring-1 ring-[#728156]"
                          : "bg-white border-[#CFE1B9]/70 hover:bg-[#F8FAF7] hover:border-[#98A77C]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3 min-w-0">
                          <Avatar
                            seed={p.name}
                            gender={p.gender}
                            alt={p.name}
                            className="w-10 h-10 rounded-xl shrink-0"
                            fallbackText={p.name}
                          />
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-bold text-[#2D3522] truncate">{p.name}</h4>
                              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#E7F5DC] text-[#465135] shrink-0">
                                {p.age}y
                              </span>
                            </div>
                            <p className="text-xs text-[#5B6845] mt-0.5 line-clamp-1">
                              {p.occupation}
                            </p>
                          </div>
                        </div>
                        <span className="text-[10px] font-semibold bg-[#CFE1B9] text-[#2D3522] px-2 py-0.5 rounded-full shrink-0">
                          {p.archetype}
                        </span>
                      </div>

                      <p className="text-xs text-[#647460] mt-2 line-clamp-2 leading-relaxed">
                        {p.background_story}
                      </p>

                      <div className="mt-3 flex items-center justify-between text-[11px] text-[#728156] pt-2 border-t border-[#CFE1B9]/40">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-[#98A77C]" />
                          {p.location}
                        </span>
                        <div className="flex gap-1">
                          {p.personality_traits?.slice(0, 2).map((t, idx) => (
                            <span
                              key={idx}
                              className="bg-[#F4F7F4] text-[#465135] px-1.5 py-0.5 rounded text-[10px]"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Persona Deep-Dive Dossier Column */}
          <div className="lg:col-span-7">
            {selectedPersona ? (
              <div className="bg-white rounded-3xl p-7 border border-[#CFE1B9]/70 shadow-xs space-y-6">
                {/* Dossier Header */}
                <div className="flex items-start justify-between gap-4 pb-4 border-b border-[#F4F7F4]">
                  <div className="flex items-center gap-4 min-w-0">
                    <Avatar
                      seed={selectedPersona.name}
                      gender={selectedPersona.gender}
                      alt={selectedPersona.name}
                      className="w-14 h-14 rounded-2xl shadow-sm border border-[#CFE1B9]/80 shrink-0"
                      fallbackText={selectedPersona.name}
                    />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2.5">
                        <h3 className="text-xl font-bold text-[#2D3522] truncate">
                          {selectedPersona.name}
                        </h3>
                        <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-[#E7F5DC] text-[#465135] shrink-0">
                          ID: {selectedPersona.id}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-[#728156] mt-1 flex items-center gap-2 truncate">
                        <Briefcase className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate">
                          {selectedPersona.occupation} • {selectedPersona.location} •{" "}
                          {selectedPersona.age} y/o ({selectedPersona.gender})
                        </span>
                      </p>
                    </div>
                  </div>

                  <Link
                    href={`/interviews?persona=${selectedPersona.id}`}
                    className="px-3.5 py-2 bg-[#E7F5DC] hover:bg-[#CFE1B9] text-[#2D3522] rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-xs shrink-0"
                  >
                    <span>Interview 1-on-1</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#728156]" />
                  </Link>
                </div>

                {/* Narrative Profile */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] mb-1.5">
                    Background Narrative
                  </h4>
                  <p className="text-sm text-[#2D3522] bg-[#F8FAF7] p-4 rounded-2xl border border-[#CFE1B9]/50 leading-relaxed">
                    {selectedPersona.background_story}
                  </p>
                </div>

                {/* Behavioral Patterns */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] mb-3">
                    Behavioral & Workflow Dynamics
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="p-3.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]/40 space-y-1">
                      <span className="text-[11px] font-bold text-[#5B6845] uppercase">
                        Current Tools
                      </span>
                      <p className="text-xs text-[#2D3522] font-medium">
                        {selectedPersona.behavioral_patterns?.current_tools || "Standard industry tools"}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]/40 space-y-1">
                      <span className="text-[11px] font-bold text-[#5B6845] uppercase">
                        Usage Frequency
                      </span>
                      <p className="text-xs text-[#2D3522] font-medium">
                        {selectedPersona.behavioral_patterns?.usage_frequency || "Daily workflow"}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]/40 space-y-1">
                      <span className="text-[11px] font-bold text-[#5B6845] uppercase">
                        Primary Pain Points
                      </span>
                      <p className="text-xs text-[#2D3522] font-medium">
                        {selectedPersona.behavioral_patterns?.primary_pain_points || "Inefficient steps"}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]/40 space-y-1">
                      <span className="text-[11px] font-bold text-[#5B6845] uppercase">
                        Willingness to Pay
                      </span>
                      <p className="text-xs text-[#2D3522] font-medium">
                        {selectedPersona.behavioral_patterns?.willingness_to_pay || "Moderate budget"}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]/40 space-y-1 md:col-span-2">
                      <span className="text-[11px] font-bold text-rose-700 uppercase flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-rose-600" />
                        Dealbreaker Churn Triggers
                      </span>
                      <p className="text-xs text-[#2D3522] font-medium">
                        {selectedPersona.behavioral_patterns?.churn_triggers || "Lack of reliability or excessive friction"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Psychographic & Opinion Tendency Gauges */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156]">
                    Cognitive Tendencies & Biases
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
                    <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/50 text-center">
                      <span className="text-[10px] text-[#728156] font-semibold block">Price Sensitivity</span>
                      <span className="text-sm font-bold text-[#2D3522]">
                        {Math.round((selectedPersona.opinion_seeds?.price_sensitivity || 0.5) * 100)}%
                      </span>
                      <div className="w-full bg-[#CFE1B9]/50 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-[#728156] h-full"
                          style={{
                            width: `${(selectedPersona.opinion_seeds?.price_sensitivity || 0.5) * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/50 text-center">
                      <span className="text-[10px] text-[#728156] font-semibold block">Tech Comfort</span>
                      <span className="text-sm font-bold text-[#2D3522]">
                        {Math.round((selectedPersona.opinion_seeds?.tech_comfort || 0.5) * 100)}%
                      </span>
                      <div className="w-full bg-[#CFE1B9]/50 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-[#728156] h-full"
                          style={{
                            width: `${(selectedPersona.opinion_seeds?.tech_comfort || 0.5) * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/50 text-center">
                      <span className="text-[10px] text-[#728156] font-semibold block">Change Openness</span>
                      <span className="text-sm font-bold text-[#2D3522]">
                        {Math.round((selectedPersona.opinion_seeds?.openness_to_change || 0.5) * 100)}%
                      </span>
                      <div className="w-full bg-[#CFE1B9]/50 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-[#728156] h-full"
                          style={{
                            width: `${(selectedPersona.opinion_seeds?.openness_to_change || 0.5) * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/50 text-center">
                      <span className="text-[10px] text-[#728156] font-semibold block">Decision Style</span>
                      <span className="text-xs font-bold text-[#2D3522] capitalize mt-1">
                        {selectedPersona.psychological_profile?.decision_style || "Analytical"}
                      </span>
                      <span className="text-[10px] text-[#88976C] font-mono block mt-1">
                        MBTI: {selectedPersona.psychological_profile?.mbti || "INTJ"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Persona Personality Tags */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#728156] mb-2">
                    Observed Traits
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPersona.personality_traits?.map((t, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-[#E7F5DC] text-[#465135] rounded-lg text-xs font-semibold border border-[#CFE1B9]"
                      >
                        #{t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-3xl p-16 text-center border border-[#CFE1B9]/60 space-y-3">
                <Brain className="w-10 h-10 text-[#98A77C] mx-auto" />
                <h4 className="text-base font-bold text-[#2D3522]">Select a Persona</h4>
                <p className="text-xs text-[#647460] max-w-sm mx-auto">
                  Click on any respondent from the cohort list to inspect their behavioral traits, risk preferences, and psychographic baseline.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
