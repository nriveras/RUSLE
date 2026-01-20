"""
Process router for RUSLE calculations.
"""

import logging
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import geopandas as gpd
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.services.gee_service import is_gee_initialized, load_area_from_gaul
from app.services.rusle_calculator import RUSLECalculator, RUSLEInput
from app.services.shapefile_handler import ShapefileHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
shapefile_handler = ShapefileHandler(settings.upload_dir)

# Store results in memory (in production, use Redis or database)
_results_cache: Dict[str, Any] = {}


class DEMSource(str, Enum):
    """Available DEM sources."""
    SRTM = "SRTM"
    MERIT = "MERIT"


class ProcessRequest(BaseModel):
    """Request model for RUSLE processing."""
    session_id: Optional[str] = Field(
        None,
        description="Session ID from file upload. Required if not using admin_region."
    )
    admin_region: Optional[str] = Field(
        None,
        description="Administrative region name (uses FAO GAUL). Alternative to session_id."
    )
    date_from: str = Field(
        ...,
        description="Start date for analysis (YYYY-MM-DD)",
        examples=["2022-01-01"]
    )
    date_to: str = Field(
        ...,
        description="End date for analysis (YYYY-MM-DD)",
        examples=["2023-01-01"]
    )
    dem_source: DEMSource = Field(
        DEMSource.SRTM,
        description="Digital Elevation Model source"
    )
    export_scale: int = Field(
        90,
        ge=10,
        le=1000,
        description="Export resolution in meters"
    )
    
    @field_validator('date_from', 'date_to')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    def model_post_init(self, __context):
        if not self.session_id and not self.admin_region:
            raise ValueError("Either session_id or admin_region must be provided")


class FactorInfo(BaseModel):
    """Information about a RUSLE factor."""
    name: str
    description: str
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    tile_url: Optional[str] = None


class ProcessResponse(BaseModel):
    """Response model for RUSLE processing."""
    job_id: str
    status: str
    message: str
    computation_time: Optional[float] = None
    factors: Optional[Dict[str, FactorInfo]] = None
    soil_loss_tile_url: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None


class JobStatus(BaseModel):
    """Job status response."""
    job_id: str
    status: str
    progress: int = 0
    message: str = ""
    result: Optional[ProcessResponse] = None


