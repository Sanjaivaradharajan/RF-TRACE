import { useMemo, useState } from 'react';
import type { Analysis } from '../hooks/useAnalysis';
import { Btn, Card, Empty, Page, Row } from '../components/ui';

export function Modulation({ a }: { a: Analysis }) {
  const m = a.result?.modulation;
  if (!m) return <Page title="Modulation"><Empty /></Page>;
  const confPct = Math.min(100, Math.max(0, m.confidence > 1 ? m.confidence : m.confidence * 100));

  return (
    <Page title="Modulation" sub="Classifier output and supporting evidence">
      <div className="grid lg:grid-cols-3 gap-3">
        <Card title="Classification probabilities" className="lg:col-span-2">
          <div className="space-y-3">
            {(Object.entries(m.probs) as [string, number][])
              .sort((x, y) => y[1] - x[1])
              .map(([k, rawV]) => {
                const pct = Math.min(100, Math.max(0, rawV > 1 ? rawV : rawV * 100));
                const isDetected = k === m.detected;
                return (
                  <div key={k} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className={`font-mono font-bold ${isDetected ? 'text-accent' : 'text-main'}`}>
                        {k}
                        {isDetected && (
                          <span className="text-[10px] bg-accent/20 text-accent border border-accent/30 rounded-xs px-1.5 py-0.5 ml-2 uppercase tracking-wider font-semibold">
                            Detected
                          </span>
                        )}
                      </span>
                      <span className="font-mono font-semibold text-main">{pct.toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-raised border border-line rounded-xs overflow-hidden p-0.5">
                      <div
                        className={`h-full transition-all duration-500 rounded-xs ${
                          isDetected
                            ? 'bg-accent glow-accent'
                            : pct > 20
                            ? 'bg-sky-600/80 dark:bg-sky-500/80'
                            : 'bg-slate-400/80 dark:bg-slate-500/80'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
          </div>
        </Card>
        <Card title="Result">
          <div className="text-xs uppercase font-mono tracking-wider text-muted font-bold mb-1">Detected Scheme</div>
          <div className="font-mono text-3xl font-bold text-accent glow-accent mb-4">{m.detected}</div>
          <div className="pt-3 border-t border-line/40 space-y-1.5">
            <div className="flex justify-between items-center text-xs uppercase font-semibold text-sub tracking-wider">
              <span>Confidence Score</span>
              <span className="font-mono text-main font-bold text-sm">{confPct.toFixed(1)}%</span>
            </div>
            <div className="h-3 bg-raised border border-line rounded-xs overflow-hidden p-0.5">
              <div
                className="h-full bg-accent glow-accent transition-all duration-500 rounded-xs"
                style={{ width: `${confPct}%` }}
              />
            </div>
          </div>
        </Card>
        <Card title="CNN evidence">
          <ul className="text-sm space-y-1.5 list-disc pl-4 text-sub font-medium">
            {m.cnnEvidence.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        </Card>
        <Card title="DSP evidence" className="lg:col-span-2">
          {m.dspEvidence.map((e) => (
            <Row key={e.metric} k={`${e.metric} — ${e.note}`} v={e.value} />
          ))}
        </Card>
      </div>
    </Page>
  );
}

export function BitStream({ a }: { a: Analysis }) {
  const [q, setQ] = useState(''); const [view, setView] = useState<'bin' | 'hex'>('bin'); const [copied, setCopied] = useState(false);
  const bits = a.result?.bits ?? '';
  const hex = useMemo(() => (bits.match(/.{1,8}/g) ?? []).map((b) => parseInt(b.padEnd(8, '0'), 2).toString(16).padStart(2, '0')).join(' '), [bits]);
  const valid = /^[01]+$/.test(q);
  const parts = valid ? bits.split(new RegExp(`(${q})`)) : [bits];
  const copy = async () => { await navigator.clipboard.writeText(view === 'hex' ? hex : bits); setCopied(true); setTimeout(() => setCopied(false), 1200); };
  if (!a.result) return <Page title="Bit Stream"><Empty /></Page>;
  return (
    <Page title="Bit Stream" sub={`${bits.length} bits · ${Math.ceil(bits.length / 8)} bytes`}>
      <Card title="Recovered data" right={<div className="flex gap-2"><Btn onClick={() => setView(view === 'bin' ? 'hex' : 'bin')}>{view === 'bin' ? 'Show hex' : 'Show binary'}</Btn><Btn onClick={copy}>{copied ? 'Copied' : 'Copy'}</Btn></div>}>
        <div className="flex items-center gap-2 mb-3"><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search bit pattern, e.g. 10110"
          className="bg-raised border border-line text-main placeholder:text-muted rounded-sm px-2 py-1.5 text-sm font-mono w-64" aria-label="Search bit pattern" />
          {q && <span className="text-xs text-sub font-medium">{valid ? `${parts.length > 1 ? (parts.length - 1) / 2 : 0} matches` : 'Use 0 and 1 only'}</span>}</div>
        <div className="font-mono text-sm break-all leading-6 max-h-96 overflow-auto text-main">
          {view === 'hex' ? hex : parts.map((p, i) => (i % 2 ? <mark key={i} className="bg-accent/30 text-accent font-bold px-0.5">{p}</mark> : <span key={i}>{p}</span>))}
        </div>
      </Card>
    </Page>
  );
}

const st = { candidate: 'text-accent border-accent/40 font-semibold', inconclusive: 'text-warn border-warn/40 font-semibold', rejected: 'text-sub border-line' } as const;
export function Fec({ a }: { a: Analysis }) {
  if (!a.result) return <Page title="FEC / Interleaving"><Empty /></Page>;
  return (
    <Page title="FEC / Interleaving" sub="Candidate schemes ranked by score">
      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-3">{a.result.fec.map((f) => (
        <Card key={f.name} title={f.name} right={<span className={`text-[10px] border rounded-sm px-1.5 py-0.5 ${st[f.status]}`}>{f.status}</span>}>
          <div className="font-mono text-xl font-bold text-main">{(f.score * 100).toFixed(0)}%</div>
          <div className="h-1.5 bg-raised border border-line mt-1 mb-2 rounded-xs"><div className="h-full bg-accent" style={{ width: `${f.score * 100}%` }} /></div>
          <p className="text-xs text-sub font-medium">{f.note}</p></Card>))}</div>
    </Page>
  );
}
