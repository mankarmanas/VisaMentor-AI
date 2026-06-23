import { useState } from "react";

interface ChatInputProps {
  onSend: (question: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-700 p-4 bg-gray-900">
      <div className="flex gap-3 items-end">

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about OPT, CPT, STEM OPT, EAD..."
          disabled={isLoading}
          rows={1}
          className="flex-1 bg-gray-800 text-gray-100 placeholder-gray-500 
                     rounded-xl px-4 py-3 text-sm resize-none outline-none 
                     border border-gray-700 focus:border-blue-500
                     disabled:opacity-50"
        />

        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 
                     disabled:cursor-not-allowed text-white rounded-xl 
                     px-4 py-3 text-sm font-medium transition-colors"
        >
          {isLoading ? "..." : "Send"}
        </button>

      </div>
    </div>
  );
}