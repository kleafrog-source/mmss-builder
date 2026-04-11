import os
import json
import markdown
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

MMSS_DATA_PATH = "D:\\project\\mmss_core\\ai\\obsidian_export\\NEW-DATABASE-MMSS"

def parse_markdown_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Parses a markdown file to extract MMSS data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # This is a placeholder for parsing logic. 
        # We will need to refine this based on the actual file content.
        # For now, let's assume data is in a json block.
        if "```json" in content:
            json_content = content.split("```json")[1].split("```")[0]
            return json.loads(json_content)
        else:
            # Fallback for files that are just json
            return json.loads(content)
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def build_tree() -> Dict[str, Any]:
    """Builds the MMSS hierarchy."""
    
    # This is a placeholder. 
    # We will build the tree based on the parsed MMSS data.
    # For now, returning a sample tree structure.
    
    root = {"name": "MMSS Systems", "children": []}
    
    for dirpath, _, filenames in os.walk(MMSS_DATA_PATH):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(dirpath, filename)
                data = parse_markdown_file(file_path)
                if data:
                    # Assuming the data has a 'name' field
                    name = data.get("package_id", data.get("metadata", {}).get("architectural_class", filename))
                    root["children"].append({"name": name, "attributes": data})

    return root


@app.get("/api/mmss-tree")
async def get_mmss_tree():
    """
    Endpoint to get the MMSS data as a tree structure.
    """
    tree = build_tree()
    return tree

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)