import axios from 'axios';

// API base URL - adjust based on your backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const queryQuestions = async (question, subject = null) => {
  const response = await api.post('/query', {
    question,
    top_k: 5,
    subject
  });
  return response.data;
};

export const getSubjects = async () => {
  const response = await api.get('/subjects');
  return response.data;
};

export const uploadQuestionPaper = async (file, namespace) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('namespace', namespace);

  const response = await api.post('/process-s3-file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
