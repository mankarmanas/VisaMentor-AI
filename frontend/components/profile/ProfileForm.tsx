"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";

interface ProfileData {
  university: string;
  program: string;
  program_start_date: string;
  program_end_date: string;
  stem_eligible: boolean;
}

interface ProfileFormProps {
  onComplete: (data: ProfileData) => void;
  isSettings?: boolean;
}

export default function ProfileForm({ onComplete, isSettings = false }: ProfileFormProps) {
  const [form, setForm] = useState<ProfileData>({
    university: "",
    program: "",
    program_start_date: "",
    program_end_date: "",
    stem_eligible: false,
  });
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(isSettings);

  useEffect(() => {
    if (isSettings) {
      apiClient.getProfile().then((profile) => {
        if (profile.has_profile) {
          setForm({
            university: profile.university || "",
            program: profile.program || "",
            program_start_date: profile.program_start_date || "",
            program_end_date: profile.program_end_date || "",
            stem_eligible: profile.stem_eligible || false,
          });
        }
        setFetching(false);
      });
    }
  }, [isSettings]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onComplete(form);
    setLoading(false);
  };

  if (fetching) {
    return <p className="text-gray-400 text-sm text-center">Loading your profile...</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div>
        <label className="text-gray-400 text-sm mb-1 block">University</label>
        <input
          type="text"
          required
          placeholder="e.g. University of Texas at Dallas"
          value={form.university}
          onChange={(e) => setForm({ ...form, university: e.target.value })}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="text-gray-400 text-sm mb-1 block">Program / Major</label>
        <input
          type="text"
          required
          placeholder="e.g. MS Computer Science"
          value={form.program}
          onChange={(e) => setForm({ ...form, program: e.target.value })}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="text-gray-400 text-sm mb-1 block">Program Start Date</label>
        <input
          type="date"
          required
          value={form.program_start_date}
          onChange={(e) => setForm({ ...form, program_start_date: e.target.value })}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="text-gray-400 text-sm mb-1 block">Program End Date</label>
        <input
          type="date"
          required
          value={form.program_end_date}
          onChange={(e) => setForm({ ...form, program_end_date: e.target.value })}
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="stem"
          checked={form.stem_eligible}
          onChange={(e) => setForm({ ...form, stem_eligible: e.target.checked })}
          className="w-4 h-4 accent-blue-500"
        />
        <label htmlFor="stem" className="text-gray-400 text-sm">
          My program is STEM eligible
        </label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-3 text-sm font-medium transition-colors disabled:opacity-50 mt-2"
      >
        {loading ? "Saving..." : isSettings ? "Update Profile" : "Get Started"}
      </button>
    </form>
  );
}