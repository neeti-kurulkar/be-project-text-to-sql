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

export default apiClient;
