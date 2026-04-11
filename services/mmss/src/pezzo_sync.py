"""Synchronization with Pezzo."""

import httpx
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from .config import settings
from .mmss_adapter import MMSSPackage, MMSSElement, mmss_adapter


class PezzoPrompt(BaseModel):
    """Pezzo prompt model."""
    id: str
    name: str
    description: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = None


class PezzoSync:
    """Synchronization service for MMSS <-> Pezzo."""
    
    def __init__(self, pezzo_url: str = None, api_key: str = None):
        self.pezzo_url = pezzo_url or settings.pezzo_url
        self.api_key = api_key or settings.pezzo_api_key
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def import_to_pezzo(
        self,
        mmss: MMSSPackage,
        prompt_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> PezzoPrompt:
        """Import MMSS structure to Pezzo as prompt.
        
        Args:
            mmss: MMSS package to import
            prompt_name: Name for the prompt (defaults to mmss.pkg)
            description: Optional description
        
        Returns:
            Created PezzoPrompt
        """
        name = prompt_name or mmss.pkg
        content = mmss_adapter.extract_prompt_content(mmss)
        
        # Convert MMSS to Pezzo format
        payload = {
            "name": name,
            "content": content,
            "description": description or f"MMSS structure: {mmss.pkg} v{mmss.ver}",
            "metadata": {
                "mmss": {
                    "package": mmss.pkg,
                    "version": mmss.ver,
                    "operations_count": len(mmss.ops),
                    "operations": [op.i for op in mmss.ops]
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.pezzo_url}/api/prompts",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
        
        return PezzoPrompt(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            content=content,
            metadata=data.get("metadata", {})
        )
    
    async def export_from_pezzo(
        self,
        prompt_id: str,
        base_structure: Optional[Dict[str, Any]] = None
    ) -> MMSSPackage:
        """Export prompt from Pezzo to MMSS structure.
        
        Args:
            prompt_id: Pezzo prompt ID
            base_structure: Optional base structure to merge with
        
        Returns:
            MMSSPackage
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.pezzo_url}/api/prompts/{prompt_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
        
        # Get latest version content
        if "versions" in data and data["versions"]:
            content = data["versions"][0].get("content", "")
        else:
            content = data.get("content", "")
        
        # Try to get original MMSS metadata
        metadata = data.get("metadata", {})
        mmss_meta = metadata.get("mmss", {})
        
        # If we have original MMSS structure, use it
        if base_structure:
            return mmss_adapter.build_mmss_from_prompt(content, base_structure)
        
        # Otherwise try to parse from content
        try:
            # Maybe the content is JSON
            data = json.loads(content)
            if mmss_adapter.validate_structure(data):
                return mmss_adapter.parse_mmss_structure(data)
        except json.JSONDecodeError:
            pass
        
        # Build from prompt content
        return mmss_adapter.build_mmss_from_prompt(content)
    
    async def update_mmss_version(
        self,
        prompt_id: str,
        mmss: MMSSPackage,
        message: str = "Updated from MMSS"
    ) -> Dict[str, Any]:
        """Update prompt in Pezzo with new MMSS version.
        
        Args:
            prompt_id: Pezzo prompt ID
            mmss: Updated MMSS package
            message: Version commit message
        
        Returns:
            Version data
        """
        content = mmss_adapter.extract_prompt_content(mmss)
        
        payload = {
            "content": content,
            "message": message,
            "metadata": {
                "mmss": {
                    "package": mmss.pkg,
                    "version": mmss.ver,
                    "operations_count": len(mmss.ops)
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.pezzo_url}/api/prompts/{prompt_id}/versions",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def find_mmss_prompts(
        self,
        limit: int = 100
    ) -> List[PezzoPrompt]:
        """Find all prompts with MMSS metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.pezzo_url}/api/prompts?limit={limit}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
        
        mmss_prompts = []
        for item in data:
            metadata = item.get("metadata", {})
            if "mmss" in metadata:
                mmss_prompts.append(PezzoPrompt(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description"),
                    content=item.get("content", ""),
                    metadata=metadata
                ))
        
        return mmss_prompts
    
    async def sync_directory(
        self,
        directory: str = None,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Sync all MMSS files from directory to Pezzo.
        
        Args:
            directory: Directory to scan (defaults to mmss-builder path)
            dry_run: If True, only report what would be done
        
        Returns:
            List of sync results
        """
        results = []
        mmss_files = mmss_adapter.find_mmss_files(directory)
        
        for filepath in mmss_files:
            try:
                mmss = mmss_adapter.load_from_file(str(filepath))
                
                if dry_run:
                    results.append({
                        "file": str(filepath),
                        "action": "would_import",
                        "name": mmss.pkg
                    })
                else:
                    prompt = await self.import_to_pezzo(mmss)
                    results.append({
                        "file": str(filepath),
                        "action": "imported",
                        "prompt_id": prompt.id,
                        "name": prompt.name
                    })
            except Exception as e:
                results.append({
                    "file": str(filepath),
                    "action": "error",
                    "error": str(e)
                })
        
        return results


# Singleton instance
pezzo_sync = PezzoSync()
