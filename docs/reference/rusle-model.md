# RUSLE Model Reference

This document describes the scientific background and implementation of the Revised Universal Soil Loss Equation (RUSLE) in this project.

## The RUSLE Equation

$$
A = R \times K \times L \times S \times C \times P
$$

Where **A** is the average annual soil loss in tonnes per hectare per year (t/ha/year).

## Factor Descriptions

### R-Factor: Rainfall Erosivity

**What it measures**: The erosive potential of rainfall based on intensity and duration.

**Data Source**: [CHIRPS Daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY) precipitation data.

**Calculation Method**:

The R-factor is calculated using the modified Fournier index:

$$
R = \sum_{i=1}^{12} \frac{p_i^2}{P}
$$

Where:

- $p_i$ = monthly precipitation (mm)
- $P$ = annual precipitation (mm)

**Implementation**:

```python
def calculate_r_factor(aoi, start_date, end_date):
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date) \
        .filterBounds(aoi)
    
    # Sum precipitation and apply erosivity model
    annual_precip = chirps.sum()
    r_factor = annual_precip.multiply(0.0483).add(0.6207)
    
    return r_factor.clip(aoi)
```

---

### K-Factor: Soil Erodibility

**What it measures**: The inherent susceptibility of soil to erosion based on texture, organic matter, structure, and permeability.

**Data Source**: [OpenLandMap Soil Texture](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02) datasets.

**Typical Values**:

| Soil Type | K-Factor |
|-----------|----------|
| Clay | 0.05 - 0.15 |
| Silty clay | 0.15 - 0.25 |
| Loam | 0.25 - 0.35 |
| Sandy loam | 0.10 - 0.20 |
| Sand | 0.02 - 0.10 |

**Implementation**:

The K-factor is derived from soil texture classes using lookup tables based on USDA soil surveys.

---

### LS-Factor: Slope Length and Steepness

**What it measures**: The combined effect of slope length (L) and slope steepness (S) on erosion.

**Data Source**: [SRTM Digital Elevation Model](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) (30m resolution).

**Calculation Method**:

$$
LS = \left(\frac{\lambda}{22.13}\right)^m \times (65.41 \sin^2\theta + 4.56 \sin\theta + 0.065)
$$

Where:

- $\lambda$ = slope length (m)
- $\theta$ = slope angle
- $m$ = slope length exponent (0.2-0.5 based on slope gradient)

**Implementation**:

```python
def calculate_ls_factor(aoi):
    dem = ee.Image("USGS/SRTMGL1_003").clip(aoi)
    slope = ee.Terrain.slope(dem)
    
    # Convert to radians and calculate LS
    slope_rad = slope.multiply(math.pi / 180)
    ls_factor = slope_rad.sin().pow(2).multiply(65.41) \
        .add(slope_rad.sin().multiply(4.56)) \
        .add(0.065)
    
    return ls_factor
```

---

### C-Factor: Cover Management

**What it measures**: The effect of vegetation cover and land management on reducing erosion.

**Data Source**: [MODIS NDVI](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13A2) (250m, 16-day composite).

**Calculation Method** (De Jong, 1994):

$$
C = e^{-\alpha \times \frac{NDVI}{\beta - NDVI}}
$$

Where:

- $\alpha$ = 2 (empirical constant)
- $\beta$ = 1 (empirical constant)
- NDVI = Normalized Difference Vegetation Index

**Typical Values**:

| Land Cover | C-Factor |
|------------|----------|
| Dense forest | 0.001 - 0.01 |
| Grassland | 0.01 - 0.10 |
| Cropland | 0.10 - 0.50 |
| Bare soil | 0.80 - 1.00 |

---

### P-Factor: Support Practice

**What it measures**: The effect of conservation practices (terracing, contour farming, etc.) on reducing erosion.

**Data Source**: [MODIS Land Cover](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1) (500m annual).

**Lookup Table** (Chuenchum et al., 2019):

| MODIS Class | Land Cover | P-Factor |
|-------------|------------|----------|
| 1-5 | Forests | 0.8 |
| 6-10 | Shrublands/Grasslands | 0.8 |
| 11 | Wetlands | 1.0 |
| 12 | Croplands | 0.5 |
| 13 | Urban | 1.0 |
| 14 | Cropland/Vegetation Mix | 0.5 |
| 15-17 | Snow/Barren/Water | 1.0 |

---

## Data Sources Summary

| Factor | Dataset | Resolution | Provider |
|--------|---------|------------|----------|
| R | CHIRPS Daily | 5.5 km | UCSB |
| K | OpenLandMap | 250 m | EnvirometriX |
| LS | SRTM DEM | 30 m | USGS |
| C | MODIS NDVI | 250 m | NASA |
| P | MODIS Land Cover | 500 m | NASA |

## References

1. **Renard et al. (1997)**: Predicting Soil Erosion by Water: A Guide to Conservation Planning with RUSLE.

2. **Williams (1995)**: SWAT Theory Documentation.

3. **Uddin et al. (2018)**: Assessment of land cover change and soil erosion in Nepal.

4. **De Jong (1994)**: Derivation of vegetative variables for soil erosion modeling.

5. **Chuenchum et al. (2019)**: Estimation of soil erosion and sediment yield in the Lancang–Mekong river.
