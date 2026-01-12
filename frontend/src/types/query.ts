export interface QueryMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  results?: QueryResult;
}

export interface QueryResult {
  columns: string[];
  rows: any[];
  rowCount: number;
  explanation: string;
}

export interface SuggestedQuestion {
  id: string;
  question: string;
  category: string;
}
