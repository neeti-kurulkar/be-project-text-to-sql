export interface AnalysisResult {
  analysis_id: string;
  question: string;
  sql_query: string | null;
  results: Record<string, any>[] | null;
  columns: string[] | null;
  row_count: number;
  insights: string | null;
  summary: string | null;
  visualizations: VisualizationResult | null;
  error: string | null;
  status: 'success' | 'error' | 'processing';
}

export interface VisualizationResult {
  visualized: boolean;
  reason: string;
  charts: Chart[];
  error: string | null;
}

export interface Chart {
  type: string;
  title: string;
  path: string;
  description: string;
}

export interface SampleQuestion {
  id: number;
  question: string;
  category: string;
}

// Authentication Types
export type UserRole = 'Admin' | 'Analyst';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  company: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// Theme Types
export type Theme = 'light' | 'dark';

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}