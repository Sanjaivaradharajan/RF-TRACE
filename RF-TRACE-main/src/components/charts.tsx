import { useEffect, useRef } from 'react';
import type { AnalysisResult } from '../types';

export function SpectrumChart({ d }: { d: AnalysisResult['spectrum'] }) {
  const W = 800, H = 320, m = { l: 48, r: 16, t: 16, b: 32 };
  const f0 = d.freqMHz[0], f1 = d.freqMHz[d.freqMHz.length - 1], y0 = -100, y1 = 0;
  const x = (f: number) => m.l + ((f - f0) / (f1 - f0)) * (W - m.l - m.r);
  const y = (p: number) => m.t + ((y1 - p) / (y1 - y0)) * (H - m.t - m.b);

  const path = d.freqMHz
    .map((f, i) => `${i === 0 ? 'M' : 'L'}${x(f).toFixed(1)},${y(d.powerDb[i]).toFixed(1)}`)
    .join(' ');

  const marks = [
    [d.fcMHz - d.bwMHz / 2, 'var(--color-warn)', 'BW-'],
    [d.fcMHz, 'var(--color-accent)', 'fc'],
    [d.fcMHz + d.bwMHz / 2, 'var(--color-warn)', 'BW+'],
  ] as const;

  return (
    <div className="bg-panel border border-line rounded-xl shadow-lg p-4 transition-colors duration-200 space-y-3">
      <header className="flex items-center justify-between pb-3 border-b border-line/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent glow-accent animate-pulse" />
          <h3 className="font-mono font-bold text-xs uppercase tracking-wider text-main">POWER SPECTRUM</h3>
        </div>
        <span className="font-mono text-[11px] text-muted">
          fc: {d.fcMHz.toFixed(3)} MHz | BW: {d.bwMHz.toFixed(3)} MHz
        </span>
      </header>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Power spectrum">
        {[-100, -80, -60, -40, -20, 0].map((p) => (
          <g key={p}>
            <line x1={m.l} x2={W - m.r} y1={y(p)} y2={y(p)} stroke="var(--color-line)" strokeWidth="1" strokeDasharray="2 4" />
            <text x={m.l - 6} y={y(p) + 4} textAnchor="end" className="font-mono text-[10px]" fill="var(--color-text-muted)">
              {p}
            </text>
          </g>
        ))}
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const f = f0 + t * (f1 - f0);
          return (
            <text key={t} x={x(f)} y={H - 8} textAnchor="middle" className="font-mono text-[10px]" fill="var(--color-text-muted)">
              {f.toFixed(2)}
            </text>
          );
        })}
        <path d={path} fill="none" stroke="var(--color-accent)" strokeWidth="1.6" />
        {marks.map(([f, c, l]) => (
          <g key={l}>
            <line x1={x(f)} x2={x(f)} y1={m.t} y2={H - m.b} stroke={c} strokeDasharray="4 3" strokeWidth="1.2" />
            <text x={x(f) + 4} y={m.t + 12} className="font-mono text-[10px] font-bold" fill={c}>
              {l}
            </text>
          </g>
        ))}
        <text x={12} y={H / 2} className="font-mono text-[10px]" fill="var(--color-text-muted)" transform={`rotate(-90 12 ${H / 2})`} textAnchor="middle">
          Power (dB)
        </text>
        <text x={W / 2} y={H - 2} className="font-mono text-[10px]" fill="var(--color-text-muted)" textAnchor="middle">
          Frequency (MHz)
        </text>
      </svg>
    </div>
  );
}

const color = (v: number) => {
  const t = Math.min(1, Math.max(0, v));
  return `rgb(${Math.round(255 * Math.max(0, t * 2 - 1))},${Math.round(230 * Math.pow(t, 0.9))},${Math.round(60 + 160 * (1 - Math.abs(t * 2 - 0.7)))})`;
};

