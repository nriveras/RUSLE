"""
Google Earth Engine service for authentication and data fetching.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import ee

logger = logging.getLogger(__name__)

# Track initialization status
_gee_initialized = False


def initialize_earth_engine(project_id: str, force: bool = False) -> bool:
    """
    Initialize Google Earth Engine with the specified project.

    Args:
        project_id: GEE Cloud Project ID
        force: Force re-authentication

    Returns:
        True if initialization successful
    """
    global _gee_initialized

    if _gee_initialized and not force:
        return True

    try:
        # Try to authenticate
        ee.Authenticate(force=force)

        # Initialize with project
        ee.Initialize(project=project_id)

        # Verify connection
        _ = ee.Number(1).getInfo()

        _gee_initialized = True
        logger.info(f"GEE initialized with project: {project_id}")
        return True

    except ee.EEException as e:
        logger.error(f"GEE initialization failed: {e}")
        if "not registered" in str(e):
            logger.error(
                f"Project '{project_id}' is not registered for Earth Engine. "
                f"Register at: https://console.cloud.google.com/earth-engine/configuration?project={project_id}"
            )
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing GEE: {e}")
        raise


def is_gee_initialized() -> bool:
    """Check if GEE is initialized."""
    return _gee_initialized


def load_precipitation_data(aoi: ee.Geometry) -> ee.ImageCollection:
    """
    Load CHIRPS precipitation data.

    Args:
        aoi: Area of interest geometry

    Returns:
        CHIRPS precipitation ImageCollection
    """
    return (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .select('precipitation')
        .filterBounds(aoi)
    )


def load_soil_data(aoi: ee.Geometry) -> tuple:
    """
    Load soil data from OpenLandMap.

    Args:
        aoi: Area of interest geometry

    Returns:
        Tuple of (organic_carbon, clay, sand, silt) images
    """
    organic_carbon = (
        ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
        .select('b0')
        .clip(aoi)
    )

    clay = (
        ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02")
        .select('b0')
        .clip(aoi)
    )

    sand = (
        ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02")
        .select('b0')
        .clip(aoi)
    )

    # Silt calculated as remainder (no direct dataset available)
    silt = ee.Image(100).subtract(clay).subtract(sand).rename('silt').clip(aoi)

    return organic_carbon, clay, sand, silt


def load_dem(source: str = 'SRTM') -> ee.Image:
    """
    Load Digital Elevation Model.

    Args:
        source: DEM source ('SRTM' or 'MERIT')

    Returns:
        DEM image
    """
    if source.upper() == 'SRTM':
        return ee.Image("USGS/SRTMGL1_003").select('elevation')
    elif source.upper() == 'MERIT':
        return ee.Image("MERIT/DEM/v1_0_3").select('dem')
    else:
        raise ValueError(f"Unknown DEM source: {source}")


def load_landsat8() -> ee.ImageCollection:
    """
    Load Landsat 8 Surface Reflectance collection with scaling.

    Returns:
        Landsat 8 ImageCollection with scaled values
    """
    def apply_scale_factors(image):
        optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
        thermal = image.select('ST_B.*').multiply(0.00341802).add(149.0)
        return image.addBands(optical, None, True).addBands(thermal, None, True)

    return (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .map(apply_scale_factors)
    )


def load_modis_landcover(aoi: ee.Geometry) -> ee.Image:
    """
    Load MODIS land cover (most recent).

    Args:
        aoi: Area of interest geometry

    Returns:
        MODIS land cover image
    """
    return (
        ee.ImageCollection("MODIS/061/MCD12Q1")
        .select('LC_Type1')
        .sort('system:time_start', False)
        .first()
        .clip(aoi)
    )


def load_area_from_gaul(region_name: str, admin_level: int = 1) -> ee.FeatureCollection:
    """
    Load administrative boundary from FAO GAUL.

    Args:
        region_name: Name of the region to search
        admin_level: Administrative level (0=country, 1=region/state, 2=province/county)

    Returns:
        Feature collection for the region
    
    Examples:
        - Level 0: "Spain", "France", "Germany", "Italy"
        - Level 1: "Cataluña", "Île-de-France", "Bayern", "Toscana"
        - Level 2: "Barcelona", "Paris", "Milano"
    """
    if admin_level == 0:
        gaul = ee.FeatureCollection("FAO/GAUL/2015/level0")
        return gaul.filter(ee.Filter.stringContains('ADM0_NAME', region_name))
    elif admin_level == 1:
        gaul = ee.FeatureCollection("FAO/GAUL/2015/level1")
        return gaul.filter(ee.Filter.stringContains('ADM1_NAME', region_name))
    else:
        gaul = ee.FeatureCollection("FAO/GAUL/2015/level2")
        return gaul.filter(ee.Filter.stringContains('ADM2_NAME', region_name))
