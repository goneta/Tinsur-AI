"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface User {
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string) => boolean;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const ALLOWED_USERS = ["user-001", "user-002", "user-003"];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore auth state from localStorage on mount
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem("auth-user");
      if (savedUser && ALLOWED_USERS.includes(savedUser)) {
        setUser({ username: savedUser });
      }
    } catch (error) {
      // Handle localStorage unavailable or other errors
      console.warn("Failed to restore auth state from localStorage:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = (username: string): boolean => {
    if (ALLOWED_USERS.includes(username)) {
      setUser({ username });
      try {
        localStorage.setItem("auth-user", username);
      } catch (error) {
        console.warn("Failed to save auth state to localStorage:", error);
      }
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem("auth-user");
    } catch (error) {
      console.warn("Failed to clear auth state from localStorage:", error);
    }
  };

  const isAuthenticated = !isLoading && user !== null;

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
