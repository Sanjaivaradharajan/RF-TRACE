import { useEffect, useState, type ReactNode } from 'react';
import type { Analysis } from '../hooks/useAnalysis';
import { Btn } from '../components/ui';

export const NAV = ['Dashboard', 'Signal Analysis', 'Spectrum', 'Waterfall', 'Constellation', 'Modulation', 'Bit Stream', 'FEC / Interleaving', 'Signal Profile', 'Settings'] as const;
export type PageId = (typeof NAV)[number];

const dot = {
  idle: 'bg-slate-400',
  running: 'bg-accent animate-ping',
  complete: 'bg-emerald-500 shadow-[0_0_8px_#10b981]',
  error: 'bg-bad shadow-[0_0_8px_#f43f5e]',
} as const;

export function AppLayout({ page, setPage, a, children }: { page: PageId; setPage: (p: PageId) => void; a: Analysis; children: ReactNode }) {
  const fileName = a.file?.name ?? a.result?.file.name ?? 'No capture loaded';
  const [theme, setTheme] = useState<'light' | 'dark'>(
    () => (localStorage.getItem('rf_theme') as 'light' | 'dark') || 'dark'
  );

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    localStorage.setItem('rf_theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-bg">
      <aside className="md:w-64 md:min-h-screen shrink-0 bg-panel border-b md:border-b-0 md:border-r border-line flex md:flex-col overflow-x-auto">
        <div className="flex items-center gap-3 px-4 py-4 shrink-0 border-b border-line/60">
          <div className="w-8 h-8 rounded-md bg-accent/15 border border-accent/40 flex items-center justify-center shadow-xs">
            <svg width="18" height="18" viewBox="0 0 22 22" fill="none" stroke="var(--color-accent)" strokeWidth="2.2">
              <path d="M1 11h4l2-7 4 14 3-10 2 3h5" />
            </svg>
          </div>
          <div>
            <div className="font-mono font-black tracking-widest text-main text-sm leading-none">RF-TRACE</div>
            <div className="text-[10px] font-mono tracking-wider text-muted uppercase mt-0.5">SIGINT Workstation</div>
          </div>
        </div>

        <nav className="flex md:flex-col md:p-2 gap-1 overflow-y-auto" aria-label="Main Navigation">
          {NAV.map((n) => {
            const active = page === n;
            return (
              <button
                key={n}
                onClick={() => setPage(n)}
                aria-current={active}
                className={`text-left whitespace-nowrap text-xs uppercase font-mono tracking-wider px-3.5 py-2.5 rounded-sm border-l-2 font-bold transition-all duration-150 ${
                  active
                    ? 'bg-raised text-accent border-accent shadow-2xs font-black'
                    : 'text-sub border-transparent hover:text-main hover:bg-raised/50 hover:border-line'
                }`}
              >
                {n}
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        {/* Top-navigation header */}
        <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 px-5 py-3 bg-panel border-b border-line text-xs shadow-xs">
          <div className="flex items-center gap-3">
            <span className="font-mono font-extrabold text-sm tracking-wider text-main uppercase">
              RF-TRACE <span className="text-accent">|</span> SIGINT Workstation
            </span>
            <div className="hidden sm:flex items-center gap-2 border-l border-line/60 pl-3">
              <span className="text-muted uppercase font-mono text-[10px] tracking-wider">Capture:</span>
              <span className="font-mono font-bold text-main max-w-xs truncate bg-raised px-2 py-0.5 rounded-xs border border-line/50">{fileName}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Live status indicators */}
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 font-mono font-bold text-[11px] text-main px-2.5 py-1 rounded-sm bg-raised/40 border border-line/40">
                <span className="w-2 h-2 rounded-full bg-emerald-500 glow-emerald animate-pulse" />
                <span>Backend Online</span>
              </span>
              <span className="flex items-center gap-1.5 font-mono font-bold text-[11px] text-main px-2.5 py-1 rounded-sm bg-raised/40 border border-line/40">
                <span className="w-2 h-2 rounded-full bg-accent glow-accent" />
                <span>SDR Linked</span>
              </span>
            </div>

            <div className="flex items-center gap-2 border-l border-line/60 pl-2">
              <Btn onClick={toggleTheme}>{theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}</Btn>
              <Btn onClick={a.reset}>Reset</Btn>
              <Btn primary onClick={a.run} disabled={!a.file || a.state === 'running'}>
                Run Analysis
              </Btn>
            </div>
          </div>
        </header>

        {a.isPreview && (
          <div className="px-5 py-1.5 text-xs bg-warn/10 text-warn border-b border-warn/30 font-mono flex items-center justify-between">
            <span>[PREVIEW MODE] Synthetic data mode active. Connect backend (`VITE_USE_MOCK=false`) for live hardware IQ capture.</span>
          </div>
        )}

        <main className="p-5 flex-1 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
