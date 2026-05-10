import apiClient from './apiClient';

export const authAPI = {
  login: (data) => apiClient.post('/auth/login', data),
  register: (data) => apiClient.post('/auth/register', data),
  getProfile: () => apiClient.get('/auth/profile'),
  updateProfile: (data) => apiClient.put('/auth/profile', data),
};

export const resumeAPI = {
  getAll: (page = 1, perPage = 50) => apiClient.get('/resumes', { params: { page, per_page: perPage } }),
  upload: (formData) => apiClient.post('/resumes', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getById: (id) => apiClient.get(`/resumes/${id}`),
  delete: (id) => apiClient.delete(`/resumes/${id}`),
};

export const jobAPI = {
  getAll: () => apiClient.get('/job-postings'),
  create: (data) => apiClient.post('/job-postings', data),
  getById: (id) => apiClient.get(`/job-postings/${id}`),
  update: (id, data) => apiClient.put(`/job-postings/${id}`, data),
  delete: (id) => apiClient.delete(`/job-postings/${id}`),
};

export const analysisAPI = {
  analyze: (data) => apiClient.post('/analysis/analyze', data),
  bulkAnalyze: (data) => apiClient.post('/analysis/bulk-analyze', data),
  getById: (id) => apiClient.get(`/analysis/${id}`),
  biasCheck: (resumeId) => apiClient.post('/analysis/bias', { resume_id: resumeId }),
};

export const chatAPI = {
  hrChat: (messages) => apiClient.post('/chat/hr', { messages }),
  candidateChat: (resumeId, messages) => apiClient.post(`/chat/candidate/${resumeId}`, { messages }),
};
