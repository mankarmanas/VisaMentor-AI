"use client";

import { useState, useEffect } from "react";
import { onAuthChange } from "@/lib/auth";
import type { User } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import ProfileForm from "@/components/profile/ProfileForm";
import ChatWindow from "@/components/chat/ChatWindow";
import Sidebar from "@/components/chat/Sidebar";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProfile, setShowProfile] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [resetKey, setResetKey] = useState(0);

  useEffect(() => {
    const unsubscribe = onAuthChange(async (u) => {
      if (!u) {
        window.location.href = "/login";
        return;
      }

      setUser(u);

      // register user in DB (saves name, email, photo)
      const result = await apiClient.registerUser();

      // if no profile → show profile form
      if (!result.has_profile) {
        setShowProfile(true);
      }

      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleProfileComplete = async (data: {
    university: string;
    program: string;
    program_end_date: string;
    stem_eligible: boolean;
  }) => {
    await apiClient.saveProfile(data);
    setShowProfile(false);
  };

  const handleSettingsComplete = async (data: {
    university: string;
    program: string;
    program_end_date: string;
    stem_eligible: boolean;
  }) => {
    await apiClient.saveProfile(data);
    setShowSettings(false);
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setResetKey((k) => k + 1);
  };

  const handleSessionSelect = (sessionId: string) => {
    apiClient["sessionId" as keyof typeof apiClient] = sessionId as never;
    setCurrentSessionId(sessionId);
    setResetKey((k) => k + 1);
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-950">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  if (showProfile) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-950">
        <div className="w-full max-w-md px-6">
          <h1 className="text-white text-2xl font-semibold mb-2 text-center">
            Welcome to Visa Mentor AI
          </h1>
          <p className="text-gray-400 text-sm text-center mb-8">
            Tell us about yourself so we can personalize your answers
          </p>
          <ProfileForm onComplete={handleProfileComplete} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <div className="flex items-center px-4 py-3 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <Sidebar
              currentSessionId={currentSessionId}
              onSessionSelect={handleSessionSelect}
              onNewChat={handleNewChat}
              onOpenSettings={() => setShowSettings(true)}
            />
            <span className="text-white font-semibold">Visa Mentor AI</span>
          </div>
        </div>

        <ChatWindow key={resetKey} sessionId={currentSessionId} />
      </div>

      {/* Settings modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center">
          <div className="bg-gray-900 rounded-2xl w-full max-w-md px-6 py-8 mx-4 relative">
            <button
              onClick={() => setShowSettings(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <h2 className="text-white text-xl font-semibold mb-6">Update Profile</h2>
            <ProfileForm onComplete={handleSettingsComplete} isSettings={true} />
          </div>
        </div>
      )}
    </div>
  );
}