"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithGoogle, onAuthChange } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthChange((user) => {
      if (user) {
        router.push("/");
      }
    });
    return () => unsubscribe();
  }, [router]);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
      router.push("/");
    } catch (err) {
      setError("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-950">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-10 flex flex-col items-center gap-6 w-full max-w-sm">
        
        <div className="text-center">
          <h1 className="text-white text-2xl font-semibold">Visa Mentor AI</h1>
          <p className="text-gray-400 text-sm mt-2">F1 visa assistant for international students</p>
        </div>

        <div className="w-full border-t border-gray-800" />

        <div className="text-center">
          <p className="text-gray-300 text-sm">Sign in to continue</p>
        </div>

        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-white text-gray-900 font-medium py-3 px-4 rounded-xl hover:bg-gray-100 transition-colors disabled:opacity-50"
        >
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {loading ? "Signing in..." : "Continue with Google"}
        </button>

        {error && (
          <p className="text-red-400 text-sm text-center">{error}</p>
        )}

        <p className="text-gray-600 text-xs text-center">
          By signing in you agree to our terms of service
        </p>

      </div>
    </div>
  );
}