"""
RUSLE (Revised Universal Soil Loss Equation) Utility Functions.

This module provides functions for calculating soil erosion using the RUSLE model
with Google Earth Engine. Based on code by Lucas Rivero Iribarne.

References:
    - Williams (1995): SWAT Theory Documentation
    - Uddin et al. (2018): Assessment of land cover change and soil erosion
    - De Jong (1994): Derivation of vegetative variables for soil erosion modeling
    - Chuenchum et al. (2019): Estimation of soil erosion and sediment yield
"""

import math
from typing import Dict, Optional, Tuple

import ee
import geemap

# Import authentication helper
from gee_auth import initialize_gee, print_auth_status, setup_project


# =============================================================================
# Configuration Constants
# =============================================================================

# Default visualization palettes
DEFAULT_PALETTE = ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000']
SLOPE_PALETTE = ['green', 'yellow', 'red']

# P-Factor values by land cover class (Chuenchum et al., 2019)
P_FACTOR_VALUES = {
    1: 0.8,   # Evergreen Needleleaf Forests
    2: 0.8,   # Evergreen Broadleaf Forests
    3: 0.8,   # Deciduous Needleleaf Forests
    4: 0.8,   # Deciduous Broadleaf Forests
    5: 0.8,   # Mixed Forests
    6: 0.8,   # Closed Shrublands
    7: 0.8,   # Open Shrublands
    8: 0.8,   # Woody Savannas
    9: 0.8,   # Savannas
    10: 0.8,  # Grasslands
    11: 1.0,  # Permanent Wetlands
    12: 0.5,  # Croplands
    13: 1.0,  # Urban and Built-up Lands
    14: 0.5,  # Cropland/Natural Vegetation Mosaics
    15: 1.0,  # Permanent Snow and Ice
    16: 1.0,  # Barren
    17: 1.0,  # Water Bodies
}


# =============================================================================
# Data Loading Functions
# =============================================================================

def load_area_of_interest(
    admin_name: str,
    admin_level: int = 1
) -> ee.FeatureCollection:
    """
    Load area of interest from FAO GAUL administrative boundaries.

    Args:
        admin_name: Name of the administrative region.
        admin_level: Administrative level (1 for provinces/states).

    Returns:
        ee.FeatureCollection: Area of interest feature collection.
    """
    collection_id = f"FAO/GAUL/2015/level{admin_level}"
    return (
        ee.FeatureCollection(collection_id)
        .filter(ee.Filter.eq(f'ADM{admin_level}_NAME', admin_name))
    )


def load_precipitation_data(
    aoi: ee.FeatureCollection
) -> ee.ImageCollection:
    """
    Load CHIRPS precipitation data for the area of interest.

    Args:
        aoi: Area of interest as ee.FeatureCollection.

    Returns:
        ee.ImageCollection: CHIRPS precipitation image collection.
    """
    return (
        ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
        .filter(ee.Filter.bounds(aoi))
    )


def load_soil_data(
    aoi: ee.FeatureCollection
) -> Tuple[ee.Image, ee.Image, ee.Image, ee.Image]:
    """
    Load OpenLandMap soil data (organic carbon, clay, sand, silt).

    Args:
        aoi: Area of interest as ee.FeatureCollection.

    Returns:
        Tuple containing:
            - c_org: Organic carbon image
            - clay: Clay content image
            - sand: Sand content image
            - silt: Silt content image (calculated)
    """
    # Surface layer (b0) data
    c_org = (
        ee.Image('OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02')
        .select('b0')
        .clip(aoi)
    )
    clay = (
        ee.Image('OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02')
        .select('b0')
        .clip(aoi)
    )
    sand = (
        ee.Image('OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02')
        .select('b0')
        .clip(aoi)
    )
    # Silt calculated as remainder
    silt = ee.Image(100).subtract(clay).subtract(sand).rename('silt')

    return c_org, clay, sand, silt


