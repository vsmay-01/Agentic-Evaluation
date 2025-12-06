import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Single evaluation
export async function evaluate(payload) {
  const response = await api.post('/evaluate/', payload);
  return response.data;
}

// Batch evaluation
export async function submitBatch(payload) {
  const response = await api.post('/api/batch', payload);
  return response.data;
}

// Get batch status
export async function getBatchStatus(batchId) {
  const response = await api.get(`/api/batch/status/${batchId}`);
  return response.data;
}

// Get batch result
export async function getBatchResult(batchId) {
  const response = await api.get(`/api/batch/result/${batchId}`);
  return response.data;
}

// Health check
export async function healthCheck() {
  const response = await api.get('/health/ready');
  return response.data;
}

export default api;
