import React, { useEffect, useState } from 'react';
import { plotService } from '../services/plotService';
import { alertService } from '../services/alertService';

export default function Dashboard() {
  const [plots, setPlots] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [alertSummary, setAlertSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [plotsRes, alertsRes, summaryRes] = await Promise.all([
        plotService.getAll(),
        alertService.getRecent(),
        alertService.getSummary(),
      ]);

      setPlots(plotsRes.data);
      setAlerts(alertsRes.data.slice(0, 5));
      setAlertSummary(summaryRes.data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {alertSummary && (
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Total</p>
            <p className="text-2xl font-bold">{alertSummary.total_alerts}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg shadow">
            <p className="text-red-700 text-sm">Critical</p>
            <p className="text-2xl font-bold text-red-700">{alertSummary.critical}</p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg shadow">
            <p className="text-orange-700 text-sm">High</p>
            <p className="text-2xl font-bold text-orange-700">{alertSummary.high}</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg shadow">
            <p className="text-yellow-700 text-sm">Medium</p>
            <p className="text-2xl font-bold text-yellow-700">{alertSummary.medium}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg shadow">
            <p className="text-blue-700 text-sm">Low</p>
            <p className="text-2xl font-bold text-blue-700">{alertSummary.low}</p>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-2xl font-bold mb-4">Your Plots</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plots.map((plot) => (
            <div key={plot.id} className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold">{plot.name}</h3>
              <p className="text-gray-600 text-sm">{plot.crop_type}</p>
              <p className="text-gray-500 text-xs mt-2">{plot.location}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-4">Recent Alerts</h2>
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div key={alert.id} className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
              <p className="font-semibold">{alert.message}</p>
              <p className="text-sm text-gray-600">{alert.severity}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}