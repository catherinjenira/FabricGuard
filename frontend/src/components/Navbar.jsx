import React from 'react';
import { Bell, Cpu, ShieldCheck, UserCheck, RefreshCw } from 'lucide-react';

export function Navbar({ title = 'Fabric Defect Quality Station' }) {
  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Title & Path */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-white tracking-tight">{title}</h1>
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700/60 text-xs text-slate-300">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Station #4 - Jacquard Line</span>
        </div>
      </div>

      {/* Action / Telemetry badges */}
      <div className="flex items-center gap-4">
        {/* Model status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700 text-xs text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>Model: <span className="font-mono text-slate-100">YOLOv8s-Fabric-1.4</span></span>
        </div>

        {/* HITL Triage status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
          <span>Uncertainty Guard: Active</span>
        </div>

        {/* Inspector Profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-xs">
            QA
          </div>
          <div className="text-left hidden sm:block">
            <span className="block text-xs font-semibold text-slate-200">Elena Vance</span>
            <span className="block text-[10px] text-slate-500">Lead QA Inspector</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;

