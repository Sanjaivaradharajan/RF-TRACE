export type Provenance = 'Measured' | 'Estimated' | 'Metadata' | 'Unknown';
export type ModName = 'BPSK' | 'QPSK' | '8PSK' | 'FSK' | '16QAM';
export type RunState = 'idle' | 'running' | 'complete' | 'error';
export type BackendState = 'mock' | 'checking' | 'online' | 'offline';

export interface Param { label: string; value: string | null; unit?: string; source: Provenance; note?: string }
export interface FileInfo { name: string; sizeBytes: number; format: 'IQ' | 'WAV'; sampleFormat: string; durationS: number | null }
export interface FecCandidate { name: string; score: number; status: 'candidate' | 'rejected' | 'inconclusive'; note: string }
export interface DspEvidence { metric: string; value: string; note: string }

/** Contract the Python/FastAPI backend should return from GET /api/analyses/{id} */
export interface AnalysisResult {
  file: FileInfo;
  params: { fs: Param; fc: Param; bw: Param; symbolRate: Param; snr: Param; modulation: Param };
  spectrum: { freqMHz: number[]; powerDb: number[]; fcMHz: number; bwMHz: number };
  waterfall: { data: number[][]; fMinMHz: number; fMaxMHz: number; durationS: number }; // values 0..1
  constellation: { rx: { i: number; q: number }[]; ideal: { i: number; q: number }[] };
  modulation: { detected: ModName; confidence: number; probs: Record<ModName, number>; cnnEvidence: string[]; dspEvidence: DspEvidence[] };
  bits: string; // '0'/'1' characters
  fec: FecCandidate[];
  demod: { status: 'Complete' | 'Partial' | 'Failed'; recoveredBits: number };
}
