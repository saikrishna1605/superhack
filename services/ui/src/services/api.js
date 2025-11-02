import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => 
    api.post('/api/auth/login', null, { params: { email, password } }),
  register: (userData) => 
    api.post('/api/auth/register', userData),
  getCurrentUser: () => 
    api.get('/api/auth/me'),
};

// MSP API
export const mspAPI = {
  getDashboard: () => 
    api.get('/api/msp/dashboard'),
  getClients: (skip = 0, limit = 100) => 
    api.get('/api/msp/clients', { params: { skip, limit } }),
  getClient: (clientId) => 
    api.get(`/api/msp/clients/${clientId}`),
  createClient: (clientData) => 
    api.post('/api/msp/clients', clientData),
  getClientHealthScore: (clientId) => 
    api.get(`/api/msp/clients/${clientId}/health-score`),
  getRecommendations: (type = null) => 
    api.get('/api/msp/recommendations', { params: { recommendation_type: type } }),
};

// IT Team API
export const itAPI = {
  getDashboard: () => 
    api.get('/api/it/dashboard'),
  getSoftware: (department = null, skip = 0, limit = 100) => 
    api.get('/api/it/software', { params: { department, skip, limit } }),
  createSoftware: (softwareData) => 
    api.post('/api/it/software', softwareData),
  getSoftwareUsage: (licenseId) => 
    api.get(`/api/it/software/${licenseId}/usage`),
  getAnomalies: (resolved = null) => 
    api.get('/api/it/anomalies', { params: { resolved } }),
  deactivateUnused: (licenseId, daysInactive = 30) => 
    api.post(`/api/it/software/${licenseId}/deactivate-unused`, null, { 
      params: { days_inactive: daysInactive } 
    }),
  getDepartmentalSpend: () => 
    api.get('/api/it/spend/department'),
  getSpendingTrend: (year = 2024, fromMonth = 1, toMonth = 12) =>
    api.get('/api/it/spending-trend', { params: { year, from_month: fromMonth, to_month: toMonth } }),
  getCostBreakdown: () =>
    api.get('/api/it/cost-breakdown'),
};

// Analytics API
export const analyticsAPI = {
  getRevenueTrends: (days = 30) => 
    api.get('/api/analytics/trends/revenue', { params: { days } }),
  getCostTrends: (days = 30) => 
    api.get('/api/analytics/trends/cost', { params: { days } }),
  getExecutiveSummary: () => 
    api.get('/api/analytics/reports/executive-summary'),
};

export default api;