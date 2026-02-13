import './Dashboard.css';
import React from 'react';
import { useState, useEffect } from 'react';

import { AlertTriangle, CheckCircle, Activity, Globe, Lock, RefreshCw } from 'lucide-react';

function Dashboard({ stats, recentEvents, loading }) {

    const displayStats = stats || { scanned: 0, threatsBlocked: 0, trustScore: 100 };
    return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-8">
      {/* ... header code ... */}

      {/* Hero Stats - Use displayStats to avoid "cannot read property of null" */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatCard title="Total Pages Scanned" value={displayStats.scanned} icon={<Globe className="text-blue-400" />} />
        <StatCard title="Threats Neutralized" value={displayStats.threatsBlocked} icon={<AlertTriangle className="text-red-400" />} />
        <StatCard title="Security Trust Score" value={`${displayStats.trustScore}%`} icon={<Lock className="text-green-400" />} />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {/* ... table header ... */}
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            {/* ... thead ... */}
            <tbody className="divide-y divide-slate-800">
              {/* 3. Safety: Use optional chaining (?.) and fallback to empty array ([]) */}
              {(recentEvents || []).length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-slate-500 italic">
                    No scan data received yet.
                  </td>
                </tr>
              ) : (
                recentEvents.map((event) => (
                  <tr key={event.id} className="hover:bg-slate-800/50 transition-colors">
                    {/* ... table cell content ... */}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    );
}


const StatCard = ({ title, value, icon }) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl relative overflow-hidden group">
    <div className="flex justify-between items-start mb-4 relative z-10">
      <div className="p-3 bg-slate-950 rounded-lg group-hover:scale-110 transition-transform">{icon}</div>
    </div>
    <div className="relative z-10">
      <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-3xl font-bold tracking-tight">{value}</p>
    </div>
    {/* Decorative background element */}
    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
      {React.cloneElement(icon, { size: 100 })}
    </div>
  </div>
);


export default Dashboard;