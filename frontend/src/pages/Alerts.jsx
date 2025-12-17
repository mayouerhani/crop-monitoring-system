import React, { useEffect, useState } from 'react';
import { alertService } from '../services/alertService';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, [filterSeverity]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertService.getAll();
      
      const filtered = filterSeverity === 'all'
        ? response.data
        : response.data.filter((a) => a.severity === filterSeverity);

      setAlerts(filtered);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Alerts</h1>

      <div className="flex gap-2">
        {['all', 'critical', 'high', 'medium', 'low'].map((severity) => (
          <button
            key={severity}
            onClick={() => setFilterSeverity(severity)}
            className={`px-4 py-2 rounded-lg font-medium ${
              filterSeverity === severity
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500"
          >
            <h3 className="font-semibold">{alert.message}</h3>
            <p className="text-sm text-gray-600 mt-1">{alert.alert_type}</p>
            {alert.recommendations && (
              <ul className="text-sm mt-2">
                {alert.recommendations.slice(0, 2).map((rec, i) => (
                  <li key={i}>• {rec}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}