"""Optimizer logic and job management."""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from .gepa_client import GEPAClient, GEPAConfig, OptimizationResult
from .pezzo_client import PezzoClient


class JobStatus(str, Enum):
    """Optimization job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OptimizationJob(BaseModel):
    """Optimization job model."""
    id: str
    prompt_id: Optional[str] = None
    prompt_name: Optional[str] = None
    prompt_content: Optional[str] = None  # Direct content for standalone mode
    status: JobStatus
    config: GEPAConfig
    result: Optional[OptimizationResult] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OptimizerService:
    """Service for managing prompt optimization jobs."""
    
    def __init__(
        self,
        gepa_client: GEPAClient = None,
        pezzo_client: PezzoClient = None
    ):
        self.gepa = gepa_client or GEPAClient()
        self.pezzo = pezzo_client or PezzoClient()
        self.jobs: Dict[str, OptimizationJob] = {}
        self._lock = asyncio.Lock()
    
    async def create_job(
        self,
        prompt_id: Optional[str] = None,
        prompt_name: Optional[str] = None,
        prompt_content: Optional[str] = None,
        config: Optional[GEPAConfig] = None
    ) -> OptimizationJob:
        """Create new optimization job."""
        job = OptimizationJob(
            id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            prompt_name=prompt_name,
            prompt_content=prompt_content,
            status=JobStatus.PENDING,
            config=config or GEPAConfig(),
            created_at=datetime.utcnow()
        )
        
        async with self._lock:
            self.jobs[job.id] = job
        
        return job
    
    async def run_job(self, job_id: str) -> OptimizationJob:
        """Execute optimization job."""
        async with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
        
        try:
            # Get prompt content
            content = None
            prompt = None
            
            if job.prompt_content:
                # Direct content mode (standalone, no Pezzo required)
                content = job.prompt_content
            elif job.prompt_id:
                prompt = await self.pezzo.get_prompt(job.prompt_id)
                if prompt:
                    content = prompt.latest_version.content if prompt.latest_version else ""
            elif job.prompt_name:
                prompt = await self.pezzo.get_prompt_by_name(job.prompt_name)
                if prompt:
                    content = prompt.latest_version.content if prompt.latest_version else ""
            
            if not content:
                raise ValueError("No prompt content available. Provide prompt_content, prompt_id, or prompt_name")
            
            # Run optimization
            result = await self.gepa.optimize_prompt(
                prompt=content,
                config=job.config
            )
            
            # Update job
            async with self._lock:
                job.result = result
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
            
            # Create new version in Pezzo (only if Pezzo is connected)
            if prompt and prompt.id:
                try:
                    await self.pezzo.create_version(
                        prompt_id=prompt.id,
                        content=result.optimized_prompt,
                        message=f"GEPA optimization: fitness={result.fitness_score:.3f}",
                        metadata={
                            "optimization": {
                                "iterations": result.iterations,
                                "fitness_score": result.fitness_score,
                                "improvements": result.improvements
                            }
                        }
                    )
                except Exception as e:
                    # Pezzo not available, skip version creation
                    pass
            
        except Exception as e:
            async with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.utcnow()
        
        return job
    
    async def run_job_async(self, job_id: str):
        """Run job in background."""
        asyncio.create_task(self.run_job(job_id))
    
    async def get_job(self, job_id: str) -> Optional[OptimizationJob]:
        """Get job by ID."""
        async with self._lock:
            return self.jobs.get(job_id)
    
    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 100
    ) -> list[OptimizationJob]:
        """List jobs, optionally filtered by status."""
        async with self._lock:
            jobs = list(self.jobs.values())
            if status:
                jobs = [j for j in jobs if j.status == status]
            return sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]
    
    async def optimize_mmss_and_save(
        self,
        mmss_structure: Dict[str, Any],
        prompt_name: str,
        target_field: str = "content",
        config: Optional[GEPAConfig] = None
    ) -> OptimizationJob:
        """Optimize MMSS structure and save to Pezzo."""
        job = await self.create_job(
            prompt_name=prompt_name,
            config=config
        )
        
        try:
            # Optimize MMSS
            result = await self.gepa.optimize_mmss_structure(
                mmss_structure=mmss_structure,
                target_field=target_field,
                config=job.config
            )
            
            # Try to save to Pezzo (optional for standalone mode)
            prompt_id = None
            try:
                prompt = await self.pezzo.create_prompt(
                    name=prompt_name,
                    content=result.optimized_prompt,
                    description=f"Optimized MMSS structure from {prompt_name}",
                    metadata={
                        "source": "mmss-builder",
                        "mmss_structure": True,
                        "optimization": {
                            "iterations": result.iterations,
                            "fitness_score": result.fitness_score
                        }
                    }
                )
                prompt_id = prompt.id
            except Exception:
                # Pezzo not available, continue without saving
                pass
            
            # Update job
            async with self._lock:
                job.prompt_id = prompt_id
                job.result = result
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                
        except Exception as e:
            async with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.utcnow()
        
        return job


# Singleton instance
optimizer_service = OptimizerService()
