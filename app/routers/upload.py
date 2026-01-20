"""
Upload router for handling file uploads.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.services.shapefile_handler import ShapefileHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize shapefile handler
shapefile_handler = ShapefileHandler(settings.upload_dir)


class UploadResponse(BaseModel):
    """Response model for file upload."""
    session_id: str
    filename: str
    feature_count: int
    area_km2: float
    bounds: dict
    crs: str
    message: str


class UploadError(BaseModel):
    """Error response model."""
    detail: str


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": UploadError},
        413: {"model": UploadError}
    }
)
async def upload_shapefile(
    file: UploadFile = File(..., description="Shapefile as ZIP or GeoJSON"),
):
    """
    Upload a shapefile (ZIP) or GeoJSON for the area of interest.
    
    The ZIP file should contain at least .shp, .shx, and .dbf files.
    Optionally include .prj for coordinate reference system.
    
    Returns session_id to use for subsequent processing requests.
    """
    # Validate file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB"
        )
    
    # Validate file type
    filename = file.filename or "upload.zip"
    if not (filename.lower().endswith('.zip') or filename.lower().endswith('.geojson')):
        raise HTTPException(
            status_code=400,
            detail="Please upload a ZIP file containing shapefile components or a GeoJSON file"
        )
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Process the upload
        gdf, extract_path = shapefile_handler.process_upload(
            file_content=content,
            filename=filename,
            session_id=session_id
        )
        
        # Calculate area
        area_km2 = shapefile_handler.calculate_area_km2(gdf)
        
        # Validate area
        if area_km2 > settings.max_aoi_area_km2:
            shapefile_handler.cleanup_session(session_id)
            raise HTTPException(
                status_code=400,
                detail=f"Area of interest too large ({area_km2:.0f} km²). "
                       f"Maximum allowed is {settings.max_aoi_area_km2:.0f} km²"
            )
        
        # Get bounds
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        
        logger.info(
            f"Upload successful: session={session_id}, "
            f"features={len(gdf)}, area={area_km2:.2f}km²"
        )
        
        return UploadResponse(
            session_id=session_id,
            filename=filename,
            feature_count=len(gdf),
            area_km2=round(area_km2, 2),
            bounds={
                "minx": round(bounds[0], 6),
                "miny": round(bounds[1], 6),
                "maxx": round(bounds[2], 6),
                "maxy": round(bounds[3], 6)
            },
            crs=str(gdf.crs),
            message="Upload successful. Use the session_id for processing."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        shapefile_handler.cleanup_session(session_id)
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.delete("/upload/{session_id}")
async def cleanup_upload(session_id: str):
    """
    Clean up uploaded files for a session.
    
    Call this after processing is complete or if the session is no longer needed.
    """
    try:
        shapefile_handler.cleanup_session(session_id)
        return {"message": f"Session {session_id} cleaned up successfully"}
    except Exception as e:
        logger.error(f"Cleanup failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upload/{session_id}/preview")
async def preview_upload(session_id: str):
    """
    Get a preview of the uploaded AOI as GeoJSON.
    """
    session_dir = settings.upload_dir / session_id
    
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Find and load the shapefile
    import geopandas as gpd
    
    # Try to find extracted files
    extract_dir = session_dir / "extracted"
    if extract_dir.exists():
        shp_files = list(extract_dir.rglob("*.shp"))
        if shp_files:
            gdf = gpd.read_file(shp_files[0])
            return gdf.__geo_interface__
    
    # Try GeoJSON
    geojson_files = list(session_dir.glob("*.geojson"))
    if geojson_files:
        gdf = gpd.read_file(geojson_files[0])
        return gdf.__geo_interface__
    
    raise HTTPException(status_code=404, detail="No geometry data found for session")
