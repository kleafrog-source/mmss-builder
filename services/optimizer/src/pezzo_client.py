"""Pezzo API Client."""

import httpx
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from .config import settings


class PromptVersion(BaseModel):
    """Prompt version model."""
    id: str
    sha: str
    message: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class Prompt(BaseModel):
    """Prompt model."""
    id: str
    name: str
    description: Optional[str] = None
    versions: List[PromptVersion] = []
    latest_version: Optional[PromptVersion] = None
    metadata: Optional[Dict[str, Any]] = None


class PezzoClient:
    """Client for Pezzo API."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.pezzo_url
        self.api_key = api_key or settings.pezzo_api_key
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get prompt by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/prompts/{prompt_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return Prompt(**data)
    
    async def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get prompt by name."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/prompts?name={name}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                return Prompt(**data[0])
            return None
    
    async def create_prompt(
        self,
        name: str,
        content: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Prompt:
        """Create new prompt."""
        payload = {
            "name": name,
            "content": content,
            "description": description,
            "metadata": metadata or {}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/prompts",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return Prompt(**response.json())
    
    async def create_version(
        self,
        prompt_id: str,
        content: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptVersion:
        """Create new version of prompt."""
        payload = {
            "content": content,
            "message": message,
            "metadata": metadata or {}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/prompts/{prompt_id}/versions",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return PromptVersion(**response.json())
    
    async def list_prompts(
        self,
        tag: Optional[str] = None,
        limit: int = 100
    ) -> List[Prompt]:
        """List all prompts."""
        params = {"limit": limit}
        if tag:
            params["tag"] = tag
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/prompts",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return [Prompt(**item) for item in data]


# Singleton instance
pezzo_client = PezzoClient()
