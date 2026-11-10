import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ScanLine, 
  Layers, 
  ClipboardCheck, 
  History, 
  Activity, 
  ShieldCheck, 
  Sparkles 
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Live Inspection', path: '/inspection', icon: ScanLine },
  { name: 'Batch Inspection', path: '/batch', icon: Layers },
  { name: 'Review Queue', path: '/review', icon: ClipboardCheck, badge: 'HITL' },
  { name: 'Audit History', path: '/history', icon: History },
  { name: 'Model Telemetry', path: '/performance', icon: Activity },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800">
        <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            FabricGuard<span className="text-emerald-400">.ai</span>
          </span>
          <span className="block text-[10px] uppercase tracking-wider font-semibold text-slate-500">
            Industrial Vision HITL
          </span>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider uppercase text-slate-500">
          Inspection Controls
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm shadow-emerald-950/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-md bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Edge Engine Status */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              YOLOv8 Edge Engine
            </span>
            <span className="text-emerald-400 font-mono text-[11px]">8.1ms</span>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800">
            <span>Accuracy (mAP@50)</span>
            <span className="text-slate-300 font-semibold font-mono">93.4%</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

