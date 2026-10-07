# RF-TRACE: Backend Architecture Specification

**Document Status:** Complete  
**Date:** September 23, 2026  
**Target Core:** Python 3.10+ / FastAPI / PyTorch / SciPy / NumPy  
**Reference Document:** `Architecture planning.pdf` (Smart India Hackathon 2026 - Problem Statement 26147)

---

## 1. System Architecture Overview

RF-TRACE backend is an AI-assisted signal intelligence processing server designed to ingest raw `.IQ` and `.wav` radio frequency recordings, perform digital signal processing (DSP), run convolutional neural network (CNN) modulation classification, fuse multi-modal evidence, recover bitstreams, evaluate Forward Error Correction (FEC) & interleaving, and output structured signal profiles.

```
                  ┌──────────────────────────────────────────────┐
                  │              FastAPI Server                  │
                  │               (backend/)                     │
                  └──────────────────────┬───────────────────────┘
                                         │
 ┌───────────────────────────────────────┼───────────────────────────────────────┐
 │                                       ▼                                       │
 │  ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐  │
 │  │ 1. File Ingestion │ ───► │ 2. Preprocessing  │ ───► │  3. DSP Engine    │  │
 │  │ (Loader & Parser) │      │ (DC, Norm, Filter)│      │ (FFT, STFT, IQ)   │  │
 │  └───────────────────┘      └───────────────────┘      └─────────┬─────────┘  │
 │                                                                    │          │
 │  ┌───────────────────┐      ┌───────────────────┐                  │          │
 │  │ 6. Parameter Extr.│ ◄─── │ 5. Evidence Fusion│ ◄────────────────┼──────────┤
 │  └─────────┬─────────┘      └─────────▲─────────┘                  │          │
 │            │                          │                            │          │
 │            │                ┌─────────┴─────────┐                  │          │
 │            │                │ 4. PyTorch CNN    │ ◄────────────────┘          │
 │            │                │ (Mod Classifier)  │                             │
 │            │                └───────────────────┘                             │
 │            ▼                                                                  │
 │  ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐  │
 │  │ 7. Demodulation   │ ───► │ 8. Bit Recovery   │ ───► │ 9/10. Deinterleave│  │
 │  │ (BPSK/QPSK/FSK...)│      │ (Bits, Hex, ASCII)│      │    & FEC Viterbi  │  │
 │  └───────────────────┘      └───────────────────┘      └─────────┬─────────┘  │
 │                                                                    │          │
 │                                                                    ▼          │
 │                             ┌───────────────────┐      ┌───────────────────┐  │
 │                             │ 12. Profile Report│ ◄─── │ 11. Correlation   │  │
 │                             │  (Aggregator/JSON)│      │ (Structure/Sync)  │  │
 │                             └───────────────────┘      └───────────────────┘  │
 └───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure & File Mapping

```
RF-TRACE-main/
├── backend/
│   ├── main.py                     # FastAPI entry point & CORS middleware
│   ├── config.py                   # System configuration & environment variables
│   ├── requirements.txt            # Python dependencies
│   ├── api/                        # API route handlers
│   │   ├── __init__.py
│   │   ├── upload.py               # POST /api/upload
│   │   ├── analysis.py             # POST /api/analysis
│   │   └── results.py              # GET /api/analysis/{id}/status & /results
│   ├── signal/                     # DSP & Signal Processing core
│   │   ├── __init__.py
│   │   ├── loader.py               # IQ & WAV reader (.wav, .iq 8/16/32-bit int/float)
│   │   ├── preprocessing.py        # DC offset removal, normalization, bandpass filtering
│   │   ├── spectrum.py             # FFT power spectral density (PSD) & center freq detection
│   │   ├── waterfall.py            # Short-Time Fourier Transform (STFT) spectrogram generator
│   │   ├── constellation.py        # I/Q sample extraction & ideal point reference generation
│   │   └── parameters.py          # Bandwidth, SNR, noise floor, symbol rate estimation
│   ├── ai/                         # PyTorch Neural Network & Inference
│   │   ├── __init__.py
│   │   ├── model.py                # 1D/2D CNN Architecture definition (PyTorch)
│   │   ├── classifier.py           # Model loading, softmax inference, top-k scoring
│   │   ├── inference.py            # Preprocessing IQ blocks into CNN input tensors
│   │   └── training/               # Offline synthetic dataset & training suite
│   │       ├── generate_dataset.py # Synthetic IQ generator (BPSK, QPSK, 8PSK, FSK, 16QAM)
│   │       ├── dataset.py          # PyTorch Dataset & DataLoader implementation
│   │       ├── train.py            # Model training loop & checkpoint saver
│   │       └── evaluate.py         # Test set evaluation & confusion matrix exporter
│   ├── fusion/                     # Evidence Fusion Engine
│   │   ├── __init__.py
│   │   └── evidence_fusion.py     # Combines CNN probability + constellation variance + PSD features
│   ├── demodulation/               # Digital Demodulators & Symbol Recovery
│   │   ├── __init__.py
│   │   ├── bpsk.py                 # BPSK Costas loop / carrier recovery & slicer
│   │   ├── qpsk.py                 # QPSK symbol slicer & phase recovery
│   │   ├── psk.py                  # 8PSK slicer
│   │   ├── fsk.py                  # Dual-filter / discriminator FSK demodulator
│   │   └── qam.py                  # 16QAM rectangular slicer & AGC
│   ├── interleaving/               # De-interleaving Analyzers
│   │   ├── __init__.py
│   │   ├── block.py                # Block de-interleaver (NxM matrix transpose)
│   │   ├── convolutional.py        # Shift register de-interleaver
│   │   ├── diagonal.py             # Diagonal matrix de-interleaver
│   │   └── pseudo_random.py        # LFSR PRNG seed candidate matching
│   ├── fec/                        # Forward Error Correction Decoders
│   │   ├── __init__.py
│   │   ├── convolutional.py        # Hard/Soft decision convolutional encoder model
│   │   ├── viterbi.py              # Soft-input Viterbi decoder algorithm
│   │   ├── reed_solomon.py         # RS(255,223) candidate verification wrapper
│   │   └── ldpc.py                 # LDPC belief propagation stub
│   ├── correlation/                # Bitstream Pattern Analysis
│   │   ├── __init__.py
│   │   └── bit_analysis.py         # Autocorrelation, 0/1 entropy, preamble candidate search
│   ├── reports/                    # Final Report Generator
│   │   ├── __init__.py
│   │   └── signal_profile.py       # Formats 12-phase pipeline output to frontend JSON schema
│   └── models/
│       └── modulation_model.pt     # Trained PyTorch CNN model weights file
```

---

## 3. Core Module Specifications

### 3.1. File Ingestion & Reader (`backend/signal/loader.py`)
* **Inputs**: Raw byte stream or file path (`.iq`, `.wav`, `.cfile`).
* **Formats Supported**:
  * `.wav`: Uncompressed WAV (PCM int16, float32) parsed via `scipy.io.wavfile` or `wave`.
  * `.iq`: Interleaved I/Q samples (int8, int16, float32, float64).
* **Output**: Standardized `SignalBuffer` dataclass:
  ```python
  class SignalBuffer:
      iq_samples: np.ndarray  # Complex128 array [I + j*Q]
      sample_rate: float      # Sampling frequency in Hz
      center_freq: float      # Center frequency in Hz (if known)
      duration_s: float       # Duration in seconds
      file_format: str        # 'IQ' or 'WAV'
      sample_format: str      # 'float32', 'int16', etc.
  ```

### 3.2. Signal Preprocessing (`backend/signal/preprocessing.py`)
* **DC Offset Removal**: `iq = iq - np.mean(iq)`
* **Normalization**: Peak power normalization (`iq = iq / np.max(np.abs(iq))`).
* **Filtering**: SciPy Butterworth bandpass filter to eliminate out-of-band noise.

### 3.3. DSP Analysis Engine (`backend/signal/spectrum.py`, `waterfall.py`, `constellation.py`)
* **Spectrum (FFT/PSD)**: Computes Welch Power Spectral Density using `scipy.signal.welch`. Outputs `frequencies_mhz` and `power_db`.
* **Waterfall (STFT)**: Computes Spectrogram using `scipy.signal.spectrogram`. Downsamples grid to 64x64 or 128x128 matrix for smooth browser rendering.
* **Constellation**: Samples 1,000 to 5,000 normalized complex points `(I, Q)` for scatter plotting.

### 3.4. PyTorch CNN Classifier (`backend/ai/model.py`, `classifier.py`)
* **Architecture**: 1D ResNet / ConvNet taking shape `(2, N_SAMPLES)` where channel 0 is In-Phase (I) and channel 1 is Quadrature (Q).
* **Target Modulation Classes**:
  1. BPSK
  2. QPSK
  3. 8PSK
  4. FSK (2-FSK / 4-FSK)
  5. 16QAM
* **Output**: Softmax probability distribution dictionary:
  `{"BPSK": 0.02, "QPSK": 0.94, "8PSK": 0.03, "FSK": 0.00, "16QAM": 0.01}`

### 3.5. Evidence Fusion Engine (`backend/fusion/evidence_fusion.py`)
* **Core Concept**: Prevents reliance on CNN alone by combining:
  1. CNN probability vector ($P_{\text{CNN}}$).
  2. Constellation cluster variance ($E_{\text{const}}$).
  3. Power spectrum kurtosis / peakiness ($E_{\text{spec}}$).
  4. Phase histogram symmetry ($E_{\text{phase}}$).
* **Formula**: $C_{\text{final}} = w_1 \cdot P_{\text{CNN}} + w_2 \cdot E_{\text{const}} + w_3 \cdot E_{\text{spec}}$

### 3.6. Demodulation & Bitstream Recovery (`backend/demodulation/`, `backend/fec/`)
* **Carrier & Symbol Sync**: Gardner timing error detector (TED) + Costas loop phase lock.
* **Slicing**: Maps complex symbols to hard bit decisions (`0` and `1`).
* **Viterbi Decoding**: Soft decision Viterbi algorithm for $K=7, R=1/2$ convolutional code decoding.

---

## 4. API Endpoints & Response Contracts

### Endpoint 1: Upload File
* **Route**: `POST /api/upload`
* **Content-Type**: `multipart/form-data`
* **Response**:
```json
{
  "fileId": "uuid-1234-5678",
  "filename": "capture_433mhz.iq",
  "sizeBytes": 1048576,
  "format": "IQ",
  "sampleFormat": "int16",
  "durationS": 2.5
}
```

### Endpoint 2: Start Analysis Pipeline
* **Route**: `POST /api/analysis`
* **Payload**:
```json
{
  "fileId": "uuid-1234-5678",
  "sampleRate": 2000000,
  "centerFreq": 433920000
}
```
* **Response**:
```json
{
  "analysisId": "job-9876-5432",
  "status": "queued"
}
```

### Endpoint 3: Pipeline Status
* **Route**: `GET /api/analysis/{id}/status`
* **Response**:
```json
{
  "analysisId": "job-9876-5432",
  "state": "running",
  "stage": 4,
  "stageName": "AI / CNN Modulation Recognition",
  "progressPct": 35.0,
  "error": null
}
```

### Endpoint 4: Full Analysis Results
* **Route**: `GET /api/analysis/{id}/results`
* **Response**: Matches the frontend `AnalysisResult` TypeScript type interface defined in `src/types/analysis.ts`.

---

## 5. Technology Stack & Dependencies

| Tool / Library | Role |
| :--- | :--- |
| **Python 3.10+** | Base Runtime Environment |
| **FastAPI + Uvicorn** | High-performance Async Web Framework |
| **PyTorch (`torch`)** | CNN Neural Network Training & Inference |
| **SciPy & NumPy** | Fast Fourier Transform, Filters, Matrix Operations |
| **Librosa / SoundFile** | Audio / WAV file format decoding |
| **Pydantic v2** | API Schema validation & Serialization |
