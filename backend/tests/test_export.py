import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app
from backend.reports.exporter import generate_latex_report
from backend.reports.signal_profile import generate_full_analysis_report
from backend.signal.loader import SignalBuffer
import numpy as np

client = TestClient(app)

def test_latex_generator():
    t = np.linspace(0, 0.01, 2000)
    buf = SignalBuffer(
        iq_samples=np.sin(2 * np.pi * 1000 * t) + 1j * np.cos(2 * np.pi * 1000 * t),
        sample_rate=2000000.0,
        center_freq=433920000.0,
        duration_s=0.01,
        file_format="IQ",
        sample_format="float32",
        filename="test_signal.iq",
        num_samples=2000,
    )
    report_data = generate_full_analysis_report(buf)
    tex = generate_latex_report(report_data)
    assert "\\documentclass" in tex
    assert "RF-TRACE SIGNAL PROFILE REPORT" in tex
    assert "test\\_signal.iq" in tex or "test_signal.iq" in tex

def test_latex_endpoint():
    res = client.get("/api/analysis/test-job-123/export/latex")
    assert res.status_code == 200
    assert "text/x-tex" in res.headers["content-type"]
    assert "\\begin{document}" in res.text
