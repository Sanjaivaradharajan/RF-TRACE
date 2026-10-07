import { useEffect, useState } from 'react';
import { api, STAGES, USE_MOCK } from '../services/api';
import { mockResult } from '../services/mock';
import type { AnalysisResult, BackendState, RunState } from '../types';

export function useAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<RunState>(USE_MOCK ? 'complete' : 'idle');
  const [stage, setStage] = useState(USE_MOCK ? STAGES.length - 1 : -1);
  const [result, setResult] = useState<AnalysisResult | null>(USE_MOCK ? mockResult() : null);
  const [error, setError] = useState<string | null>(null);
  const [backend, setBackend] = useState<BackendState>(USE_MOCK ? 'mock' : 'checking');

  useEffect(() => { if (!USE_MOCK) api.health().then(() => setBackend('online')).catch(() => setBackend('offline')); }, []);

  const run = async () => {
    if (!file) return;
    setState('running'); setResult(null); setError(null); setStage(0);
    try { setResult(await api.analyze(file, setStage)); setStage(STAGES.length - 1); setState('complete'); }
    catch (e) { setError(e instanceof Error ? e.message : 'Analysis failed'); setState('error'); }
  };
  const reset = () => { setFile(null); setResult(null); setError(null); setState('idle'); setStage(-1); };
  return { file, setFile, state, stage, result, error, backend, run, reset, isPreview: USE_MOCK };
}
export type Analysis = ReturnType<typeof useAnalysis>;
