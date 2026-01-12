import { useState, useEffect } from 'react';
import { type QueryHistoryItem } from '../types/data';

const STORAGE_KEY = 'finq-query-history';
const MAX_HISTORY_ITEMS = 50;

export function useQueryHistory() {
  const [history, setHistory] = useState<QueryHistoryItem[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Convert timestamp strings back to Date objects
        return parsed.map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
      }
    } catch (error) {
      console.error('Error loading query history:', error);
    }
    return [];
  });

  // Save to localStorage whenever history changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving query history:', error);
    }
  }, [history]);

  const addQuery = (question: string, executionTime: number) => {
    const newItem: QueryHistoryItem = {
      id: Date.now().toString(),
      question,
      timestamp: new Date(),
      executionTime
    };

    setHistory(prev => {
      const updated = [newItem, ...prev];
      // Keep only the most recent items
      return updated.slice(0, MAX_HISTORY_ITEMS);
    });
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing query history:', error);
    }
  };

  return {
    history,
    addQuery,
    clearHistory
  };
}
