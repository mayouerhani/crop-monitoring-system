import apiClient from './api';

export const alertService = {
  getAll: () =>
    apiClient.get('/alerts/'),
  
  getRecent: () =>
    apiClient.get('/alerts/recent/'),
  
  getCritical: () =>
    apiClient.get('/alerts/critical/'),
  
  getByPlot: (plotId) =>
    apiClient.get('/alerts/by_plot/', { params: { plot_id: plotId } }),
  
  getSummary: () =>
    apiClient.get('/alerts/summary/'),
  
  analyzePlot: (plotId) =>
    apiClient.post('/analysis/analyze_latest/', { plot_id: plotId }),
  
  batchAnalyze: () =>
    apiClient.post('/analysis/batch_analyze/'),
};