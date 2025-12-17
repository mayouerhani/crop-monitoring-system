import apiClient from './api';

export const plotService = {
  getAll: () =>
    apiClient.get('/plots/'),
  
  getById: (id) =>
    apiClient.get(`/plots/${id}/`),
  
  getSensorDataSummary: (id) =>
    apiClient.get(`/plots/${id}/sensor_data_summary/`),
  
  getActiveAlerts: (id) =>
    apiClient.get(`/plots/${id}/active_alerts/`),
  
  create: (data) =>
    apiClient.post('/plots/', data),
  
  update: (id, data) =>
    apiClient.patch(`/plots/${id}/`, data),
  
  delete: (id) =>
    apiClient.delete(`/plots/${id}/`),
};