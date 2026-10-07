import { useState } from 'react';
import { api, getApiBaseUrl, USE_MOCK } from '../services/api';
import { Btn, Card, Page, Row } from '../components/ui';

export default function Settings() {
  const [url, setUrl] = useState(() => getApiBaseUrl());
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const saveUrl = () => {
    localStorage.setItem('rf_api_url', url.trim());
    setStatus('Saved API URL to local configuration.');
  };

  const testConnection = async () => {
    setLoading(true);
    setStatus('Testing backend connection...');
    const ok = await api.health(url.trim());
    setLoading(false);
    if (ok) {
      setStatus('SUCCESS: FastAPI backend & PyTorch CNN engine are online and reachable!');
    } else {
      setStatus('ERROR: Could not reach backend at ' + url.trim() + '. Make sure backend service is running.');
    }
  };

  return (
    <Page title="Settings" sub="Manage backend API endpoints, PyTorch CNN model configuration, and hardware connection parameters.">
      <div className="grid lg:grid-cols-2 gap-4">
        <Card title="Backend Endpoint Configuration">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-mono font-bold uppercase text-sub mb-1">
                FastAPI Backend URL
              </label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://rf-trace-backend.onrender.com or http://localhost:8000"
                className="w-full bg-raised border border-line text-main font-mono text-xs rounded-sm px-3 py-2 focus:border-accent outline-none"
              />
              <p className="text-[11px] text-muted mt-1 font-mono">
                Enter your deployed Render backend URL (e.g. https://your-backend.onrender.com) or local server endpoint.
              </p>
            </div>

            <div className="flex gap-2">
              <Btn primary onClick={saveUrl}>
                Save URL
              </Btn>
              <Btn onClick={testConnection} disabled={loading}>
                {loading ? 'Testing...' : 'Test Connection'}
              </Btn>
            </div>

            {status && (
              <div
                className={`p-3 rounded-sm text-xs font-mono ${
                  status.startsWith('SUCCESS')
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : status.startsWith('ERROR')
                    ? 'bg-bad/10 text-bad border border-bad/30'
                    : 'bg-raised text-sub border border-line'
                }`}
              >
                {status}
              </div>
            )}
          </div>
        </Card>

        <Card title="System Telemetry & Architecture">
          <Row k="Pipeline Mode" v={USE_MOCK ? 'Mock Preview' : 'Live PyTorch / DSP Engine'} />
          <Row k="AI Framework" v="PyTorch 2.x (ResNet1D Classifier)" />
          <Row k="Signal Processing" v="SciPy & NumPy DSP Pipeline" />
          <Row k="Active Endpoint" v={url} />
        </Card>
      </div>
    </Page>
  );
}
