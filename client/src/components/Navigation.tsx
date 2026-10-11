"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  Compass,
  Users,
  ClipboardList,
  MessageSquare,
  BarChart3,
  Activity,
  LogOut,
  LogIn,
} from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LLMConfig, Experiment } from "@/types/api";
import { useAuth } from "@/lib/authContext";

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
  const { user, isAuthenticated, logout } = useAuth();
  const [llmConfig, setLlmConfig] = useState<LLMConfig | null>(null);
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);
  const [activeExp, setActiveExp] = useState<Experiment | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    api
      .checkHealth()
      .then((data) => {
        setServerOnline(true);
        setLlmConfig(data.llm_config);
      })
      .catch(() => {
        setServerOnline(false);
      });

    api
      .getExperiment()
      .then((exp) => setActiveExp(exp))
      .catch(() => setActiveExp(null));
  }, [isAuthenticated, pathname]);

  if (!isAuthenticated || pathname === "/login" || pathname === "/register") {
    return null;
  }

  return (
    <aside className="w-72 bg-white/90 backdrop-blur-md border-r border-[#CFE1B9]/60 flex flex-col justify-between shrink-0 h-screen sticky top-0 shadow-sm z-30">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-[#E7F5DC]/80 flex items-center gap-3">
          <div className="relative w-10 h-10 shrink-0">
            <Image
              src="/synthra_logo_cutout.png"
              alt="SynthaResearch Logo"
              width={40}
              height={40}
              className="w-full h-full object-contain rounded-2xl drop-shadow-sm"
              priority
            />
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

        {/* Active Product Widget */}
        {activeExp && (
          <div className="mx-4 mt-4 p-3 rounded-2xl bg-[#F8FAF7] border border-[#CFE1B9]/70 flex items-center justify-between">
            <div className="min-w-0 pr-2">
              <span className="text-[9px] font-bold tracking-wider text-[#728156] uppercase block">
                Active Product
              </span>
              <p className="text-xs font-bold text-[#2D3522] truncate">
                {activeExp.product_name}
              </p>
            </div>
            <Link
              href="/"
              className="text-[10px] font-bold text-[#5B6845] hover:text-[#2D3522] px-2 py-1 rounded-lg bg-white border border-[#CFE1B9] shrink-0 transition-colors shadow-2xs"
            >
              Switch
            </Link>
          </div>
        )}

        {/* Navigation items */}
        <div className="px-4 py-5 space-y-1.5">
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

      <div className="p-3 space-y-3">
        {/* User Account / Profile Box */}
        {isAuthenticated && user ? (
          <div className="p-3 rounded-2xl bg-white border border-[#CFE1B9] shadow-xs flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-[#465135] text-[#CFE1B9] flex items-center justify-center font-bold text-xs uppercase shrink-0 shadow-xs">
                {user.full_name ? user.full_name[0] : user.email[0]}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-[#2D3522] truncate">
                  {user.full_name || user.email.split("@")[0]}
                </p>
                <p className="text-[10px] text-[#728156] truncate font-mono">
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={() => logout()}
              title="Sign Out"
              className="p-1.5 rounded-lg text-[#88976C] hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-xl bg-[#465135] hover:bg-[#353D27] text-white text-xs font-semibold shadow-xs transition-colors"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </Link>
        )}

        {/* System Status Footbar */}
        <div className="p-3.5 rounded-2xl bg-[#F4F7F4] border border-[#CFE1B9]/60 space-y-2.5">
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
              <span className="text-[#88976C]">Database:</span>
              <span className="font-mono text-[#465135] text-[10px]">MongoDB</span>
            </div>
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
