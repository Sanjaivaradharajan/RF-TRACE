import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from backend.config import UPLOAD_DIR
from backend.signal.loader import load_signal

router = APIRouter(prefix="/api", tags=["Upload"])

# In-memory store of loaded buffers
uploaded_buffers = {}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads an IQ or WAV file and returns metadata."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    file_id = f"file-{uuid.uuid4().hex[:8]}"
    save_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        sig_buf = load_signal(save_path)
        sig_buf.filename = file.filename
        uploaded_buffers[file_id] = sig_buf

        return {
            "fileId": file_id,
            "filename": sig_buf.filename,
            "sizeBytes": save_path.stat().st_size,
            "format": sig_buf.file_format,
            "sampleFormat": sig_buf.sample_format,
            "durationS": sig_buf.duration_s,
        }
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=400, detail=f"Failed to parse signal file: {str(e)}"
        )
