/**
 * Formatting helpers for UI presentation.
 */

export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const d = new Date(dateString);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

export function formatPercent(value, decimals = 1) {
  if (value === undefined || value === null) return '0%';
  const num = typeof value === 'number' ? value : parseFloat(value);
  const normalized = num > 1.0 ? num : num * 100;
  return `${normalized.toFixed(decimals)}%`;
}

export function formatBytes(bytes, decimals = 2) {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export function formatDefectName(name) {
  if (!name) return 'Unknown';
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const DEFECT_COLORS = {
  // 10-Epoch Roboflow YOLO11n-seg Classes
  needle_mark_defect: '#a855f7', // Purple
  hole_defect: '#ef4444',        // Red
  missing_yarn_defect: '#3b82f6',// Blue
  stain_defect: '#f59e0b',       // Amber

  // General fabric defect taxonomies
  hole: '#ef4444',        // Red
  stain: '#f59e0b',       // Amber
  weaving_slub: '#a855f7',// Purple
  yarn_defect: '#3b82f6', // Blue
  crease: '#10b981',      // Emerald
  color_spot: '#ec4899',  // Pink
  knot: '#14b8a6',        // Teal
  foreign_fiber: '#f97316'// Orange
};

export function getDefectColor(defectName) {
  const key = (defectName || '').toLowerCase().replace(/\s+/g, '_');
  return DEFECT_COLORS[key] || '#64748b';
}

export function getSeverityBadge(severity) {
  switch ((severity || '').toLowerCase()) {
    case 'critical':
      return { bg: 'bg-red-500/10 text-red-400 border-red-500/30', label: 'CRITICAL' };
    case 'high':
      return { bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30', label: 'HIGH' };
    case 'medium':
      return { bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30', label: 'MEDIUM' };
    case 'low':
    default:
      return { bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', label: 'LOW' };
  }
}

