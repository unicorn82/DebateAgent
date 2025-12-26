import axios from 'axios';

// API base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Topic Generation APIs
export const generateTopics = async (topic) => {
  const response = await api.post('/api/topics/generate', { topic });
  console.log(response);
  return response.data;
};

export const generateAffirmativeOption = async (topic) => {
  const response = await api.post('/api/topics/affirmative', { topic });
  return response.data;
};

export const generateNegativeOption = async (topic) => {
  const response = await api.post('/api/topics/negative', { topic });
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

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
