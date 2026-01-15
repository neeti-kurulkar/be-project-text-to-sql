import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('finq_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (token expired)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      localStorage.removeItem('finq_token');
      localStorage.removeItem('finq_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Query API
export const executeQuery = async (sql: string) => {
  const response = await apiClient.post('/api/query/execute', { sql });
  return response.data;
};

// Tables API
export const listTables = async () => {
  const response = await apiClient.get('/api/tables');
  return response.data;
};

export const getTableData = async (
  tableName: string,
  page: number = 1,
  pageSize: number = 50
) => {
  const response = await apiClient.get(`/api/tables/${tableName}`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

// Stats API
export const getQuickStats = async () => {
  const response = await apiClient.get('/api/stats');
  return response.data;
};

// Charts API
export const getAllCharts = async (year?: number) => {
  const response = await apiClient.get('/api/charts/all', {
    params: year ? { year } : undefined,
  });
  return response.data;
};

export const getRevenueByCountry = async (year?: number) => {
  const response = await apiClient.get('/api/charts/revenue-by-country', {
    params: year ? { year } : undefined,
  });
  return response.data;
};

export const getRevenueTrend = async () => {
  const response = await apiClient.get('/api/charts/revenue-trend');
  return response.data;
};

export const getQuarterlyRevenue = async () => {
  const response = await apiClient.get('/api/charts/quarterly-revenue');
  return response.data;
};

export const getTopExpenses = async (limit: number = 5, year?: number) => {
  const response = await apiClient.get('/api/charts/top-expenses', {
    params: { limit, ...(year ? { year } : {}) },
  });
  return response.data;
};

export const getRegionalDistribution = async (year?: number) => {
  const response = await apiClient.get('/api/charts/regional-distribution', {
    params: year ? { year } : undefined,
  });
  return response.data;
};

export const getProfitLoss = async () => {
  const response = await apiClient.get('/api/charts/profit-loss');
  return response.data;
};

export const getYoYGrowth = async () => {
  const response = await apiClient.get('/api/charts/yoy-growth');
  return response.data;
};

export const getExpenseBreakdown = async (year?: number) => {
  const response = await apiClient.get('/api/charts/expense-breakdown', {
    params: year ? { year } : undefined,
  });
  return response.data;
};

// NL2SQL API
export const processNaturalLanguageQuery = async (question: string) => {
  const response = await apiClient.post('/api/nl2sql/query', { question });
  return response.data;
};

export const getNL2SQLHealth = async () => {
  const response = await apiClient.get('/api/nl2sql/health');
  return response.data;
};

export const getExampleStats = async () => {
  const response = await apiClient.get('/api/nl2sql/examples/stats');
  return response.data;
};

// Insights API
export const getAutomatedInsights = async () => {
  const response = await apiClient.get('/api/insights/automated');
  return response.data;
};

export default apiClient;
