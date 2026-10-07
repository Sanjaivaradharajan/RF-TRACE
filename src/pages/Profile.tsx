import type { Analysis } from '../hooks/useAnalysis';
import { Card, Empty, Page, Row, SourceBadge } from '../components/ui';
import { ExportMenu } from '../components/ExportMenu';

export default function Profile({ a }: { a: Analysis }) {
  const r = a.result;
  if (!r) return <Page title="Signal Profile"><Empty /></Page>;
  const ones = [...r.bits].filter((b) => b === '1').length, top = r.fec.reduce((x, y) => (y.score > x.score ? y : x));
  const modConf = Math.min(100, Math.max(0, r.modulation.confidence > 1 ? r.modulation.confidence : r.modulation.confidence * 100));
  const fecScore = Math.min(100, Math.max(0, top.score > 1 ? top.score : top.score * 100));

  return (
    <Page title="Signal Profile" sub="Consolidated report" actions={<ExportMenu result={r} />}>
      <div className="grid lg:grid-cols-3 gap-3">
        <Card title="Input file"><Row k="Name" v={r.file.name} /><Row k="Format" v={r.file.format} /><Row k="Sample format" v={r.file.sampleFormat} /></Card>
        <Card title="Signal parameters" className="lg:col-span-2">
          {Object.values(r.params).map((p) => <Row key={p.label} k={p.label} v={<span className="inline-flex items-center gap-2">{p.value ?? 'Unknown'} {p.unit}<SourceBadge s={p.source} /></span>} />)}</Card>
        <Card title="Modulation">
          <Row k="Detected" v={r.modulation.detected} />
          <div className="py-2 text-sm border-b border-line/40 last:border-0 hover:bg-raised/40 px-2 -mx-2 rounded-xs transition-colors">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs uppercase font-semibold text-sub tracking-wider">Confidence</span>
              <span className="font-mono text-right text-main font-bold">{modConf.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-raised border border-line rounded-xs overflow-hidden p-0.5">
              <div
                className="h-full bg-accent glow-accent transition-all duration-500 rounded-xs"
                style={{ width: `${modConf}%` }}
              />
            </div>
          </div>
        </Card>
        <Card title="DSP evidence" className="lg:col-span-2">{r.modulation.dspEvidence.map((e) => <Row key={e.metric} k={e.metric} v={e.value} />)}</Card>
        <Card title="FEC / interleaving">
          <Row k="Top candidate" v={top.name} />
          <div className="py-2 text-sm border-b border-line/40 last:border-0 hover:bg-raised/40 px-2 -mx-2 rounded-xs transition-colors">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs uppercase font-semibold text-sub tracking-wider">Score</span>
              <span className="font-mono text-right text-main font-bold">{fecScore.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-raised border border-line rounded-xs overflow-hidden p-0.5">
              <div
                className="h-full bg-accent glow-accent transition-all duration-500 rounded-xs"
                style={{ width: `${fecScore}%` }}
              />
            </div>
          </div>
        </Card>
        <Card title="Demodulation"><Row k="Status" v={r.demod.status} /><Row k="Recovered bits" v={r.demod.recoveredBits} /></Card>
        <Card title="Bit analysis"><Row k="Ones / zeros" v={`${ones} / ${r.bits.length - ones}`} /><Row k="Ones ratio" v={(ones / r.bits.length).toFixed(3)} /></Card>
      </div>
    </Page>
  );
}
