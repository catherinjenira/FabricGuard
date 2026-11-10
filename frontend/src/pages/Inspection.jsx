import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ScanLine, RotateCcw, Sparkles } from 'lucide-react';
import ImageUploader from '../components/ImageUploader';
import BoundingBoxViewer from '../components/BoundingBoxViewer';
import DetectionResult from '../components/DetectionResult';
import { useInspection } from '../hooks/useInspection';

export function Inspection() {
  const navigate = useNavigate();
  const { loading, progress, result, inspectImage, reset } = useInspection();
  const [selectedIndex, setSelectedIndex] = useState(null);

  const handleInspect = async (file, options) => {
    setSelectedIndex(null);
    await inspectImage(file, options);
  };

  const handleOpenReview = () => {
    navigate('/review');
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ScanLine className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold text-white tracking-tight">Real-Time Fabric Inspection</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Feed individual textile swatches for real-time defect segmentation and uncertainty scoring.
          </p>
        </div>

        {result && (
          <button
            onClick={() => {
              reset();
              setSelectedIndex(null);
            }}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-1.5 self-start sm:self-auto transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Swatch Inspection</span>
          </button>
        )}
      </div>

      {/* Main Workspace Layout */}
      {!result ? (
        <div className="max-w-3xl mx-auto py-4">
          <ImageUploader 
            onInspect={handleInspect} 
            loading={loading} 
            progress={progress} 
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Visual Canvas (8 cols) */}
          <div className="lg:col-span-7 xl:col-span-8 h-[600px]">
            <BoundingBoxViewer
              imageUrl={result.annotated_url || result.image_url}
              defects={result.defects}
              selectedIndex={selectedIndex}
              onSelectDefect={(idx) => setSelectedIndex(idx)}
            />
          </div>

          {/* Diagnosis & Breakdown (4-5 cols) */}
          <div className="lg:col-span-5 xl:col-span-4">
            <DetectionResult
              result={result}
              selectedIndex={selectedIndex}
              onSelectDefect={(idx) => setSelectedIndex(idx)}
              onOpenReview={handleOpenReview}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default Inspection;

