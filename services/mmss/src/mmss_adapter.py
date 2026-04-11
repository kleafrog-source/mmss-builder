"""MMSS Structure Adapter."""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel

from .config import settings


class MMSSElement(BaseModel):
    """Single MMSS element."""
    i: str  # ID
    f: str  # Formula/content
    domain: Optional[str] = None
    physics_map: Optional[str] = None
    error_guard: Optional[str] = None


class MMSSPackage(BaseModel):
    """MMSS package structure."""
    pkg: str  # Package name
    ver: str  # Version
    ops: List[MMSSElement] = []
    metadata: Optional[Dict[str, Any]] = None


class MMSSAdapter:
    """Adapter for MMSS structures."""
    
    def __init__(self, builder_path: str = None):
        self.builder_path = Path(builder_path or settings.mmss_builder_path)
    
    def parse_mmss_structure(self, data: Dict[str, Any]) -> MMSSPackage:
        """Parse MMSS structure from dict."""
        return MMSSPackage(**data)
    
    def parse_mmss_json(self, json_str: str) -> MMSSPackage:
        """Parse MMSS structure from JSON string."""
        data = json.loads(json_str)
        return self.parse_mmss_structure(data)
    
    def extract_prompt_content(self, mmss: MMSSPackage) -> str:
        """Extract prompt content from MMSS structure.
        
        Combines formulas and descriptions into optimizable text.
        """
        parts = []
        
        # Add package info
        parts.append(f"Package: {mmss.pkg}")
        parts.append(f"Version: {mmss.ver}")
        parts.append("")
        
        # Add operations
        for op in mmss.ops:
            parts.append(f"[{op.i}]")
            if op.domain:
                parts.append(f"Domain: {op.domain}")
            if op.physics_map:
                parts.append(f"Physics Map: {op.physics_map}")
            parts.append(f"Formula: {op.f}")
            if op.error_guard:
                parts.append(f"Note: {op.error_guard}")
            parts.append("")
        
        return "\n".join(parts)
    
    def build_mmss_from_prompt(
        self,
        prompt_content: str,
        base_structure: Optional[Dict[str, Any]] = None
    ) -> MMSSPackage:
        """Build MMSS structure from optimized prompt content.
        
        Attempts to parse the optimized content back into MMSS format.
        """
        if base_structure:
            mmss = self.parse_mmss_structure(base_structure)
        else:
            mmss = MMSSPackage(
                pkg="mmss_optimized",
                ver="1.0",
                ops=[]
            )
        
        # Parse prompt content for formulas
        lines = prompt_content.split("\n")
        current_op = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for package name
            if line.startswith("Package:"):
                mmss.pkg = line.split(":", 1)[1].strip()
                continue
            
            # Check for version
            if line.startswith("Version:"):
                mmss.ver = line.split(":", 1)[1].strip()
                continue
            
            # Check for operation ID
            op_match = re.match(r"\[([^\]]+)\]", line)
            if op_match:
                if current_op:
                    mmss.ops.append(current_op)
                current_op = MMSSElement(i=op_match.group(1), f="")
                continue
            
            # Parse fields
            if current_op:
                if line.startswith("Domain:"):
                    current_op.domain = line.split(":", 1)[1].strip()
                elif line.startswith("Physics Map:"):
                    current_op.physics_map = line.split(":", 1)[1].strip()
                elif line.startswith("Formula:"):
                    current_op.f = line.split(":", 1)[1].strip()
                elif line.startswith("Note:"):
                    current_op.error_guard = line.split(":", 1)[1].strip()
        
        # Add last operation
        if current_op:
            mmss.ops.append(current_op)
        
        return mmss
    
    def load_from_file(self, filepath: str) -> MMSSPackage:
        """Load MMSS structure from file."""
        path = Path(filepath)
        content = path.read_text(encoding="utf-8")
        
        if path.suffix == ".json":
            return self.parse_mmss_json(content)
        else:
            # Try to parse as JSON anyway
            try:
                return self.parse_mmss_json(content)
            except json.JSONDecodeError:
                raise ValueError(f"Cannot parse {filepath} as MMSS structure")
    
    def save_to_file(
        self,
        mmss: MMSSPackage,
        filepath: str,
        format: str = "json"
    ) -> None:
        """Save MMSS structure to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            content = json.dumps(mmss.model_dump(), indent=2, ensure_ascii=False)
        else:
            # Custom text format
            content = self.extract_prompt_content(mmss)
        
        path.write_text(content, encoding="utf-8")
    
    def validate_structure(self, data: Dict[str, Any]) -> bool:
        """Validate MMSS structure."""
        required_fields = ["pkg", "ver", "ops"]
        return all(field in data for field in required_fields)
    
    def find_mmss_files(self, directory: str = None) -> List[Path]:
        """Find all MMSS JSON files in directory."""
        base_dir = Path(directory) if directory else self.builder_path
        
        if not base_dir.exists():
            return []
        
        # Find .json files that look like MMSS
        mmss_files = []
        for path in base_dir.rglob("*.json"):
            try:
                content = path.read_text(encoding="utf-8")
                data = json.loads(content)
                if self.validate_structure(data):
                    mmss_files.append(path)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        
        return mmss_files


# Singleton instance
mmss_adapter = MMSSAdapter()
