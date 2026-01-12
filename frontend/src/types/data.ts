export interface TableInfo {
  name: string;
  displayName: string;
  rowCount: number;
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  timestamp: Date;
  executionTime: number;
}
