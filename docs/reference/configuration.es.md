# Referencia de Configuración

Referencia completa de todas las opciones de configuración en la aplicación RUSLE.

## Variables de Entorno

Todas las variables de entorno usan el prefijo `RUSLE_`.

### Configuración de la Aplicación

| Variable | Tipo | Por Defecto | Descripción |
|----------|------|-------------|-------------|
| `RUSLE_DEBUG` | bool | `false` | Habilitar modo de depuración y registro detallado |
| `RUSLE_HOST` | string | `0.0.0.0` | Dirección de enlace del servidor |
| `RUSLE_PORT` | int | `8000` | Puerto del servidor |

### Google Earth Engine

| Variable | Tipo | Por Defecto | Descripción |
|----------|------|-------------|-------------|
| `RUSLE_GEE_PROJECT` | string | `ee-nriveras` | ID del Proyecto Cloud de GEE |
| `RUSLE_GEE_SERVICE_ACCOUNT` | string | - | Email de cuenta de servicio (opcional) |
| `RUSLE_GEE_CREDENTIALS_PATH` | string | - | Ruta al archivo JSON de clave de cuenta de servicio |

### Límites de Procesamiento

| Variable | Tipo | Por Defecto | Descripción |
|----------|------|-------------|-------------|
| `RUSLE_MAX_UPLOAD_SIZE_MB` | int | `50` | Tamaño máximo de archivo de carga |
| `RUSLE_MAX_AOI_AREA_KM2` | float | `50000` | Área máxima de interés (km²) |
| `RUSLE_DEFAULT_EXPORT_SCALE` | int | `90` | Resolución de exportación por defecto (metros) |

### Rutas

| Variable | Tipo | Por Defecto | Descripción |
|----------|------|-------------|-------------|
| `RUSLE_UPLOAD_DIR` | ruta | `data/uploads` | Directorio de cargas |
| `RUSLE_OUTPUT_DIR` | ruta | `data/output` | Directorio de salidas |

## Archivo de Configuración

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
RUSLE_GEE_PROJECT=tu-id-de-proyecto
RUSLE_DEBUG=true
RUSLE_MAX_UPLOAD_SIZE_MB=100
RUSLE_MAX_AOI_AREA_KM2=100000
RUSLE_DEFAULT_EXPORT_SCALE=90
```

## Configuración con Pydantic

La configuración se gestiona a través de `app/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Aplicación
    app_name: str = "RUSLE Soil Loss Calculator"
    app_version: str = "0.1.0"
    debug: bool = False

    # Google Earth Engine
    gee_project: str = "ee-nriveras"
    gee_service_account: Optional[str] = None
    gee_credentials_path: Optional[str] = None

    # Valores por defecto de procesamiento
    default_export_scale: int = 90
    max_upload_size_mb: int = 50
    max_aoi_area_km2: float = 50000

    class Config:
        env_prefix = "RUSLE_"
        env_file = ".env"
```

## Rangos de Parámetros RUSLE

Rangos de validación para los factores RUSLE:

| Parámetro | Mín | Máx | Unidad |
|-----------|-----|-----|--------|
| Factor R | 0 | 20,000 | MJ·mm/ha/h/año |
| Factor K | 0 | 1 | t·ha·h/ha/MJ/mm |
| Factor LS | 0 | 100 | adimensional |
| Factor C | 0 | 1 | adimensional |
| Factor P | 0 | 1 | adimensional |

## Registro (Logging)

Configura el nivel de registro mediante `RUSLE_DEBUG`:

```python
import logging

# Cuando RUSLE_DEBUG=true
logging.basicConfig(level=logging.DEBUG)

# Cuando RUSLE_DEBUG=false (por defecto)
logging.basicConfig(level=logging.INFO)
```

## Configuración de Docker

En `docker-compose.yml`:

```yaml
environment:
  - RUSLE_GEE_PROJECT=${RUSLE_GEE_PROJECT:-ee-nriveras}
  - RUSLE_DEBUG=${RUSLE_DEBUG:-false}
  - RUSLE_MAX_UPLOAD_SIZE_MB=${RUSLE_MAX_UPLOAD_SIZE_MB:-50}
  - RUSLE_MAX_AOI_AREA_KM2=${RUSLE_MAX_AOI_AREA_KM2:-50000}
  - RUSLE_DEFAULT_EXPORT_SCALE=${RUSLE_DEFAULT_EXPORT_SCALE:-90}
```

## Autenticación con Cuenta de Servicio

Para despliegues en producción sin autenticación interactiva:

1. Crea una cuenta de servicio en Google Cloud Console
2. Habilita la API de Earth Engine para la cuenta de servicio
3. Descarga el archivo de clave JSON
4. Configura el entorno:

```bash
RUSLE_GEE_SERVICE_ACCOUNT=rusle@proyecto.iam.gserviceaccount.com
RUSLE_GEE_CREDENTIALS_PATH=/ruta/a/credenciales.json
```

!!! warning "Registro de Cuenta de Servicio"
    Las cuentas de servicio deben registrarse en Earth Engine en [signup.earthengine.google.com/#!/service_accounts](https://signup.earthengine.google.com/#!/service_accounts)
