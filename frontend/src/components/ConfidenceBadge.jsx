import React from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle } from 'lucide-react';
import { formatPercent } from '../utils/formatters';

export function ConfidenceBadge({ confidence = 0, uncertainty = 0, size = 'md' }) {
  const confValue = confidence > 1 ? confidence / 100 : confidence;
  
  let config = {
    color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    icon: CheckCircle2,
    label: 'High Confidence'
  };

  if (confValue < 0.65 || uncertainty > 0.35) {
    config = {
      color: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      icon: AlertTriangle,
      label: 'Borderline / Review'
    };
  } else if (confValue < 0.85) {
    config = {
      color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: AlertCircle,
      label: 'Moderate'
    };
  }

  const Icon = config.icon;
  const isSmall = size === 'sm';

  return (
    <div className={`inline-flex items-center gap-1.5 rounded-lg border font-mono font-medium ${config.color} ${
      isSmall ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'
    }`}>
      <Icon className={isSmall ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{formatPercent(confValue)}</span>
      {uncertainty > 0 && (
        <span className="text-[10px] opacity-75 font-sans border-l border-current/20 pl-1.5 ml-0.5">
          u: {(uncertainty * 100).toFixed(0)}%
        </span>
      )}
    </div>
  );
}

export default ConfidenceBadge;

