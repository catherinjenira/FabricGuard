import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Inspection from './pages/Inspection';
import BatchInspection from './pages/BatchInspection';
import ReviewQueue from './pages/ReviewQueue';
import History from './pages/History';
import ModelPerformance from './pages/ModelPerformance';

export function App() {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Fixed Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar />

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inspection" element={<Inspection />} />
            <Route path="/batch" element={<BatchInspection />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/history" element={<History />} />
            <Route path="/performance" element={<ModelPerformance />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;

