import { useState, useEffect, useCallback } from 'react';
import { getAllCharts } from '../services/api';
import type { AllChartsData } from '../types/charts';

export interface UseAllChartsResult {
  data: AllChartsData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useAllCharts(year?: number): UseAllChartsResult {
  const [data, setData] = useState<AllChartsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await getAllCharts(year);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load charts';
      setError(errorMessage);
      console.error('Error fetching charts:', err);
    } finally {
      setLoading(false);
    }
  }, [year]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
