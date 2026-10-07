import sys
import time
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.main import app

client = TestClient(app)
IQ_FOLDER = Path(__file__).resolve().parent.parent.parent / "IQ Files"


def test_fsk_signal_processing():
    # Generate 2-FSK synthetic file with clear modulation index
    fsk_file = IQ_FOLDER / "demo_fsk.iq"
    seq_len = 8000
    sps = 8
    bits = np.random.randint(0, 2, seq_len // sps)
    freqs = (2 * bits - 1) * (0.25 / sps)
    phase = np.cumsum(np.repeat(freqs, sps))
    fsk_iq = np.exp(1j * 2 * np.pi * phase).astype(np.complex64)

    # Save as float32 IQ file
    iq_interleaved = np.empty((seq_len * 2,), dtype=np.float32)
    iq_interleaved[0::2] = np.real(fsk_iq)
    iq_interleaved[1::2] = np.imag(fsk_iq)
    with open(fsk_file, "wb") as f:
        f.write(iq_interleaved.tobytes())

    # Upload & Analyze FSK file
    with open(fsk_file, "rb") as f:
        up_resp = client.post(
            "/api/upload",
            files={"file": ("demo_fsk.iq", f, "application/octet-stream")},
        )
    assert up_resp.status_code == 200
    file_id = up_resp.json()["fileId"]

    start_resp = client.post("/api/analysis", json={"fileId": file_id})
    assert start_resp.status_code == 200
    analysis_id = start_resp.json()["analysisId"]

    # Fetch results
    res_resp = client.get(f"/api/analysis/{analysis_id}/results")
    assert res_resp.status_code == 200
    res = res_resp.json()

    # Check 1: Modulation == FSK
    assert res["modulation"]["detected"] == "FSK"
    assert res["modulation"]["probs"]["FSK"] > 0.90

    # Check 2: Spectrum
    assert len(res["spectrum"]["freqMHz"]) > 0
    assert len(res["spectrum"]["powerDb"]) > 0

    # Check 3: Waterfall
    assert len(res["waterfall"]["data"]) > 0

    # Check 4: Constellation
    assert len(res["constellation"]["rx"]) > 0
    assert len(res["constellation"]["ideal"]) > 0

    # Check 5: Bitstream & Demodulation
    assert len(res["bits"]) > 0
    assert res["demod"]["status"] == "Complete"

    # Check 6: Signal Parameters
    assert "fs" in res["params"]
    assert "fc" in res["params"]
    assert "modulation" in res["params"]
    assert res["params"]["modulation"]["value"] == "FSK"

    print("FSK complete pipeline verification 100% SUCCESSFUL!")
