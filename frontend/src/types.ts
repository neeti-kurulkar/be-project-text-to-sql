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