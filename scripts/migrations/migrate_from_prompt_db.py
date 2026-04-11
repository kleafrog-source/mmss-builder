"""Migration script from prompt-db-local to Pezzo/MMSS.

Reads prompts from legacy prompt-db-local and migrates them to:
1. Pezzo (as prompts with metadata)
2. Optionally converts to MMSS format
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel


class LegacyPrompt(BaseModel):
    """Legacy prompt structure from prompt-db-local."""
    id: Optional[str] = None
    name: str
    content: str
    description: Optional[str] = None
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MigrationConfig(BaseModel):
    """Migration configuration."""
    source_path: str
    pezzo_url: str
    pezzo_api_key: str
    convert_to_mmss: bool = False
    dry_run: bool = False
    tag_prefix: str = "migrated"


class PromptDBMigrator:
    """Migrator from prompt-db-local to Pezzo."""
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.headers = {
            "Content-Type": "application/json",
        }
        if config.pezzo_api_key:
            self.headers["Authorization"] = f"Bearer {config.pezzo_api_key}"
        
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
    
    def read_json_db(self, filepath: str) -> List[LegacyPrompt]:
        """Read prompts from JSON file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Database file not found: {filepath}")
        
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        prompts = []
        if isinstance(data, list):
            for item in data:
                prompts.append(LegacyPrompt(**item))
        elif isinstance(data, dict) and "prompts" in data:
            for item in data["prompts"]:
                prompts.append(LegacyPrompt(**item))
        
        return prompts
    
    def read_directory(self, directory: str) -> List[LegacyPrompt]:
        """Read prompts from directory of JSON files."""
        prompts = []
        dir_path = Path(directory)
        
        for json_file in dir_path.glob("*.json"):
            try:
                content = json_file.read_text(encoding="utf-8")
                data = json.loads(content)
                
                # Single prompt file
                if isinstance(data, dict) and "content" in data:
                    prompt = LegacyPrompt(**data)
                    if not prompt.name:
                        prompt.name = json_file.stem
                    prompts.append(prompt)
                # Multiple prompts in file
                elif isinstance(data, list):
                    for item in data:
                        prompt = LegacyPrompt(**item)
                        if not prompt.name:
                            prompt.name = json_file.stem
                        prompts.append(prompt)
            except Exception as e:
                print(f"Warning: Failed to read {json_file}: {e}")
        
        return prompts
    
    def to_mmss_structure(self, prompt: LegacyPrompt) -> Dict[str, Any]:
        """Convert legacy prompt to MMSS structure."""
        return {
            "pkg": f"migrated_{prompt.name}",
            "ver": "1.0-migrated",
            "ops": [
                {
                    "i": "MIGRATED_PROMPT",
                    "f": prompt.content,
                    "domain": "Migrated",
                    "physics_map": "N/A",
                    "error_guard": "Migrated from prompt-db-local"
                }
            ],
            "metadata": {
                "original_id": prompt.id,
                "original_name": prompt.name,
                "original_description": prompt.description,
                "original_tags": prompt.tags,
                "migrated_at": datetime.utcnow().isoformat(),
                "source": "prompt-db-local"
            }
        }
    
    async def migrate_prompt(self, prompt: LegacyPrompt) -> Dict[str, Any]:
        """Migrate single prompt to Pezzo."""
        # Prepare tags
        tags = [f"{self.config.tag_prefix}"] + prompt.tags
        
        # Prepare metadata
        metadata = {
            "migrated": True,
            "migrated_at": datetime.utcnow().isoformat(),
            "original_metadata": prompt.metadata or {},
            "original_tags": prompt.tags,
            "migration_source": "prompt-db-local"
        }
        
        # If converting to MMSS, transform content
        content = prompt.content
        if self.config.convert_to_mmss:
            mmss = self.to_mmss_structure(prompt)
            content = json.dumps(mmss, indent=2, ensure_ascii=False)
            metadata["mmss_converted"] = True
        
        payload = {
            "name": prompt.name,
            "content": content,
            "description": prompt.description or f"Migrated from prompt-db-local",
            "metadata": metadata,
            "tags": tags
        }
        
        if self.config.dry_run:
            return {
                "status": "dry_run",
                "prompt_name": prompt.name,
                "payload": payload
            }
        
        # Send to Pezzo
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.pezzo_url}/api/prompts",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    "status": "success",
                    "prompt_id": data.get("id"),
                    "prompt_name": data.get("name")
                }
            else:
                return {
                    "status": "failed",
                    "prompt_name": prompt.name,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
    
    async def run_migration(self, source: str) -> Dict[str, Any]:
        """Run full migration."""
        print(f"Starting migration from: {source}")
        print(f"Target: {self.config.pezzo_url}")
        print(f"Convert to MMSS: {self.config.convert_to_mmss}")
        print(f"Dry run: {self.config.dry_run}")
        print("-" * 50)
        
        # Load prompts
        source_path = Path(source)
        if source_path.is_file():
            prompts = self.read_json_db(source)
        elif source_path.is_dir():
            prompts = self.read_directory(source)
        else:
            raise ValueError(f"Source not found: {source}")
        
        self.stats["total"] = len(prompts)
        print(f"Found {len(prompts)} prompts to migrate\n")
        
        # Migrate each prompt
        results = []
        for prompt in prompts:
            print(f"Migrating: {prompt.name}...", end=" ")
            
            try:
                result = await self.migrate_prompt(prompt)
                results.append(result)
                
                if result["status"] == "success":
                    self.stats["success"] += 1
                    print(f"✓ (ID: {result.get('prompt_id', 'N/A')})")
                elif result["status"] == "dry_run":
                    self.stats["success"] += 1
                    print("[DRY RUN]")
                else:
                    self.stats["failed"] += 1
                    print(f"✗ ({result.get('error', 'Unknown error')})")
                    
            except Exception as e:
                self.stats["failed"] += 1
                print(f"✗ ({str(e)})")
                results.append({
                    "status": "error",
                    "prompt_name": prompt.name,
                    "error": str(e)
                })
        
        print("\n" + "-" * 50)
        print("Migration complete!")
        print(f"Total: {self.stats['total']}")
        print(f"Success: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        
        return {
            "stats": self.stats,
            "results": results
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate prompts from prompt-db-local to Pezzo"
    )
    parser.add_argument(
        "source",
        help="Path to prompt-db-local (JSON file or directory)"
    )
    parser.add_argument(
        "--pezzo-url",
        default=os.getenv("PEZZO_API_URL", "http://localhost:3001"),
        help="Pezzo API URL"
    )
    parser.add_argument(
        "--pezzo-api-key",
        default=os.getenv("PEZZO_API_KEY", ""),
        help="Pezzo API key"
    )
    parser.add_argument(
        "--convert-to-mmss",
        action="store_true",
        help="Convert prompts to MMSS format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without doing it"
    )
    parser.add_argument(
        "--tag-prefix",
        default="migrated",
        help="Prefix for migration tags"
    )
    
    args = parser.parse_args()
    
    config = MigrationConfig(
        source_path=args.source,
        pezzo_url=args.pezzo_url,
        pezzo_api_key=args.pezzo_api_key,
        convert_to_mmss=args.convert_to_mmss,
        dry_run=args.dry_run,
        tag_prefix=args.tag_prefix
    )
    
    migrator = PromptDBMigrator(config)
    result = asyncio.run(migrator.run_migration(args.source))
    
    # Save detailed results
    if not args.dry_run:
        output_file = f"migration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {output_file}")
    
    return 0 if result["stats"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
