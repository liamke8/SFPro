"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function NewTemplatePage() {
  const [name, setName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [userPrompt, setUserPrompt] = useState("");
  const [model, setModel] = useState("ollama/llama3");
  const [error, setError] = useState("");
  const router = useRouter();
  const { user } = useAuth(); // Assuming the user object has org_id

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!user) {
      setError("You must be logged in to create a template.");
      return;
    }

    try {
      await api.post("/templates/", {
        name,
        system_prompt: systemPrompt,
        user_prompt: userPrompt,
        model,
        org_id: user.org_id,
      });
      router.push("/templates"); // Redirect to the list page after creation
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred.");
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Create New Prompt Template</h1>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
        {error && <p className="text-red-500">{error}</p>}
        <div>
          <label className="block mb-1">Template Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div>
          <label className="block mb-1">Model</label>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div>
          <label className="block mb-1">System Prompt (Optional)</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full p-2 border rounded"
            rows={4}
          />
        </div>
        <div>
          <label className="block mb-1">User Prompt</label>
          <textarea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            className="w-full p-2 border rounded"
            rows={8}
            required
          />
        </div>
        <button type="submit" className="p-2 bg-blue-500 text-white rounded">
          Create Template
        </button>
      </form>
    </div>
  );
}
