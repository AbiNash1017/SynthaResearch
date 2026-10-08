"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  Users,
  ClipboardList,
  MessageSquare,
  BarChart3,
  Settings,
  Sparkles,
  Bot,
  Activity,
} from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LLMConfig } from "@/types/api";

const NAV_ITEMS = [
  {
    name: "Workspace & Setup",
    href: "/",
    icon: Compass,
    badge: "Step 1",
  },
  {
    name: "Synthetic Personas",
    href: "/personas",
    icon: Users,
    badge: "Step 2",
  },
  {
    name: "Surveys & Matrix",
    href: "/surveys",
    icon: ClipboardList,
    badge: "Step 3",
  },
  {
    name: "Live Interviews",
    href: "/interviews",
    icon: MessageSquare,
    badge: "Step 4",
  },
  {
    name: "Analytics & Reports",
    href: "/reports",
    icon: BarChart3,
    badge: "Step 5",
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [llmConfig, setLlmConfig] = useState<LLMConfig | null>(null);
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);

  useEffect(() => {
    api
      .checkHealth()
      .then((data) => {
        setServerOnline(true);
        setLlmConfig(data.llm_config);
      })
      .catch(() => {
        setServerOnline(false);
      });
  }, []);

  return (
    <aside className="w-72 bg-white/90 backdrop-blur-md border-r border-[#CFE1B9]/60 flex flex-col justify-between shrink-0 h-screen sticky top-0 shadow-sm z-30">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-[#E7F5DC]/80 flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#728156] to-[#98A77C] flex items-center justify-center text-white shadow-md shadow-[#728156]/20">
            <Sparkles className="w-5 h-5 text-[#E7F5DC]" />
          </div>
          <div>
            <h1 className="text-base font-bold text-[#2D3522] tracking-tight leading-none">
              SynthaResearch
            </h1>
            <p className="text-[11px] font-medium text-[#728156] mt-1 tracking-wide uppercase">
              Synthetic User Lab
            </p>
          </div>
        </div>

        {/* Navigation items */}
        <div className="px-4 py-6 space-y-1.5">
          <div className="px-3 pb-2 text-[10px] font-bold tracking-wider text-[#728156] uppercase">
            Simulation Pipeline
          </div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`group flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-[#E7F5DC] text-[#465135] font-semibold shadow-xs border border-[#CFE1B9]"
                    : "text-[#5B6845] hover:bg-[#F4F7F4] hover:text-[#2D3522]"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`p-1.5 rounded-lg transition-colors ${
                      isActive
                        ? "bg-[#728156] text-white shadow-xs"
                        : "text-[#728156] group-hover:bg-[#E7F5DC]"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span>{item.name}</span>
                </div>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-medium ${
                    isActive
                      ? "bg-[#CFE1B9] text-[#2D3522]"
                      : "bg-[#F4F7F4] text-[#88976C] group-hover:bg-[#E7F5DC]"
                  }`}
                >
                  {item.badge}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* System Status Footbar */}
      <div className="p-4 m-3 rounded-2xl bg-[#F4F7F4] border border-[#CFE1B9]/60 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                serverOnline === true
                  ? "bg-emerald-500 ring-4 ring-emerald-100"
                  : serverOnline === false
                  ? "bg-rose-500 ring-4 ring-rose-100"
                  : "bg-amber-400 animate-pulse"
              }`}
            />
            <span className="text-xs font-semibold text-[#465135]">
              {serverOnline === true
                ? "Backend Connected"
                : serverOnline === false
                ? "Backend Offline"
                : "Connecting..."}
            </span>
          </div>
          <Activity className="w-3.5 h-3.5 text-[#88976C]" />
        </div>

        <div className="text-[11px] text-[#5B6845] space-y-1 pt-1 border-t border-[#CFE1B9]/50">
          <div className="flex justify-between items-center">
            <span className="text-[#88976C]">Engine:</span>
            <span className="font-mono text-[#465135] text-[10px] truncate max-w-[120px]">
              {llmConfig?.model ? llmConfig.model.split("/")[1] || llmConfig.model : "OpenRouter"}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#88976C]">Port:</span>
            <span className="font-mono text-[#465135] text-[10px]">:8000</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function Header({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="px-8 py-6 bg-white/60 backdrop-blur-md border-b border-[#CFE1B9]/60 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-2xl font-bold text-[#2D3522] tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-[#728156] mt-0.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </header>
  );
}
