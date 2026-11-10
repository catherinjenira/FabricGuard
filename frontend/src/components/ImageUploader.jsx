import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Sliders, CheckCircle2, AlertCircle, X, Sparkles } from 'lucide-react';
import { validateImageFile } from '../utils/validators';

const FABRIC_TYPES = [
  { id: 'cotton_weave', label: 'Cotton Plain Weave' },
  { id: 'denim_twill', label: 'Denim Twill' },
  { id: 'jacquard_silk', label: 'Silk Jacquard' },
  { id: 'poly_knit', label: 'Polyester Knit' },
  { id: 'linen_coarse', label: 'Coarse Linen' }
];

export function ImageUploader({ 
  onInspect, 
  loading = false, 
  progress = 0,
  defaultFabric = 'cotton_weave' 
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fabricType, setFabricType] = useState(defaultFabric);
  const [enhanceClahe, setEnhanceClahe] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);
  const [validationError, setValidationError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setValidationError(validation.error);
      return;
    }
    setValidationError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const triggerInspect = () => {
    if (!selectedFile || loading) return;
    onInspect(selectedFile, {
      fabricType,
      enhanceClahe,
      confidenceThreshold
    });
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 backdrop-blur-md space-y-6">
      {/* Upload Zone */}
      {!previewUrl ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-emerald-500 bg-emerald-500/10'
              : 'border-slate-700/80 hover:border-slate-500 bg-slate-950/40'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => handleFile(e.target.files?.[0])}
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
          />
          <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-300 mb-3 shadow-inner">
            <Upload className="w-6 h-6 text-emerald-400" />
          </div>
          <span className="text-sm font-semibold text-slate-200">
            Click to upload fabric image or drag & drop
          </span>
          <span className="text-xs text-slate-500 mt-1">
            JPEG, PNG or WebP up to 15MB • Standard $640 \times 640$ or High-Res
          </span>
        </div>
      ) : (
        /* Preview Banner */
        <div className="relative rounded-xl border border-slate-700 overflow-hidden bg-slate-950">
          <div className="h-64 w-full flex items-center justify-center bg-black/60">
            <img
              src={previewUrl}
              alt="Fabric preview"
              className="max-h-full max-w-full object-contain"
            />
          </div>
          <button
            onClick={handleClear}
            disabled={loading}
            className="absolute top-3 right-3 p-1.5 rounded-lg bg-slate-900/80 hover:bg-rose-500 text-slate-300 hover:text-white transition-colors border border-slate-700"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span className="truncate max-w-xs font-mono">{selectedFile?.name}</span>
            <span>{(selectedFile?.size / (1024 * 1024)).toFixed(2)} MB</span>
          </div>
        </div>
      )}

      {/* Validation Message */}
      {validationError && (
        <div className="flex items-center gap-2 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-3 rounded-lg">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Control Configuration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 border-t border-slate-800/80 text-xs">
        {/* Fabric Type Selector */}
        <div>
          <label className="block text-slate-400 font-semibold mb-1.5">Textile Structure</label>
          <select
            value={fabricType}
            onChange={(e) => setFabricType(e.target.value)}
            disabled={loading}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            {FABRIC_TYPES.map((f) => (
              <option key={f.id} value={f.id}>{f.label}</option>
            ))}
          </select>
        </div>

        {/* Confidence Threshold */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-slate-400 font-semibold">Min Confidence</label>
            <span className="font-mono text-emerald-400 font-bold">{Math.round(confidenceThreshold * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            disabled={loading}
            className="w-full accent-emerald-500 cursor-pointer"
          />
        </div>

        {/* CLAHE Contrast Filter */}
        <div className="flex flex-col justify-end">
          <label className="flex items-center gap-2 cursor-pointer select-none py-2 text-slate-300">
            <input
              type="checkbox"
              checked={enhanceClahe}
              onChange={(e) => setEnhanceClahe(e.target.checked)}
              disabled={loading}
              className="w-4 h-4 rounded text-emerald-500 bg-slate-950 border-slate-700 focus:ring-0 accent-emerald-500 cursor-pointer"
            />
            <span className="font-semibold flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Apply CLAHE Contrast
            </span>
          </label>
        </div>
      </div>

      {/* Action Button & Progress */}
      <div>
        <button
          onClick={triggerInspect}
          disabled={!selectedFile || loading}
          className={`w-full py-3 px-4 rounded-xl font-bold text-sm tracking-wide transition-all duration-200 flex items-center justify-center gap-2 ${
            !selectedFile || loading
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
              : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold shadow-lg shadow-emerald-500/20 active:scale-[0.99]'
          }`}
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Analyzing Textile Weave ({progress}%)...</span>
            </>
          ) : (
            <>
              <Sliders className="w-4 h-4" />
              <span>Run Automated Defect Inspection</span>
            </>
          )}
        </button>

        {loading && (
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-3 overflow-hidden">
            <div
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageUploader;

