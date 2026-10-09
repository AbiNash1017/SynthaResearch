"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/authContext";
import {
  Sparkles,
  Mail,
  Lock,
  User,
  ArrowRight,
  Loader2,
  AlertCircle,
  Eye,
  EyeOff,
  Users,
  Compass,
} from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await register(email, password, fullName || undefined);
      router.push("/");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to create account. Please try again.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-10 bg-gradient-to-br from-[#F8FAF7] via-[#F2F6F0] to-[#E8F0E4]">
      {/* Centered Modern Auth Split Card */}
      <div className="w-full max-w-5xl bg-white/95 backdrop-blur-xl rounded-[32px] border border-[#CFE1B9]/80 shadow-2xl shadow-[#465135]/10 overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[660px]">
        {/* LEFT COLUMN: Registration Form */}
        <div className="lg:col-span-6 p-6 sm:p-10 lg:p-12 flex flex-col justify-between order-2 lg:order-1">
          <div>
            {/* Brand Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="relative w-11 h-11 shrink-0">
                <Image
                  src="/synthra_logo_cutout.png"
                  alt="SynthaResearch Logo"
                  width={44}
                  height={44}
                  className="w-full h-full object-contain rounded-2xl drop-shadow-sm"
                  priority
                />
              </div>
              <div>
                <h2 className="text-lg font-bold text-[#2D3522] tracking-tight">
                  SynthaResearch
                </h2>
                <p className="text-[11px] font-medium text-[#728156] tracking-wide uppercase">
                  Universal User Lab
                </p>
              </div>
            </div>

            <div className="mb-6">
              <h1 className="text-2xl font-bold text-[#1C2417] tracking-tight">
                Create Your Account
              </h1>
              <p className="text-xs text-[#728156] mt-1">
                Get started with autonomous persona generation and AI simulation.
              </p>
            </div>

            {/* Error Banner */}
            {error && (
              <div className="mb-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200/80 flex items-start gap-2.5 text-rose-700 text-xs">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-500 mt-0.5" />
                <div>
                  <p className="font-semibold text-rose-800">Registration Failed</p>
                  <p className="mt-0.5 text-rose-600">{error}</p>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-[#465135] uppercase tracking-wider mb-1">
                  Full Name (Optional)
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#88976C] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Morgan"
                    className="w-full pl-10 pr-4 py-2 bg-[#F8FAF7] border border-[#CFE1B9] rounded-xl text-sm text-[#1C2417] focus:outline-none focus:ring-2 focus:ring-[#728156] focus:border-transparent transition-all placeholder:text-[#88976C]/60"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#465135] uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#88976C] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    required
                    className="w-full pl-10 pr-4 py-2 bg-[#F8FAF7] border border-[#CFE1B9] rounded-xl text-sm text-[#1C2417] focus:outline-none focus:ring-2 focus:ring-[#728156] focus:border-transparent transition-all placeholder:text-[#88976C]/60"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#465135] uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#88976C] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    required
                    minLength={6}
                    className="w-full pl-10 pr-10 py-2 bg-[#F8FAF7] border border-[#CFE1B9] rounded-xl text-sm text-[#1C2417] focus:outline-none focus:ring-2 focus:ring-[#728156] focus:border-transparent transition-all placeholder:text-[#88976C]/60"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#88976C] hover:text-[#465135] transition-colors p-1"
                    title={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#465135] uppercase tracking-wider mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#88976C] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat your password"
                    required
                    minLength={6}
                    className="w-full pl-10 pr-10 py-2 bg-[#F8FAF7] border border-[#CFE1B9] rounded-xl text-sm text-[#1C2417] focus:outline-none focus:ring-2 focus:ring-[#728156] focus:border-transparent transition-all placeholder:text-[#88976C]/60"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#88976C] hover:text-[#465135] transition-colors p-1"
                    title={showConfirmPassword ? "Hide password" : "Show password"}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-4 bg-[#465135] hover:bg-[#353D27] text-white rounded-xl text-sm font-semibold shadow-md shadow-[#465135]/20 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed mt-3"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creating account...</span>
                  </>
                ) : (
                  <>
                    <span>Create Free Account</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Bottom Switch to Login */}
          <div className="mt-6 pt-4 border-t border-[#CFE1B9]/40 text-center text-xs text-[#728156]">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-bold text-[#465135] hover:text-[#2D3522] hover:underline transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* RIGHT COLUMN: Illustration (signup.jpg) */}
        <div className="lg:col-span-6 relative bg-[#E7F0E2] min-h-[340px] sm:min-h-[420px] lg:min-h-full flex flex-col justify-between p-6 sm:p-8 overflow-hidden group order-1 lg:order-2">
          <Image
            src="/signup.jpg"
            alt="Multi-Persona User Research Team"
            fill
            priority
            sizes="(max-width: 1024px) 100vw, 50vw"
            className="object-cover object-center group-hover:scale-105 transition-transform duration-700 ease-out"
          />

          {/* Ambient overlay gradient */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#1C2417]/85 via-[#1C2417]/25 to-transparent pointer-events-none" />

          {/* Top Badge */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-md border border-white/60 shadow-sm text-xs font-semibold text-[#2D3522]">
              <Sparkles className="w-3.5 h-3.5 text-[#728156]" />
              <span>Persona Synthesis</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#1C2417]/60 backdrop-blur-md border border-white/20 text-[11px] font-mono text-[#CFE1B9]">
              <Compass className="w-3 h-3 text-[#CFE1B9]" />
              <span>5-Step Pipeline</span>
            </div>
          </div>

          {/* Bottom Highlights Card */}
          <div className="relative z-10 space-y-3 mt-auto">
            <div className="p-5 rounded-2xl bg-white/85 backdrop-blur-md border border-white/70 shadow-lg space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#465135] text-[#CFE1B9] flex items-center justify-center">
                  <Users className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-[#1C2417]">
                  Demographically Grounded Personas
                </h3>
              </div>
              <p className="text-xs text-[#5B6845] leading-relaxed">
                Generate high-fidelity target audiences with realistic biases, technical literacy, psychological traits, and authentic reactions.
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#E7F5DC] text-[#465135] border border-[#CFE1B9]">
                  Cognitive Profiles
                </span>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-[#E7F5DC] text-[#465135] border border-[#CFE1B9]">
                  Qualitative Insights
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
