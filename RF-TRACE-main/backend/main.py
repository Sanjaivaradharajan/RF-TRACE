import sys
from pathlib import Path

# Ensure project root is in sys.path for robust module loading on Render/cloud deployments
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.config import ALLOWED_ORIGINS, HOST, PORT

app = FastAPI(
    title="RF-TRACE Signal Intelligence Engine",
    description="Backend API for AI-assisted signal recognition, DSP parameter extraction, and bitstream recovery.",
    version="1.0.0",
)

# CORS middleware for React frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
from backend.api import upload, analysis, results
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(results.router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "RF-TRACE Signal Intelligence Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }



@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "RF-TRACE-backend"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
