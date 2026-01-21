# Web Application

The RUSLE web application provides an intuitive interface for soil erosion analysis without writing code.

## Starting the Application

```bash
# Production mode
python run.py

# Development mode (auto-reload)
python run.py --reload

# Custom host and port
python run.py --host 127.0.0.1 --port 3000
```

Access the application at **[http://localhost:8000/app](http://localhost:8000/app)**

## User Interface

### Main Dashboard

The application consists of three main sections:

1. **Input Panel** (left) - Configure analysis parameters
2. **Map View** (center) - Interactive visualization
3. **Results Panel** (right) - Statistics and export options

### Input Options

#### Area of Interest

Choose one of the following methods:

| Method | Description | Supported Formats |
|--------|-------------|-------------------|
| **File Upload** | Upload your own boundary | Shapefile (ZIP), GeoJSON |
| **Admin Region** | Select from FAO GAUL | Country, Region, District |

!!! tip "File Size Limit"
    Maximum upload size is **50 MB** by default. Adjust with `RUSLE_MAX_UPLOAD_SIZE_MB` environment variable.

#### Date Range

- **Start Date**: Beginning of analysis period
- **End Date**: End of analysis period (default: 1 year from start)

The date range affects the **R-factor** (rainfall erosivity) and **C-factor** (vegetation cover) calculations.

#### Export Settings

- **Scale**: Output resolution in meters (default: 90m)
- **Filename**: Custom name for exports

## Map Visualization

### Layer Controls

Toggle individual layers:

| Layer | Description |
|-------|-------------|
| **Soil Loss** | Final RUSLE result (A factor) |
| **R-Factor** | Rainfall erosivity |
| **K-Factor** | Soil erodibility |
| **LS-Factor** | Slope length and steepness |
| **C-Factor** | Vegetation cover |
| **P-Factor** | Conservation practices |

### Color Legend

Soil loss classification:

| Class | Range (t/ha/year) | Color |
|-------|-------------------|-------|
| Very Low | 0 - 5 | Green |
| Low | 5 - 10 | Yellow-Green |
| Moderate | 10 - 20 | Yellow |
| High | 20 - 50 | Orange |
| Very High | > 50 | Red |

## API Endpoints

The web application exposes a REST API:

### Upload File

```bash
POST /api/upload
Content-Type: multipart/form-data

curl -X POST -F "file=@region.zip" http://localhost:8000/api/upload
```

### Calculate RUSLE

```bash
POST /api/process
Content-Type: application/json

{
  "aoi_id": "uploaded-file-id",
  "date_from": "2023-01-01",
  "date_to": "2024-01-01",
  "scale": 90
}
```

### Get Results

```bash
GET /api/visualize/{job_id}
```

## Troubleshooting

### "GEE not initialized"

Ensure Google Earth Engine is properly authenticated:

```bash
earthengine authenticate
```

### Slow Processing

Large areas or fine resolutions can be slow. Try:

- Reducing the area of interest
- Increasing the scale (e.g., 250m instead of 90m)
- Checking your GEE quotas

### Map Not Loading

Check browser console for errors. Common causes:

- Ad blockers interfering with tile loading
- CORS issues with custom deployments
