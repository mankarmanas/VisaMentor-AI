"use client";

import { useState, useEffect } from "react";
import { onAuthChange, signOutUser } from "@/lib/auth";
import type { User } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import type { Session } from "@/lib/api";

interface SidebarProps {
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
  onOpenSettings: () => void;
}

export default function Sidebar({
  currentSessionId,
  onSessionSelect,
  onNewChat,
  onOpenSettings,
}: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    const unsubscribe = onAuthChange((u) => {
      setUser(u);
      if (u) loadSessions();
    });
    return () => unsubscribe();
  }, []);

  const loadSessions = async () => {
    const data = await apiClient.getSessions();
    setSessions(data);
  };

  const handleSignOut = async () => {
    await signOutUser();
    window.location.href = "/login";
  };

  const handleNewChat = () => {
    apiClient.resetSession();
    onNewChat();
    setIsOpen(false);
    loadSessions();
  };

  const handleSessionClick = (sessionId: string) => {
    onSessionSelect(sessionId);
    setIsOpen(false);
  };

  const handleOpen = () => {
    setIsOpen(true);
    loadSessions();
  };

  const handleDeleteSession = async (sessionId: string) => {
    await apiClient.deleteSession(sessionId);
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      onNewChat();
      apiClient.resetSession();
    }
  };

  return (
    <>
      {/* Hamburger button */}
      <button
        onClick={handleOpen}
        className="p-2 text-gray-400 hover:text-white transition-colors"
        aria-label="Open menu"
      >
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <div
        className={`fixed top-0 left-0 h-full w-72 bg-gray-900 border-r border-gray-800 z-50 transform transition-transform duration-300 flex flex-col ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
          <h2 className="text-white font-semibold">Visa Mentor AI</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* New chat button */}
        <div className="px-3 py-3 border-b border-gray-800">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto px-3 py-3">
          <p className="text-gray-600 text-xs uppercase tracking-wider px-2 mb-2">Recent chats</p>
          {sessions.length === 0 ? (
            <p className="text-gray-600 text-sm px-2">No previous chats</p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`group flex items-center justify-between rounded-lg mb-1 px-3 py-2 ${
                  currentSessionId === session.id
                    ? "bg-gray-700"
                    : "hover:bg-gray-800"
                }`}
              >
                <button
                  onClick={() => handleSessionClick(session.id)}
                  className="flex-1 text-left"
                >
                  <p className={`truncate text-sm ${
                    currentSessionId === session.id ? "text-white" : "text-gray-400 group-hover:text-white"
                  }`}>
                    {session.title}
                  </p>
                  <p className="text-xs text-gray-600 mt-0.5">
                    {new Date(session.created_at).toLocaleDateString()}
                  </p>
                </button>

                <button
                  onClick={() => handleDeleteSession(session.id)}
                  className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all ml-2"
                >
                  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6l-1 14H6L5 6" />
                    <path d="M10 11v6M14 11v6" />
                    <path d="M9 6V4h6v2" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        {/* User profile at bottom */}
        {user && (
          <div className="px-4 py-4 border-t border-gray-800">
            <div className="flex items-center gap-3 mb-3">
              {user.photoURL && (
                <img
                  src={user.photoURL}
                  alt="Profile"
                  className="w-8 h-8 rounded-full"
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">{user.displayName}</p>
                <p className="text-gray-500 text-xs truncate">{user.email}</p>
              </div>
              <button
                onClick={onOpenSettings}
                className="text-gray-400 hover:text-white transition-colors"
                title="Settings"
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                </svg>
              </button>
            </div>
            <button
              onClick={handleSignOut}
              className="w-full text-left text-sm text-gray-400 hover:text-white transition-colors px-2 py-1"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </>
  );
}