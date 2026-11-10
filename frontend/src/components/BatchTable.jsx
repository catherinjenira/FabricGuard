import React from 'react';
import { CheckCircle2, AlertOctagon, AlertTriangle, Eye, Layers } from 'lucide-react';
import { formatPercent } from '../utils/formatters';

export function BatchTable({ 
  inspections = [], 
  onSelectInspection, 
  selectedId = null 
}) {
  if (!inspections || inspections.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500 bg-slate-900/40 border border-slate-800 rounded-2xl">
        <Layers className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <span className="text-sm font-semibold text-slate-400 block">No Batch Swatches Loaded</span>
        <span className="text-xs text-slate-600">Upload multiple fabric rolls to inspect high-throughput batches.</span>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Swatch</th>
              <th className="py-3 px-4">Filename</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Defects</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Speed</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {inspections.map((item) => {
              const isSelected = selectedId === item.id;
              const isPass = item.status === 'PASS';
              const isFlagged = item.status === 'FLAGGED_FOR_REVIEW' || item.flagged_for_review;

              return (
                <tr
                  key={item.id}
                  onClick={() => onSelectInspection && onSelectInspection(item)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-slate-800/80'
                      : 'hover:bg-slate-800/40 bg-slate-900/30'
                  }`}
                >
                  {/* Swatch Preview */}
                  <td className="py-2.5 px-4">
                    <div className="w-10 h-10 rounded-lg overflow-hidden border border-slate-700 bg-slate-950 flex items-center justify-center">
                      <img
                        src={item.image_url}
                        alt="Swatch"
                        className="w-full h-full object-cover"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>
                  </td>

                  {/* Filename */}
                  <td className="py-2.5 px-4 font-mono font-medium text-slate-200">
                    <span className="truncate max-w-[140px] block" title={item.filename}>
                      {item.filename}
                    </span>
                  </td>

                  {/* Status Badge */}
                  <td className="py-2.5 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-bold text-[10px] border ${
                      isFlagged
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                        : isPass
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                    }`}>
                      {isFlagged ? (
                        <AlertTriangle className="w-3 h-3" />
                      ) : isPass ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <AlertOctagon className="w-3 h-3" />
                      )}
                      <span>{isFlagged ? 'REVIEW' : isPass ? 'PASS' : 'DEFECT'}</span>
                    </span>
                  </td>

                  {/* Defects Count */}
                  <td className="py-2.5 px-4 font-mono font-semibold text-slate-300">
                    {item.defect_count}
                  </td>

                  {/* Confidence */}
                  <td className="py-2.5 px-4 font-mono text-slate-400">
                    {formatPercent(item.max_confidence)}
                  </td>

                  {/* Latency */}
                  <td className="py-2.5 px-4 font-mono text-slate-500">
                    {item.inference_time_ms ? `${item.inference_time_ms}ms` : '—'}
                  </td>

                  {/* Action */}
                  <td className="py-2.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectInspection && onSelectInspection(item);
                      }}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                      title="Inspect Details"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default BatchTable;
