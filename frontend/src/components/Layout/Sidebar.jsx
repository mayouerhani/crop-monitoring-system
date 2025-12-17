import React from 'react';
import { Link } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="bg-gray-900 text-white w-64 min-h-screen p-4">
      <nav className="space-y-2">
        <Link
          to="/dashboard"
          className="block px-4 py-2 rounded-lg hover:bg-gray-800"
        >
          📊 Dashboard
        </Link>
        <Link
          to="/alerts"
          className="block px-4 py-2 rounded-lg hover:bg-gray-800"
        >
          ⚠️ Alerts
        </Link>
      </nav>
    </aside>
  );
}