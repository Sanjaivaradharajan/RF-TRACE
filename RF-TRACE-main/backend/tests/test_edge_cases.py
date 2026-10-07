import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.main import app

client = TestClient(app)


def test_empty_filename_upload():
    # Empty filename check
    resp = client.post("/api/upload", files={"file": ("", b"some data", "text/plain")})
    assert resp.status_code in [400, 422]


def test_nonexistent_analysis_status():
    # Polling unknown analysis ID returns clean complete fallback status
    resp = client.get("/api/analysis/unknown-job-id/status")
    assert resp.status_code == 200
    assert resp.json()["state"] == "complete"


def test_nonexistent_analysis_results():
    # Fetching unknown results returns clean fallback report
    resp = client.get("/api/analysis/unknown-job-id/results")
    assert resp.status_code == 200
    res = resp.json()
    assert "spectrum" in res
    assert "waterfall" in res
    assert "constellation" in res
