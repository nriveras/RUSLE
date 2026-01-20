"""
Visualization router for map generation.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.config import settings
from app.services.gee_service import is_gee_initialized

logger = logging.getLogger(__name__)
router = APIRouter()

# Import results cache from process router
from app.routers.process import _results_cache


class MapConfig(BaseModel):
    """Map configuration for visualization."""
    center_lat: float
    center_lng: float
    zoom: int = 9
    layers: List[Dict[str, Any]]


@router.get("/visualize/{job_id}")
async def get_map_config(job_id: str) -> MapConfig:
    """
    Get map configuration for visualizing RUSLE results.
    
    Returns center coordinates and layer configurations including tile URLs.
    """
    if job_id not in _results_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cached = _results_cache[job_id]
    
    try:
        import ee
        
        # Get center of AOI
        centroid = cached['aoi'].centroid().coordinates().getInfo()
        
        # Prepare layer configurations
        layers = [
            {
                'name': 'Soil Loss (ton/ha/yr)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].soil_loss, {
                    'min': 0, 'max': 50,
                    'palette': ['00ff00', '7fff00', 'ffff00', 'ffa500', 'ff4500', 'ff0000', '8b0000']
                }),
                'visible': True,
                'opacity': 0.8
            },
            {
                'name': 'R Factor (Rainfall Erosivity)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].r_factor, {
                    'min': 0, 'max': 5000,
                    'palette': ['blue', 'green', 'yellow', 'orange', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
            {
                'name': 'K Factor (Soil Erodibility)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].k_factor, {
                    'min': 0.3, 'max': 0.5,
                    'palette': ['blue', 'green', 'yellow', 'orange', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
            {
                'name': 'L Factor (Slope Length)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].l_factor, {
                    'min': 1, 'max': 1.2,
                    'palette': ['green', 'yellow', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
            {
                'name': 'S Factor (Slope Steepness)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].s_factor, {
                    'min': 0, 'max': 45,
                    'palette': ['green', 'yellow', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
            {
                'name': 'C Factor (Vegetation Cover)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].c_factor, {
                    'min': 0, 'max': 0.5,
                    'palette': ['green', 'yellow', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
            {
                'name': 'P Factor (Erosion Control)',
                'type': 'tile',
                'url': _get_tile_url(cached['result'].p_factor, {
                    'min': 0, 'max': 1,
                    'palette': ['blue', 'green', 'yellow', 'orange', 'red']
                }),
                'visible': False,
                'opacity': 0.8
            },
        ]
        
        return MapConfig(
            center_lat=centroid[1],
            center_lng=centroid[0],
            zoom=9,
            layers=layers
        )
        
    except Exception as e:
        logger.error(f"Failed to generate map config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualize/{job_id}/folium", response_class=HTMLResponse)
async def get_folium_map(
    job_id: str,
    width: str = Query("100%", description="Map width"),
    height: str = Query("600px", description="Map height")
):
    """
    Generate a Folium map HTML for the RUSLE results.
    
    Can be embedded in an iframe or displayed directly.
    """
    if job_id not in _results_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cached = _results_cache[job_id]
    
    try:
        import ee
        import folium
        from folium import plugins
        
        # Get center of AOI
        centroid = cached['aoi'].centroid().coordinates().getInfo()
        center = [centroid[1], centroid[0]]
        
        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=9,
            tiles='cartodbpositron'
        )
        
        # Add EE tile layers
        def add_ee_layer(image, vis_params, name, show=True):
            map_id = image.getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format
            folium.TileLayer(
                tiles=tile_url,
                attr='Google Earth Engine',
                name=name,
                overlay=True,
                show=show
            ).add_to(m)
        
        # Add soil loss layer
        add_ee_layer(
            cached['result'].soil_loss,
            {'min': 0, 'max': 50, 'palette': ['00ff00', '7fff00', 'ffff00', 'ffa500', 'ff4500', 'ff0000', '8b0000']},
            'Soil Loss (ton/ha/yr)',
            show=True
        )
        
        # Add factor layers (hidden by default)
        add_ee_layer(
            cached['result'].r_factor,
            {'min': 0, 'max': 5000, 'palette': ['blue', 'green', 'yellow', 'orange', 'red']},
            'R Factor (Rainfall Erosivity)',
            show=False
        )
        
        add_ee_layer(
            cached['result'].k_factor,
            {'min': 0.3, 'max': 0.5, 'palette': ['blue', 'green', 'yellow', 'orange', 'red']},
            'K Factor (Soil Erodibility)',
            show=False
        )
        
        add_ee_layer(
            cached['result'].l_factor,
            {'min': 1, 'max': 1.2, 'palette': ['green', 'yellow', 'red']},
            'L Factor (Slope Length)',
            show=False
        )
        
        add_ee_layer(
            cached['result'].s_factor,
            {'min': 0, 'max': 45, 'palette': ['green', 'yellow', 'red']},
            'S Factor (Slope Steepness)',
            show=False
        )
        
        add_ee_layer(
            cached['result'].c_factor,
            {'min': 0, 'max': 0.5, 'palette': ['green', 'yellow', 'red']},
            'C Factor (Vegetation Cover)',
            show=False
        )
        
        add_ee_layer(
            cached['result'].p_factor,
            {'min': 0, 'max': 1, 'palette': ['blue', 'green', 'yellow', 'orange', 'red']},
            'P Factor (Erosion Control)',
            show=False
        )
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add colorbar for soil loss
        import branca.colormap as cm
        colormap = cm.LinearColormap(
            colors=['#00ff00', '#7fff00', '#ffff00', '#ffa500', '#ff4500', '#ff0000', '#8b0000'],
            vmin=0,
            vmax=50,
            caption='Soil Loss (ton/ha/year)'
        )
        colormap.add_to(m)
        
        # Return HTML
        return m._repr_html_()
        
    except Exception as e:
        logger.error(f"Failed to generate Folium map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legend")
async def get_legend_info():
    """
    Get legend information for RUSLE soil loss classes.
    """
    return {
        'soil_loss_classes': [
            {'range': '0-5', 'label': 'Very Low', 'color': '#00ff00'},
            {'range': '5-10', 'label': 'Low', 'color': '#7fff00'},
            {'range': '10-20', 'label': 'Moderate', 'color': '#ffff00'},
            {'range': '20-30', 'label': 'High', 'color': '#ffa500'},
            {'range': '30-40', 'label': 'Very High', 'color': '#ff4500'},
            {'range': '40-50', 'label': 'Severe', 'color': '#ff0000'},
            {'range': '>50', 'label': 'Very Severe', 'color': '#8b0000'},
        ],
        'unit': 'ton/ha/year'
    }


def _get_tile_url(image, vis_params):
    """Helper to get tile URL for an EE image."""
    map_id = image.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format
