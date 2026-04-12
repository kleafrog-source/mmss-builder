"""FastAPI endpoints for Optimizer Service."""

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .config import settings
from .optimizer import (
    OptimizerService,
    OptimizationJob,
    JobStatus,
    optimizer_service
)
from .gepa_client import GEPAConfig


app = FastAPI(
    title="GEPA Optimizer Service",
    description="Сервис для оптимизации промптов через GEPA",
    version="0.1.0"
)


# ============== Pydantic Models ==============

class OptimizeRequest(BaseModel):
    """Request for prompt optimization."""
    prompt_id: Optional[str] = None
    prompt_name: Optional[str] = None
    prompt_content: Optional[str] = None
    config: Optional[GEPAConfig] = None
    objective: str = "quality"
    async_mode: bool = True


class OptimizeResponse(BaseModel):
    """Response from optimization request."""
    job_id: str
    status: JobStatus
    message: str


class JobResponse(BaseModel):
    """Job status response."""
    job: OptimizationJob


class OptimizeMMSSRequest(BaseModel):
    """Request for MMSS optimization."""
    mmss_structure: Dict[str, Any]
    prompt_name: str
    target_field: str = "content"
    config: Optional[GEPAConfig] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    gepa_available: bool
    pezzo_available: bool


# ============== Endpoints ==============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health."""
    from .gepa_client import gepa_client
    from .pezzo_client import pezzo_client
    from .config import settings
    
    gepa_ok = await gepa_client.health_check()
    
    # Check Pezzo
    pezzo_ok = False
    try:
        await pezzo_client.list_prompts(limit=1)
        pezzo_ok = True
    except Exception:
        pass
    
    # Check Mistral API
    has_mistral = bool(settings.mistral_api_key)
    
    return HealthResponse(
        status="healthy" if (gepa_ok or has_mistral) and pezzo_ok else "degraded",
        gepa_available=gepa_ok or has_mistral,
        pezzo_available=pezzo_ok
    )


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(
    request: OptimizeRequest,
    background_tasks: BackgroundTasks
):
    """Start prompt optimization job."""
    # Create job
    job = await optimizer_service.create_job(
        prompt_id=request.prompt_id,
        prompt_name=request.prompt_name,
        prompt_content=request.prompt_content,
        config=request.config
    )
    
    if request.async_mode:
        # Run in background
        background_tasks.add_task(optimizer_service.run_job, job.id)
        return OptimizeResponse(
            job_id=job.id,
            status=JobStatus.PENDING,
            message="Optimization job started in background"
        )
    else:
        # Run synchronously
        job = await optimizer_service.run_job(job.id)
        return OptimizeResponse(
            job_id=job.id,
            status=job.status,
            message="Optimization completed" if job.status == JobStatus.COMPLETED else job.error
        )


@app.post("/optimize-mmss", response_model=OptimizeResponse)
async def optimize_mmss(request: OptimizeMMSSRequest):
    """Optimize MMSS structure and save to Pezzo."""
    job = await optimizer_service.optimize_mmss_and_save(
        mmss_structure=request.mmss_structure,
        prompt_name=request.prompt_name,
        target_field=request.target_field,
        config=request.config
    )
    
    return OptimizeResponse(
        job_id=job.id,
        status=job.status,
        message="MMSS optimization completed" if job.status == JobStatus.COMPLETED else job.error
    )


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get optimization job status."""
    job = await optimizer_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job=job)


@app.get("/jobs", response_model=List[OptimizationJob])
async def list_jobs(
    status: Optional[JobStatus] = None,
    limit: int = 100
):
    """List optimization jobs."""
    return await optimizer_service.list_jobs(status=status, limit=limit)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "GEPA Optimizer Service",
        "version": "0.1.0",
        "endpoints": [
            "/health",
            "/optimize",
            "/optimize-mmss",
            "/jobs",
            "/jobs/{job_id}"
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
