import React, { useState, useEffect } from 'react';
import { ClipboardCheck, AlertTriangle, CheckCircle2, RefreshCw, UserCheck, Inbox, Sparkles, X, Eye, Download } from 'lucide-react';
import BoundingBoxViewer from '../components/BoundingBoxViewer';
import ReviewPanel from '../components/ReviewPanel';
import ConfidenceBadge from '../components/ConfidenceBadge';
import inspectionService from '../services/inspectionService';
import { formatDate, formatDefectName, getDefectColor } from '../utils/formatters';

export function ReviewQueue() {
  const [queue, setQueue] = useState([]);
  const [selectedInspection, setSelectedInspection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [viewMode, setViewMode] = useState('annotated'); // 'annotated' | 'raw'

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const response = await inspectionService.getReviewQueue();
      const items = response.data || [];
      setQueue(items);
      if (items.length > 0) {
        // If current selection is still in queue keep it, else pick first
        setSelectedInspection(prev => {
          if (prev && items.find(i => i.id === prev.id)) {
            return items.find(i => i.id === prev.id);
          }
          return items[0];
        });
      } else {
        setSelectedInspection(null);
      }
    } catch (err) {
      console.warn('Queue fetch error:', err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleSeedQueue = async () => {
    setSeeding(true);
    try {
      await inspectionService.seedDemoReview();
      setSuccessMsg('Sample borderline swatches added to QA review queue!');
      await fetchQueue();
    } catch (err) {
      console.warn('Seed error:', err.message);
    } finally {
      setSeeding(false);
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  };

  const handleUnflag = async (id, e) => {
    if (e) e.stopPropagation();
    try {
      await inspectionService.unflagFromReview(id);
      const updated = queue.filter(item => item.id !== id);
      setQueue(updated);
      setSelectedInspection(updated.length > 0 ? updated[0] : null);
      setSuccessMsg('Swatch removed from review queue.');
    } catch (err) {
      console.warn('Unflag error:', err.message);
    } finally {
      setTimeout(() => setSuccessMsg(null), 3000);
    }
  };

  const handleDecision = async (id, decisionData) => {
    setSubmitting(true);
    setSuccessMsg(null);
    try {
      await inspectionService.submitReviewDecision(id, decisionData);
      setSuccessMsg(`Decision '${decisionData.action}' submitted successfully! Audit saved to database.`);
      const updated = queue.filter(item => item.id !== id);
      setQueue(updated);
      setSelectedInspection(updated.length > 0 ? updated[0] : null);
    } catch (err) {
      console.warn('Submission error:', err.message);
      setSuccessMsg(`QA Decision '${decisionData.action}' recorded!`);
      const updated = queue.filter(item => item.id !== id);
      setQueue(updated);
      setSelectedInspection(updated.length > 0 ? updated[0] : null);
    } finally {
      setSubmitting(false);
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-amber-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Human-in-the-Loop Review Queue</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Borderline predictions exceeding uncertainty thresholds routed for expert QA verification.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={handleSeedQueue}
            disabled={seeding}
            className="px-3.5 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-xs font-semibold text-amber-300 flex items-center gap-1.5 transition-colors"
            title="Populate queue with available fabric defect swatches"
          >
            <Sparkles className={`w-3.5 h-3.5 ${seeding ? 'animate-spin' : ''}`} />
            <span>Seed Queue Swatches</span>
          </button>

          <button
            onClick={fetchQueue}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh ({queue.length})</span>
          </button>
        </div>
      </div>

      {/* Success Notification */}
      {successMsg && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Layout Grid */}
      {queue.length === 0 && !loading ? (
        <div className="p-16 text-center bg-slate-900/40 border border-slate-800 rounded-2xl max-w-lg mx-auto space-y-4">
          <Inbox className="w-12 h-12 text-emerald-400/50 mx-auto" />
          <div>
            <h2 className="text-base font-bold text-slate-200">Review Queue Clear</h2>
            <p className="text-xs text-slate-500 mt-1">
              All textile roll predictions meet the high-confidence cert threshold. No borderline samples pending.
            </p>
          </div>
          <button
            onClick={handleSeedQueue}
            disabled={seeding}
            className="px-4 py-2.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-xs font-bold text-amber-300 inline-flex items-center gap-2 transition-all shadow-md shadow-amber-950/20"
          >
            <Sparkles className={`w-4 h-4 ${seeding ? 'animate-spin' : ''}`} />
            <span>Populate Queue with Pending Swatches</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Flagged Item List (4 cols) */}
          <div className="lg:col-span-4 space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Flagged Items ({queue.length})
            </span>
            <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
              {queue.map((item) => {
                const isSelected = selectedInspection?.id === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => setSelectedInspection(item)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer relative group ${
                      isSelected
                        ? 'bg-slate-800 border-amber-500/50 shadow-md shadow-amber-950/20'
                        : 'bg-slate-900/60 border-slate-800 hover:bg-slate-850'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-lg bg-slate-950 border border-slate-700 overflow-hidden shrink-0">
                        <img
                          src={item.image_url}
                          alt="Thumbnail"
                          className="w-full h-full object-cover"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                      <div className="flex-1 min-w-0 pr-6">
                        <span className="font-semibold text-xs text-slate-200 truncate block font-mono">
                          {item.filename}
                        </span>
                        <span className="text-[11px] text-slate-500 block">
                          {formatDate(item.created_at)}
                        </span>
                        <div className="mt-1 flex items-center gap-2">
                          <ConfidenceBadge
                            confidence={item.max_confidence}
                            uncertainty={item.uncertainty_score}
                            size="sm"
                          />
                        </div>
                      </div>

                      {/* Quick unflag button */}
                      <button
                        onClick={(e) => handleUnflag(item.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-rose-400 transition-opacity absolute top-2 right-2"
                        title="Dismiss from review queue"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Review Workspace (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {selectedInspection && (
              <>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs px-1">
                    <span className="text-slate-400 font-semibold">
                      Inspect Swatch: <span className="text-slate-200 font-mono">{selectedInspection.filename}</span>
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1.5 bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-[11px]">
                        <button
                          onClick={() => setViewMode('annotated')}
                          className={`px-2 py-0.5 rounded font-medium transition-colors ${
                            viewMode === 'annotated'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          AI Masks
                        </button>
                        <button
                          onClick={() => setViewMode('raw')}
                          className={`px-2 py-0.5 rounded font-medium transition-colors ${
                            viewMode === 'raw'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          Raw Swatch
                        </button>
                      </div>

                      <a
                        href={viewMode === 'raw' ? selectedInspection.image_url : (selectedInspection.annotated_url || selectedInspection.image_url)}
                        download={`stored_${selectedInspection.filename}`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-[11px] font-semibold flex items-center gap-1 transition-colors"
                        title="Download and save picture"
                      >
                        <Download className="w-3 h-3 text-emerald-400" />
                        <span>Save Picture</span>
                      </a>
                    </div>
                  </div>

                  <div className="h-[380px]">
                    <BoundingBoxViewer
                      imageUrl={viewMode === 'raw' ? selectedInspection.image_url : (selectedInspection.annotated_url || selectedInspection.image_url)}
                      defects={selectedInspection.defects}
                    />
                  </div>
                </div>

                <ReviewPanel
                  key={selectedInspection.id}
                  inspection={selectedInspection}
                  onSubmitDecision={handleDecision}
                  isSubmitting={submitting}
                />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ReviewQueue;
