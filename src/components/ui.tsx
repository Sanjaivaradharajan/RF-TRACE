import type { ReactNode } from 'react';
import type { Provenance } from '../types';

const tone: Record<Provenance, string> = {
  Measured: 'text-emerald-700 dark:text-emerald-400 border-emerald-500/40 bg-emerald-500/10 font-bold shadow-2xs',
  Estimated: 'text-amber-700 dark:text-amber-400 border-amber-500/40 bg-amber-500/10 font-bold shadow-2xs',
  Metadata: 'text-sky-700 dark:text-sky-400 border-sky-500/40 bg-sky-500/10 font-bold shadow-2xs',
  Unknown: 'text-muted border-line bg-raised/50 font-medium',
};

export const SourceBadge = ({ s }: { s: Provenance }) => (
  <span className={`text-[10px] font-mono tracking-wider uppercase border rounded-xs px-2 py-0.5 ${tone[s]}`}>{s}</span>
);

export const Card = ({ title, right, children, className = '' }: { title: string; right?: ReactNode; children: ReactNode; className?: string }) => (
  <section className={`bg-panel border border-line rounded-md shadow-xs hover:border-line/90 hover:shadow-sm transition-all duration-200 ${className}`}>
    <header className="flex items-center justify-between gap-3 px-4 py-3 border-b border-line bg-raised/40">
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-3.5 bg-accent/80 rounded-xs" />
        <h3 className="text-xs font-bold tracking-wider uppercase text-main font-mono">{title}</h3>
      </div>
      {right}
    </header>
    <div className="p-4">{children}</div>
  </section>
);

export const Page = ({ title, sub, actions, children }: { title: string; sub?: string; actions?: ReactNode; children: ReactNode }) => (
  <div className="space-y-5">
    <div className="flex flex-wrap items-end justify-between gap-3 border-b border-line/70 pb-3">
      <div>
        <h1 className="text-xl md:text-2xl font-black tracking-tight text-main">{title}</h1>
        {sub && <p className="text-xs text-sub mt-1 font-medium tracking-wide">{sub}</p>}
      </div>
      {actions}
    </div>
    {children}
  </div>
);

export const Empty = ({ text = 'No analysis data. Upload a capture file on the Dashboard and run the signal analysis pipeline.' }: { text?: string }) => (
  <div className="border border-dashed border-line/80 rounded-md p-12 text-center text-sm text-sub font-medium bg-raised/20">
    <div className="w-8 h-8 mx-auto mb-3 rounded-full bg-raised flex items-center justify-center text-muted border border-line">!</div>
    {text}
  </div>
);

export const Btn = ({ children, primary, ...p }: { primary?: boolean } & React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button
    {...p}
    className={`px-4 py-2 text-xs md:text-sm rounded-sm border font-bold uppercase tracking-wider transition-all duration-150 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed ${
      primary
        ? 'bg-accent text-white dark:text-slate-950 border-accent hover:brightness-110 shadow-xs glow-accent'
        : 'border-line bg-raised text-main hover:border-slate-400 hover:text-title'
    }`}
  >
    {children}
  </button>
);

export const Row = ({ k, v }: { k: string; v: ReactNode }) => (
  <div className="flex justify-between items-center gap-4 py-2 text-sm border-b border-line/40 last:border-0 hover:bg-raised/40 px-2 -mx-2 rounded-xs transition-colors">
    <span className="text-xs uppercase font-semibold text-sub tracking-wider">{k}</span>
    <span className="font-mono text-right text-main font-bold">{v}</span>
  </div>
);
