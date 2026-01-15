export interface TableInfo {
  name: string;
  displayName: string;
  rowCount: number;
}

export interface CachedQueryResponse {
  sql?: string;
  results?: {
    columns: string[];
    rows: any[];
    rowCount: number;
  };
  insights?: {
    summary: string;
    key_insights: string[];
    trends?: string[];
    anomalies?: string[];
    metrics?: Record<string, any>;
  };
  visualization?: {
    should_visualize: boolean;
    chart_type?: 'bar' | 'line' | 'pie';
    chart_config?: any;
    reason?: string;
  };
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  timestamp: Date;
  executionTime: number;
  cachedResponse?: CachedQueryResponse;
}
