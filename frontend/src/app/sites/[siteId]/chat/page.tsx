"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage({ params }: { params: { siteId: string } }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const chatMutation = useMutation({
    mutationFn: (newMessage: string) => {
      return api.post("/chat/completions", {
        message: newMessage,
        site_id: parseInt(params.siteId, 10),
      });
    },
    onSuccess: (data) => {
      // Add the assistant's response to the message history
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.data.response },
      ]);
    },
    onError: (error: any) => {
        setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Error: ${error.response?.data?.detail || error.message}` },
        ]);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user's message to history
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    // Call the mutation
    chatMutation.mutate(input);

    // Clear the input field
    setInput("");
  };

  return (
    <div className="flex flex-col h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Chat with Site {params.siteId}</h1>
      <div className="flex-1 overflow-y-auto mb-4 p-4 border rounded">
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-3 rounded-lg max-w-lg ${
                  msg.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>
      </div>
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the site..."
          className="flex-1 p-2 border rounded-l-lg"
          disabled={chatMutation.isPending}
        />
        <button
          type="submit"
          className="p-2 bg-blue-500 text-white rounded-r-lg disabled:bg-blue-300"
          disabled={chatMutation.isPending}
        >
          {chatMutation.isPending ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}
