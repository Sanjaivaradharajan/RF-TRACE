import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config import ALLOWED_ORIGINS, DEFAULT_SAMPLE_RATE, HOST, PORT
from backend.main import app


def test_config():
    assert HOST == "0.0.0.0"
    assert PORT == 8000
    assert DEFAULT_SAMPLE_RATE == 2_000_000
    assert "http://localhost:5173" in ALLOWED_ORIGINS


def test_fastapi_app_setup():
    assert app.title == "RF-TRACE Signal Intelligence Engine"
    assert app.version == "1.0.0"
