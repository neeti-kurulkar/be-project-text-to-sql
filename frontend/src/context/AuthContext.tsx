import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

// Auth Types
type UserRole = 'Admin' | 'Analyst';

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

// Mock users for authentication
const MOCK_USERS = [
  {
    id: '1',
    email: 'admin@finq.com',
    password: 'admin123',
    name: 'Sarah Chen',
    role: 'Admin' as UserRole,
    company: 'Acme Corp'
  },
  {
    id: '2',
    email: 'analyst@finq.com',
    password: 'analyst123',
    name: 'Mike Rodriguez',
    role: 'Analyst' as UserRole,
    company: 'Acme Corp'
  }
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check localStorage for existing user on mount
    try {
      const savedUser = localStorage.getItem('finq_user');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      }
    } catch (error) {
      console.error('Error loading user from localStorage:', error);
      localStorage.removeItem('finq_user');
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Find matching user
    const matchedUser = MOCK_USERS.find(
      u => u.email === email && u.password === password
    );

    if (!matchedUser) {
      throw new Error('Invalid email or password');
    }

    // Create user object (exclude password)
    const { password: _, ...userWithoutPassword } = matchedUser;
    const authenticatedUser: User = userWithoutPassword;

    // Set user state
    setUser(authenticatedUser);

    // Persist to localStorage
    try {
      localStorage.setItem('finq_user', JSON.stringify(authenticatedUser));
    } catch (error) {
      console.error('Error saving user to localStorage:', error);
    }
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem('finq_user');
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
