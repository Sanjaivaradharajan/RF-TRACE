import sys
from pathlib import Path
import numpy as np
import wave
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.main import app

client = TestClient(app)

def test_different_files(tmp_path):
    # File 1: 440 Hz Sine wave WAV (Mono)
    file1 = tmp_path / "sine_440hz.wav"
    t = np.linspace(0, 0.1, 4410)
    samples1 = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    with wave.open(str(file1), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(samples1.tobytes())

    # File 2: Dual tone 1200/2200 Hz WAV (Stereo I/Q)
    file2 = tmp_path / "fsk_1200hz.wav"
    left = (np.sin(2 * np.pi * 1200 * t) * 32767).astype(np.int16)
    right = (np.cos(2 * np.pi * 2200 * t) * 32767).astype(np.int16)
    interleaved = np.empty((4410 * 2,), dtype=np.int16)
    interleaved[0::2] = left
    interleaved[1::2] = right
    with wave.open(str(file2), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(interleaved.tobytes())

    # Upload File 1
    with open(file1, "rb") as f:
        resp1 = client.post("/api/upload", files={"file": ("sine_440hz.wav", f, "audio/wav")})
    assert resp1.status_code == 200
    file_id1 = resp1.json()["fileId"]

    # Upload File 2
    with open(file2, "rb") as f:
        resp2 = client.post("/api/upload", files={"file": ("fsk_1200hz.wav", f, "audio/wav")})
    assert resp2.status_code == 200
    file_id2 = resp2.json()["fileId"]

    assert file_id1 != file_id2

    # Start analysis 1
    a1 = client.post("/api/analysis", json={"fileId": file_id1}).json()["analysisId"]
    # Start analysis 2
    a2 = client.post("/api/analysis", json={"fileId": file_id2}).json()["analysisId"]

    res1 = client.get(f"/api/analysis/{a1}/results").json()
    res2 = client.get(f"/api/analysis/{a2}/results").json()

    assert res1["file"]["name"] == "sine_440hz.wav"
    assert res2["file"]["name"] == "fsk_1200hz.wav"
    assert res1["spectrum"]["powerDb"] != res2["spectrum"]["powerDb"]
    assert res1["bits"] != res2["bits"]
    print("Different files produced unique results successfully!")
