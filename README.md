# RF-TRACE — Full-Stack RF Signal Intelligence & Analysis Platform

**RF-TRACE** is an end-to-end Signal Intelligence (SIGINT) and RF Analysis platform that combines a **FastAPI Python DSP & Deep Learning Backend** with a high-performance **React + TypeScript + Vite Frontend**.

It automatically processes raw complex I/Q recorded signals (`.iq`, `.cf32`, `.ci16`, `.wav`), computes spectral heatmaps, extracts constellation geometry, classifies modulations using a PyTorch 1D ResNet CNN + DSP Evidence Fusion engine, demodulates symbol streams, and performs FEC/Interleaving candidate analysis.

---

## Architecture Overview

```
                          RF Signal Ingestion (.iq / .wav)
                                         │
                                         ▼
                            Signal Loader & Preprocessing
                           (DC Offset Removal & Norm)
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
                 ▼                       ▼                       ▼
            FFT Spectrum        STFT Spectrogram       Constellation Scatter
            & 3dB Bandwidth        Waterfall Matrix         & Ideal Geometry
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         │
                                         ▼
                           PyTorch CNN Modulation Model
                            + DSP Evidence Fusion Engine
                           (BPSK, QPSK, 8PSK, FSK, 16QAM)
                                         │
                                         ▼
                        Demodulation & Strobe Recovery
                       (Gardner Timing & Discriminator)
                                         │
                                         ▼
                        Dynamic FEC & Interleaving Scoring
                           (Viterbi, Block, RS, LDPC)
                                         │
                                         ▼
                        10 Interactive Workstation Views
```

---

## Prerequisites

Before running RF-TRACE, ensure you have installed:

* **Python 3.10+** (with `pip`)
* **Node.js 18+** (with `npm`)

---

## Quick Start Guide — How to Run

### Step 1: Start the FastAPI Backend Server

