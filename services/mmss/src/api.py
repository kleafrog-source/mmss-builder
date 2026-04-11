"""FastAPI endpoints for MMSS Service."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .config import settings
from .mmss_adapter import (
    MMSSPackage,
    MMSSElement,
    mmss_adapter
)
from .pezzo_sync import PezzoPrompt, pezzo_sync


app = FastAPI(
    title="MMSS Integration Service",
    description="Сервис для интеграции MMSS-структур с Pezzo",
    version="0.1.0"
)


# ============== Pydantic Models ==============

class MMSSImportRequest(BaseModel):
    """Request to import MMSS to Pezzo."""
    mmss_structure: Dict[str, Any]
    prompt_name: Optional[str] = None
    description: Optional[str] = None


class MMSSExportRequest(BaseModel):
    """Request to export from Pezzo."""
    prompt_id: str


class MMSSFileRequest(BaseModel):
    """Request to load MMSS from file."""
    filepath: str


class MMSSSyncRequest(BaseModel):
    """Request to sync directory."""
    directory: Optional[str] = None
    dry_run: bool = False


class MMSSOptimizeRequest(BaseModel):
    """Request to optimize via optimizer service."""
    mmss_structure: Dict[str, Any]
    prompt_name: str
    target_field: str = "content"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    mmss_builder_path: str
    pezzo_available: bool


class SyncResponse(BaseModel):
    """Sync operation response."""
    results: List[Dict[str, Any]]
    total: int
    imported: int
    errors: int


# ============== Endpoints ==============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health."""
    pezzo_ok = False
    try:
        await pezzo_sync.find_mmss_prompts(limit=1)
        pezzo_ok = True
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if pezzo_ok else "degraded",
        mmss_builder_path=str(mmss_adapter.builder_path),
        pezzo_available=pezzo_ok
    )


@app.post("/import", response_model=PezzoPrompt)
async def import_to_pezzo(request: MMSSImportRequest):
    """Import MMSS structure to Pezzo."""
    try:
        mmss = mmss_adapter.parse_mmss_structure(request.mmss_structure)
        prompt = await pezzo_sync.import_to_pezzo(
            mmss=mmss,
            prompt_name=request.prompt_name,
            description=request.description
        )
        return prompt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/export/{prompt_id}", response_model=MMSSPackage)
async def export_from_pezzo(prompt_id: str):
    """Export prompt from Pezzo to MMSS structure."""
    try:
        mmss = await pezzo_sync.export_from_pezzo(prompt_id)
        return mmss
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/load-file", response_model=MMSSPackage)
async def load_from_file(request: MMSSFileRequest):
    """Load MMSS structure from file."""
    try:
        mmss = mmss_adapter.load_from_file(request.filepath)
        return mmss
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/save-file")
async def save_to_file(
    mmss: MMSSPackage,
    filepath: str,
    format: str = "json"
):
    """Save MMSS structure to file."""
    try:
        mmss_adapter.save_to_file(mmss, filepath, format)
        return {"status": "saved", "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync", response_model=SyncResponse)
async def sync_directory(request: MMSSSyncRequest):
    """Sync MMSS files from directory to Pezzo."""
    results = await pezzo_sync.sync_directory(
        directory=request.directory,
        dry_run=request.dry_run
    )
    
    imported = sum(1 for r in results if r.get("action") == "imported")
    errors = sum(1 for r in results if r.get("action") == "error")
    
    return SyncResponse(
        results=results,
        total=len(results),
        imported=imported,
        errors=errors
    )


@app.get("/find-files")
async def find_mmss_files(directory: Optional[str] = None):
    """Find all MMSS JSON files in directory."""
    files = mmss_adapter.find_mmss_files(directory)
    return {
        "files": [str(f) for f in files],
        "count": len(files)
    }


@app.post("/optimize")
async def optimize_mmss(request: MMSSOptimizeRequest):
    """Optimize MMSS via optimizer service and save to Pezzo."""
    import httpx
    
    try:
        # Forward to optimizer service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.optimizer_url}/optimize-mmss",
                json={
                    "mmss_structure": request.mmss_structure,
                    "prompt_name": request.prompt_name,
                    "target_field": request.target_field
                },
                timeout=300.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Optimizer service unavailable: {str(e)}"
        )


@app.get("/prompts", response_model=List[PezzoPrompt])
async def list_mmss_prompts(limit: int = 100):
    """List all prompts with MMSS metadata from Pezzo."""
    try:
        return await pezzo_sync.find_mmss_prompts(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MMSS Integration Service",
        "version": "0.1.0",
        "endpoints": [
            "/health",
            "/import",
            "/export/{prompt_id}",
            "/load-file",
            "/save-file",
            "/sync",
            "/find-files",
            "/optimize",
            "/prompts"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
