import type { Analysis } from '../hooks/useAnalysis';
import { Card, Empty, Page, SourceBadge } from '../components/ui';

export default function SignalAnalysis({ a }: { a: Analysis }) {
  if (!a.result) return <Page title="Signal Analysis"><Empty /></Page>;
  return (
    <Page title="Signal Analysis" sub="Each value is labeled with how it was obtained.">
      <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
        {Object.values(a.result.params).map((p) => (
          <Card key={p.label} title={p.label} right={<SourceBadge s={p.source} />}>
            <div className="font-mono text-2xl text-main">{p.value ?? 'Unknown'}<span className="text-sm text-sub ml-1.5">{p.unit}</span></div>
            {p.note && <p className="text-xs text-muted mt-1">{p.note}</p>}
          </Card>
        ))}
      </div>
    </Page>
  );
}
