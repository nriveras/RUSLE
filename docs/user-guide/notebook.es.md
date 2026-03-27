# Jupyter Notebook

El Jupyter Notebook proporciona un entorno interactivo para el análisis RUSLE, ideal para investigación, experimentación y flujos de trabajo personalizados.

## Abrir el Notebook

1. **Activar el entorno**:
   ```bash
   source .venv/bin/activate
   ```

2. **Abrir en VS Code** o **Jupyter Lab**:
   ```bash
   # VS Code (recomendado)
   code 00_scripts/RUSLE.ipynb

   # O Jupyter Lab
   jupyter lab 00_scripts/RUSLE.ipynb
   ```

3. **Seleccionar el intérprete Python**: Elige `.venv` cuando se solicite

## Estructura del Notebook

El notebook `00_scripts/RUSLE.ipynb` está organizado de la siguiente manera:

### 1. Configuración y Autenticación

```python
import ee
from rusle_utils import initialize_gee

# Inicializar Google Earth Engine
initialize_gee("tu-id-de-proyecto")
```

### 2. Definir Área de Interés

```python
# Opción 1: Desde coordenadas
aoi = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])

# Opción 2: Desde GeoJSON
aoi = ee.Geometry(geojson_dict)

# Opción 3: Desde FAO GAUL
countries = ee.FeatureCollection("FAO/GAUL/2015/level0")
germany = countries.filter(ee.Filter.eq('ADM0_NAME', 'Germany'))
aoi = germany.geometry()
```

### 3. Calcular Factores RUSLE

Cada factor se calcula paso a paso:

```python
from rusle_utils import (
    calculate_r_factor,
    calculate_k_factor,
    calculate_ls_factor,
    calculate_c_factor,
    calculate_p_factor
)

# Factor R: Erosividad de la Lluvia
r_factor = calculate_r_factor(aoi, start_date, end_date)

# Factor K: Erodibilidad del Suelo
k_factor = calculate_k_factor(aoi)

# Factor LS: Longitud e Inclinación de Pendiente
ls_factor = calculate_ls_factor(aoi)

# Factor C: Gestión de Cobertura
c_factor = calculate_c_factor(aoi, start_date, end_date)

# Factor P: Prácticas de Conservación
p_factor = calculate_p_factor(aoi)
```

### 4. Calcular Pérdida de Suelo

```python
# Ecuación RUSLE: A = R × K × LS × C × P
soil_loss = r_factor.multiply(k_factor) \
    .multiply(ls_factor) \
    .multiply(c_factor) \
    .multiply(p_factor)
```

### 5. Visualización

```python
import geemap

# Crear mapa interactivo
Map = geemap.Map()
Map.centerObject(aoi, zoom=8)

# Agregar capas
Map.addLayer(soil_loss, {'min': 0, 'max': 50, 'palette': ['green', 'yellow', 'red']}, 'Pérdida de Suelo')
Map
```

## Funciones Utilitarias

El módulo `00_scripts/rusle_utils.py` proporciona funciones reutilizables:

| Función | Descripción |
|---------|-------------|
| `initialize_gee()` | Inicializar conexión con Earth Engine |
| `calculate_r_factor()` | Erosividad de la lluvia desde CHIRPS |
| `calculate_k_factor()` | Erodibilidad del suelo desde OpenLandMap |
| `calculate_ls_factor()` | Pendiente desde SRTM DEM |
| `calculate_c_factor()` | Vegetación desde MODIS NDVI |
| `calculate_p_factor()` | Cobertura terrestre desde MODIS |
| `export_to_drive()` | Exportar raster a Google Drive |

## Personalización

### Paletas de Visualización Personalizadas

```python
# Paleta de severidad de erosión
EROSION_PALETTE = ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000']

Map.addLayer(soil_loss, {
    'min': 0,
    'max': 100,
    'palette': EROSION_PALETTE
}, 'Pérdida de Suelo')
```

### Valores Personalizados del Factor P

Modifica el diccionario `P_FACTOR_VALUES` para diferentes escenarios de gestión del suelo:

```python
# Factores P personalizados para agricultura en terrazas
P_FACTOR_VALUES = {
    12: 0.3,  # Cultivos con terrazas
    14: 0.4,  # Mosaico cultivo/vegetación
    # ... otras clases
}
```

## Exportar Resultados

### A Google Drive

```python
from rusle_utils import export_to_drive

export_to_drive(
    image=soil_loss,
    description='RUSLE_Alemania_2023',
    folder='RUSLE_Exports',
    scale=90,
    region=aoi
)
```