def load_dem(dem_source: str = 'SRTM') -> ee.Image:
    """
    Load Digital Elevation Model.

    Args:
        dem_source: DEM source ('SRTM' or 'MERIT').

    Returns:
        ee.Image: Digital elevation model.
    """
    sources = {
        'SRTM': 'USGS/SRTMGL1_003',
        'MERIT': 'MERIT/DEM/v1_0_3'
    }
    return ee.Image(sources.get(dem_source, sources['SRTM']))


def load_landsat8() -> ee.ImageCollection:
    """
    Load and preprocess Landsat 8 Surface Reflectance data.

    Returns:
        ee.ImageCollection: Preprocessed Landsat 8 collection.
    """
    def apply_scale_factors(image: ee.Image) -> ee.Image:
        """Apply scaling factors to optical bands."""
        optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
        return image.addBands(optical_bands, None, True)

    return (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .map(apply_scale_factors)
    )


def load_modis_landcover(aoi: ee.FeatureCollection) -> ee.Image:
    """
    Load most recent MODIS land cover data.

    Args:
        aoi: Area of interest as ee.FeatureCollection.

    Returns:
        ee.Image: MODIS land cover image.
    """
    return (
        ee.ImageCollection('MODIS/006/MCD12Q1')
        .select('LC_Type1')
        .sort('system:time_start', False)
        .first()
        .clip(aoi.geometry())
    )


# =============================================================================
# RUSLE Factor Calculation Functions
# =============================================================================

def calculate_k_factor(
    sand: ee.Image,
    silt: ee.Image,
    clay: ee.Image,
    c_org: ee.Image
) -> ee.Image:
    """
    Calculate soil erodibility factor (K) using Williams (1995) method.

    K = f_csand * f_cl_si * f_orgc * f_hisand

    Args:
        sand: Sand content percentage image.
        silt: Silt content percentage image.
        clay: Clay content percentage image.
        c_org: Organic carbon percentage image.

    Returns:
        ee.Image: K factor image.
    """
    # f_csand: Factor for coarse sand content
    f_csand = (
        ee.Image(0.2)
        .add(
            ee.Image(0.3)
            .multiply(
                ee.Image(-0.256)
                .multiply(silt.divide(100).subtract(1))
                .exp()
            )
        )
        .rename('f_csand')
    )

    # f_cl_si: Clay-silt ratio factor
    f_cl_si = (
        silt.divide(clay.add(silt))
        .pow(0.3)
        .rename('f_cl_si')
    )

    # f_orgc: Organic carbon factor
    f_orgc = (
        ee.Image(1)
        .subtract(
            ee.Image(0.25)
            .multiply(c_org)
            .divide(
                c_org.add(
                    ee.Image(3.72)
                    .subtract(ee.Image(2.95).multiply(c_org))
                    .exp()
                )
            )
        )
        .rename('f_orgc')
    )

    # f_hisand: High sand content factor
    sand_fraction = ee.Image(1).subtract(sand.divide(100))
    f_hisand = (
        ee.Image(1)
        .subtract(
            ee.Image(0.7)
            .multiply(sand_fraction)
            .divide(
                sand_fraction.add(
                    ee.Image(-5.51)
                    .add(ee.Image(22.9).multiply(sand_fraction))
                    .exp()
                )
            )
        )
        .rename('f_hisand')
    )

    # Combine all factors
    k_factor = (
        f_csand
        .multiply(f_cl_si)
        .multiply(f_orgc)
        .multiply(f_hisand)
        .rename('K_factor')
    )

    return k_factor


def calculate_r_factor(
    precipitation: ee.ImageCollection,
    date_from: str,
    date_to: str,
    aoi: ee.FeatureCollection
) -> ee.Image:
    """
    Calculate rainfall erosivity factor (R).

    R = 0.0483 * P^1.610

    Args:
        precipitation: Precipitation image collection.
        date_from: Start date (YYYY-MM-DD).
        date_to: End date (YYYY-MM-DD).
        aoi: Area of interest.

    Returns:
        ee.Image: R factor image.
    """
    # Sum precipitation over the period
    pcp_sum = (
        precipitation
        .select('precipitation')
        .filterDate(date_from, date_to)
        .sum()
        .clip(aoi)
    )

    # Calculate R factor
    r_factor = (
        pcp_sum
        .pow(1.610)
        .multiply(0.0483)
        .rename('R_factor')
    )

    return r_factor


