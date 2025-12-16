"""
FastAPI server for PoC Frontend
Connects to PoC Server backend
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from layer2.poc_server import PoCServer
from layer2.poc_archive import ContributionStatus, MetalType

app = FastAPI(title="Syntheverse PoC API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PoC Server
try:
    poc_server = PoCServer(
        groq_api_key=None,  # Uses GROQ_API_KEY env var
        output_dir="test_outputs/poc_reports",
        tokenomics_state_file="test_outputs/l2_tokenomics_state.json",
        archive_file="test_outputs/poc_archive.json"
    )
    print("✓ PoC Server initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Failed to initialize PoC Server: {e}")
    poc_server = None


@app.get("/")
async def root():
    return {"message": "Syntheverse PoC API", "status": "running"}


@app.get("/api/archive/statistics")
async def get_archive_statistics():
    """Get archive statistics."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        stats = poc_server.get_archive_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/archive/contributions")
async def get_contributions(
    status: Optional[str] = None,
    contributor: Optional[str] = None,
    metal: Optional[str] = None
):
    """Get contributions with optional filters."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        # Convert string filters to enums if needed
        status_filter = ContributionStatus(status) if status else None
        metal_filter = MetalType(metal) if metal else None
        
        contributions = poc_server.archive.get_all_contributions(
            status=status_filter,
            contributor=contributor,
            metal=metal_filter
        )
        
        # Convert to list of dicts for JSON serialization
        return [dict(contrib) for contrib in contributions]
        return contributions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/archive/contributions/{submission_hash}")
async def get_contribution(submission_hash: str):
    """Get a single contribution by hash."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        contribution = poc_server.archive.get_contribution(submission_hash)
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        return dict(contribution) if contribution else None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit")
async def submit_contribution(
    submission_hash: Optional[str] = Form(None),
    title: str = Form(...),
    contributor: str = Form(...),
    category: Optional[str] = Form("scientific"),
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Submit a new contribution."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    
    try:
        # Generate hash if not provided
        if not submission_hash:
            submission_hash = uuid.uuid4().hex
        
        # Handle file upload
        content = text_content or ""
        if file:
            # For now, just read the file content as text
            # In production, you'd extract text from PDF
            file_content = await file.read()
            content = f"[File: {file.filename}]\n\n{file_content.decode('utf-8', errors='ignore')}"
        
        # Submit contribution
        result = poc_server.submit_contribution(
            submission_hash=submission_hash,
            title=title,
            contributor=contributor,
            text_content=content,
            category=category
        )
        
        return {
            "success": True,
            "submission_hash": result["submission_hash"],
            "status": result["status"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate/{submission_hash}")
async def evaluate_contribution(submission_hash: str):
    """Evaluate a contribution."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    
    try:
        result = poc_server.evaluate_contribution(submission_hash)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sandbox-map")
async def get_sandbox_map():
    """Get sandbox map data."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        map_data = poc_server.get_sandbox_map()
        return map_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tokenomics/epoch-info")
async def get_epoch_info():
    """Get epoch information."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        epoch_info = poc_server.get_epoch_info()
        return epoch_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tokenomics/statistics")
async def get_tokenomics_statistics():
    """Get tokenomics statistics."""
    if not poc_server:
        raise HTTPException(status_code=503, detail="PoC Server not initialized")
    try:
        stats = poc_server.get_tokenomics_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "5001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
