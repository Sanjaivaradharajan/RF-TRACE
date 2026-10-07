import { useEffect, useRef, useState } from 'react';
import type { AnalysisResult } from '../types';
import { exportToJson, exportToLatex, exportToPdf } from '../services/exportReport';

export function ExportMenu({ result }: { result: AnalysisResult }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="px-4 py-2 text-xs md:text-sm rounded-sm border font-bold uppercase tracking-wider transition-all duration-150 active:scale-[0.98] bg-accent text-white dark:text-slate-950 border-accent hover:brightness-110 shadow-xs glow-accent flex items-center gap-2"
      >
        <span>Export Report</span>
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-panel border border-line ring-1 ring-black ring-opacity-5 z-50 divide-y divide-line/40 animate-in fade-in zoom-in-95 duration-100">
          <div className="p-1">
            <button
              onClick={() => {
                exportToPdf(result);
                setOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-xs font-mono font-bold text-main hover:bg-raised hover:text-accent rounded-xs flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-accent text-sm">📄</span>
                <span>PDF Document</span>
              </div>
              <span className="text-[10px] text-sub font-normal uppercase border border-line px-1 rounded-xs">.pdf</span>
            </button>

            <button
              onClick={() => {
                exportToLatex(result);
                setOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-xs font-mono font-bold text-main hover:bg-raised hover:text-accent rounded-xs flex items-center justify-between transition-colors mt-0.5"
            >
              <div className="flex items-center gap-2">
                <span className="text-amber-500 text-sm">📝</span>
                <span>LaTeX Source</span>
              </div>
              <span className="text-[10px] text-sub font-normal uppercase border border-line px-1 rounded-xs">.tex</span>
            </button>

            <button
              onClick={() => {
                exportToJson(result);
                setOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-xs font-mono font-bold text-main hover:bg-raised hover:text-accent rounded-xs flex items-center justify-between transition-colors mt-0.5"
            >
              <div className="flex items-center gap-2">
                <span className="text-emerald-500 text-sm">💾</span>
                <span>JSON Data</span>
              </div>
              <span className="text-[10px] text-sub font-normal uppercase border border-line px-1 rounded-xs">.json</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
