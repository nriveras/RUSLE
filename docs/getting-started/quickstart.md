# Quick Start

Get up and running with RUSLE in minutes. This guide assumes you've completed the [installation](installation.md) steps.

## Run the Web Application

The fastest way to use RUSLE is through the web interface:

```bash
# Start the server
python run.py

# Or with auto-reload for development
python run.py --reload
```

Open your browser at **[http://localhost:8000/app](http://localhost:8000/app)**

## Using the Web Interface

### Step 1: Define Your Area of Interest

You have three options:

1. **Upload a File** - Upload a Shapefile (ZIP) or GeoJSON
2. **Select Administrative Region** - Choose from FAO GAUL boundaries
3. **Draw on Map** - Coming soon

### Step 2: Set Analysis Parameters

- **Date Range**: Select the time period for analysis
- **Export Scale**: Resolution in meters (default: 90m)

### Step 3: Run Analysis

Click **Calculate RUSLE** to start the analysis. The process will:

1. Fetch satellite data from Google Earth Engine
2. Calculate all RUSLE factors (R, K, L, S, C, P)
3. Generate the final soil loss map

### Step 4: Explore Results

The interactive map allows you to:

- Toggle individual RUSLE factor layers
- View the final soil loss classification
- Export results to Google Drive

## Using the Jupyter Notebook

For more control and customization:

1. Open VS Code and select the `.venv` Python interpreter
2. Open `00_scripts/RUSLE.ipynb`
3. Run the cells sequentially

The notebook provides:

- Step-by-step explanation of each RUSLE factor
- Interactive visualization with `geemap`
- Customizable parameters and thresholds

## Example Analysis

Here's a minimal Python example:

```python
import ee
from app.services.gee_service import initialize_earth_engine
from app.services.rusle_calculator import RUSLECalculator, RUSLEInput

# Initialize GEE
initialize_earth_engine("your-project-id")

# Define area of interest
aoi = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])

# Create input
rusle_input = RUSLEInput(
    aoi=aoi,
    date_from="2023-01-01",
    date_to="2024-01-01",
    scale=90
)

# Calculate
calculator = RUSLECalculator(rusle_input)
result = calculator.calculate()

print(f"Analysis complete: {result}")
```

## Next Steps

- [GEE Setup](gee-setup.md) - Configure Google Earth Engine
- [Web Application Guide](../user-guide/web-app.md) - Detailed web app documentation
- [RUSLE Model Reference](../reference/rusle-model.md) - Understand the science
