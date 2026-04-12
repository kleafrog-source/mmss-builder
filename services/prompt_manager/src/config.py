"""Configuration for Prompt Manager Service."""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Service settings."""
    
    # Service
    host: str = Field(default="0.0.0.0", alias="PROMPT_MANAGER_HOST")
    port: int = Field(default=8002, alias="PROMPT_MANAGER_PORT")
    log_level: str = Field(default="INFO", alias="PROMPT_MANAGER_LOG_LEVEL")
    
    # Storage
    data_dir: Path = Field(default=Path("./data/prompts"), alias="PROMPT_DATA_DIR")
    
    # Optimizer integration
    optimizer_url: str = Field(default="http://localhost:8000", alias="OPTIMIZER_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
