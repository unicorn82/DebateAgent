import axios from 'axios';

// API base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
let authToken = null;

export const setAuthToken = (token) => {
  authToken = token;
};

// Request interceptor to add Authorization header
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Topic Generation APIs
export const generateTopics = async (topic) => {
  const response = await api.post('/api/topics/generate', { topic });
  console.log(response);
  return response.data;
};

export const generateAffirmativeOption = async (topic, providerId = null) => {
  const response = await api.post('/api/topics/affirmative', { topic, provider_id: providerId });
  return response.data;
};

export const generateNegativeOption = async (topic, providerId = null) => {
  const response = await api.post('/api/topics/negative', { topic, provider_id: providerId });
  return response.data  ;
};

// Affirmative Team APIs
export const generateAffirmativeStatement = async (data) => {
  const response = await api.post('/api/affirmative/statement', data);
  return response.data;
};

export const generateAffirmativeRebuttal = async (data) => {
  const response = await api.post('/api/affirmative/rebuttal', data);
  return response.data;
};

export const generateAffirmativeClosing = async (data) => {
  const response = await api.post('/api/affirmative/closing', data);
  return response.data  ;
};

// Negative Team APIs
export const generateNegativeStatement = async (data) => {
  const response = await api.post('/api/negative/statement', data);
  return response.data;
};

export const generateNegativeRebuttal = async (data) => {
  const response = await api.post('/api/negative/rebuttal', data);
  return response.data;
};

export const generateNegativeClosing = async (data) => {
  const response = await api.post('/api/negative/closing', data);
  return response.data;
};

// Judge API
export const judgeDebate = async (data) => {
  const response = await api.post('/api/judge/debate', data);
  return response.data;
};

// Configuration APIs
export const getTemperature = async () => {
  const response = await api.get('/api/config/temperature');
  return response .data;
};

export const setTemperature = async (temperature) => {
  const response = await api.post('/api/config/temperature', { temperature });
  return response.data;
};

export const getProviders = async () => {
  const response = await api.get('/api/config/providers');
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getTokenInfo = async () => {
  const response = await api.get('/api/token/info');
  return response.data;
};

export default api;
