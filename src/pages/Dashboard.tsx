import { useRef, useState } from 'react';
import type { Analysis } from '../hooks/useAnalysis';
import { STAGES } from '../services/api';
import { Btn, Card, Page, Row } from '../components/ui';

const fmt = (b: number) => (b > 1e6 ? `${(b / 1e6).toFixed(2)} MB` : `${(b / 1e3).toFixed(1)} KB`);
export default function Dashboard({ a }: { a: Analysis }) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const pick = (f?: File) => { if (f && /\.(iq|wav|cfile)$/i.test(f.name)) a.setFile(f); };
  const info = a.file ? { name: a.file.name, size: fmt(a.file.size), fmt: /\.wav$/i.test(a.file.name) ? 'WAV' : 'IQ', sf: '—', dur: '—' }
    : a.result ? { name: a.result.file.name, size: fmt(a.result.file.sizeBytes), fmt: a.result.file.format, sf: a.result.file.sampleFormat, dur: `${a.result.file.durationS} s` } : null;
  return (
    <Page title="Dashboard" sub="Upload a capture and run the analysis pipeline.">
      <div className="grid lg:grid-cols-3 gap-3">
        <Card title="Input" className="lg:col-span-2">
          <div onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
            onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0]); }}
            className={`border border-dashed rounded-sm py-12 text-center ${over ? 'border-accent bg-accent/5' : 'border-line bg-raised/30'}`}>
            <p className="text-sm font-semibold text-main">Drop an <span className="font-mono text-accent">.IQ</span> or <span className="font-mono text-accent">.WAV</span> file here</p>
            <p className="text-xs text-sub font-medium mt-1 mb-4">Raw IQ files may need a sampling rate and sample format in Settings.</p>
            <div className="flex justify-center gap-2">
              <Btn onClick={() => input.current?.click()}>Upload IQ file</Btn><Btn onClick={() => input.current?.click()}>Upload WAV file</Btn>
              <Btn primary onClick={a.run} disabled={!a.file || a.state === 'running'}>Run Analysis</Btn>
            </div>
            <input ref={input} type="file" accept=".iq,.wav,.cfile" hidden onChange={(e) => pick(e.target.files?.[0])} />
          </div>
          {a.error && <p className="mt-3 text-sm font-medium text-bad">{a.error}. Check that the backend is running and try again.</p>}
        </Card>
        <Card title="File information">
          {info ? <><Row k="Name" v={info.name} /><Row k="Size" v={info.size} /><Row k="Format" v={info.fmt} /><Row k="Sample format" v={info.sf} /><Row k="Duration" v={info.dur} /></>
            : <p className="text-sm font-medium text-sub">No file selected.</p>}
        </Card>
      </div>
      <Card title="Analysis pipeline">
        <ol className="flex flex-wrap gap-y-2 items-center text-sm font-medium">
          {STAGES.map((s, i) => {
            const st = a.state === 'complete' || i < a.stage ? 'done' : i === a.stage && a.state === 'running' ? 'active' : 'todo';
            return (
              <li key={s} className="flex items-center">
                <span className={`px-3 py-1.5 border rounded-sm font-semibold ${st === 'done' ? 'border-accent/50 text-accent bg-accent/10' : st === 'active' ? 'border-warn text-warn bg-warn/10' : 'border-line text-sub'}`}>{s}</span>
                {i < STAGES.length - 1 && <span className="mx-2 text-muted">→</span>}
              </li>
            );
          })}
        </ol>
      </Card>
    </Page>
  );
}
