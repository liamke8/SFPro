"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface Template {
  id: number;
  name: string;
  model: string;
}

export default function TemplatesPage() {
  const { user } = useAuth();

  const { data: templates, isLoading, error } = useQuery<Template[]>({
    queryKey: ["templates", user?.org_id],
    queryFn: async () => {
      if (!user) return [];
      const response = await api.get(`/templates/org/${user.org_id}`);
      return response.data;
    },
    enabled: !!user, // Only run the query if the user is loaded
  });

  if (isLoading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">An error has occurred: {error.message}</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Prompt Templates</h1>
        <Link href="/templates/new" className="p-2 bg-blue-500 text-white rounded">
          Create New Template
        </Link>
      </div>
      <div className="space-y-4">
        {templates && templates.length > 0 ? (
          templates.map((template) => (
            <div key={template.id} className="p-4 border rounded shadow-sm">
              <h2 className="text-lg font-semibold">{template.name}</h2>
              <p className="text-sm text-gray-500">Model: {template.model}</p>
            </div>
          ))
        ) : (
          <p>No templates found. Create one!</p>
        )}
      </div>
    </div>
  );
}
