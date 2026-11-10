import React, { useState, useRef } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Eye, Layers, Tag } from 'lucide-react';
import { getDefectColor, formatDefectName, formatPercent } from '../utils/formatters';

export function BoundingBoxViewer({ 
  imageUrl, 
  defects = [], 
  selectedIndex = null,
  onSelectDefect = () => {} 
}) {
  const [zoom, setZoom] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [showConf, setShowConf] = useState(true);
  const containerRef = useRef(null);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3.0));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.75));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden flex flex-col h-full">
      {/* Control Toolbar */}
      <div className="px-4 py-2.5 bg-slate-950/70 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-400">View Controls</span>
          <div className="h-4 w-px bg-slate-800 mx-1" />
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-colors ${
              showBoxes ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Boxes</span>
          </button>
          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2.5 py-1 rounded-md flex items-center gap-1.5 transition-colors ${
              showLabels ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
            }`}
          >
            <Tag className="w-3.5 h-3.5" />
            <span>Labels</span>
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-slate-900 rounded-lg p-0.5 border border-slate-800">
          <button
            onClick={handleZoomOut}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="px-2 font-mono text-[11px] text-slate-300">{Math.round(zoom * 100)}%</span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 ml-1 border-l border-slate-800"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Viewport Container */}
      <div 
        ref={containerRef}
        className="flex-1 relative overflow-auto p-4 flex items-center justify-center bg-slate-950 min-h-[380px]"
      >
        <div 
          className="relative transition-transform duration-150 inline-block shadow-2xl rounded-lg overflow-hidden border border-slate-800"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
        >
          <img
            src={imageUrl}
            alt="Fabric under test"
            className="block max-h-[500px] w-auto max-w-full select-none pointer-events-none"
          />

          {/* SVG Overlay for Vector Bounding Boxes */}
          {showBoxes && (
            <svg 
              className="absolute inset-0 w-full h-full pointer-events-auto"
              viewBox="0 0 1000 1000"
              preserveAspectRatio="none"
            >
              {defects.map((defect, idx) => {
                const box = defect.box;
                if (!box) return null;
                const isSelected = selectedIndex === idx;
                const color = getDefectColor(defect.class_name);
                
                const x = box.xmin * 1000;
                const y = box.ymin * 1000;
                const w = (box.xmax - box.xmin) * 1000;
                const h = (box.ymax - box.ymin) * 1000;

                return (
                  <g 
                    key={idx} 
                    className="cursor-pointer group"
                    onClick={() => onSelectDefect(idx)}
                  >
                    {/* Bounding Rectangle */}
                    <rect
                      x={x}
                      y={y}
                      width={w}
                      height={h}
                      fill={isSelected ? `${color}33` : `${color}15`}
                      stroke={color}
                      strokeWidth={isSelected ? 6 : 3}
                      strokeDasharray={defect.uncertainty > 0.35 ? "8 4" : "none"}
                      className="transition-all duration-150 hover:stroke-[5px]"
                    />

                    {/* Defect Label Badge */}
                    {showLabels && (
                      <g transform={`translate(${x}, ${Math.max(28, y)})`}>
                        <rect
                          x={0}
                          y={-24}
                          width={Math.max(100, (defect.class_name.length + 6) * 11)}
                          height={24}
                          fill={color}
                          rx={4}
                        />
                        <text
                          x={6}
                          y={-7}
                          fill="#ffffff"
                          fontSize="13"
                          fontWeight="bold"
                          fontFamily="sans-serif"
                        >
                          {formatDefectName(defect.class_name)} {showConf && `${formatPercent(defect.confidence, 0)}`}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </svg>
          )}
        </div>
      </div>
    </div>
  );
}

export default BoundingBoxViewer;

