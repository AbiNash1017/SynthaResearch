"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, AuthResponse } from "@/types/api";
import {
  getStoredToken,
  setStoredToken,
  getStoredUser,
  setStoredUser,
  clearStoredAuth,
} from "./auth";
import { api } from "./api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (email: string, password: string, fullName?: string) => Promise<AuthResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isCancelled = false;

    // Asynchronously resolve stored credentials to comply with React 19 rules
    Promise.resolve().then(async () => {
      const storedToken = getStoredToken();
      const storedUser = getStoredUser();

      if (!storedToken) {
        if (!isCancelled) setIsLoading(false);
        return;
      }

      if (!isCancelled) {
        setToken(storedToken);
        setUser(storedUser);
      }

      try {
        const freshUser = await api.auth.getMe();
        if (!isCancelled) {
          setUser(freshUser);
          setStoredUser(freshUser);
        }
      } catch {
        clearStoredAuth();
        if (!isCancelled) {
          setUser(null);
          setToken(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    });

    return () => {
      isCancelled = true;
    };
  }, []);

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    const data = await api.auth.login({ email, password });
    setStoredToken(data.access_token);
    setStoredUser(data.user);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (
    email: string,
    password: string,
    fullName?: string
  ): Promise<AuthResponse> => {
    const data = await api.auth.register({
      email,
      password,
      full_name: fullName,
    });
    setStoredToken(data.access_token);
    setStoredUser(data.user);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch {
      // Ignore network errors on logout
    } finally {
      clearStoredAuth();
      setUser(null);
      setToken(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
