import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend, 
  trendUpIsPositive = true,
  colorScheme = 'emerald' 
}) {
  const colorMap = {
    emerald: {
      border: 'border-emerald-500/20',
      bg: 'bg-emerald-500/5',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    },
    amber: {
      border: 'border-amber-500/20',
      bg: 'bg-amber-500/5',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    },
    rose: {
      border: 'border-rose-500/20',
      bg: 'bg-rose-500/5',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    },
    blue: {
      border: 'border-blue-500/20',
      bg: 'bg-blue-500/5',
      iconBg: 'bg-blue-500/10 text-blue-400 border-blue-500/30'
    }
  };

  const scheme = colorMap[colorScheme] || colorMap.emerald;

  return (
    <div className={`p-5 rounded-2xl border ${scheme.border} ${scheme.bg} bg-slate-900/60 backdrop-blur-sm relative overflow-hidden transition-all duration-200 hover:border-slate-700`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${scheme.iconBg}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-extrabold text-white font-mono tracking-tight">{value}</span>
        {trend && (
          <span className={`inline-flex items-center text-xs font-semibold ${
            trendUpIsPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {trendUpIsPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
      )}
    </div>
  );
}

export default StatCard;

