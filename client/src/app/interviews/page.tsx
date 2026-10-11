"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Header } from "@/components/Navigation";
import { api } from "@/lib/api";
import {
  Persona,
  InterviewSessionSummary,
  Experiment,
} from "@/types/api";
import {
  Send,
  Loader2,
  Users,
  RotateCcw,
  Bot,
  User,
  History,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

const PROMPT_SUGGESTIONS = [
  "What is the single biggest workflow pain point you encounter every week?",
  "If this tool cost $29/seat/month, how would your team justify the expense?",
  "What would cause you to immediately churn or abandon this software?",
  "How does your current tool stack handle this problem right now?",
  "What feature would make this an instant must-have for your day-to-day work?",
];

function InterviewsContent() {
  const searchParams = useSearchParams();
  const personaParam = searchParams.get("persona");

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [pastSessions, setPastSessions] = useState<InterviewSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    Array<{ sender: "user" | "persona"; text: string; timestamp: string }>
  >([]);
  const [inputMessage, setInputMessage] = useState("");
  const [, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  function initNewSession(persona: Persona, prodName?: string) {
    const newId = `session_${persona.id}_${Date.now()}`;
    setActiveSessionId(newId);
    const pName = prodName || activeExp?.product_name || "this product";
    setMessages([
      {
        sender: "persona",
        text: `Hi there! I'm ${persona.name}, working as ${persona.occupation}. Happy to share my thoughts on ${pName}. What would you like to explore?`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }

  async function loadSessionTranscript(sessionId: string, persona?: Persona, prodName?: string) {
    try {
      const detail = await api.getInterviewSession(sessionId);
      // Strictly ensure transcript persona matches the selected persona
      if (persona && detail.persona_id && detail.persona_id !== persona.id) {
        initNewSession(persona, prodName);
        return;
      }
      setActiveSessionId(detail.session_id);
      if (persona) setSelectedPersona(persona);

      const mapped: Array<{ sender: "user" | "persona"; text: string; timestamp: string }> = [];
      detail.turns.forEach((t) => {
        mapped.push({
          sender: "user",
          text: t.user_message,
          timestamp: new Date(t.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        });
        mapped.push({
          sender: "persona",
          text: t.persona_response,
          timestamp: new Date(t.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        });
      });

      if (mapped.length === 0 && persona) {
        initNewSession(persona, prodName);
      } else {
        setMessages(mapped);
      }
    } catch (err: unknown) {
      console.error(err);
      if (persona) initNewSession(persona, prodName);
    }
  }

  useEffect(() => {
    let ignore = false;
    Promise.allSettled([
      api.getExperiment(),
      api.listPersonas(),
      api.listInterviews(),
    ]).then(([expRes, personasRes, interviewsRes]) => {
      if (ignore) return;
      let exp: Experiment | null = null;
      if (expRes.status === "fulfilled") {
        exp = expRes.value;
        setActiveExp(exp);
      }

      let foundList: Persona[] = [];
      if (personasRes.status === "fulfilled" && personasRes.value.personas) {
        foundList = personasRes.value.personas;
        setPersonas(foundList);
      }

      const sessions = interviewsRes.status === "fulfilled" ? (interviewsRes.value.sessions || []) : [];
      setPastSessions(sessions);

      // Pick selected persona
      if (foundList.length > 0) {
        const target = personaParam
          ? foundList.find((p) => p.id === personaParam)
          : foundList[0];
        const chosen = target || foundList[0];
        setSelectedPersona(chosen);

        // Check if there is an existing session for this persona in this product
        const existing = sessions.find((s) => s.persona_id === chosen.id);
        if (existing && existing.turns_count > 0) {
          loadSessionTranscript(existing.session_id, chosen, exp?.product_name);
        } else {
          initNewSession(chosen, exp?.product_name);
        }
      } else {
        setSelectedPersona(null);
        setMessages([]);
      }
      setLoading(false);
    });
    return () => {
      ignore = true;
    };
  }, [personaParam]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  function handleSelectPersona(p: Persona) {
    setSelectedPersona(p);
    const existing = pastSessions.find((s) => s.persona_id === p.id);
    if (existing && existing.turns_count > 0) {
      loadSessionTranscript(existing.session_id, p, activeExp?.product_name);
    } else {
      initNewSession(p, activeExp?.product_name);
    }
  }

  async function handleSendMessage(e?: React.FormEvent) {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || !selectedPersona || sending) return;

    const userText = inputMessage.trim();
    setInputMessage("");

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: userText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);

    setSending(true);
    setStatusMsg(null);

    try {
      const res = await api.sendInterviewMessage({
        persona_id: selectedPersona.id,
        user_message: userText,
        session_id: activeSessionId || undefined,
      });

      setActiveSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        {
          sender: "persona",
          text: res.persona_response,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);

      // Refresh past sessions list
      api.listInterviews().then((r) => setPastSessions(r.sessions)).catch(() => {});
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to receive response from synthetic persona.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    } finally {
      setSending(false);
    }
  }

  async function handleResetInterviews() {
    if (!confirm("Are you sure you want to clear all interview logs?")) return;
    try {
      await api.resetInterviews();
      setPastSessions([]);
      if (selectedPersona) initNewSession(selectedPersona);
      setStatusMsg({
        type: "success",
        text: "Interview history cleared.",
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to reset interviews.";
      setStatusMsg({
        type: "error",
        text: msg,
      });
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        title="Live 1-on-1 Qualitative Interviews"
        subtitle={
          selectedPersona
            ? `Deep conversational inquiry with ${selectedPersona.name} (${selectedPersona.archetype})`
            : "Chat directly with synthetic user personas powered by continuous dynamic memory"
        }
        actions={
          <div className="flex items-center gap-3">
            <button
              onClick={handleResetInterviews}
              className="px-3 py-1.5 rounded-xl border border-[#CFE1B9] text-[#5B6845] hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 text-xs font-semibold flex items-center gap-1.5 transition-all"
              title="Reset interview logs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Logs</span>
            </button>
            <Link
              href="/reports"
              className="px-4 py-2 bg-[#728156] hover:bg-[#5B6845] text-white text-sm font-semibold rounded-xl shadow-xs flex items-center gap-2 transition-all"
            >
              <span>Next: Reports & Scoring</span>
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

        {personas.length === 0 ? (
          <div className="bg-white rounded-3xl p-16 text-center border border-[#CFE1B9]/70 space-y-4 shadow-xs">
            <Users className="w-12 h-12 text-[#98A77C] mx-auto" />
            <h3 className="text-base font-bold text-[#2D3522]">
              No Personas Available for {activeExp?.product_name || "this Product"}
            </h3>
            <p className="text-xs text-[#647460] max-w-md mx-auto leading-relaxed">
              This product is freshly configured and has no synthetic personas generated yet. Generate personas in Step 2 before conducting qualitative 1-on-1 interviews.
            </p>
            <div className="pt-2">
              <Link
                href="/personas"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#728156] hover:bg-[#5B6845] text-white text-xs font-semibold rounded-xl transition-all shadow-xs"
              >
                <span>Go to Persona Pool</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-210px)] min-h-[640px]">
          {/* Persona selector sidebar */}
          <div className="lg:col-span-4 bg-white rounded-3xl border border-[#CFE1B9]/70 shadow-xs flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#F4F7F4] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-[#728156]" />
                <h3 className="text-sm font-bold text-[#2D3522]">Respondent Roster</h3>
              </div>
              <span className="text-[11px] font-mono text-[#88976C]">
                {personas.length} Available
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {personas.map((p) => {
                const isSelected = selectedPersona?.id === p.id;
                const session = pastSessions.find((s) => s.persona_id === p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => handleSelectPersona(p)}
                    className={`w-full text-left p-3.5 rounded-2xl transition-all cursor-pointer border ${
                      isSelected
                        ? "bg-[#E7F5DC]/70 border-[#728156] shadow-xs"
                        : "bg-[#F8FAF7] border-[#CFE1B9]/60 hover:bg-[#E7F5DC]/30 hover:border-[#98A77C]"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-[#2D3522]">{p.name}</span>
                        <span className="text-[10px] text-[#728156] font-mono">
                          {p.age}y
                        </span>
                      </div>
                      <span className="text-[9px] font-semibold px-2 py-0.5 rounded-full bg-white text-[#5B6845] border border-[#CFE1B9]/50">
                        {p.archetype}
                      </span>
                    </div>

                    <p className="text-[11px] text-[#647460] mt-1 line-clamp-1">
                      {p.occupation}
                    </p>

                    <div className="mt-2 flex items-center justify-between text-[10px] text-[#88976C] pt-1.5 border-t border-[#CFE1B9]/40">
                      <span>{p.location}</span>
                      {session && (
                        <span className="text-[#728156] font-semibold flex items-center gap-1">
                          <History className="w-3 h-3" />
                          {session.turns_count} turns
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Persona Quick Card */}
            {selectedPersona && (
              <div className="p-4 bg-[#F4F7F4] border-t border-[#CFE1B9]/60 space-y-2 text-xs">
                <span className="text-[10px] font-bold text-[#728156] uppercase tracking-wider block">
                  Active Respondent Dossier
                </span>
                <p className="text-[#2D3522] leading-relaxed line-clamp-3 text-[11px]">
                  {selectedPersona.background_story}
                </p>
                <div className="flex items-center gap-2 text-[10px] text-[#5B6845]">
                  <span>MBTI: {selectedPersona.psychological_profile?.mbti || "INTJ"}</span>
                  <span>•</span>
                  <span>
                    Price Sens:{" "}
                    {Math.round((selectedPersona.opinion_seeds?.price_sensitivity || 0.5) * 100)}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Interactive Chat Console */}
          <div className="lg:col-span-8 bg-white rounded-3xl border border-[#CFE1B9]/70 shadow-xs flex flex-col overflow-hidden">
            {/* Chat header */}
            <div className="px-6 py-4 border-b border-[#F4F7F4] flex items-center justify-between bg-white/60 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#E7F5DC] text-[#728156] flex items-center justify-center font-bold">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#2D3522]">
                    {selectedPersona ? selectedPersona.name : "Interview Room"}
                  </h3>
                  <p className="text-xs text-[#728156]">
                    {selectedPersona ? selectedPersona.archetype : "Select a respondent"} • Memory & Persona Consistency Active
                  </p>
                </div>
              </div>

              {selectedPersona && (
                <button
                  onClick={() => initNewSession(selectedPersona)}
                  className="px-3 py-1.5 rounded-xl bg-[#F8FAF7] hover:bg-[#E7F5DC] text-xs font-semibold text-[#5B6845] border border-[#CFE1B9] transition-all"
                >
                  Start Fresh Session
                </button>
              )}
            </div>

            {/* Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#FAFDF7]">
              {messages.map((m, idx) => {
                const isUser = m.sender === "user";
                return (
                  <div
                    key={idx}
                    className={`flex items-start gap-3 ${
                      isUser ? "flex-row-reverse" : "flex-row"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                        isUser
                          ? "bg-[#728156] text-white"
                          : "bg-[#CFE1B9] text-[#2D3522]"
                      }`}
                    >
                      {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </div>

                    <div
                      className={`max-w-[75%] p-4 rounded-2xl shadow-xs leading-relaxed text-sm ${
                        isUser
                          ? "bg-[#728156] text-white rounded-tr-xs"
                          : "bg-white text-[#2D3522] border border-[#CFE1B9]/80 rounded-tl-xs"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{m.text}</p>
                      <span
                        className={`block text-[10px] mt-1.5 font-mono ${
                          isUser ? "text-[#E7F5DC]/80 text-right" : "text-[#88976C]"
                        }`}
                      >
                        {m.timestamp}
                      </span>
                    </div>
                  </div>
                );
              })}

              {sending && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#CFE1B9] text-[#2D3522] flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="p-4 rounded-2xl bg-white border border-[#CFE1B9]/80 shadow-xs flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-[#728156]" />
                    <span className="text-xs text-[#728156] font-medium">
                      {selectedPersona?.name} is thinking and formulating thoughts...
                    </span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Prompt Starters */}
            <div className="px-6 py-2.5 bg-white border-t border-[#F4F7F4] flex gap-2 overflow-x-auto">
              <span className="text-[10px] font-bold text-[#728156] uppercase tracking-wider shrink-0 self-center">
                Suggest:
              </span>
              {PROMPT_SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setInputMessage(s)}
                  className="px-2.5 py-1 rounded-lg bg-[#F8FAF7] hover:bg-[#E7F5DC] text-[#465135] text-[11px] font-medium whitespace-nowrap border border-[#CFE1B9]/60 transition-all cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form
              onSubmit={handleSendMessage}
              className="p-4 bg-white border-t border-[#CFE1B9]/60 flex items-center gap-3"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={`Ask ${selectedPersona?.name || "the persona"} anything...`}
                disabled={sending || !selectedPersona}
                className="flex-1 px-4 py-3 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9] focus:outline-none focus:ring-2 focus:ring-[#728156] text-sm text-[#2D3522] placeholder:text-[#98A77C]/70"
              />
              <button
                type="submit"
                disabled={sending || !inputMessage.trim() || !selectedPersona}
                className="px-5 py-3 bg-[#728156] hover:bg-[#5B6845] text-white rounded-2xl text-sm font-bold shadow-xs hover:shadow-md transition-all flex items-center gap-2 cursor-pointer disabled:opacity-40"
              >
                {sending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span>Send</span>
              </button>
            </form>
          </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function InterviewsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-[#728156]" />
        </div>
      }
    >
      <InterviewsContent />
    </Suspense>
  );
}
