"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api";
import type { ChatResponse } from "@/lib/api";
import MessageBubble from "@/components/chat/MessageBubble";
import ChatInput from "@/components/chat/ChatInput";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
}

interface ChatWindowProps {
  sessionId?: string | null;
}

export default function ChatWindow({ sessionId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadMessages = useCallback(async (sid: string) => {
    const data = await apiClient.getMessages(sid);
    const loaded: Message[] = data.map((m) => ({
      role: m.role as "user" | "assistant",
      content: m.content,
    }));
    setMessages(loaded);
    apiClient["sessionId" as keyof typeof apiClient] = sid as never;
  }, []);

  useEffect(() => {
    if (sessionId) {
      loadMessages(sessionId);
    } else {
      setMessages([]);
    }
  }, [sessionId, loadMessages]);

  const handleSend = async (question: string) => {
    const userMessage: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage(question);
      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: Message = {
        role: "assistant",
        content: "Something went wrong. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <p className="text-gray-400 text-lg font-medium">Ask me anything about F1 visa</p>
            <p className="text-gray-600 text-sm mt-2">OPT · STEM OPT · CPT · EAD · SEVIS</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            content={msg.content}
            sources={msg.sources}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-800 text-gray-400 rounded-2xl px-4 py-3 text-sm">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}