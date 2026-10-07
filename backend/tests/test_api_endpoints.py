import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_start_analysis_and_results():
    payload = {"fileId": "demo-file", "sampleRate": 2000000.0}
    response = client.post("/api/analysis", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "analysisId" in res

    analysis_id = res["analysisId"]

    # Check status
    status_resp = client.get(f"/api/analysis/{analysis_id}/status")
    assert status_resp.status_code == 200

    # Check results
    results_resp = client.get(f"/api/analysis/{analysis_id}/results")
    assert results_resp.status_code == 200
    results_data = results_resp.json()
    assert "spectrum" in results_data
    assert "waterfall" in results_data
    assert "constellation" in results_data
    assert "modulation" in results_data
