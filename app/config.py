"""
Configuration settings for the RUSLE Web Application.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "RUSLE Soil Loss Calculator"
    app_version: str = "0.1.0"
    debug: bool = False

    # Google Earth Engine
    gee_project: str = "ee-nriveras"
    gee_service_account: Optional[str] = None
    gee_credentials_path: Optional[str] = None

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "data" / "uploads"
    output_dir: Path = base_dir / "data" / "output"
    static_dir: Path = base_dir / "app" / "static"
    templates_dir: Path = base_dir / "app" / "templates"

    # Processing defaults
    default_export_scale: int = 90  # meters
    max_upload_size_mb: int = 50
    max_aoi_area_km2: float = 50000  # Maximum AOI area in km²

    # RUSLE parameter ranges for validation
    r_factor_range: tuple = (0, 20000)
    k_factor_range: tuple = (0, 1)
    ls_factor_range: tuple = (0, 100)
    c_factor_range: tuple = (0, 1)
    p_factor_range: tuple = (0, 1)

    class Config:
        env_file = ".env"
        env_prefix = "RUSLE_"

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
