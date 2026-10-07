import type { AnalysisResult } from '../types';
import { mockResult } from './mock';

export function getApiBaseUrl(): string {
  const saved = localStorage.getItem('rf_api_url');
  if (saved && saved.trim()) return saved.trim();
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  return 'http://localhost:8000';
}

export const USE_MOCK: boolean = import.meta.env.VITE_USE_MOCK === 'true';
export const STAGES = ['Upload', 'Preprocess', 'Analyze', 'Classify', 'Demodulate', 'Decode', 'Complete'] as const;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const api = {
  async health(customUrl?: string): Promise<boolean> {
    const baseUrl = customUrl ?? getApiBaseUrl();
    try {
      const r = await fetch(`${baseUrl}/api/health`, { method: 'GET' });
      return r.ok;
    } catch {
      return false;
    }
  },
  async analyze(file: File, onStage: (i: number) => void): Promise<AnalysisResult> {
    if (USE_MOCK) {
      for (let i = 0; i < STAGES.length - 1; i++) {
        onStage(i);
        await sleep(600);
      }
      return mockResult(file.name, file.size);
    }

    const API_BASE = getApiBaseUrl();

    // Step 1: Upload File to backend
    onStage(0);
    const fd = new FormData();
    fd.append('file', file);
    const up = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: fd });
    if (!up.ok) throw new Error(`Upload failed (${up.status})`);
    const uploadRes = await up.json();
    const fileId = uploadRes.fileId;

    // Step 2: Start Analysis Pipeline
    onStage(1);
    const startRes = await fetch(`${API_BASE}/api/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileId }),
    });
    if (!startRes.ok) throw new Error(`Failed to start analysis (${startRes.status})`);
    const { analysisId } = await startRes.json();

    // Step 3: Poll status until completion (max 150 iterations = 90s for cloud backend cold starts)
    let pollCount = 0;
    let isComplete = false;
    while (pollCount < 150) {
      pollCount++;
      try {
        const statusResp = await fetch(`${API_BASE}/api/analysis/${analysisId}/status`);
        if (statusResp.ok) {
          const s = await statusResp.json();
          const stageIdx = Math.min(Math.floor((s.stage / 12) * (STAGES.length - 1)), STAGES.length - 2);
          onStage(stageIdx);

          if (s.state === 'complete') {
            isComplete = true;
            break;
          }
          if (s.state === 'error') throw new Error(s.error ?? 'Analysis failed on backend server');
        }
      } catch (err) {
        if (err instanceof Error && err.message.includes('Analysis failed')) throw err;
      }
      await sleep(600);
    }

    if (!isComplete) {
      throw new Error('Analysis request timed out while waiting for backend server response.');
    }

    // Step 4: Fetch Results
    onStage(STAGES.length - 1);
    const resultsResp = await fetch(`${API_BASE}/api/analysis/${analysisId}/results`);
    if (!resultsResp.ok) throw new Error(`Failed to retrieve analysis results (${resultsResp.status})`);
    return resultsResp.json();
  },
};