@router.post("/process", response_model=ProcessResponse)
async def process_rusle(request: ProcessRequest):
    """
    Process RUSLE calculation for the specified area and date range.
    
    Provide either:
    - session_id: From a previous file upload
    - admin_region: Name of administrative region (uses FAO GAUL boundaries)
    
    Returns tile URLs for visualization and basic statistics.
    """
    if not is_gee_initialized():
        raise HTTPException(
            status_code=503,
            detail="Google Earth Engine is not initialized. Please check server configuration."
        )
    
    import uuid
    job_id = str(uuid.uuid4())
    
    try:
        # Get AOI geometry
        if request.session_id:
            aoi = _get_aoi_from_session(request.session_id)
        else:
            aoi = _get_aoi_from_admin(request.admin_region)
        
        # Create calculator and inputs
        calculator = RUSLECalculator()
        inputs = RUSLEInput(
            aoi=aoi,
            date_from=request.date_from,
            date_to=request.date_to,
            dem_source=request.dem_source.value,
            export_scale=request.export_scale
        )
        
        # Run calculation
        result = calculator.calculate(inputs)
        
        # Get tile URLs for visualization
        soil_loss_vis = {
            'min': 0,
            'max': 50,
            'palette': ['00ff00', '7fff00', 'ffff00', 'ffa500', 'ff4500', 'ff0000', '8b0000']
        }
        
        factor_vis = {
            'min': 0,
            'max': 1,
            'palette': ['blue', 'green', 'yellow', 'orange', 'red']
        }
        
        # Build response with tile URLs
        soil_loss_tile_url = calculator.get_tile_url(result.soil_loss, soil_loss_vis)
        
        factors = {
            'R': FactorInfo(
                name='Rainfall Erosivity',
                description='Effect of rainfall intensity and duration',
                unit='MJ·mm/(ha·h·yr)',
                tile_url=calculator.get_tile_url(
                    result.r_factor,
                    {'min': 0, 'max': 5000, 'palette': factor_vis['palette']}
                )
            ),
            'K': FactorInfo(
                name='Soil Erodibility',
                description='Susceptibility of soil to erosion',
                unit='t·ha·h/(ha·MJ·mm)',
                tile_url=calculator.get_tile_url(
                    result.k_factor,
                    {'min': 0.3, 'max': 0.5, 'palette': factor_vis['palette']}
                )
            ),
            'L': FactorInfo(
                name='Slope Length',
                description='Effect of slope length on erosion',
                unit='dimensionless',
                tile_url=calculator.get_tile_url(
                    result.l_factor,
                    {'min': 1, 'max': 1.2, 'palette': factor_vis['palette']}
                )
            ),
            'S': FactorInfo(
                name='Slope Steepness',
                description='Effect of slope gradient on erosion',
                unit='dimensionless',
                tile_url=calculator.get_tile_url(
                    result.s_factor,
                    {'min': 0, 'max': 45, 'palette': factor_vis['palette']}
                )
            ),
            'C': FactorInfo(
                name='Vegetation Cover',
                description='Effect of vegetation on reducing erosion',
                unit='dimensionless',
                tile_url=calculator.get_tile_url(
                    result.c_factor,
                    {'min': 0, 'max': 0.5, 'palette': factor_vis['palette']}
                )
            ),
            'P': FactorInfo(
                name='Erosion Control Practices',
                description='Effect of conservation practices',
                unit='dimensionless',
                tile_url=calculator.get_tile_url(
                    result.p_factor,
                    {'min': 0, 'max': 1, 'palette': factor_vis['palette']}
                )
            ),
        }
        
        # Cache result for later retrieval
        _results_cache[job_id] = {
            'result': result,
            'aoi': aoi,
            'request': request
        }
        
        return ProcessResponse(
            job_id=job_id,
            status='completed',
            message='RUSLE calculation completed successfully',
            computation_time=result.computation_time,
            factors=factors,
            soil_loss_tile_url=soil_loss_tile_url
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/process/{job_id}/statistics")
async def get_statistics(job_id: str):
    """
    Get detailed statistics for a completed RUSLE calculation.
    """
    if job_id not in _results_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cached = _results_cache[job_id]
    calculator = RUSLECalculator()
    
    try:
        stats = calculator.get_statistics(
            cached['result'].soil_loss,
            cached['aoi'],
            scale=cached['request'].export_scale
        )
        return {
            'job_id': job_id,
            'statistics': stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute statistics: {str(e)}")


@router.post("/process/{job_id}/export")
async def export_result(
    job_id: str,
    background_tasks: BackgroundTasks,
    folder: str = Query("RUSLE_exports", description="Google Drive folder name")
):
    """
    Export RUSLE result to Google Drive.
    
    The export runs as a background task in Google Earth Engine.
    """
    if job_id not in _results_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cached = _results_cache[job_id]
    calculator = RUSLECalculator()
    
    try:
        request = cached['request']
        description = f"RUSLE_soil_loss_{request.date_from}_to_{request.date_to}"
        
        task = calculator.export_to_drive(
            image=cached['result'].soil_loss,
            description=description,
            aoi=cached['aoi'],
            scale=request.export_scale,
            folder=folder
        )
        
        return {
            'message': 'Export task started',
            'task_id': task.id,
            'description': description,
            'folder': folder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


def _get_aoi_from_session(session_id: str):
    """Load AOI geometry from uploaded session."""
    import ee
    
    session_dir = settings.upload_dir / session_id
    if not session_dir.exists():
        raise ValueError(f"Session not found: {session_id}")
    
    # Find and load the data
    extract_dir = session_dir / "extracted"
    if extract_dir.exists():
        shp_files = list(extract_dir.rglob("*.shp"))
        if shp_files:
            gdf = gpd.read_file(shp_files[0])
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs("EPSG:4326")
            return shapefile_handler.gdf_to_ee_geometry(gdf)
    
    geojson_files = list(session_dir.glob("*.geojson"))
    if geojson_files:
        gdf = gpd.read_file(geojson_files[0])
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        return shapefile_handler.gdf_to_ee_geometry(gdf)
    
    raise ValueError("No geometry data found for session")


def _get_aoi_from_admin(admin_region: str):
    """Load AOI from FAO GAUL administrative boundaries."""
    import ee
    
    fc = load_area_from_gaul(admin_region, admin_level=1)
    
    # Check if we got results
    count = fc.size().getInfo()
    if count == 0:
        raise ValueError(f"Administrative region not found: {admin_region}")
    
    return fc.geometry()