Open a terminal in your cloned `RF-TRACE` repository root folder (do **NOT** `cd` into the `backend` folder directly, as the local `backend/signal/` directory will shadow Python's built-in `signal` library):

```bash
# 1. Navigate to your repository root directory
cd RF-TRACE

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Start the FastAPI development server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```


The backend server will start at: **`http://127.0.0.1:8000`**  
FastAPI Interactive API Documentation (Swagger): **`http://127.0.0.1:8000/docs`**

---

### Step 2: Start the React Frontend UI

Open a second terminal window in the project root folder:

```bash
# 1. Install frontend node modules
npm install

# 2. Start Vite development server
npm run dev
```

The frontend web application will launch at: **`http://localhost:5173`**

*(Note: The frontend is configured to automatically communicate with the backend at `http://127.0.0.1:8000` when `USE_MOCK = false` in `src/services/api.ts`.)*

---

## Deploying the Backend to Render

Push the backend changes to the GitHub branch connected to your Render service:

```bash
git add backend/fusion/evidence_fusion.py backend/main.py backend/requirements.txt
git commit -m "Fix PyTorch CNN evidence fusion logic and Render CPU deployment"
git push origin main
```

Configure the Render web service with these settings:

| Setting | Value |
| :--- | :--- |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | `3.10`, `3.11`, or `3.12` |

For a separately deployed frontend, set `VITE_API_URL` to the backend base URL, for example `https://<your-render-backend-name>.onrender.com`, then redeploy the frontend so the build picks up the variable. The web UI's **Settings** can also be used to enter the backend URL; a URL saved there takes precedence over `VITE_API_URL` in that browser.

After deployment, verify the backend at `https://<your-render-backend-name>.onrender.com/api/health`. It should return `{"status":"ok","service":"RF-TRACE-backend"}`. Run the backend tests locally with:

```bash
pytest backend/tests/
```

---

## AI Model Training & Evaluation Scripts

RF-TRACE includes a built-in PyTorch training pipeline combining Kaggle RadioML 2016.10A real-world frames with oversampled synthetic signal augmentations (CFO, phase noise, dynamic RRC roll-off).

### 1. Download Kaggle RadioML Dataset (Optional)
```bash
python -m backend.ai.training.download_dataset
```
*(Requires Kaggle API key configured in `~/.kaggle/kaggle.json`)*

### 2. Prepare Training Subset
```bash
python -m backend.ai.training.prepare_dataset
```

### 3. Train PyTorch CNN Model
```bash
python -m backend.ai.training.train
```
*(Trains the ResNet CNN for 20 epochs and saves trained weights to `backend/models/modulation_model.pt`)*

### 4. Evaluate Accuracy & Generate Charts
```bash
python -m backend.ai.training.evaluate
```
*(Outputs SNR Accuracy curves and Confusion Matrix plots in `backend/ai/training/results/`)*

---

## Running Automated Tests

Run the complete backend unit and integration test suite using `pytest`:

```bash
pytest backend/tests/
```

All 13 test suites verify:
* API Endpoint Health & File Uploads ([`test_api_endpoints.py`](file:///c:/Users/waaji/Desktop/RF-TRACE/RF-TRACE-main/backend/tests/test_api_endpoints.py))
* FSK Quadrature Discriminator & Frequency Phase Derivatives ([`test_fsk_processing.py`](file:///c:/Users/waaji/Desktop/RF-TRACE/RF-TRACE-main/backend/tests/test_fsk_processing.py))
* Dynamic IQ & WAV format detection ([`test_iq_files_folder.py`](file:///c:/Users/waaji/Desktop/RF-TRACE/RF-TRACE-main/backend/tests/test_iq_files_folder.py))
* Signal Preprocessing & DC offset removal ([`test_signal_processing.py`](file:///c:/Users/waaji/Desktop/RF-TRACE/RF-TRACE-main/backend/tests/test_signal_processing.py))
* Edge case error handling ([`test_edge_cases.py`](file:///c:/Users/waaji/Desktop/RF-TRACE/RF-TRACE-main/backend/tests/test_edge_cases.py))

---

## 10 Technical Workstation Views

| View Name | Description | Key Capabilities |
| :--- | :--- | :--- |
| **Dashboard** | System Status & Overview | Live backend connection health, quick metrics, recent analyses. |
| **Ingestion** | Signal Upload & Import | Drag & drop `.iq` / `.wav` files, format detection (`float32`/`int16`). |
| **Spectrum** | Power Spectral Density (PSD) | Welch FFT spectrum, 3dB bandwidth estimation, carrier frequency markers. |
| **Waterfall** | STFT Spectrogram Matrix | 2D time-frequency intensity heatmap with 5th-99.5th percentile dynamic contrast. |
| **Constellation** | I/Q Scatter Diagram | Real-time I/Q scatter plot overlaid with ideal modulation reference points. |
| **Modulation** | AI Classifier & Fusion | Softmax class probabilities, CNN residual embeddings, DSP physics evidence. |
| **Parameters** | Signal Parameter Profile | FS, FC, BW, SNR, Symbol Rate with strict provenance badges (`Measured`, `Metadata`). |
| **Demodulation** | Symbol Slicing & Strobe | Gardner timing recovery & Quadrature Frequency Discriminator. |
| **FEC / Interleaving** | Error Correction Candidates | Dynamic Viterbi, Block Interleaver, Reed-Solomon $GF(2^8)$, and LDPC scoring. |
| **Signal Profile** | Complete SIGINT Report | Consolidated export report aggregating all 12 pipeline stages. |

---

## Project Directory Structure

```
RF-TRACE-main/
├── backend/                  # FastAPI Python DSP & AI Backend
│   ├── ai/                   # PyTorch ResNet model & inference engine
│   │   ├── training/         # Dataset generation, training & evaluation scripts
│   ├── api/                  # FastAPI routers & endpoint handlers
│   ├── demodulation/         # Symbol timing recovery & slicing
│   ├── fec/                  # Viterbi, Interleaver, RS & LDPC candidate analyzers
│   ├── fusion/               # Evidence Fusion engine (AI + DSP physics rules)
│   ├── models/               # Saved PyTorch model weights (.pt)
│   ├── reports/              # Consolidated Signal Profile report generator
│   ├── signal/               # Signal loading, preprocessing, FFT PSD, Waterfall
│   ├── tests/                # Pytest integration test suite
│   └── main.py               # FastAPI application entry point
├── src/                      # React + TypeScript + Vite Frontend
│   ├── components/           # UI kit and SVG/Canvas chart renderers
│   ├── pages/                # 10 Workstation view page components
│   ├── services/             # API client & mock fallback services
│   └── types/                # TypeScript interface data contracts
└── README.md                 # System setup and execution guide
```
