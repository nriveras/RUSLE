# Referencia del Modelo RUSLE

Este documento describe el trasfondo científico y la implementación de la Ecuación Universal de Pérdida de Suelo Revisada (RUSLE) en este proyecto.

## La Ecuación RUSLE

$$
A = R \times K \times L \times S \times C \times P
$$

Donde **A** es la pérdida media anual de suelo en toneladas por hectárea por año (t/ha/año).

## Descripción de los Factores

### Factor R: Erosividad de la Lluvia

**Qué mide**: El potencial erosivo de la lluvia basado en la intensidad y duración.

**Fuente de Datos**: Datos de precipitación [CHIRPS Daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY).

**Método de Cálculo**:

El Factor R se calcula usando el índice de Fournier modificado:

$$
R = \sum_{i=1}^{12} \frac{p_i^2}{P}
$$

Donde:

- $p_i$ = precipitación mensual (mm)
- $P$ = precipitación anual (mm)

**Implementación**:

```python
def calculate_r_factor(aoi, start_date, end_date):
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date) \
        .filterBounds(aoi)
    
    # Sumar precipitación y aplicar modelo de erosividad
    annual_precip = chirps.sum()
    r_factor = annual_precip.multiply(0.0483).add(0.6207)
    
    return r_factor.clip(aoi)
```

---

### Factor K: Erodibilidad del Suelo

**Qué mide**: La susceptibilidad inherente del suelo a la erosión basada en textura, materia orgánica, estructura y permeabilidad.

**Fuente de Datos**: Conjuntos de datos de [Textura del Suelo OpenLandMap](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02).

**Valores Típicos**:

| Tipo de Suelo | Factor K |
|---------------|----------|
| Arcilla | 0.05 - 0.15 |
| Arcilla limosa | 0.15 - 0.25 |
| Franco | 0.25 - 0.35 |
| Franco arenoso | 0.10 - 0.20 |
| Arena | 0.02 - 0.10 |

**Implementación**:

El Factor K se deriva de las clases de textura del suelo usando tablas de referencia basadas en encuestas de suelo USDA.

---

### Factor LS: Longitud e Inclinación de Pendiente

**Qué mide**: El efecto combinado de la longitud de pendiente (L) y la inclinación de pendiente (S) sobre la erosión.

**Fuente de Datos**: [Modelo Digital de Elevación SRTM](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) (resolución de 30m).

**Método de Cálculo**:

$$
LS = \left(\frac{\lambda}{22.13}\right)^m \times (65.41 \sin^2\theta + 4.56 \sin\theta + 0.065)
$$

Donde:

- $\lambda$ = longitud de pendiente (m)
- $\theta$ = ángulo de pendiente
- $m$ = exponente de longitud de pendiente (0.2-0.5 según gradiente de pendiente)

**Implementación**:

```python
def calculate_ls_factor(aoi):
    dem = ee.Image("USGS/SRTMGL1_003").clip(aoi)
    slope = ee.Terrain.slope(dem)
    
    # Convertir a radianes y calcular LS
    slope_rad = slope.multiply(math.pi / 180)
    ls_factor = slope_rad.sin().pow(2).multiply(65.41) \
        .add(slope_rad.sin().multiply(4.56)) \
        .add(0.065)
    
    return ls_factor
```

---

### Factor C: Gestión de Cobertura

**Qué mide**: El efecto de la cobertura vegetal y la gestión del suelo en la reducción de la erosión.

**Fuente de Datos**: [MODIS NDVI](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13A2) (250m, compuesto de 16 días).

**Método de Cálculo** (De Jong, 1994):

$$
C = e^{-\alpha \times \frac{NDVI}{\beta - NDVI}}
$$

Donde:

- $\alpha$ = 2 (constante empírica)
- $\beta$ = 1 (constante empírica)
- NDVI = Índice de Vegetación de Diferencia Normalizada

**Valores Típicos**:

| Cobertura Terrestre | Factor C |
|--------------------|----------|
| Bosque denso | 0.001 - 0.01 |
| Pastizal | 0.01 - 0.10 |
| Cultivos | 0.10 - 0.50 |
| Suelo desnudo | 0.80 - 1.00 |

---

### Factor P: Práctica de Apoyo

**Qué mide**: El efecto de las prácticas de conservación (terrazas, cultivo en contorno, etc.) en la reducción de la erosión.

**Fuente de Datos**: [Cobertura Terrestre MODIS](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1) (500m anual).

**Tabla de Referencia** (Chuenchum et al., 2019):

| Clase MODIS | Cobertura Terrestre | Factor P |
|-------------|---------------------|----------|
| 1-5 | Bosques | 0.8 |
| 6-10 | Arbustales/Pastizales | 0.8 |
| 11 | Humedales | 1.0 |
| 12 | Cultivos | 0.5 |
| 13 | Urbano | 1.0 |
| 14 | Mosaico Cultivo/Vegetación | 0.5 |
| 15-17 | Nieve/Estéril/Agua | 1.0 |

---

## Resumen de Fuentes de Datos

| Factor | Conjunto de Datos | Resolución | Proveedor |
|--------|-------------------|------------|-----------|
| R | CHIRPS Daily | 5.5 km | UCSB |
| K | OpenLandMap | 250 m | EnvirometriX |
| LS | SRTM DEM | 30 m | USGS |
| C | MODIS NDVI | 250 m | NASA |
| P | Cobertura MODIS | 500 m | NASA |

## Referencias

1. **Renard et al. (1997)**: Predicting Soil Erosion by Water: A Guide to Conservation Planning with RUSLE.

2. **Williams (1995)**: SWAT Theory Documentation.

3. **Uddin et al. (2018)**: Assessment of land cover change and soil erosion in Nepal.

4. **De Jong (1994)**: Derivation of vegetative variables for soil erosion modeling.

5. **Chuenchum et al. (2019)**: Estimation of soil erosion and sediment yield in the Lancang–Mekong river.
