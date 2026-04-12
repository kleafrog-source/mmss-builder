"""JSON file storage for MMSS prompts."""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from .config import settings


class PromptMetadata(BaseModel):
    """Prompt metadata."""
    id: str
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str] = []
    category: str = "general"


class Prompt(BaseModel):
    """Prompt with MMSS structure."""
    metadata: PromptMetadata
    mmss_structure: Dict[str, Any]
    optimization_history: List[Dict[str, Any]] = []


class PromptStorage:
    """File-based storage for prompts."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        raw_path = data_dir or settings.data_dir
        # Convert to Path and resolve, handling string paths with spaces
        if isinstance(raw_path, str):
            raw_path = raw_path.strip()
        self.data_dir = Path(raw_path).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Use data_dir directly for prompts (not data_dir/prompts to avoid duplication)
        self.prompts_dir = self.data_dir
        self.backups_dir = self.data_dir / "backups"
        self.backups_dir.mkdir(exist_ok=True)
    
    def _get_path(self, prompt_id: str) -> Path:
        """Get file path for prompt."""
        return self.prompts_dir / f"{prompt_id}.json"
    
    async def list_prompts(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[PromptMetadata]:
        """List all prompts with optional filtering."""
        prompts = []
        
        for file_path in self.prompts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = PromptMetadata(**data["metadata"])
                    
                    # Apply filters
                    if category and metadata.category != category:
                        continue
                    if tags and not any(t in metadata.tags for t in tags):
                        continue
                    if search and search.lower() not in metadata.name.lower():
                        continue
                    
                    prompts.append(metadata)
            except Exception:
                continue
        
        # Sort by updated_at descending
        prompts.sort(key=lambda x: x.updated_at, reverse=True)
        return prompts
    
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get prompt by ID."""
        file_path = self._get_path(prompt_id)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Prompt(**data)
        except Exception:
            return None
    
    async def save_prompt(self, prompt: Prompt) -> Prompt:
        """Save or update prompt."""
        # Update timestamp
        prompt.metadata.updated_at = datetime.utcnow().isoformat()
        
        file_path = self._get_path(prompt.metadata.id)
        
        # Backup if exists
        if file_path.exists():
            backup_path = self.backups_dir / f"{prompt.metadata.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(file_path, backup_path)
        
        # Save
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(prompt.model_dump(), f, indent=2, ensure_ascii=False)
        
        return prompt
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete prompt."""
        file_path = self._get_path(prompt_id)
        
        if not file_path.exists():
            return False
        
        # Backup before delete
        backup_path = self.backups_dir / f"{prompt_id}_deleted_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(file_path, backup_path)
        
        file_path.unlink()
        return True
    
    async def add_optimization_result(
        self,
        prompt_id: str,
        optimization_result: Dict[str, Any]
    ) -> Optional[Prompt]:
        """Add optimization result to prompt history."""
        prompt = await self.get_prompt(prompt_id)
        if not prompt:
            return None
        
        optimization_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "fitness_score": optimization_result.get("fitness_score"),
            "iterations": optimization_result.get("iterations"),
            "improvements": optimization_result.get("improvements", []),
            "optimized_mmss": optimization_result.get("optimized_mmss")
        }
        
        prompt.optimization_history.append(optimization_record)
        prompt.metadata.version = self._bump_version(prompt.metadata.version)
        
        return await self.save_prompt(prompt)
    
    def _bump_version(self, version: str) -> str:
        """Bump patch version number."""
        try:
            parts = version.split(".")
            if len(parts) == 3:
                major, minor, patch = parts
                new_patch = str(int(patch) + 1)
                return f"{major}.{minor}.{new_patch}"
        except:
            pass
        return version
    
    async def export_prompt(self, prompt_id: str, format: str = "mmss") -> Optional[Dict[str, Any]]:
        """Export prompt in specified format."""
        prompt = await self.get_prompt(prompt_id)
        if not prompt:
            return None
        
        if format == "mmss":
            return prompt.mmss_structure
        elif format == "full":
            return prompt.model_dump()
        elif format == "prompt":
            # Extract just the prompt text from MMSS
            ops = prompt.mmss_structure.get("ops", [])
            texts = []
            for op in ops:
                if isinstance(op, dict) and "f" in op:
                    texts.append(op["f"])
            return {"prompt": "\n\n".join(texts)}
        
        return None
    
    async def import_mmss(
        self,
        mmss_structure: Dict[str, Any],
        category: str = "imported",
        tags: List[str] = []
    ) -> Prompt:
        """Import MMSS structure as new prompt."""
        import uuid
        
        pkg_name = mmss_structure.get("pkg", "unnamed")
        ver = mmss_structure.get("ver", "1.0.0")
        
        metadata = PromptMetadata(
            id=str(uuid.uuid4()),
            name=pkg_name,
            description=mmss_structure.get("metadata", {}).get("description", ""),
            version=ver,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            tags=tags,
            category=category
        )
        
        prompt = Prompt(
            metadata=metadata,
            mmss_structure=mmss_structure
        )
        
        return await self.save_prompt(prompt)


# Singleton instance
storage = PromptStorage()
