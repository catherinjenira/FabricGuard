import React, { useState } from 'react';
import { CheckCircle2, XCircle, Edit3, MessageSquare, User, Save, AlertTriangle } from 'lucide-react';
import { formatDefectName, getDefectColor } from '../utils/formatters';

const DEFECT_CLASSES = [
  'hole', 'stain', 'weaving_slub', 'yarn_defect',
  'crease', 'color_spot', 'knot', 'foreign_fiber'
];

export function ReviewPanel({ 
  inspection, 
  onSubmitDecision, 
  isSubmitting = false 
}) {
  const [action, setAction] = useState('APPROVED');
  const [reviewerName, setReviewerName] = useState('Elena Vance (QA Lead)');
  const [notes, setNotes] = useState('');
  const [editableDefects, setEditableDefects] = useState(inspection?.defects || []);

  if (!inspection) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center text-slate-500 text-xs">
        Select a flagged roll from the queue to conduct QA review.
      </div>
    );
  }

  const handleClassChange = (index, newClass) => {
    setAction('MODIFIED');
    setEditableDefects(prev => {
      const updated = [...prev];
      updated[index] = {
        ...updated[index],
        class_name: newClass
      };
      return updated;
    });
  };

  const handleRemoveDefect = (index) => {
    setAction('MODIFIED');
    setEditableDefects(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    onSubmitDecision(inspection.id, {
      reviewer_name: reviewerName,
      action: action,
      notes: notes,
      corrected_defects: action === 'MODIFIED' ? editableDefects : inspection.defects
    });
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-md space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <span className="font-bold text-white text-base">Human QA Verification Panel</span>
          <span className="block text-xs text-slate-500 font-mono mt-0.5">
            Audit ID: {inspection.id.substring(0, 13)}...
          </span>
        </div>
        <div className="px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Active Learning Triage</span>
        </div>
      </div>

      {/* Decision Radio Buttons */}
      <div className="space-y-2">
        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
          QA Verdict Decision
        </label>
        <div className="grid grid-cols-3 gap-3">
          <button
            type="button"
            onClick={() => setAction('APPROVED')}
            className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-1.5 transition-all ${
              action === 'APPROVED'
                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Approve Defect</span>
          </button>

          <button
            type="button"
            onClick={() => setAction('REJECTED')}
            className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-1.5 transition-all ${
              action === 'REJECTED'
                ? 'bg-rose-500/20 border-rose-500 text-rose-300'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <XCircle className="w-4 h-4 text-rose-400" />
            <span>False Alarm</span>
          </button>

          <button
            type="button"
            onClick={() => setAction('MODIFIED')}
            className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-1.5 transition-all ${
              action === 'MODIFIED'
                ? 'bg-blue-500/20 border-blue-500 text-blue-300'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <Edit3 className="w-4 h-4 text-blue-400" />
            <span>Modify / Reclass</span>
          </button>
        </div>
      </div>

      {/* Reclassification Editor (if Modified) */}
      {action === 'MODIFIED' && (
        <div className="space-y-3 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <span className="text-xs font-semibold text-slate-300 block">Edit Defect Classification:</span>
          {editableDefects.length === 0 ? (
            <p className="text-xs text-slate-500">All defects removed (marked as defect-free pass).</p>
          ) : (
            editableDefects.map((d, i) => (
              <div key={i} className="flex items-center justify-between gap-3 text-xs">
                <span className="font-mono text-slate-400">Box #{i + 1}</span>
                <select
                  value={d.class_name}
                  onChange={(e) => handleClassChange(i, e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-md px-2 py-1 text-slate-200"
                >
                  {DEFECT_CLASSES.map(cls => (
                    <option key={cls} value={cls}>{formatDefectName(cls)}</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => handleRemoveDefect(i)}
                  className="text-rose-400 hover:text-rose-300 px-2 py-1 rounded bg-rose-500/10 border border-rose-500/20"
                >
                  Remove
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Reviewer Meta */}
      <div className="space-y-3">
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5" />
            <span>Inspector Identity</span>
          </label>
          <input
            type="text"
            value={reviewerName}
            onChange={(e) => setReviewerName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Audit Notes & Justification</span>
          </label>
          <textarea
            rows="3"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. Slub caused by warp bobbin knot at reed cycle 240."
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 resize-none"
          />
        </div>
      </div>

      {/* Submit Decision */}
      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full py-3 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs tracking-wide flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
      >
        <Save className="w-4 h-4" />
        <span>{isSubmitting ? 'Recording Audit...' : 'Confirm QA Decision & Record to Retraining Pool'}</span>
      </button>
    </div>
  );
}

export default ReviewPanel;

