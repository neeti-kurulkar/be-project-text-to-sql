export interface QueryMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  results?: QueryResult;
  insights?: QueryInsights;
  visualization?: QueryVisualization;
  agentTrace?: AgentTrace[];
  executionTime?: number;
}

export interface QueryResult {
  columns: string[];
  rows: any[];
  rowCount: number;
  explanation: string;
}

export interface QueryInsights {
  summary: string;
  key_insights: string[];
  trends?: string[];
  anomalies?: string[];
  metrics?: Record<string, any>;
}

export interface QueryVisualization {
  should_visualize: boolean;
  chart_type?: 'bar' | 'line' | 'pie';
  chart_config?: {
    type: string;
    data: any[];
    title?: string;
    x_axis?: { dataKey: string; label: string };
    y_axis?: { dataKey: string; label: string };
    bars?: { dataKey: string; fill: string; name: string }[];
    lines?: { dataKey: string; stroke: string; name: string }[];
    dataKey?: string;
    nameKey?: string;
    colors?: string[];
  };
  reason?: string;
}

export interface AgentTrace {
  agent: string;
  duration: number;
  status: string;
  details?: Record<string, any>;
}

export interface SuggestedQuestion {
  id: string;
  question: string;
  category: string;
}

export interface NL2SQLResponse {
  success: boolean;
  query_id: string;
  original_question: string;
  sql?: { query: string; execution_time: number };
  results?: { columns: string[]; rows: any[]; row_count: number };
  insights?: QueryInsights;
  visualization?: QueryVisualization;
  intent?: Record<string, any>;
  agent_trace?: AgentTrace[];
  total_time: number;
  error?: string;
}
