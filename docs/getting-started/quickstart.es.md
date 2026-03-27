# Inicio Rápido

Empieza a usar RUSLE en minutos. Esta guía asume que has completado los pasos de [instalación](installation.md).

## Ejecutar la Aplicación Web

La forma más rápida de usar RUSLE es a través de la interfaz web:

```bash
# Iniciar el servidor
python run.py

# O con recarga automática para desarrollo
python run.py --reload
```

Abre tu navegador en **[http://localhost:8000/app](http://localhost:8000/app)**

## Usar la Interfaz Web

### Paso 1: Definir tu Área de Interés

Tienes tres opciones:

1. **Subir un Archivo** - Sube un Shapefile (ZIP) o GeoJSON
2. **Seleccionar Región Administrativa** - Elige de los límites FAO GAUL
3. **Dibujar en el Mapa** - Próximamente

### Paso 2: Configurar los Parámetros de Análisis

- **Rango de Fechas**: Selecciona el período de tiempo para el análisis
- **Escala de Exportación**: Resolución en metros (por defecto: 90m)

### Paso 3: Ejecutar el Análisis

Haz clic en **Calcular RUSLE** para iniciar el análisis. El proceso:

1. Descargará datos satelitales de Google Earth Engine
2. Calculará todos los factores RUSLE (R, K, L, S, C, P)
3. Generará el mapa final de pérdida de suelo

### Paso 4: Explorar los Resultados

El mapa interactivo te permite:

- Activar/desactivar capas de factores RUSLE individuales
- Ver la clasificación final de pérdida de suelo
- Exportar resultados a Google Drive

## Usar el Jupyter Notebook

Para mayor control y personalización:

1. Abre VS Code y selecciona el intérprete Python `.venv`
2. Abre `00_scripts/RUSLE.ipynb`
3. Ejecuta las celdas secuencialmente

El notebook ofrece:

- Explicación paso a paso de cada factor RUSLE
- Visualización interactiva con `geemap`
- Parámetros y umbrales personalizables

## Ejemplo de Análisis

Aquí hay un ejemplo mínimo en Python:

```python
import ee
from app.services.gee_service import initialize_earth_engine
from app.services.rusle_calculator import RUSLECalculator, RUSLEInput

# Inicializar GEE
initialize_earth_engine("tu-id-de-proyecto")

# Definir área de interés
aoi = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])

# Crear entrada
rusle_input = RUSLEInput(
    aoi=aoi,
    date_from="2023-01-01",
    date_to="2024-01-01",
    scale=90
)

# Calcular
calculator = RUSLECalculator(rusle_input)
result = calculator.calculate()

print(f"Análisis completo: {result}")
```

## Próximos Pasos

- [Configuración de GEE](gee-setup.md) - Configurar Google Earth Engine
- [Guía de la Aplicación Web](../user-guide/web-app.md) - Documentación detallada de la app web
- [Referencia del Modelo RUSLE](../reference/rusle-model.md) - Entender la ciencia
