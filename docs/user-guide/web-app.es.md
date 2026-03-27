# Aplicación Web

La aplicación web RUSLE proporciona una interfaz intuitiva para el análisis de erosión del suelo sin necesidad de escribir código.

## Iniciar la Aplicación

```bash
# Modo producción
python run.py

# Modo desarrollo (recarga automática)
python run.py --reload

# Host y puerto personalizados
python run.py --host 127.0.0.1 --port 3000
```

Accede a la aplicación en **[http://localhost:8000/app](http://localhost:8000/app)**

## Interfaz de Usuario

### Panel Principal

La aplicación consta de tres secciones principales:

1. **Panel de Entrada** (izquierda) - Configura los parámetros del análisis
2. **Vista del Mapa** (centro) - Visualización interactiva
3. **Panel de Resultados** (derecha) - Estadísticas y opciones de exportación

### Opciones de Entrada

#### Área de Interés

Elige uno de los siguientes métodos:

| Método | Descripción | Formatos Soportados |
|--------|-------------|---------------------|
| **Subir Archivo** | Sube tu propio límite | Shapefile (ZIP), GeoJSON |
| **Región Admin** | Selecciona de FAO GAUL | País, Región, Distrito |

!!! tip "Límite de Tamaño de Archivo"
    El tamaño máximo de carga es **50 MB** por defecto. Ajusta con la variable de entorno `RUSLE_MAX_UPLOAD_SIZE_MB`.

#### Rango de Fechas

- **Fecha de Inicio**: Comienzo del período de análisis
- **Fecha de Fin**: Fin del período de análisis (por defecto: 1 año desde el inicio)

El rango de fechas afecta los cálculos del **Factor R** (erosividad de la lluvia) y **Factor C** (cobertura vegetal).

#### Configuración de Exportación

- **Escala**: Resolución de salida en metros (por defecto: 90m)
- **Nombre del Archivo**: Nombre personalizado para las exportaciones

## Visualización del Mapa

### Controles de Capas

Activa/desactiva capas individuales:

| Capa | Descripción |
|------|-------------|
| **Pérdida de Suelo** | Resultado final RUSLE (factor A) |
| **Factor R** | Erosividad de la lluvia |
| **Factor K** | Erodibilidad del suelo |
| **Factor LS** | Longitud e inclinación de pendiente |
| **Factor C** | Cobertura vegetal |
| **Factor P** | Prácticas de conservación |

### Leyenda de Colores

Clasificación de pérdida de suelo:

| Clase | Rango (t/ha/año) | Color |
|-------|------------------|-------|
| Muy Baja | 0 - 5 | Verde |
| Baja | 5 - 10 | Verde-Amarillo |
| Moderada | 10 - 20 | Amarillo |
| Alta | 20 - 50 | Naranja |
| Muy Alta | > 50 | Rojo |

## Endpoints de la API

La aplicación web expone una API REST:

### Subir Archivo

```bash
POST /api/upload
Content-Type: multipart/form-data

curl -X POST -F "file=@region.zip" http://localhost:8000/api/upload
```

### Calcular RUSLE

```bash
POST /api/process
Content-Type: application/json

{
  "aoi_id": "id-del-archivo-subido",
  "date_from": "2023-01-01",
  "date_to": "2024-01-01",
  "scale": 90
}
```

### Obtener Resultados

```bash
GET /api/visualize/{job_id}
```

## Solución de Problemas

### "GEE not initialized"

Asegúrate de que Google Earth Engine esté correctamente autenticado:

```bash
earthengine authenticate
```

### Procesamiento Lento

Áreas grandes o resoluciones finas pueden ser lentas. Intenta:

- Reducir el área de interés
- Aumentar la escala (ej. 250m en lugar de 90m)
- Verificar tus cuotas de GEE

### Mapa No Carga

Revisa la consola del navegador para ver errores. Causas comunes:

- Bloqueadores de anuncios interfiriendo con la carga de tiles
- Problemas de CORS con despliegues personalizados
