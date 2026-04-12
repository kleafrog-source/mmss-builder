"""Configuration for Optimizer Service."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Service settings."""
    
    # Service
    host: str = Field(default="0.0.0.0", alias="OPTIMIZER_HOST")
    port: int = Field(default=8000, alias="OPTIMIZER_PORT")
    log_level: str = Field(default="INFO", alias="OPTIMIZER_LOG_LEVEL")
    
    # GEPA
    gepa_mcp_url: str = Field(default="http://localhost:3003", alias="GEPA_MCP_SERVER_URL")
    gepa_api_key: str = Field(default="", alias="GEPA_API_KEY")
    gepa_iterations: int = Field(default=5, alias="GEPA_OPTIMIZATION_ITERATIONS")
    gepa_population: int = Field(default=3, alias="GEPA_POPULATION_SIZE")
    
    # Mistral API (for real GEPA)
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-large-latest", alias="MISTRAL_MODEL")
    
    # Pezzo
    pezzo_url: str = Field(default="http://localhost:3001", alias="PEZZO_API_URL")
    pezzo_api_key: str = Field(default="", alias="PEZZO_API_KEY")
    
    # Redis (для очередей)
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
