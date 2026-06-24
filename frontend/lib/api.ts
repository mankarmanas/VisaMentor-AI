import { auth } from "@/lib/firebase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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

export interface Session {
  id: string;
  title: string;
  created_at: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface UserProfile {
  has_profile: boolean;
  name?: string;
  email?: string;
  photo_url?: string;
  university?: string;
  program?: string;
  program_start_date?: string;
  program_end_date?: string;
  stem_eligible?: boolean;
}

export interface ProfileData {
  university: string;
  program: string;
  program_start_date: string;
  program_end_date: string;
  stem_eligible: boolean;
}

export class ApiClient {
  private sessionId: string | null = null;

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const uid = auth.currentUser?.uid;
    if (uid) {
      headers["x-user-uid"] = uid;
    }
    return headers;
  }

  async registerUser(): Promise<{ has_profile: boolean }> {
    const user = auth.currentUser;
    if (!user) return { has_profile: false };

    const response = await fetch(`${API_BASE}/users/register`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        email: user.email || "",
        name: user.displayName || "",
        photo_url: user.photoURL || "",
        university: "",
        program: "",
        program_end_date: "2025-01-01",
        stem_eligible: false,
      }),
    });

    if (!response.ok) return { has_profile: false };
    return await response.json();
  }

  async getProfile(): Promise<UserProfile> {
    const response = await fetch(`${API_BASE}/users/profile`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) return { has_profile: false };
    return await response.json();
  }

  async saveProfile(data: ProfileData): Promise<void> {
    await fetch(`${API_BASE}/users/profile`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
  }

  async sendMessage(question: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: this.getHeaders(),
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

  async getSessions(): Promise<Session[]> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) return [];
    const data = await response.json();
    return data.sessions;
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (!response.ok) return [];
    const data = await response.json();
    return data.messages;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
  }

  resetSession(): void {
    this.sessionId = null;
  }

  getSessionId(): string | null {
    return this.sessionId;
  }
}

export const apiClient = new ApiClient();