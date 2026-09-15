"""
FastAPI Main — Document Classification API endpoints.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Document Classifier",
    description="AI-powered document classification pipeline",
    version="1.0.0",
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Results Storage (in-memory for POC) ──────────────────────────────────

classification_history: list[dict] = []

# ─── Sample Documents Directory ───────────────────────────────────────────

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ─── Endpoints ────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "AI Document Classifier",
        "status": "running",
        "model": os.getenv("MIMO_MODEL", "mimo-v2.5"),
    }


@app.post("/api/classify")
async def classify_document(file: UploadFile = File(...)):
    """
    Classify an uploaded document.
    
    Accepts: PDF, PNG, JPG, JPEG, TIFF, BMP
    Returns: Classification result with type, confidence, routing decision
    """
    from app.pipeline import run_pipeline
    
    # Validate file type
    allowed_types = {
        "application/pdf": "pdf",
        "image/png": "image",
        "image/jpeg": "image",
        "image/jpg": "image",
        "image/tiff": "image",
        "image/bmp": "image",
    }
    
    file_type = allowed_types.get(file.content_type)
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(allowed_types.keys())}",
        )
    
    # Read file
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    # Run pipeline
    try:
        result = await run_pipeline(file_bytes, file.filename, file_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    
    # Store result
    result["timestamp"] = datetime.now().isoformat()
    classification_history.insert(0, result)
    
    # Keep only last 100 results
    if len(classification_history) > 100:
        classification_history.pop()
    
    return result


@app.get("/api/history")
async def get_history():
    """Get classification history."""
    return {
        "total": len(classification_history),
        "results": classification_history,
    }


@app.get("/api/stats")
async def get_stats():
    """Get classification statistics."""
    if not classification_history:
        return {
            "total_classifications": 0,
            "type_distribution": {},
            "route_distribution": {},
            "avg_confidence": 0,
            "avg_latency_ms": 0,
        }
    
    type_dist = {}
    route_dist = {}
    total_confidence = 0
    total_latency = 0
    
    for r in classification_history:
        doc_type = r.get("classification", {}).get("type", "unknown")
        route = r.get("routing", {}).get("decision", "unknown")
        
        type_dist[doc_type] = type_dist.get(doc_type, 0) + 1
        route_dist[route] = route_dist.get(route, 0) + 1
        total_confidence += r.get("classification", {}).get("confidence", 0)
        total_latency += r.get("total_latency_ms", 0)
    
    n = len(classification_history)
    
    return {
        "total_classifications": n,
        "type_distribution": type_dist,
        "route_distribution": route_dist,
        "avg_confidence": round(total_confidence / n, 1),
        "avg_latency_ms": round(total_latency / n),
    }


@app.get("/api/samples")
async def list_samples():
    """List available sample documents."""
    if not SAMPLE_DIR.exists():
        return {"samples": [], "message": "Run generate_samples.py first"}
    
    samples = []
    for f in sorted(SAMPLE_DIR.iterdir()):
        if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".pdf", ".tiff", ".bmp"]:
            samples.append({
                "name": f.name,
                "path": str(f),
                "size_kb": round(f.stat().st_size / 1024, 1),
            })
    
    return {"samples": samples}


@app.post("/api/classify-sample/{filename}")
async def classify_sample(filename: str):
    """Classify a pre-loaded sample document."""
    file_path = SAMPLE_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample not found: {filename}")
    
    from app.pipeline import run_pipeline
    
    file_bytes = file_path.read_bytes()
    
    # Determine file type
    suffix = file_path.suffix.lower()
    file_type = "pdf" if suffix == ".pdf" else "image"
    
    try:
        result = await run_pipeline(file_bytes, filename, file_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    
    result["timestamp"] = datetime.now().isoformat()
    classification_history.insert(0, result)
    
    return result
