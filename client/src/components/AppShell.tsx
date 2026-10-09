"use client";

import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/authContext";
import { Sidebar } from "@/components/Navigation";
import { useEffect } from "react";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const isAuthRoute = pathname === "/login" || pathname === "/register";

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated && !isAuthRoute) {
      router.replace("/login");
    } else if (isAuthenticated && isAuthRoute) {
      router.replace("/");
    }
  }, [isLoading, isAuthenticated, isAuthRoute, router]);

  return (
    <div className="min-h-screen flex w-full bg-[#F8FAF7] text-[#1C2417]">
      {isAuthenticated && !isAuthRoute && <Sidebar />}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto w-full">
        {children}
      </main>
    </div>
  );
}
