// PREVIEW DATA ONLY. Synthetic values generated for UI layout; not the output of any analysis.
import type { AnalysisResult, ModName } from '../types';
const rng = (s = 42) => () => { s |= 0; s = (s + 0x6d2b79f5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const gauss = (r: () => number) => Math.sqrt(-2 * Math.log(r() + 1e-9)) * Math.cos(2 * Math.PI * r());

export function mockResult(name = 'sample_capture.iq', size = 8388608): AnalysisResult {
  const r = rng(), fc = 433.92, fs = 2.4, bw = 0.18, N = 256;
  const freqMHz = Array.from({ length: N }, (_, k) => fc - fs / 2 + (k * fs) / N);
  const powerDb = freqMHz.map((f) => -92 + 2.5 * gauss(r) + 52 * Math.exp(-(((f - fc) / (bw / 2.2)) ** 2)) + (Math.abs(f - (fc + 0.7)) < 0.01 ? 14 : 0));
  const rows = 64, cols = 128;
  const data = Array.from({ length: rows }, (_, y) => Array.from({ length: cols }, (_, x) => {
    const burst = y % 20 < 14 ? 1 : 0.25;
    return Math.min(1, Math.max(0, 0.12 + 0.05 * r() + burst * 0.75 * Math.exp(-(((x - cols / 2) / 9) ** 2))));
  }));
  const s = Math.SQRT1_2, ideal = [[s, s], [-s, s], [-s, -s], [s, -s]].map(([i, q]) => ({ i, q }));
  const rx = Array.from({ length: 500 }, () => { const p = ideal[Math.floor(r() * 4)]; return { i: p.i + 0.1 * gauss(r), q: p.q + 0.1 * gauss(r) }; });
  const bits = Array.from({ length: 512 }, () => (r() > 0.5 ? '1' : '0')).join('');
  const probs: Record<ModName, number> = { BPSK: 0.06, QPSK: 0.81, '8PSK': 0.08, FSK: 0.02, '16QAM': 0.03 };
  return {
    file: { name, sizeBytes: size, format: name.toLowerCase().endsWith('.wav') ? 'WAV' : 'IQ', sampleFormat: 'complex int16', durationS: 1.75 },
    params: {
      fs: { label: 'Sampling frequency', value: '2.400', unit: 'MS/s', source: 'Metadata', note: 'From file header / user input' },
      fc: { label: 'Carrier frequency', value: '433.920', unit: 'MHz', source: 'Measured', note: 'Spectral peak centroid' },
      bw: { label: 'Occupied bandwidth', value: '180.0', unit: 'kHz', source: 'Measured', note: '99% power' },
      symbolRate: { label: 'Symbol rate', value: '75.0', unit: 'kBd', source: 'Estimated', note: 'Cyclostationary estimate' },
      snr: { label: 'SNR', value: '17.8', unit: 'dB', source: 'Estimated' },
      modulation: { label: 'Modulation', value: 'QPSK', source: 'Estimated', note: 'CNN + DSP fusion' },
    },
    spectrum: { freqMHz, powerDb, fcMHz: fc, bwMHz: bw },
    waterfall: { data, fMinMHz: fc - fs / 2, fMaxMHz: fc + fs / 2, durationS: 1.75 },
    constellation: { rx, ideal },
    modulation: {
      detected: 'QPSK', confidence: 0.81, probs,
      cnnEvidence: ['Four-cluster constellation pattern', 'Low amplitude variance across symbols', 'Phase histogram peaks at ±45°, ±135°'],
      dspEvidence: [
        { metric: '4th-order cumulant C42', value: '-1.02', note: 'Close to QPSK reference' },
        { metric: 'Amplitude variance', value: '0.03', note: 'Constant-envelope behavior' },
        { metric: 'Spectral line at 4×fc', value: 'Present', note: 'Consistent with M=4 PSK' },
      ],
    },
    bits,
    fec: [
      { name: 'Block', score: 0.34, status: 'inconclusive', note: 'Weak periodicity at n=15' },
      { name: 'Convolutional', score: 0.52, status: 'inconclusive', note: 'Rate 1/2 hypothesis, K=7' },
      { name: 'Diagonal interleaving', score: 0.21, status: 'rejected', note: 'No diagonal correlation' },
      { name: 'Pseudo-random interleaving', score: 0.18, status: 'rejected', note: 'No stable permutation found' },
      { name: 'Convolutional / Viterbi', score: 0.87, status: 'candidate', note: 'Low path-metric on rate 1/2, K=7' },
      { name: 'Reed-Solomon', score: 0.44, status: 'inconclusive', note: 'RS(255,223) syndrome inconclusive' },
      { name: 'LDPC', score: 0.12, status: 'rejected', note: 'Parity checks fail' },
      { name: 'Concatenated FEC', score: 0.63, status: 'candidate', note: 'Viterbi + RS chain plausible' },
    ],
    demod: { status: 'Complete', recoveredBits: bits.length },
  };
}
