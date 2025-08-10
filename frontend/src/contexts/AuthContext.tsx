"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import api from "@/lib/api";
import { jwtDecode } from "jwt-decode"; // You'll need to install jwt-decode

interface User {
  id: number; // Our integer ID from the backend
  email: string;
  name: string;
  org_id: number;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          // Set token for the api client
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          // Fetch user profile from our backend
          const response = await api.get("/users/me");
          setUser(response.data);
          setToken(storedToken);
        } catch (error) {
          console.error("Failed to fetch user or invalid token:", error);
          localStorage.removeItem("token");
        }
      }
      setIsLoading(false);
    };
    initializeAuth();
  }, []);

  const login = async (newToken: string) => {
    localStorage.setItem("token", newToken);
    api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    const response = await api.get("/users/me");
    setUser(response.data);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
