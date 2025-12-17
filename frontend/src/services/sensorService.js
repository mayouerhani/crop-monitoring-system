import apiClient from './api';

export const sensorService = {
  getReadings: (plotId, sensorType, limit = 100) =>
    apiClient.get(`/sensor-readings/`, {
      params: { plot_id: plotId, sensor_type: sensorType, limit },
    }),
  
  getLatest: (plotId) =>
    apiClient.get(`/sensor-readings/latest/`, {
      params: { plot_id: plotId },
    }),
};