import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Auth Types
type UserRole = 'admin' | 'analyst' | 'viewer';

interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  company: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check localStorage for existing user on mount
    try {
      const savedUser = localStorage.getItem('finq_user');
      const savedToken = localStorage.getItem('finq_token');

      if (savedUser && savedToken) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      }
    } catch (error) {
      console.error('Error loading user from localStorage:', error);
      localStorage.removeItem('finq_user');
      localStorage.removeItem('finq_token');
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();

      // Store token
      localStorage.setItem('finq_token', data.token);

      // Store user
      setUser(data.user);
      localStorage.setItem('finq_user', JSON.stringify(data.user));
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(error.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem('finq_user');
      localStorage.removeItem('finq_token');
    } catch (error) {
      console.error('Error removing user from localStorage:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
