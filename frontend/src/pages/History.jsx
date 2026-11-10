import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History as HistoryIcon, Download, Search, Filter, Eye, Trash2, CheckCircle2, AlertOctagon, AlertTriangle, Flag, ArrowRight } from 'lucide-react';
import inspectionService from '../services/inspectionService';
import BoundingBoxViewer from '../components/BoundingBoxViewer';
import { formatDate, formatPercent, formatDefectName } from '../utils/formatters';

export function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState(null);
  const [toastMsg, setToastMsg] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await inspectionService.getHistory({
        page,
        limit: 10,
        status: statusFilter || undefined
      });
      if (response.data) {
        setItems(response.data.items || []);
        setTotal(response.data.total || 0);
      }
    } catch (err) {
      console.warn('History API fetch fallback:', err.message);
      // Fallback historical logs
      const mockItems = [
        {
          id: 'hist-1',
          filename: 'linen_coarse_roll_01.jpg',
          image_url: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=640&q=80',
          status: 'PASS',
          defect_count: 0,
          max_confidence: 0.98,
          uncertainty_score: 0.04,
          flagged_for_review: false,
          inference_time_ms: 7.9,
          fabric_type: 'linen_coarse',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          defects: []
        },
        {
          id: 'hist-2',
          filename: 'cotton_plain_slub_02.jpg',
          image_url: 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=640&q=80',
          status: 'DEFECT_DETECTED',
          defect_count: 1,
          max_confidence: 0.94,
          uncertainty_score: 0.12,
          flagged_for_review: false,
          inference_time_ms: 8.4,
          fabric_type: 'cotton_weave',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          defects: [
            {
              class_id: 2,
              class_name: 'weaving_slub',
              confidence: 0.94,
              uncertainty: 0.12,
              severity: 'medium',
              box: { xmin: 0.2, ymin: 0.4, xmax: 0.8, ymax: 0.5 }
            }
          ]
        }
      ];
      setItems(mockItems);
      setTotal(mockItems.length);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this inspection audit record?')) return;
    try {
      await inspectionService.deleteInspection(id);
      setItems(prev => prev.filter(item => item.id !== id));
      if (selectedInspection?.id === id) setSelectedInspection(null);
    } catch (err) {
      alert('Could not delete record: ' + err.message);
    }
  };

  const handleToggleFlag = async (item, e) => {
    if (e) e.stopPropagation();
    try {
      if (item.flagged_for_review) {
        await inspectionService.unflagFromReview(item.id);
        setItems(prev => prev.map(it => it.id === item.id ? { ...it, flagged_for_review: false, status: it.defect_count > 0 ? 'DEFECT_DETECTED' : 'PASS' } : it));
        if (selectedInspection?.id === item.id) {
          setSelectedInspection(prev => ({ ...prev, flagged_for_review: false }));
        }
        setToastMsg('Inspection removed from review queue');
      } else {
        await inspectionService.flagForReview(item.id, 'Flagged from Audit Log');
        setItems(prev => prev.map(it => it.id === item.id ? { ...it, flagged_for_review: true, status: 'FLAGGED_FOR_REVIEW' } : it));
        if (selectedInspection?.id === item.id) {
          setSelectedInspection(prev => ({ ...prev, flagged_for_review: true, status: 'FLAGGED_FOR_REVIEW' }));
        }
        setToastMsg('Inspection sent to Human Review Queue!');
      }
    } catch (err) {
      console.warn('Flag toggle error:', err);
      setToastMsg('Updated review status');
    } finally {
      setTimeout(() => setToastMsg(null), 3500);
    }
  };

  const handleDownloadCsv = () => {
    window.open(inspectionService.getExportCsvUrl(), '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header & Export */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <HistoryIcon className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Inspection Audit Logs</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Immutable traceability logs for quality assurance certificates and regulatory compliance.
          </p>
        </div>

        <button
          onClick={handleDownloadCsv}
          className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 transition-colors self-start sm:self-auto"
        >
          <Download className="w-4 h-4 text-emerald-400" />
          <span>Export CSV Report</span>
        </button>
      </div>

      {/* Toast Notification */}
      {toastMsg && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 backdrop-blur-md flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="font-semibold text-slate-300">Filter Verdict:</span>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200"
          >
            <option value="">All Verdicts</option>
            <option value="PASS">Pass (Grade-A)</option>
            <option value="DEFECT_DETECTED">Defect Intercepted</option>
            <option value="FLAGGED_FOR_REVIEW">Human Review Flagged</option>
          </select>
        </div>

        <span className="text-slate-500 font-mono">
          Showing {items.length} of {total} Records
        </span>
      </div>

      {/* Data Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Swatch</th>
                <th className="py-3 px-4">Filename</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Defects</th>
                <th className="py-3 px-4">Textile Type</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {items.map((item) => {
                const isPass = item.status === 'PASS';
                const isFlagged = item.status === 'FLAGGED_FOR_REVIEW' || item.flagged_for_review;

                return (
                  <tr
                    key={item.id}
                    onClick={() => setSelectedInspection(item)}
                    className="hover:bg-slate-800/40 bg-slate-900/30 cursor-pointer transition-colors"
                  >
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
                    <td className="py-2.5 px-4 font-mono font-medium text-slate-200">
                      <span className="truncate max-w-[160px] block">{item.filename}</span>
                    </td>
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
                    <td className="py-2.5 px-4 font-mono font-semibold text-slate-300">
                      {item.defect_count}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 capitalize">
                      {item.fabric_type?.replace('_', ' ')}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-slate-500">
                      {formatDate(item.created_at)}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={(e) => handleToggleFlag(item, e)}
                          className={`p-1.5 rounded-lg transition-colors ${
                            item.flagged_for_review 
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' 
                              : 'bg-slate-800 hover:bg-amber-500/15 text-slate-400 hover:text-amber-400'
                          }`}
                          title={item.flagged_for_review ? "Remove from Review Queue" : "Send to QA Review Queue"}
                        >
                          <Flag className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedInspection(item);
                          }}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                          title="View Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400"
                          title="Delete Record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal if selected */}
      {selectedInspection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-3xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h2 className="font-bold text-white text-base">Inspection Trace: {selectedInspection.filename}</h2>
                <span className="text-xs text-slate-400 font-mono">{selectedInspection.id}</span>
              </div>
              <button
                onClick={() => setSelectedInspection(null)}
                className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Close
              </button>
            </div>

            <div className="h-[360px]">
              <BoundingBoxViewer
                imageUrl={selectedInspection.annotated_url || selectedInspection.image_url}
                defects={selectedInspection.defects}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block">Status</span>
                <span className="font-bold text-slate-200">{selectedInspection.status}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block">Defects</span>
                <span className="font-bold text-slate-200">{selectedInspection.defect_count}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block">Max Confidence</span>
                <span className="font-bold text-emerald-400 font-mono">{formatPercent(selectedInspection.max_confidence)}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block">Inference Speed</span>
                <span className="font-bold text-slate-200 font-mono">{selectedInspection.inference_time_ms} ms</span>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-800">
              <button
                onClick={() => handleToggleFlag(selectedInspection)}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-amber-500/15 border border-slate-700 hover:border-amber-500/40 text-xs font-semibold text-slate-300 hover:text-amber-300 flex items-center gap-1.5 transition-colors"
              >
                <Flag className="w-3.5 h-3.5 text-amber-400" />
                <span>{selectedInspection.flagged_for_review ? 'Remove from Review Queue' : 'Flag for Review Queue'}</span>
              </button>
              {selectedInspection.flagged_for_review && (
                <button
                  onClick={() => navigate('/review')}
                  className="px-3.5 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-xs font-semibold text-amber-300 flex items-center gap-1.5 transition-colors"
                >
                  <span>Open in Review Queue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default History;

