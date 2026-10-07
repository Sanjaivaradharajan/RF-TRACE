import type { Analysis } from '../hooks/useAnalysis';
import { Card, Empty, Page, Row } from '../components/ui';
import { Constellation, SpectrumChart, Waterfall } from '../components/charts';

export function Spectrum({ a }: { a: Analysis }) {
  const r = a.result;
  return <Page title="Spectrum" sub="Frequency vs power">{!r ? <Empty /> : <>
    <Card title="Power spectrum"><SpectrumChart d={r.spectrum} /></Card>
    <Card title="Markers"><Row k="Carrier frequency" v={`${r.spectrum.fcMHz.toFixed(3)} MHz`} /><Row k="Bandwidth edges" v={`${(r.spectrum.fcMHz - r.spectrum.bwMHz / 2).toFixed(3)} – ${(r.spectrum.fcMHz + r.spectrum.bwMHz / 2).toFixed(3)} MHz`} /></Card></>}</Page>;
}
export function WaterfallPage({ a }: { a: Analysis }) {
  return <Page title="Waterfall" sub="Time-frequency spectrogram">{!a.result ? <Empty /> : <Card title="Spectrogram"><Waterfall d={a.result.waterfall} /></Card>}</Page>;
}
export function ConstellationPage({ a }: { a: Analysis }) {
  return <Page title="Constellation" sub="I/Q scatter with ideal reference points">{!a.result ? <Empty /> :
    <Card title="I/Q plot" right={<span className="text-xs text-sub"><span className="text-accent">●</span> received <span className="text-warn ml-2">+</span> ideal</span>}><Constellation d={a.result.constellation} /></Card>}</Page>;
}
