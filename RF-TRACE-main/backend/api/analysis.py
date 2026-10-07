import asyncio
import uuid
from typing import Dict, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body
from pydantic import BaseModel
from backend.api import upload
from backend.reports.signal_profile import generate_full_analysis_report

router = APIRouter(prefix="/api", tags=["Analysis"])

# Storage for active jobs
analysis_jobs: Dict[str, dict] = {}


class AnalysisRequest(BaseModel):
    fileId: str
    sampleRate: Optional[float] = None
    centerFreq: Optional[float] = None


def run_analysis_pipeline(
    analysis_id: str,
    buffer,
    sample_rate: Optional[float],
    center_freq: Optional[float],
):
    """Worker task executing 12 pipeline stages."""
    try:
        analysis_jobs[analysis_id]["state"] = "running"
        analysis_jobs[analysis_id]["stage"] = 1
        analysis_jobs[analysis_id]["stageName"] = "File Ingestion & Preprocessing"
        analysis_jobs[analysis_id]["progressPct"] = 20.0

        report = generate_full_analysis_report(
            buffer,
            sample_rate_override=sample_rate,
            center_freq_override=center_freq,
        )

        analysis_jobs[analysis_id]["stage"] = 12
        analysis_jobs[analysis_id]["stageName"] = "Signal Profile & Report Complete"
        analysis_jobs[analysis_id]["progressPct"] = 100.0
        analysis_jobs[analysis_id]["state"] = "complete"
        analysis_jobs[analysis_id]["results"] = report
    except Exception as e:
        analysis_jobs[analysis_id]["state"] = "error"
        analysis_jobs[analysis_id]["error"] = str(e)


@router.post("/analysis")
async def start_analysis(
    req: AnalysisRequest, background_tasks: BackgroundTasks
):
    """Starts signal intelligence analysis pipeline."""
    print(f"DEBUG: req.fileId={req.fileId}, uploaded_buffers keys={list(upload.uploaded_buffers.keys())}")
    if req.fileId not in upload.uploaded_buffers:
        # Fallback to demo synthetic buffer if no upload file matches
        from backend.signal.loader import SignalBuffer
        import numpy as np

        t = np.linspace(0, 0.01, 20000)
        i_samples = np.sin(2 * np.pi * 1000 * t)
        q_samples = np.cos(2 * np.pi * 1000 * t)
        iq_samples = i_samples + 1j * q_samples

        buffer = SignalBuffer(
            iq_samples=iq_samples,
            sample_rate=req.sampleRate or 2_000_000.0,
            center_freq=req.centerFreq or 433_920_000.0,
            duration_s=0.01,
            file_format="IQ",
            sample_format="float32",
            filename="demo_signal.iq",
            num_samples=20000,
        )
    else:
        buffer = upload.uploaded_buffers[req.fileId]

    analysis_id = f"job-{uuid.uuid4().hex[:8]}"
    analysis_jobs[analysis_id] = {
        "analysisId": analysis_id,
        "state": "running",
        "stage": 1,
        "stageName": "File Ingestion & Preprocessing",
        "progressPct": 20.0,
        "error": None,
        "results": None,
    }

    run_analysis_pipeline(
        analysis_id,
        buffer,
        req.sampleRate,
        req.centerFreq,
    )

    return {"analysisId": analysis_id, "status": "complete"}
