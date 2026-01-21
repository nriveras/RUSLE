# Configuration Reference

Complete reference for all configuration options in the RUSLE application.

## Environment Variables

All environment variables use the `RUSLE_` prefix.

### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RUSLE_DEBUG` | bool | `false` | Enable debug mode and verbose logging |
| `RUSLE_HOST` | string | `0.0.0.0` | Server bind address |
| `RUSLE_PORT` | int | `8000` | Server port |

### Google Earth Engine

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RUSLE_GEE_PROJECT` | string | `ee-nriveras` | GEE Cloud Project ID |
| `RUSLE_GEE_SERVICE_ACCOUNT` | string | - | Service account email (optional) |
| `RUSLE_GEE_CREDENTIALS_PATH` | string | - | Path to service account JSON key |

### Processing Limits

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RUSLE_MAX_UPLOAD_SIZE_MB` | int | `50` | Maximum upload file size |
| `RUSLE_MAX_AOI_AREA_KM2` | float | `50000` | Maximum area of interest (km²) |
| `RUSLE_DEFAULT_EXPORT_SCALE` | int | `90` | Default export resolution (meters) |

### Paths

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RUSLE_UPLOAD_DIR` | path | `data/uploads` | Upload directory |
| `RUSLE_OUTPUT_DIR` | path | `data/output` | Output directory |

## Configuration File

Create a `.env` file in the project root:

```bash
# .env
RUSLE_GEE_PROJECT=your-project-id
RUSLE_DEBUG=true
RUSLE_MAX_UPLOAD_SIZE_MB=100
RUSLE_MAX_AOI_AREA_KM2=100000
RUSLE_DEFAULT_EXPORT_SCALE=90
```

## Pydantic Settings

Configuration is managed via `app/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "RUSLE Soil Loss Calculator"
    app_version: str = "0.1.0"
    debug: bool = False

    # Google Earth Engine
    gee_project: str = "ee-nriveras"
    gee_service_account: Optional[str] = None
    gee_credentials_path: Optional[str] = None

    # Processing defaults
    default_export_scale: int = 90
    max_upload_size_mb: int = 50
    max_aoi_area_km2: float = 50000

    class Config:
        env_prefix = "RUSLE_"
        env_file = ".env"
```

## RUSLE Parameter Ranges

Validation ranges for RUSLE factors:

| Parameter | Min | Max | Unit |
|-----------|-----|-----|------|
| R-factor | 0 | 20,000 | MJ·mm/ha/h/year |
| K-factor | 0 | 1 | t·ha·h/ha/MJ/mm |
| LS-factor | 0 | 100 | dimensionless |
| C-factor | 0 | 1 | dimensionless |
| P-factor | 0 | 1 | dimensionless |

## Logging

Configure logging level via `RUSLE_DEBUG`:

```python
import logging

# When RUSLE_DEBUG=true
logging.basicConfig(level=logging.DEBUG)

# When RUSLE_DEBUG=false (default)
logging.basicConfig(level=logging.INFO)
```

## Docker Configuration

In `docker-compose.yml`:

```yaml
environment:
  - RUSLE_GEE_PROJECT=${RUSLE_GEE_PROJECT:-ee-nriveras}
  - RUSLE_DEBUG=${RUSLE_DEBUG:-false}
  - RUSLE_MAX_UPLOAD_SIZE_MB=${RUSLE_MAX_UPLOAD_SIZE_MB:-50}
  - RUSLE_MAX_AOI_AREA_KM2=${RUSLE_MAX_AOI_AREA_KM2:-50000}
  - RUSLE_DEFAULT_EXPORT_SCALE=${RUSLE_DEFAULT_EXPORT_SCALE:-90}
```

## Service Account Authentication

For production deployments without interactive authentication:

1. Create a service account in Google Cloud Console
2. Enable Earth Engine API for the service account
3. Download the JSON key file
4. Configure environment:

```bash
RUSLE_GEE_SERVICE_ACCOUNT=rusle@project.iam.gserviceaccount.com
RUSLE_GEE_CREDENTIALS_PATH=/path/to/credentials.json
```

!!! warning "Service Account Registration"
    Service accounts must be registered with Earth Engine at [signup.earthengine.google.com/#!/service_accounts](https://signup.earthengine.google.com/#!/service_accounts)
