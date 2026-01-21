# Jupyter Notebook

The Jupyter notebook provides an interactive environment for RUSLE analysis, ideal for research, experimentation, and custom workflows.

## Opening the Notebook

1. **Activate the environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Open in VS Code** or **Jupyter Lab**:
   ```bash
   # VS Code (recommended)
   code 00_scripts/RUSLE.ipynb

   # Or Jupyter Lab
   jupyter lab 00_scripts/RUSLE.ipynb
   ```

3. **Select the Python interpreter**: Choose `.venv` when prompted

## Notebook Structure

The notebook `00_scripts/RUSLE.ipynb` is organized as follows:

### 1. Setup & Authentication

```python
import ee
from rusle_utils import initialize_gee

# Initialize Google Earth Engine
initialize_gee("your-project-id")
```

### 2. Define Area of Interest

```python
# Option 1: From coordinates
aoi = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])

# Option 2: From GeoJSON
aoi = ee.Geometry(geojson_dict)

# Option 3: From FAO GAUL
countries = ee.FeatureCollection("FAO/GAUL/2015/level0")
germany = countries.filter(ee.Filter.eq('ADM0_NAME', 'Germany'))
aoi = germany.geometry()
```

### 3. Calculate RUSLE Factors

Each factor is calculated step by step:

```python
from rusle_utils import (
    calculate_r_factor,
    calculate_k_factor,
    calculate_ls_factor,
    calculate_c_factor,
    calculate_p_factor
)

# R-Factor: Rainfall Erosivity
r_factor = calculate_r_factor(aoi, start_date, end_date)

# K-Factor: Soil Erodibility
k_factor = calculate_k_factor(aoi)

# LS-Factor: Slope Length & Steepness
ls_factor = calculate_ls_factor(aoi)

# C-Factor: Cover Management
c_factor = calculate_c_factor(aoi, start_date, end_date)

# P-Factor: Conservation Practices
p_factor = calculate_p_factor(aoi)
```

### 4. Calculate Soil Loss

```python
# RUSLE Equation: A = R × K × LS × C × P
soil_loss = r_factor.multiply(k_factor) \
    .multiply(ls_factor) \
    .multiply(c_factor) \
    .multiply(p_factor)
```

### 5. Visualization

```python
import geemap

# Create interactive map
Map = geemap.Map()
Map.centerObject(aoi, zoom=8)

# Add layers
Map.addLayer(soil_loss, {'min': 0, 'max': 50, 'palette': ['green', 'yellow', 'red']}, 'Soil Loss')
Map
```

## Utility Functions

The `00_scripts/rusle_utils.py` module provides reusable functions:

| Function | Description |
|----------|-------------|
| `initialize_gee()` | Initialize Earth Engine connection |
| `calculate_r_factor()` | Rainfall erosivity from CHIRPS |
| `calculate_k_factor()` | Soil erodibility from OpenLandMap |
| `calculate_ls_factor()` | Slope from SRTM DEM |
| `calculate_c_factor()` | Vegetation from MODIS NDVI |
| `calculate_p_factor()` | Land cover from MODIS |
| `export_to_drive()` | Export raster to Google Drive |

## Customization

### Custom Visualization Palettes

```python
# Erosion severity palette
EROSION_PALETTE = ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000']

Map.addLayer(soil_loss, {
    'min': 0,
    'max': 100,
    'palette': EROSION_PALETTE
}, 'Soil Loss')
```

### Custom P-Factor Values

Modify the `P_FACTOR_VALUES` dictionary for different land management scenarios:

```python
# Custom P-factors for terraced agriculture
P_FACTOR_VALUES = {
    12: 0.3,  # Croplands with terracing
    14: 0.4,  # Cropland/vegetation mosaic
    # ... other classes
}
```

## Exporting Results

### To Google Drive

```python
from rusle_utils import export_to_drive

export_to_drive(
    image=soil_loss,
    description='RUSLE_Germany_2023',
    folder='RUSLE_Exports',
    scale=90,
    region=aoi
)
```

### To Local GeoTIFF

```python
import geemap

geemap.ee_export_image(
    soil_loss,
    filename='soil_loss.tif',
    scale=90,
    region=aoi.bounds().getInfo()['coordinates']
)
```

## Tips

!!! tip "Memory Management"
    For large areas, use `bestEffort=True` in reducers to avoid timeout errors.

!!! tip "Debugging"
    Use `.getInfo()` sparingly - it fetches data from GEE servers and can be slow.

!!! tip "Reproducibility"
    Always specify exact date ranges for consistent results across runs.
