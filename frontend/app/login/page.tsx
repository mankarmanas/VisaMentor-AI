"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithGoogle, onAuthChange } from "@/lib/auth";

const TAGS = ["I-20", "CPT", "OPT", "STEM OPT", "SEVIS", "EAD"];

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthChange((user) => {
      if (user) router.push("/");
    });
    return () => unsubscribe();
  }, [router]);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
      router.push("/");
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen bg-[#07070f] flex overflow-hidden">

      {/* ── Left Panel ── */}
      <div className="flex-1 border-r border-white/[0.06] px-14 py-10 flex flex-col">
        <div className="mx-auto flex flex-col h-full">

          {/* Logo */}
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl border border-violet-500/50 bg-violet-500/10 flex items-center justify-center flex-shrink-0">
              <svg width="38" height="44" viewBox="0 0 42 48" fill="none">
                <line x1="3" y1="12" x2="39" y2="12" stroke="rgba(108,92,231,0.15)" strokeWidth="0.8"/>
                <line x1="3" y1="28" x2="39" y2="28" stroke="rgba(240,165,0,0.15)" strokeWidth="0.8"/>
                <line x1="21" y1="3" x2="3" y2="12" stroke="rgba(108,92,231,0.55)" strokeWidth="1"/>
                <line x1="21" y1="3" x2="39" y2="12" stroke="rgba(240,165,0,0.55)" strokeWidth="1"/>
                <line x1="3" y1="12" x2="3" y2="28" stroke="rgba(108,92,231,0.55)" strokeWidth="1"/>
                <line x1="39" y1="12" x2="39" y2="28" stroke="rgba(240,165,0,0.55)" strokeWidth="1"/>
                <line x1="3" y1="28" x2="21" y2="45" stroke="rgba(108,92,231,0.55)" strokeWidth="1"/>
                <line x1="39" y1="28" x2="21" y2="45" stroke="rgba(240,165,0,0.55)" strokeWidth="1"/>
                <path d="M21 3L3 12V28C3 37 11 44 21 45C31 44 39 37 39 28V12L21 3Z" stroke="#6c5ce7" strokeWidth="1.2" fill="rgba(108,92,231,0.07)"/>
                <path d="M21 14L16 24H21L18.5 34L28 22H22.5L25 14Z" stroke="#f0a500" strokeWidth="1.3" fill="none" strokeLinejoin="round"/>
                <circle cx="21" cy="3" r="3" fill="#6c5ce7"/>
                <circle cx="3" cy="12" r="3" fill="#6c5ce7"/>
                <circle cx="39" cy="12" r="3" fill="#f0a500"/>
                <circle cx="3" cy="28" r="3" fill="#6c5ce7"/>
                <circle cx="39" cy="28" r="3" fill="#f0a500"/>
                <circle cx="21" cy="45" r="3" fill="#f0a500"/>
              </svg>
            </div>
            <span className="text-white text-[30px] font-bold tracking-tight">
              VisaMentor‑<span className="text-amber-400">AI</span>
            </span>
          </div>

          {/* Hero */}
          <div className="flex-1 flex items-center">
            <div className="flex flex-col gap-5">
              <span className="text-[13px] font-bold tracking-[0.22em] text-violet-400 uppercase">
                F‑1 Student Visa Assistant
              </span>
              <h1 className="text-[52px] font-black leading-[1.1] tracking-tight whitespace-nowrap">
                <span className="text-white">Navigate your visa </span>
                <span className="text-violet-400">with confidence</span>
              </h1>
              <p className="text-[16px] text-gray-400 leading-[1.75] max-w-[580px]">
                Personalized OPT, CPT, and STEM OPT timelines calculated from
                your actual program dates — powered by official USCIS documentation.
              </p>
              <div className="w-10 h-px bg-violet-500/25 my-1" />
              <div className="flex flex-col gap-4">
                <FeatureRow icon={<ClockIcon />}  title="Exact date calculations" desc="OPT, STEM OPT, CPT timelines for your program" />
                <FeatureRow icon={<ShieldIcon />} title="Official sources only"   desc="Answers from USCIS, ICE, and SEVP docs" />
                <FeatureRow icon={<ChatIcon />}   title="Session memory"          desc="Your conversations saved across sessions" />
              </div>
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 pt-6 border-t border-white/[0.05]">
            {TAGS.map((tag) => (
              <span
                key={tag}
                className={`px-4 py-1.5 rounded-full text-[13px] font-medium border ${
                  tag === "STEM OPT"
                    ? "border-amber-500/60 text-amber-400 bg-amber-500/[0.07]"
                    : tag === "EAD"
                    ? "border-amber-800/50 text-amber-700/70"
                    : "border-white/10 text-gray-500 bg-white/[0.025]"
                }`}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right Panel ── */}
      <div className="w-[390px] flex flex-col justify-center px-10 py-10 gap-6">
        <div className="flex flex-col gap-2">
          <h2 className="text-white text-[24px] font-bold tracking-tight leading-tight">Get started</h2>
          <p className="text-[13px] text-gray-400 leading-[1.7]">
            Sign in to access your personalized F‑1 visa assistant with calculated dates and AI guidance.
          </p>
        </div>

        <div className="h-px bg-white/[0.06]" />

        <button
          type="button"
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 active:scale-[0.985] text-gray-900 font-semibold py-3 rounded-xl transition-all duration-150 text-[13.5px] shadow-2xl shadow-black/40 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <GoogleIcon />
          {loading ? "Signing in..." : "Continue with Google"}
        </button>

        {error && (
          <p className="text-red-400 text-[12px] text-center -mt-2">{error}</p>
        )}

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-white/[0.07]" />
          <span className="text-[10px] text-gray-600 tracking-[0.15em] uppercase">secure · private</span>
          <div className="flex-1 h-px bg-white/[0.07]" />
        </div>

        <div className="flex items-center justify-around py-4 px-3 rounded-2xl bg-white/[0.02] border border-white/[0.05]">
          <TrustBadge icon={<LockIcon />}    label="Encrypted" />
          <div className="w-px h-8 bg-white/[0.06]" />
          <TrustBadge icon={<NoShareIcon />} label="Never shared" />
          <div className="w-px h-8 bg-white/[0.06]" />
          <TrustBadge icon={<StorageIcon />} label="Secure storage" />
        </div>

        <p className="text-[11px] text-gray-600 text-center leading-relaxed">
          By signing in, your profile and chat history are securely stored and tied to your Google account. We never share your data.
        </p>
      </div>
    </div>
  );
}

function FeatureRow({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3.5">
      <div className="w-9 h-9 rounded-lg bg-violet-500/[0.08] border border-violet-500/[0.18] flex items-center justify-center text-violet-400 flex-shrink-0 mt-[2px]">
        {icon}
      </div>
      <p className="text-[15px] text-gray-400 leading-snug pt-[5px]">
        <span className="text-gray-100 font-semibold">{title}</span>{" — "}{desc}
      </p>
    </div>
  );
}

function TrustBadge({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="text-gray-500">{icon}</div>
      <span className="text-[10px] text-gray-600 font-medium">{label}</span>
    </div>
  );
}

function ClockIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 13 13" fill="none">
      <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M6.5 4v2.8l1.8 1.8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 1L2 3.5V7c0 2.8 2 5 4.5 5.5C9 12 11 9.8 11 7V3.5L6.5 1Z" stroke="currentColor" strokeWidth="1.2" fill="none"/>
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 13 13" fill="none">
      <rect x="1" y="1.5" width="11" height="7.5" rx="1.2" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M4 11.5l2.5-2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <path d="M3.5 5.5h6M3.5 7.5h4" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="2" y="6" width="10" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.1"/>
      <path d="M4.5 6V4.5a2.5 2.5 0 0 1 5 0V6" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <circle cx="7" cy="9.5" r="1" fill="currentColor"/>
    </svg>
  );
}

function NoShareIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.1"/>
      <path d="M7 4v3.5M7 9.5v.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

function StorageIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <ellipse cx="7" cy="4" rx="5" ry="2" stroke="currentColor" strokeWidth="1.1"/>
      <path d="M2 4v6c0 1.1 2.24 2 5 2s5-.9 5-2V4" stroke="currentColor" strokeWidth="1.1"/>
      <path d="M2 7c0 1.1 2.24 2 5 2s5-.9 5-2" stroke="currentColor" strokeWidth="1.1"/>
    </svg>
  );
}

function GoogleIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 18 18" fill="none">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908C16.658 14.233 17.64 11.927 17.64 9.2Z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18Z" fill="#34A853"/>
      <path d="M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332Z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.961L3.964 6.293C4.672 4.166 6.656 3.58 9 3.58Z" fill="#EA4335"/>
    </svg>
  );
}