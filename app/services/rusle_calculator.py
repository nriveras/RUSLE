"""
RUSLE Calculator Service.

Provides high-level interface for RUSLE soil loss calculations.
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import ee
import geemap

from app.config import settings
from app.services import gee_service

logger = logging.getLogger(__name__)


# P-Factor values by MODIS land cover class (Chuenchum et al., 2019)
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


@dataclass
class RUSLEInput:
    """Input parameters for RUSLE calculation."""
    aoi: ee.Geometry
    date_from: str
    date_to: str
    
    # Optional user-provided factors (override GEE data)
    custom_k_factor: Optional[ee.Image] = None
    custom_r_factor: Optional[ee.Image] = None
    custom_ls_factor: Optional[ee.Image] = None
    custom_c_factor: Optional[ee.Image] = None
    custom_p_factor: Optional[ee.Image] = None
    
    # Processing options
    dem_source: str = 'SRTM'
    export_scale: int = 90
    pixel_size: float = 30.0


@dataclass
class RUSLEResult:
    """Results from RUSLE calculation."""
    soil_loss: ee.Image
    r_factor: ee.Image
    k_factor: ee.Image
    l_factor: ee.Image
    s_factor: ee.Image
    c_factor: ee.Image
    p_factor: ee.Image
    
    # Metadata
    date_from: str = ""
    date_to: str = ""
    computation_time: float = 0.0
    
    # Statistics (populated after computation)
    stats: Dict[str, Any] = field(default_factory=dict)


class RUSLECalculator:
    """
    Calculator for RUSLE soil loss estimation.
    
    Implements the Revised Universal Soil Loss Equation:
    A = R * K * L * S * C * P
    """
    
    def __init__(self):
        """Initialize the RUSLE calculator."""
        self._ensure_gee_initialized()
    
    def _ensure_gee_initialized(self):
        """Ensure Google Earth Engine is initialized."""
        if not gee_service.is_gee_initialized():
            gee_service.initialize_earth_engine(settings.gee_project)
    
    def calculate(self, inputs: RUSLEInput) -> RUSLEResult:
        """
        Perform full RUSLE calculation.
        
        Args:
            inputs: RUSLEInput with AOI, dates, and optional custom factors
            
        Returns:
            RUSLEResult with all factors and soil loss
        """
        start_time = datetime.now()
        logger.info(f"Starting RUSLE calculation for period {inputs.date_from} to {inputs.date_to}")
        
        aoi = inputs.aoi
        
        # Calculate or use provided factors
        k_factor = inputs.custom_k_factor or self._calculate_k_factor(aoi)
        r_factor = inputs.custom_r_factor or self._calculate_r_factor(
            aoi, inputs.date_from, inputs.date_to
        )
        l_factor, s_factor = self._calculate_ls_factors(
            aoi, inputs.dem_source, inputs.pixel_size
        )
        if inputs.custom_ls_factor:
            # If user provides combined LS, use it for both
            l_factor = inputs.custom_ls_factor
            s_factor = ee.Image(1)
        
        c_factor = inputs.custom_c_factor or self._calculate_c_factor(
            aoi, inputs.date_from, inputs.date_to
        )
        p_factor = inputs.custom_p_factor or self._calculate_p_factor(aoi)
        
        # Calculate soil loss: A = R * K * L * S * C * P
        pixel_area_ha = (inputs.pixel_size ** 2) / 10000  # Convert m² to ha
        
        soil_loss = (
            r_factor
            .multiply(k_factor)
            .multiply(l_factor)
            .multiply(s_factor)
            .multiply(c_factor)
            .multiply(p_factor)
            .multiply(pixel_area_ha)
            .rename('soil_loss')
            .unmask(0)  # Fill any remaining gaps with 0 soil loss
            .clip(aoi)  # Clip final result to AOI
        )
        
        # Also clip all factors to AOI for consistent visualization
        # unmask already applied in individual factor calculations
        r_factor = r_factor.clip(aoi)
        k_factor = k_factor.clip(aoi)
        l_factor = l_factor.clip(aoi)
        s_factor = s_factor.clip(aoi)
        c_factor = c_factor.clip(aoi)
        p_factor = p_factor.clip(aoi)
        
        computation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"RUSLE calculation completed in {computation_time:.2f}s")
        
        return RUSLEResult(
            soil_loss=soil_loss,
            r_factor=r_factor,
            k_factor=k_factor,
            l_factor=l_factor,
            s_factor=s_factor,
            c_factor=c_factor,
            p_factor=p_factor,
            date_from=inputs.date_from,
            date_to=inputs.date_to,
            computation_time=computation_time
        )
    
    def _calculate_k_factor(self, aoi: ee.Geometry) -> ee.Image:
        """
        Calculate soil erodibility factor (K) using Williams (1995) method.
        
        K = f_csand * f_cl_si * f_orgc * f_hisand
        """
        organic_carbon, clay, sand, silt = gee_service.load_soil_data(aoi)
        
        # f_csand: Factor for coarse sand content
        f_csand = (
            ee.Image(0.2).add(
                ee.Image(0.3).multiply(
                    ee.Image(-0.256)
                    .multiply(silt.divide(100).subtract(1))
                    .exp()
                )
            )
        )
        
        # f_cl_si: Clay-silt ratio factor
        f_cl_si = silt.divide(clay.add(silt)).pow(0.3)
        
        # f_orgc: Organic carbon factor
        f_orgc = (
            ee.Image(1).subtract(
                ee.Image(0.25).multiply(organic_carbon).divide(
                    organic_carbon.add(
                        ee.Image(3.72)
                        .subtract(ee.Image(2.95).multiply(organic_carbon))
                        .exp()
                    )
                )
            )
        )
        
        # f_hisand: High sand content factor
        sand_fraction = ee.Image(1).subtract(sand.divide(100))
        f_hisand = (
            ee.Image(1).subtract(
                ee.Image(0.7).multiply(sand_fraction).divide(
                    sand_fraction.add(
                        ee.Image(-5.51)
                        .add(ee.Image(22.9).multiply(sand_fraction))
                        .exp()
                    )
                )
            )
        )
        
        k_factor = (
            f_csand.multiply(f_cl_si).multiply(f_orgc).multiply(f_hisand)
            .rename('K_factor')
            .unmask(0.04)  # Fill gaps with average K-factor value
            .clip(aoi)
        )
        
        return k_factor
    
    def _calculate_r_factor(
        self,
        aoi: ee.Geometry,
        date_from: str,
        date_to: str
    ) -> ee.Image:
        """
        Calculate rainfall erosivity factor (R).
        
        R = 0.0483 * P^1.610
        """
        precipitation = gee_service.load_precipitation_data(aoi)
        
        pcp_sum = (
            precipitation
            .select('precipitation')
            .filterDate(date_from, date_to)
            .sum()
            .clip(aoi)
        )
        
        r_factor = (
            pcp_sum.pow(1.610).multiply(0.0483)
            .rename('R_factor')
            .unmask(0)  # Fill gaps with 0 (no rainfall erosivity)
        )
        
        return r_factor
    
    def _calculate_ls_factors(
        self,
        aoi: ee.Geometry,
        dem_source: str,
        pixel_size: float
    ) -> Tuple[ee.Image, ee.Image]:
        """
        Calculate slope length (L) and steepness (S) factors.
        """
        dem = gee_service.load_dem(dem_source)
        
        # Calculate slope in degrees
        slope_deg = ee.Terrain.slope(dem).clip(aoi)
        
        # Convert to percentage
        slope_perc = (
            slope_deg.divide(180).multiply(math.pi).tan().multiply(100)
        )
        
        # L Factor: L = (λ / 22.13)^m
        m_exponent = (
            ee.Image(1)
            .where(slope_perc.gt(-1).And(slope_perc.lte(1)), 0.2)
            .where(slope_perc.gt(1).And(slope_perc.lte(3)), 0.3)
            .where(slope_perc.gt(3).And(slope_perc.lte(4.5)), 0.4)
            .where(slope_perc.gt(4.5).And(slope_perc.lte(100)), 0.5)
        )
        
        l_factor = (
            ee.Image(pixel_size).divide(22.13).pow(m_exponent)
            .rename('L_factor')
            .unmask(1)  # Fill gaps with neutral L-factor value
            .clip(aoi)
        )
        
        # S Factor: S = (0.43 + 0.3*slope + 0.043*slope²) / 6.613
        s_factor = (
            slope_perc.pow(2).multiply(0.043)
            .add(slope_perc.multiply(0.30))
            .add(0.43)
            .divide(6.613)
            .rename('S_factor')
            .unmask(0.065)  # Fill gaps with flat terrain S-factor
            .clip(aoi)
        )
        
        return l_factor, s_factor
    
    def _calculate_c_factor(
        self,
        aoi: ee.Geometry,
        date_from: str,
        date_to: str
    ) -> ee.Image:
        """
        Calculate vegetation cover factor (C) using De Jong (1994) method.
        
        C = 0.431 - 0.805 * NDVI
        """
        landsat8 = gee_service.load_landsat8()
        
        composite = (
            landsat8
            .filterDate(date_from, date_to)
            .filterBounds(aoi)
            .median()
            .clip(aoi)
        )
        
        ndvi = composite.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        
        c_factor = (
            ee.Image(0.431).subtract(ndvi.multiply(0.805))
            .rename('C_factor')
            .unmask(0.15)  # Fill gaps with moderate vegetation cover value
            .clip(aoi)
        )
        
        return c_factor
    
    def _calculate_p_factor(self, aoi: ee.Geometry) -> ee.Image:
        """
        Calculate erosion control practices factor (P) from MODIS land cover.
        Uses MODIS/061/MCD12Q1 dataset.
        """
        # Load MODIS land cover directly to avoid double clipping
        modis_lc = (
            ee.ImageCollection("MODIS/061/MCD12Q1")
            .select('LC_Type1')
            .sort('system:time_start', False)
            .first()
            .clip(aoi)
        )
        lulc = modis_lc.rename('lulc')
        
        # Build expression
        expression_parts = [
            f"(b('lulc') == {lc_class}) ? {p_value}"
            for lc_class, p_value in P_FACTOR_VALUES.items()
        ]
        expression = ": ".join(expression_parts) + ": 1.0"
        
        p_factor = (
            lulc.expression(expression)
            .rename('P_factor')
            .unmask(1.0)  # Fill gaps with neutral P-factor (no conservation)
            .clip(aoi)
        )
        
        return p_factor
    
    def get_statistics(
        self,
        image: ee.Image,
        aoi: ee.Geometry,
        scale: int = 90
    ) -> Dict[str, float]:
        """
        Calculate statistics for an image within the AOI.
        
        Returns dict with min, max, mean, std.
        """
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean()
                .combine(ee.Reducer.minMax(), '', True)
                .combine(ee.Reducer.stdDev(), '', True),
            geometry=aoi,
            scale=scale,
            maxPixels=1e9
        ).getInfo()
        
        return stats
    
    def export_to_drive(
        self,
        image: ee.Image,
        description: str,
        aoi: ee.Geometry,
        scale: int = 90,
        folder: str = 'RUSLE_exports'
    ) -> ee.batch.Task:
        """
        Export image to Google Drive.
        
        Returns the export task (can be monitored).
        """
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder=folder,
            region=aoi,
            scale=scale,
            maxPixels=1e13
        )
        task.start()
        return task
    
    def get_tile_url(
        self,
        image: ee.Image,
        vis_params: Dict[str, Any],
        scale: int = None
    ) -> str:
        """
        Get a tile URL for displaying the image on a web map.
        
        For large areas, we reproject to a coarser resolution to ensure
        all tiles can be computed within GEE limits.
        
        Args:
            image: Earth Engine image
            vis_params: Visualization parameters
            scale: Optional scale for reprojection (meters per pixel)
            
        Returns:
            Tile URL template
        """
        # For visualization, reproject to coarser resolution if scale provided
        # This helps with large areas that exceed GEE computation limits
        if scale and scale > 100:
            image = image.reproject(
                crs='EPSG:4326',
                scale=scale
            )
        
        map_id = image.getMapId(vis_params)
        return map_id['tile_fetcher'].url_format
