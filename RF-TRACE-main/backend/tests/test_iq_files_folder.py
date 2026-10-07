import sys
from pathlib import Path
import math
import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.main import app

client = TestClient(app)

IQ_FOLDER = Path(__file__).resolve().parent.parent.parent / "IQ Files"


def test_iq_files_folder_processing():
    iq_files = list(IQ_FOLDER.glob("*.iq")) + list(IQ_FOLDER.glob("*.wav"))
    assert len(iq_files) > 0, f"No IQ/WAV files found in {IQ_FOLDER}"

    for iq_path in iq_files:
        print(f"\n--- Testing sample file: {iq_path.name} ---")

        # 1. Test upload API
        with open(iq_path, "rb") as f:
            up_resp = client.post(
                "/api/upload", files={"file": (iq_path.name, f, "application/octet-stream")}
            )
        assert up_resp.status_code == 200, f"Upload failed for {iq_path.name}: {up_resp.text}"
        upload_data = up_resp.json()
        file_id = upload_data["fileId"]

        # 2. Test analysis trigger API
        start_resp = client.post("/api/analysis", json={"fileId": file_id})
        assert start_resp.status_code == 200, f"Analysis trigger failed: {start_resp.text}"
        analysis_id = start_resp.json()["analysisId"]

        # 3. Fetch status
        status_resp = client.get(f"/api/analysis/{analysis_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["state"] == "complete"

        # 4. Fetch full result
        results_resp = client.get(f"/api/analysis/{analysis_id}/results")
        assert results_resp.status_code == 200
        res = results_resp.json()

        # Validate exact keys expected by React frontend
        assert "file" in res
        assert "params" in res
        assert "spectrum" in res
        assert "waterfall" in res
        assert "constellation" in res
        assert "modulation" in res
        assert "bits" in res
        assert "fec" in res
        assert "demod" in res

        # Spectrum assertions
        spec = res["spectrum"]
        assert len(spec["freqMHz"]) > 0
        assert len(spec["powerDb"]) > 0
        assert len(spec["freqMHz"]) == len(spec["powerDb"])
        assert not any(math.isnan(x) for x in spec["freqMHz"])
        assert not any(math.isnan(x) for x in spec["powerDb"])

        # Waterfall assertions
        wf = res["waterfall"]
        assert len(wf["data"]) > 0
        assert len(wf["data"][0]) > 0
        assert wf["fMinMHz"] < wf["fMaxMHz"]

        # Constellation assertions
        const = res["constellation"]
        assert len(const["rx"]) > 0
        assert len(const["ideal"]) > 0
        assert "i" in const["rx"][0] and "q" in const["rx"][0]

        # Modulation assertions
        mod = res["modulation"]
        assert "detected" in mod
        assert "confidence" in mod
        assert "probs" in mod

        # Bitstream assertions
        bits = res["bits"]
        assert len(bits) > 0
        assert all(c in "01" for c in bits)

        print(f"Successfully verified {iq_path.name}: Detected={mod['detected']} ({mod['confidence']*100:.1f}%), Bits={len(bits)}")
