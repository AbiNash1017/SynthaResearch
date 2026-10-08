import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "SynthaResearch | Universal Synthetic User Research Platform",
  description:
    "AI-powered synthetic user research simulations, persona generation, automated surveys, 1-on-1 qualitative interviews, and deep insights.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex bg-[#F8FAF7] text-[#1C2417]">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {children}
        </div>
      </body>
    </html>
  );
}
