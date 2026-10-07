# RF-TRACE: Step-by-Step Implementation Roadmap

**Document Status:** Complete  
**Date:** September 23, 2026  
**Scope:** Complete Backend Construction & Frontend Integration  
**Reference Document:** `Architecture planning.pdf` (Smart India Hackathon 2026 - Problem Statement 26147)

---

## 1. Executive Implementation Roadmap Overview

To complete RF-TRACE and transition from the current frontend-only mockup into a fully operational AI-driven signal intelligence platform, implementation must follow a **phase-by-phase execution strategy**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PHASED ROADMAP                                  │
└─────────────────────────────────────────────────────────────────────────────┘
  Phase 1: Backend Environment & Project Initialization (FastAPI Setup)
    │
    ▼
  Phase 2: Signal Ingestion & Preprocessing Modules (IQ/WAV Readers)
    │
    ▼
  Phase 3: DSP Analysis Engine (FFT Spectrum, STFT Waterfall, Constellation)
    │
    ▼
  Phase 4: Synthetic IQ Dataset Generation & PyTorch CNN Model Training
    │
    ▼
  Phase 5: Multi-Evidence Fusion & Parameter Extraction Engine
    │
    ▼
  Phase 6: Demodulation, Bit Recovery & Viterbi FEC Decoders
    │
    ▼
  Phase 7: FastAPI Endpoints & Asynchronous Task Pipeline Wiring
    │
    ▼
  Phase 8: Ground-Truth End-to-End Test Suite & Hackathon Verification
```

---

## 2. Phase-by-Phase Task Breakdown

### Phase 1: Backend Setup & Environment Initialization
* **Action Items**:
  1. Create directory structure `RF-TRACE-main/backend/`.
  2. Create Python virtual environment (`python -m venv venv`) and `requirements.txt` with dependencies (`fastapi`, `uvicorn`, `torch`, `scipy`, `numpy`, `soundfile`, `pydantic`).
  3. Set up `main.py` with FastAPI initialization and CORS middleware allowing origin `http://localhost:5173`.
  4. Verify server start via `uvicorn backend.main:app --reload`.

### Phase 2: Ingestion & Signal Preprocessing (`Phases 1-2 in PDF`)
* **Action Items**:
  1. Implement `backend/signal/loader.py` supporting `.wav` (PCM int16/float32) and raw interleaved `.iq` files (int8, int16, float32).
  2. Build DC offset cancellation (`x - mean(x)`) and peak normalization in `preprocessing.py`.
  3. Implement automatic signal format validation and duration calculation.

### Phase 3: DSP Analysis & Visualization Engine (`Phase 3 in PDF`)
* **Action Items**:
  1. Implement FFT power spectrum density (PSD) calculation in `backend/signal/spectrum.py` using `scipy.signal.welch`.
  2. Implement Spectrogram heatmap computation in `waterfall.py` using `scipy.signal.spectrogram`.
  3. Implement I/Q constellation sampler in `constellation.py` extracting normalized complex points $(I_k, Q_k)$.
  4. Calculate physical parameters: center frequency $f_c$, 3dB bandwidth, noise floor estimation, SNR estimation.

### Phase 4: PyTorch CNN Model Training & Synthetic Dataset Pipeline (`Phases 4-5 in PDF`)
* **Action Items**:
  1. Build synthetic IQ waveform generator `backend/ai/training/generate_dataset.py` generating labeled samples for:
     * **BPSK**
     * **QPSK**
     * **8PSK**
     * **FSK** (2-FSK)
     * **16QAM**
  2. Add realistic channel impairments: AWGN noise (SNR from -5dB to +20dB), frequency offset, phase offset, and timing jitter.
  3. Build PyTorch 1D-CNN architecture in `backend/ai/model.py`.
  4. Write `train.py` script and execute training to output saved weights `models/modulation_model.pt`.
  5. Implement `classifier.py` for model loading and real-time inference.

### Phase 5: Evidence Fusion & Signal Parameter Extraction (`Phase 6 in PDF`)
* **Action Items**:
  1. Implement multi-evidence fusion in `backend/fusion/evidence_fusion.py` combining CNN softmax confidence with constellation cluster variance and power spectrum metrics.
  2. Output parameter profile with strict data provenance badges (`measured`, `estimated`, `metadata`, `inferred`).

### Phase 6: Demodulation, Bit Recovery & FEC Decoding (`Phases 7-10 in PDF`)
* **Action Items**:
  1. Build digital demodulators in `backend/demodulation/` for BPSK, QPSK, 8PSK, FSK, and 16QAM.
  2. Implement Costas loop carrier synchronization and symbol slicing to yield raw bitstreams.
  3. Implement bitstream analysis in `backend/correlation/bit_analysis.py` (0/1 ratio, entropy, hex view).
  4. Build Viterbi Soft-Decoder algorithm in `backend/fec/viterbi.py` for $K=7, R=1/2$ convolutional decoding.
  5. Build block & convolutional de-interleavers in `backend/interleaving/`.

### Phase 7: API Route Wiring & React Integration (`Phase 12 in PDF`)
* **Action Items**:
  1. Implement route handlers in `backend/api/upload.py`, `analysis.py`, and `results.py`.
  2. Connect FastAPI asynchronous background tasks to process files in non-blocking worker threads.
  3. Update React frontend `src/services/api.ts` base URL to connect to `http://localhost:8000`.
  4. Verify end-to-end data flow: Upload IQ -> Run Analysis -> Render Spectrum/Waterfall/Constellation/Modulation/Bits -> Export JSON Report.

### Phase 8: Ground-Truth Verification & Hackathon Demo Package (`Section 9 in PDF`)
* **Action Items**:
  1. Create synthetic ground-truth test generator script (`backend/tests/generate_demo_signal.py`):
     `Known Bits -> Convolutional FEC -> Block Interleave -> QPSK Modulation -> Channel Noise -> IQ File`.
  2. Run the generated ground-truth IQ file through RF-TRACE.
  3. Verify that RF-TRACE accurately identifies:
     * Modulation = **QPSK** (Confidence > 90%)
     * Interleaving = **Block Interleaver**
     * FEC = **Convolutional / Viterbi**
     * Bit Recovery Accuracy = 100% matched against original input bits.

---

## 3. Recommended Immediate Next Step

**Do NOT modify or re-write the React frontend.** The frontend in `RF-TRACE-main/src` is already correct.

**The immediate next step is to initiate Phase 1 & Phase 2:**
1. Initialize `RF-TRACE-main/backend/`.
2. Create Python environment and install `fastapi`, `uvicorn`, `numpy`, `scipy`, `torch`.
3. Implement `loader.py` and `spectrum.py` to get live FFT data flowing into the frontend.
