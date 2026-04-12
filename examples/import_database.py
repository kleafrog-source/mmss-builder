#!/usr/bin/env python3
"""Import prompts from database JSON file.

Usage:
    python examples/import_database.py data/prompts/database/producer-ai-base.json
"""

import asyncio
import json
import sys
from pathlib import Path
import httpx

PROMPT_MANAGER_URL = "http://localhost:8002"


async def import_prompts_from_file(file_path: Path):
    """Import all prompts from database file."""
    
    print(f"📂 Loading {file_path}...")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load file: {e}")
        return
    
    # Handle both array and single object
    if isinstance(data, list):
        prompts = data
    elif isinstance(data, dict):
        prompts = [data]
    else:
        print("❌ Invalid JSON structure")
        return
    
    print(f"📊 Found {len(prompts)} prompts to import\n")
    
    imported = 0
    failed = 0
    
    async with httpx.AsyncClient() as client:
        for i, item in enumerate(prompts, 1):
            # Convert to MMSS structure
            block_id = item.get("block_id", f"block_{i}")
            block_name = item.get("block_name", f"Block_{block_id}")
            
            # Create MMSS structure from the item
            mmss_structure = {
                "pkg": f"BLOCK_{block_name.upper().replace('.', '_').replace('-', '_')}",
                "ver": "1.0.0",
                "ops": [
                    {
                        "i": "CONTENT",
                        "f": json.dumps(item, indent=2, ensure_ascii=False),
                        "domain": "Database",
                        "physics_map": f"Block_{block_id}",
                        "error_guard": "Database import"
                    }
                ],
                "metadata": {
                    "block_id": block_id,
                    "block_name": block_name,
                    "source": "producer-ai-base",
                    "original_index": i
                }
            }
            
            # Add status if present
            if "status" in item:
                mmss_structure["metadata"]["status"] = item["status"]
            
            try:
                response = await client.post(
                    f"{PROMPT_MANAGER_URL}/api/prompts/import",
                    json={
                        "mmss_structure": mmss_structure,
                        "category": "database",
                        "tags": ["imported", "producer-ai", f"block_{block_id}"]
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                prompt_id = result["metadata"]["id"]
                print(f"  ✅ [{i}/{len(prompts)}] {block_name} → ID: {prompt_id[:8]}...")
                imported += 1
                
            except Exception as e:
                print(f"  ❌ [{i}/{len(prompts)}] {block_name} → {e}")
                failed += 1
    
    print(f"\n{'='*50}")
    print(f"📊 Import Complete")
    print(f"{'='*50}")
    print(f"✅ Imported: {imported}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total: {len(prompts)}")
    print(f"\n🌐 View at: http://localhost:8002")
    print(f"{'='*50}")


async def main():
    # Default file path
    default_path = Path("data/prompts/database/producer-ai-base.json")
    
    # Get path from args or use default
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = default_path
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        print(f"Usage: python import_database.py <path_to_json>")
        sys.exit(1)
    
    await import_prompts_from_file(file_path)


if __name__ == "__main__":
    asyncio.run(main())
