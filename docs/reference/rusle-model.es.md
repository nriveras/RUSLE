# Referencia del Modelo RUSLE

Este documento describe el trasfondo científico y la implementación de la Ecuación Universal de Pérdida de Suelo Revisada (RUSLE) en este proyecto.

## La Ecuación RUSLE

$$
A = R \times K \times L \times S \times C \times P
$$

Donde **A** es la pérdida media anual de suelo en toneladas métricas por hectárea por año (t/ha/año, donde t = Mg = 1.000 kg).

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

**Qué mide**: La susceptibilidad inherente del suelo a la erosión basada en textura y contenido de materia orgánica.

**Fuente de Datos**: Contenido de [carbono orgánico](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_ORGANIC-CARBON_USDA-6A1C_M_v02), [arcilla](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_CLAY-WFRACTION_USDA-3A1A1A_M_v02) y [arena](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_SAND-WFRACTION_USDA-3A1A1A_M_v02) de OpenLandMap; el limo es el resto (100 - arcilla - arena).

**Método de Cálculo** (Sharpley & Williams, 1990; usado en el modelo EPIC de Williams, 1995):

$$
K_{USLE} = f_{csand} \cdot f_{cl\text{-}si} \cdot f_{orgc} \cdot f_{hisand}
$$

$$
f_{csand} = 0.2 + 0.3 \cdot e^{-0.0256 \cdot m_s \cdot (1 - m_{silt}/100)}
$$

$$
f_{cl\text{-}si} = \left(\frac{m_{silt}}{m_c + m_{silt}}\right)^{0.3}
$$

$$
f_{orgc} = 1 - \frac{0.25 \cdot orgC}{orgC + e^{3.72 - 2.95 \cdot orgC}}
$$

$$
f_{hisand} = 1 - \frac{0.7 \cdot (1 - m_s/100)}{(1 - m_s/100) + e^{-5.51 + 22.9 \cdot (1 - m_s/100)}}
$$

Donde $m_s$, $m_{silt}$, $m_c$ son los porcentajes de arena, limo y arcilla, y $orgC$ es el porcentaje de carbono orgánico.

$K_{USLE}$ resulta en unidades consuetudinarias estadounidenses (short ton·ac·h/(100 ft·short ton·ac·in)). La implementación lo multiplica por **0.1317** (Foster et al., 1981) para convertirlo a la unidad SI usada en todo el proyecto, t·ha·h/(ha·MJ·mm). También convierte la banda de carbono orgánico de OpenLandMap, almacenada como "×5 g/kg", a porcentaje (×0.5) antes de usarla en $f_{orgc}$.

**Valores Típicos** (unidades SI, t·ha·h/(ha·MJ·mm)):

| Tipo de Suelo | Factor K |
|---------------|----------|
| Arcilla | 0.05 - 0.15 |
| Arcilla limosa | 0.15 - 0.25 |
| Franco | 0.25 - 0.35 |
| Franco arenoso | 0.10 - 0.20 |
| Arena | 0.02 - 0.10 |

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

3. **Sharpley & Williams (1990)**: EPIC - Erosion/Productivity Impact Calculator: 1. Model Documentation. USDA Technical Bulletin No. 1768.

4. **Foster et al. (1981)**: Sediment composition for nonpoint source pollution analyses. Transactions of the ASAE, 24(5), 1444-1448.

5. **Uddin et al. (2018)**: Assessment of land cover change and soil erosion in Nepal.

6. **De Jong (1994)**: Derivation of vegetative variables for soil erosion modeling.

7. **Chuenchum et al. (2019)**: Estimation of soil erosion and sediment yield in the Lancang–Mekong river.
