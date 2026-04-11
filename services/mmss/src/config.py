"""Configuration for MMSS Service."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Service settings."""
    
    # Service
    host: str = Field(default="0.0.0.0", alias="MMSS_HOST")
    port: int = Field(default=8001, alias="MMSS_PORT")
    log_level: str = Field(default="INFO", alias="MMSS_LOG_LEVEL")
    
    # MMSS Builder
    mmss_builder_path: str = Field(default="./mmss-builder", alias="MMSS_BUILDER_PATH")
    mmss_output_format: str = Field(default="json", alias="MMSS_OUTPUT_FORMAT")
    mmss_auto_sync: bool = Field(default=True, alias="MMSS_AUTO_SYNC")
    
    # Pezzo
    pezzo_url: str = Field(default="http://localhost:3001", alias="PEZZO_API_URL")
    pezzo_api_key: str = Field(default="", alias="PEZZO_API_KEY")
    
    # Optimizer Service
    optimizer_url: str = Field(default="http://localhost:8000", alias="OPTIMIZER_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
