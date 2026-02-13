import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Activity, Globe, Lock, RefreshCw } from 'lucide-react';
import Dashboard from './pages/Dashboard/Dashboard.jsx';

const App = () => {
  const [stats, setStats] = useState({ scanned: 0, threatsBlocked: 0, trustScore: 100 });
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE = "http://localhost:8080";

  const fetchData = async () => {
    try {
      // Fetch stats and logs in parallel
      const [statsRes, logsRes] = await Promise.all([
        fetch(`${API_BASE}/stats`),
        fetch(`${API_BASE}/logs`)
      ]);

      if (!statsRes.ok || !logsRes.ok) throw new Error("API Connection Failed");

      const statsData = await statsRes.json();
      const logsData = await logsRes.json();

      setStats(statsData);
      setRecentEvents(logsData);
      setError(null);
    } catch (err) {
      setError("Sentinel API is offline. Please check your Go backend.");
    } finally {
      setLoading(false);
    }
  };

  // Poll for real data every 3 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-100 p-8">
        <AlertTriangle className="w-16 h-16 text-red-500 mb-4 animate-pulse" />
        <h1 className="text-2xl font-bold mb-2">Connection Error</h1>
        <p className="text-slate-400 mb-6">{error}</p>
        <button 
          onClick={() => {setLoading(true); fetchData();}}
          className="px-6 py-2 bg-cyan-600 rounded-lg hover:bg-cyan-500 transition-colors flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" /> Retry Connection
        </button>
      </div>
    );
  }

  return (
  <>
    <Dashboard stats={stats} recentEvents={recentEvents} loading={loading} />
  </>
  );
};



export default App;