def calculate_slope_metrics(
    dem: ee.Image,
    aoi: ee.FeatureCollection
) -> Tuple[ee.Image, ee.Image]:
    """
    Calculate slope in degrees and percentage.

    Args:
        dem: Digital elevation model.
        aoi: Area of interest.

    Returns:
        Tuple containing:
            - slope_deg: Slope in degrees
            - slope_perc: Slope in percentage
    """
    elev = dem.select('elevation')
    slope_deg = ee.Terrain.slope(elev).clip(aoi)

    # Convert degrees to percentage: tan(radians) * 100
    slope_perc = (
        slope_deg
        .divide(180)
        .multiply(math.pi)
        .tan()
        .multiply(100)
    )

    return slope_deg, slope_perc


def calculate_l_factor(
    slope_perc: ee.Image,
    pixel_size: float = 30.0
) -> ee.Image:
    """
    Calculate slope length factor (L).

    L = (λ / 22.13)^m

    Args:
        slope_perc: Slope in percentage.
        pixel_size: Pixel size in meters (default 30m for Landsat).

    Returns:
        ee.Image: L factor image.
    """
    # Calculate m exponent based on slope
    m_exponent = (
        ee.Image(1)
        .where(slope_perc.gt(-1).And(slope_perc.lte(1)), 0.2)
        .where(slope_perc.gt(1).And(slope_perc.lte(3)), 0.3)
        .where(slope_perc.gt(3).And(slope_perc.lte(4.5)), 0.4)
        .where(slope_perc.gt(4.5).And(slope_perc.lte(100)), 0.5)
    )

    # Create constant raster for pixel size
    lambda_raster = slope_perc.multiply(0).add(pixel_size)

    # Calculate L factor
    l_factor = (
        lambda_raster
        .divide(22.13)
        .pow(m_exponent)
        .rename('L_factor')
    )

    return l_factor


def calculate_s_factor(slope_perc: ee.Image) -> ee.Image:
    """
    Calculate slope steepness factor (S).

    S = (0.43 + 0.3 * slope + 0.043 * slope^2) / 6.613

    Args:
        slope_perc: Slope in percentage.

    Returns:
        ee.Image: S factor image.
    """
    s_factor = (
        slope_perc.pow(2).multiply(0.043)
        .add(slope_perc.multiply(0.30))
        .add(0.43)
        .divide(6.613)
        .rename('S_factor')
    )

    return s_factor


def calculate_c_factor(
    landsat: ee.ImageCollection,
    date_from: str,
    date_to: str,
    aoi: ee.FeatureCollection
) -> ee.Image:
    """
    Calculate vegetation cover factor (C) using De Jong (1994) method.

    C = 0.431 - 0.805 * NDVI

    Args:
        landsat: Landsat image collection.
        date_from: Start date (YYYY-MM-DD).
        date_to: End date (YYYY-MM-DD).
        aoi: Area of interest.

    Returns:
        ee.Image: C factor image.
    """
    # Filter and composite Landsat
    l8_composite = (
        landsat
        .filterDate(date_from, date_to)
        .median()
        .clip(aoi)
    )

    # Calculate NDVI
    ndvi = l8_composite.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')

    # Calculate C factor (De Jong 1994)
    c_factor = (
        ee.Image(0.431)
        .subtract(ndvi.multiply(0.805))
        .rename('C_factor')
    )

    return c_factor


