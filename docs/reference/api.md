# API Reference

The RUSLE web application provides a REST API for programmatic access.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

Check if the application is running and GEE is initialized.

```http
GET /health
```

**Response**:

```json
{
  "status": "healthy",
  "gee_initialized": true,
  "version": "0.1.0"
}
```

---

### Upload File

Upload a shapefile or GeoJSON as the area of interest.

```http
POST /api/upload
Content-Type: multipart/form-data
```

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `file` | file | Shapefile (ZIP) or GeoJSON file |

**Example**:

```bash
curl -X POST \
  -F "file=@region.zip" \
  http://localhost:8000/api/upload
```

**Response**:

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

### Process RUSLE

Calculate RUSLE soil loss for a given area and time period.

```http
POST /api/process
Content-Type: application/json
```

**Request Body**:

```json
{
  "aoi_id": "abc123",
  "date_from": "2023-01-01",
  "date_to": "2024-01-01",
  "scale": 90,
  "export_to_drive": false
}
```

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `aoi_id` | string | Yes | ID from upload endpoint |
| `date_from` | string | Yes | Start date (YYYY-MM-DD) |
| `date_to` | string | Yes | End date (YYYY-MM-DD) |
| `scale` | integer | No | Resolution in meters (default: 90) |
| `export_to_drive` | boolean | No | Export results to Google Drive |

**Example**:

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

**Response**:

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

### Get Visualization

Retrieve the interactive map for a completed job.

```http
GET /api/visualize/{job_id}
```

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `job_id` | path | Job ID from process endpoint |

**Response**: HTML page with Folium map

---

### List Admin Regions

Get available administrative regions for selection.

```http
GET /api/regions
```

**Query Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `level` | integer | Admin level (0=country, 1=region, 2=district) |
| `parent` | string | Filter by parent region name |

**Example**:

```bash
curl "http://localhost:8000/api/regions?level=0"
```

**Response**:

```json
{
  "regions": [
    {"name": "Germany", "code": "DEU"},
    {"name": "France", "code": "FRA"},
    ...
  ]
}
```

---

## Error Handling

All errors return JSON with the following structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {}
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Invalid input parameters |
| `file_too_large` | 413 | Upload exceeds size limit |
| `aoi_too_large` | 400 | Area exceeds maximum |
| `gee_error` | 500 | Google Earth Engine error |
| `not_found` | 404 | Resource not found |

## Rate Limits

The API inherits Google Earth Engine's rate limits:

- ~100 concurrent requests per project
- Computation time limits vary by operation

For large batch processing, consider using the Python SDK directly.

## Python SDK Usage

For programmatic access, use the services directly:

```python
from app.services.gee_service import initialize_earth_engine
from app.services.rusle_calculator import RUSLECalculator, RUSLEInput

# Initialize
initialize_earth_engine("your-project-id")

# Configure input
rusle_input = RUSLEInput(
    aoi=ee.Geometry.Rectangle([...]),
    date_from="2023-01-01",
    date_to="2024-01-01",
    scale=90
)

# Calculate
calculator = RUSLECalculator(rusle_input)
result = calculator.calculate()
```
