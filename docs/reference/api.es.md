# Referencia de la API

La aplicación web RUSLE proporciona una API REST para acceso programático.

## URL Base

```
http://localhost:8000
```

## Endpoints

### Verificación de Salud

Verifica si la aplicación está en ejecución y GEE está inicializado.

```http
GET /health
```

**Respuesta**:

```json
{
  "status": "healthy",
  "gee_initialized": true,
  "version": "0.1.0"
}
```

---

### Subir Archivo

Sube un shapefile o GeoJSON como área de interés.

```http
POST /api/upload
Content-Type: multipart/form-data
```

**Parámetros**:

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| `file` | archivo | Shapefile (ZIP) o archivo GeoJSON |

**Ejemplo**:

```bash
curl -X POST \
  -F "file=@region.zip" \
  http://localhost:8000/api/upload
```

**Respuesta**:

```json
{
  "file_id": "abc123",
  "filename": "region.zip",
  "geometry_type": "Polygon",
  "area_km2": 15234.5,
  "bounds": [-122.5, 37.5, -122.0, 38.0]
}
```

---

### Procesar RUSLE

Calcula la pérdida de suelo RUSLE para un área y período de tiempo dados.

```http
POST /api/process
Content-Type: application/json
```

**Cuerpo de la Solicitud**:

```json
{
  "aoi_id": "abc123",
  "date_from": "2023-01-01",
  "date_to": "2024-01-01",
  "scale": 90,
  "export_to_drive": false
}
```

**Parámetros**:

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `aoi_id` | string | Sí | ID del endpoint de carga |
| `date_from` | string | Sí | Fecha de inicio (YYYY-MM-DD) |
| `date_to` | string | Sí | Fecha de fin (YYYY-MM-DD) |
| `scale` | integer | No | Resolución en metros (por defecto: 90) |
| `export_to_drive` | boolean | No | Exportar resultados a Google Drive |

**Ejemplo**:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "aoi_id": "abc123",
    "date_from": "2023-01-01",
    "date_to": "2024-01-01"
  }' \
  http://localhost:8000/api/process
```

**Respuesta**:

```json
{
  "job_id": "job_456",
  "status": "completed",
  "statistics": {
    "mean_soil_loss": 12.5,
    "max_soil_loss": 156.3,
    "min_soil_loss": 0.1,
    "area_km2": 15234.5
  },
  "map_url": "/api/visualize/job_456"
}
```

---

### Obtener Visualización

Recupera el mapa interactivo para un trabajo completado.

```http
GET /api/visualize/{job_id}
```

**Parámetros**:

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| `job_id` | ruta | ID del trabajo del endpoint de proceso |

**Respuesta**: Página HTML con mapa Folium

---

### Listar Regiones Administrativas

Obtiene las regiones administrativas disponibles para selección.

```http
GET /api/regions
```

**Parámetros de Consulta**:

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| `level` | integer | Nivel administrativo (0=país, 1=región, 2=distrito) |
| `parent` | string | Filtrar por nombre de región padre |

**Ejemplo**:

```bash
curl "http://localhost:8000/api/regions?level=0"
```

**Respuesta**:

```json
{
  "regions": [
    {"name": "Alemania", "code": "DEU"},
    {"name": "Francia", "code": "FRA"},
    ...
  ]
}
```

---

## Manejo de Errores

Todos los errores retornan JSON con la siguiente estructura:

```json
{
  "error": "codigo_de_error",
  "message": "Mensaje de error legible por humanos",
  "details": {}
}
```

### Códigos de Error Comunes

| Código | Estado HTTP | Descripción |
|--------|-------------|-------------|
| `validation_error` | 400 | Parámetros de entrada inválidos |
| `file_too_large` | 413 | La carga excede el límite de tamaño |
| `aoi_too_large` | 400 | El área excede el máximo |
| `gee_error` | 500 | Error de Google Earth Engine |
| `not_found` | 404 | Recurso no encontrado |

## Límites de Velocidad

La API hereda los límites de velocidad de Google Earth Engine:

- ~100 solicitudes concurrentes por proyecto
- Los límites de tiempo de cómputo varían según la operación

Para procesamiento por lotes grande, considera usar el SDK de Python directamente.

## Uso del SDK de Python

Para acceso programático, usa los servicios directamente:

```python
from app.services.gee_service import initialize_earth_engine
from app.services.rusle_calculator import RUSLECalculator, RUSLEInput

# Inicializar
initialize_earth_engine("tu-id-de-proyecto")

# Configurar entrada
rusle_input = RUSLEInput(
    aoi=ee.Geometry.Rectangle([...]),
    date_from="2023-01-01",
    date_to="2024-01-01",
    scale=90
)

# Calcular
calculator = RUSLECalculator(rusle_input)
result = calculator.calculate()
```