def calculate_p_factor(
    modis_lc: ee.Image,
    aoi: ee.FeatureCollection,
    p_values: Optional[Dict[int, float]] = None
) -> ee.Image:
    """
    Calculate erosion control practices factor (P) from land cover.

    Args:
        modis_lc: MODIS land cover image.
        aoi: Area of interest.
        p_values: Dictionary mapping land cover classes to P values.
                  Uses Chuenchum et al. (2019) values by default.

    Returns:
        ee.Image: P factor image.
    """
    if p_values is None:
        p_values = P_FACTOR_VALUES

    lulc = modis_lc.clip(aoi).rename('lulc')

    # Build expression string from p_values dictionary
    expression_parts = [
        f"(b('lulc') == {lc_class}) ? {p_value}"
        for lc_class, p_value in p_values.items()
    ]
    expression = ": ".join(expression_parts) + ": 9999"

    p_factor = lulc.expression(expression).rename('P_factor').clip(aoi)

    return p_factor


def calculate_rusle(
    r_factor: ee.Image,
    k_factor: ee.Image,
    l_factor: ee.Image,
    s_factor: ee.Image,
    c_factor: ee.Image,
    p_factor: ee.Image,
    pixel_area_ha: float = 0.09
) -> ee.Image:
    """
    Calculate soil loss using RUSLE equation.

    A = R * K * L * S * C * P

    Args:
        r_factor: Rainfall erosivity factor.
        k_factor: Soil erodibility factor.
        l_factor: Slope length factor.
        s_factor: Slope steepness factor.
        c_factor: Vegetation cover factor.
        p_factor: Erosion control practices factor.
        pixel_area_ha: Pixel area in hectares (default 0.09 for 30x30m).

    Returns:
        ee.Image: Soil loss in ton/ha/year.
    """
    soil_loss = (
        r_factor
        .multiply(k_factor)
        .multiply(l_factor)
        .multiply(s_factor)
        .multiply(c_factor)
        .multiply(p_factor)
        .multiply(pixel_area_ha)
        .rename('soil_loss')
    )

    return soil_loss


# =============================================================================
# Visualization Functions
# =============================================================================

def create_visualization_params(
    min_val: float,
    max_val: float,
    palette: Optional[list] = None,
    bands: Optional[list] = None
) -> Dict:
    """
    Create visualization parameters dictionary.

    Args:
        min_val: Minimum value for color scale.
        max_val: Maximum value for color scale.
        palette: List of hex color codes.
        bands: List of band names (optional).

    Returns:
        Dict: Visualization parameters.
    """
    viz_params = {
        'min': min_val,
        'max': max_val,
        'palette': palette or DEFAULT_PALETTE
    }
    if bands:
        viz_params['bands'] = bands
    return viz_params


def visualize_layer(
    image: ee.Image,
    aoi: ee.FeatureCollection,
    layer_name: str,
    viz_params: Dict,
    colorbar_label: Optional[str] = None
) -> geemap.Map:
    """
    Create a map visualization for a single layer.

    Args:
        image: Image to visualize.
        aoi: Area of interest for centering.
        layer_name: Name of the layer.
        viz_params: Visualization parameters.
        colorbar_label: Label for colorbar (optional).

    Returns:
        geemap.Map: Map with the layer added.
    """
    map_viz = geemap.Map()
    map_viz.addLayer(image, viz_params, layer_name)

    if colorbar_label:
        map_viz.add_colorbar(
            viz_params,
            label=colorbar_label,
            layer_name=layer_name
        )

    map_viz.centerObject(aoi)
    return map_viz


def export_image(
    image: ee.Image,
    output_path: str,
    aoi: ee.FeatureCollection,
    scale: int = 90,
    crs: Optional[str] = None
) -> None:
    """
    Export an Earth Engine image to local file.

    Args:
        image: Image to export.
        output_path: Path for output file.
        aoi: Area of interest for clipping.
        scale: Resolution in meters.
        crs: Coordinate reference system (optional).
    """
    geemap.ee_export_image(
        image,
        output_path,
        scale=scale,
        crs=crs,
        region=aoi.geometry(),
        file_per_band=False
    )
