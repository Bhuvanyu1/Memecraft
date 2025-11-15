import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API methods
export const memeAPI = {
  list: (params) => api.get('/memes', { params }),
  get: (id) => api.get(`/memes/${id}`),
  create: (data) => api.post('/memes', data),
  update: (id, data) => api.put(`/memes/${id}`, data),
  delete: (id) => api.delete(`/memes/${id}`),
  duplicate: (id) => api.post(`/memes/${id}/duplicate`),
};

export const templateAPI = {
  list: (params) => api.get('/templates', { params }),
  get: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  vote: (id, vote) => api.post(`/templates/${id}/vote`, null, { params: { vote } }),
  categories: () => api.get('/templates/categories/list'),
};

export const trendAPI = {
  list: (params) => api.get('/trends', { params }),
  get: (id) => api.get(`/trends/${id}`),
};

export const aiAPI = {
  generateImage: (data) => api.post('/ai/generate-image', data),
  suggestCaptions: (data) => api.post('/ai/suggest-captions', data),
  generateMeme: (params) => api.post('/ai/generate-meme', null, { params }),
  predictViral: (data) => api.post('/ai/predict-viral', data),
  faceSwap: (data) => api.post('/ai/face-swap', data),
  removeBackground: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ai/remove-background', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

export const uploadAPI = {
  image: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  file: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

export const notificationAPI = {
  list: (params) => api.get('/notifications', { params }),
  markRead: (id) => api.put(`/notifications/${id}/read`),
};

export const commentAPI = {
  list: (memeId) => api.get(`/memes/${memeId}/comments`),
  create: (memeId, data) => api.post(`/memes/${memeId}/comments`, data),
  resolve: (id) => api.put(`/comments/${id}/resolve`),
  delete: (id) => api.delete(`/comments/${id}`),
};


export const teamAPI = {
  list: () => api.get('/teams'),
  get: (id) => api.get(`/teams/${id}`),
  create: (data) => api.post('/teams', data),
  update: (id, data) => api.put(`/teams/${id}`, data),
  delete: (id) => api.delete(`/teams/${id}`),
  listMembers: (id) => api.get(`/teams/${id}/members`),
  invite: (id, data) => api.post(`/teams/${id}/invite`, data),
  acceptInvite: (id) => api.post(`/teams/${id}/accept`),
  updateMemberRole: (teamId, userId, role) => api.put(`/teams/${teamId}/members/${userId}/role`, null, { params: { role } }),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
};

export const analyticsAPI = {
  track: (data) => api.post('/analytics', data),
  getMemeAnalytics: (memeId) => api.get(`/analytics/memes/${memeId}`),
  getUserSummary: () => api.get('/analytics/user/summary'),
  getTeamSummary: (teamId) => api.get(`/analytics/teams/${teamId}/summary`),
};

export const socialAPI = {
  getStatus: () => api.get('/social/status'),
  post: (data) => api.post('/social/post', data),
  postMultiple: (data) => api.post('/social/post-multiple', data),
};

export const collaborationAPI = {
  getActiveUsers: (memeId) => api.get(`/collaboration/active-users/${memeId}`),
};


export default api;
