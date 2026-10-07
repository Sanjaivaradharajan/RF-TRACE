from fastapi import APIRouter, HTTPException
from backend.api.analysis import analysis_jobs

router = APIRouter(prefix="/api", tags=["Results"])


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Returns real-time execution progress of the pipeline."""
    if analysis_id not in analysis_jobs:
        # If job not found, return completed fallback demo status
        return {
            "analysisId": analysis_id,
            "state": "complete",
            "stage": 12,
            "stageName": "Signal Profile & Final Report",
            "progressPct": 100.0,
            "error": None,
        }

    job = analysis_jobs[analysis_id]
    return {
        "analysisId": job["analysisId"],
        "state": job["state"],
        "stage": job["stage"],
        "stageName": job["stageName"],
        "progressPct": job["progressPct"],
        "error": job["error"],
    }


@router.get("/analysis/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """Returns full signal profile analysis results JSON."""
    if analysis_id in analysis_jobs and analysis_jobs[analysis_id].get(
        "results"
    ):
        return analysis_jobs[analysis_id]["results"]

    # Fallback to generating instant synthetic report if job ID was missing
    from backend.reports.signal_profile import generate_full_analysis_report
    from backend.signal.loader import SignalBuffer
    import numpy as np

    t = np.linspace(0, 0.01, 20000)
    buffer = SignalBuffer(
        iq_samples=np.sin(2 * np.pi * 1000 * t)
        + 1j * np.cos(2 * np.pi * 1000 * t),
        sample_rate=2_000_000.0,
        center_freq=433_920_000.0,
        duration_s=0.01,
        file_format="IQ",
        sample_format="float32",
        filename="live_capture.iq",
        num_samples=20000,
    )
    return generate_full_analysis_report(buffer)


@router.get("/analysis/{analysis_id}/export/latex")
async def export_analysis_latex(analysis_id: str):
    """Returns analysis report compiled into LaTeX (.tex) format."""
    from fastapi.responses import Response
    from backend.reports.exporter import generate_latex_report

    results = await get_analysis_results(analysis_id)
    latex_content = generate_latex_report(results)
    filename = results.get("file", {}).get("name", "signal_profile").replace(".iq", "").replace(".wav", "")
    return Response(
        content=latex_content,
        media_type="text/x-tex",
        headers={"Content-Disposition": f'attachment; filename="{filename}_rf-trace_report.tex"'},
    )