export function Waterfall({ d }: { d: AnalysisResult['waterfall'] }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const rows = d.data.length, cols = d.data[0].length, s = 6;
    c.width = cols * s;
    c.height = rows * s;
    const g = c.getContext('2d')!;
    d.data.forEach((row, y) =>
      row.forEach((v, x) => {
        g.fillStyle = color(v);
        g.fillRect(x * s, y * s, s, s);
      })
    );
  }, [d]);

  return (
    <div className="bg-panel border border-line rounded-xl shadow-lg p-4 transition-colors duration-200 space-y-3">
      <header className="flex items-center justify-between pb-3 border-b border-line/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent glow-accent animate-pulse" />
          <h3 className="font-mono font-bold text-xs uppercase tracking-wider text-main">SPECTROGRAM WATERFALL</h3>
        </div>
        <span className="font-mono text-[11px] text-muted">
          0–{d.durationS}s | {d.fMinMHz.toFixed(2)}–{d.fMaxMHz.toFixed(2)} MHz
        </span>
      </header>
      <div>
        <canvas ref={ref} className="w-full border border-line rounded-xs" style={{ imageRendering: 'pixelated' }} aria-label="Spectrogram" />
        <div className="flex justify-between text-xs text-sub font-mono mt-2 px-1">
          <span>{d.fMinMHz.toFixed(2)} MHz</span>
          <span>Time ↓ 0–{d.durationS}s</span>
          <span>{d.fMaxMHz.toFixed(2)} MHz</span>
        </div>
      </div>
    </div>
  );
}

export function Constellation({ d }: { d: AnalysisResult['constellation'] }) {
  const S = 420, R = 1.6, c = S / 2, k = c / R;

  return (
    <div className="bg-panel border border-line rounded-xl shadow-lg p-4 transition-colors duration-200 space-y-3">
      <header className="flex items-center justify-between pb-3 border-b border-line/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent glow-accent animate-pulse" />
          <h3 className="font-mono font-bold text-xs uppercase tracking-wider text-main">IQ CONSTELLATION</h3>
        </div>
        <span className="font-mono text-[11px] text-muted">{d.rx.length} RX Symbols</span>
      </header>

      <svg viewBox={`0 0 ${S} ${S}`} className="w-full max-w-[520px] mx-auto" role="img" aria-label="Constellation diagram">
        <rect width={S} height={S} fill="var(--color-bg)" stroke="var(--color-line)" strokeWidth="1" />
        {[-1, -0.5, 0.5, 1].map((t) => (
          <g key={t}>
            <line x1={c + t * k} x2={c + t * k} y1={0} y2={S} stroke="var(--color-line)" strokeDasharray="2 4" opacity={0.6} />
            <line y1={c - t * k} y2={c - t * k} x1={0} x2={S} stroke="var(--color-line)" strokeDasharray="2 4" opacity={0.6} />
          </g>
        ))}
        <line x1={0} x2={S} y1={c} y2={c} stroke="var(--color-line)" strokeWidth="1.5" />
        <line x1={c} x2={c} y1={0} y2={S} stroke="var(--color-line)" strokeWidth="1.5" />
        {d.rx.map((p, n) => (
          <circle key={n} cx={c + p.i * k} cy={c - p.q * k} r={2} fill="var(--color-accent)" opacity={0.65} />
        ))}
        {d.ideal.map((p, n) => (
          <g key={n} stroke="var(--color-warn)" strokeWidth="1.8">
            <line x1={c + p.i * k - 6} x2={c + p.i * k + 6} y1={c - p.q * k} y2={c - p.q * k} />
            <line x1={c + p.i * k} x2={c + p.i * k} y1={c - p.q * k - 6} y2={c - p.q * k + 6} />
          </g>
        ))}
        <text x={S - 10} y={c - 8} textAnchor="end" className="font-mono text-xs font-bold" fill="var(--color-text-muted)">
          I
        </text>
        <text x={c + 8} y={16} className="font-mono text-xs font-bold" fill="var(--color-text-muted)">
          Q
        </text>
      </svg>
    </div>
  );
}
