import React, { useState } from 'react';
import { CheckCircle2, AlertOctagon, AlertTriangle, Clock, Layers, ShieldCheck, ArrowRight, Flag } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';
import { formatDefectName, getDefectColor, getSeverityBadge, formatPercent } from '../utils/formatters';
import inspectionService from '../services/inspectionService';

export function DetectionResult({ 
  result, 
  selectedIndex, 
  onSelectDefect,
  onOpenReview 
}) {
  if (!result) return null;

  const [flagged, setFlagged] = useState(result.status === 'FLAGGED_FOR_REVIEW' || result.flagged_for_review);
  const [flagging, setFlagging] = useState(false);

  const isPass = result.status === 'PASS';
  const isFlagged = flagged;
  const hasDefects = result.defect_count > 0;

  const handleFlagForReview = async () => {
    setFlagging(true);
    try {
      await inspectionService.flagForReview(result.id, 'Flagged by Inspector from Real-Time View');
      setFlagged(true);
    } catch (err) {
      console.warn('Flag error:', err);
      setFlagged(true);
    } finally {
      setFlagging(false);
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 backdrop-blur-md space-y-6">
      {/* Verdict Header */}
      <div className={`p-4 rounded-xl border flex items-center justify-between ${
        isFlagged
          ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
          : isPass
          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
          : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
      }`}>
        <div className="flex items-center gap-3">
          {isFlagged ? (
            <AlertTriangle className="w-6 h-6 animate-pulse" />
          ) : isPass ? (
            <CheckCircle2 className="w-6 h-6" />
          ) : (
            <AlertOctagon className="w-6 h-6" />
          )}
          <div>
            <span className="block font-bold text-sm uppercase tracking-wider">
              {isFlagged ? 'Flagged for Human QA' : isPass ? 'Fabric Roll Passed' : 'Defect Anomaly Detected'}
            </span>
            <span className="block text-xs opacity-80 font-sans">
              {isFlagged 
                ? 'Routed to review queue for QA verification.'
                : isPass
                ? 'Textile weave conforms to Grade-A specifications.'
                : `${result.defect_count} defect(s) flagged along fabric surface.`}
            </span>
          </div>
        </div>

        {/* Telemetry pill */}
        <div className="text-right font-mono text-xs">
          <span className="block font-bold">{result.inference_time_ms} ms</span>
          <span className="text-[10px] opacity-75">latency</span>
        </div>
      </div>

      {/* HITL Action Button */}
      {isFlagged ? (
        onOpenReview && (
          <button
            onClick={onOpenReview}
            className="w-full py-2.5 px-4 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-semibold text-xs flex items-center justify-center gap-2 transition-colors shadow-sm shadow-amber-950/20"
          >
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Open in Human-in-the-Loop Review Queue</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )
      ) : (
        <button
          onClick={handleFlagForReview}
          disabled={flagging}
          className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-amber-500/15 border border-slate-700 hover:border-amber-500/40 text-slate-300 hover:text-amber-300 font-semibold text-xs flex items-center justify-center gap-2 transition-colors"
        >
          <Flag className="w-3.5 h-3.5 text-amber-400" />
          <span>{flagging ? 'Sending to Queue...' : 'Send to QA Review Queue'}</span>
        </button>
      )}

      {/* Defect List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
          <span>Detected Anomalies ({result.defects?.length || 0})</span>
          <span>Confidence & Uncertainty</span>
        </div>

        {(!result.defects || result.defects.length === 0) ? (
          <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
            <CheckCircle2 className="w-8 h-8 text-emerald-500/50 mx-auto mb-2" />
            No defects found. Surface yarn structure is uniform.
          </div>
        ) : (
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {result.defects.map((defect, idx) => {
              const isSelected = selectedIndex === idx;
              const color = getDefectColor(defect.class_name);
              const severity = getSeverityBadge(defect.severity);

              return (
                <div
                  key={idx}
                  onClick={() => onSelectDefect(idx)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'bg-slate-800 border-emerald-500/50 shadow-md'
                      : 'bg-slate-950/50 border-slate-800/80 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm"
                      style={{ backgroundColor: color }}
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-slate-200">
                          {formatDefectName(defect.class_name)}
                        </span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold border ${severity.bg}`}>
                          {severity.label}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 font-mono">
                        Box: [{(defect.box?.xmin * 100).toFixed(0)}%, {(defect.box?.ymin * 100).toFixed(0)}%] to [{(defect.box?.xmax * 100).toFixed(0)}%, {(defect.box?.ymax * 100).toFixed(0)}%]
                      </span>
                    </div>
                  </div>

                  <ConfidenceBadge 
                    confidence={defect.confidence} 
                    uncertainty={defect.uncertainty}
                    size="sm"
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Roll Metadata Summary */}
      <div className="pt-4 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs text-slate-400">
        <div>
          <span className="text-slate-500">Fabric Structure:</span>{' '}
          <span className="text-slate-200 font-medium capitalize">{result.fabric_type?.replace('_', ' ')}</span>
        </div>
        <div>
          <span className="text-slate-500">Max Uncertainty:</span>{' '}
          <span className="text-slate-200 font-mono font-medium">{formatPercent(result.uncertainty_score)}</span>
        </div>
      </div>
    </div>
  );
}

export default DetectionResult;
