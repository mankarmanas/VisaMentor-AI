const API_BASE = "http://localhost:8000/api/v1";

export interface Source {
  source: string;
  category: string;
  url: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  chunks_used: number;
  session_id: string;
}

export interface ChatRequest {
  question: string;
  session_id: string | null;
}


export class ApiClient {
  private sessionId: string | null = null;

  async sendMessage(question: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        session_id: this.sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data: ChatResponse = await response.json();
    this.sessionId = data.session_id;
    return data;
  }

  async clearHistory(): Promise<void> {
    if (!this.sessionId) return;

    await fetch(`${API_BASE}/chat/clear`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ session_id: this.sessionId }),
    });

    this.sessionId = null;
  }

  getSessionId(): string | null {
    return this.sessionId;
  }
}

export const apiClient = new ApiClient();