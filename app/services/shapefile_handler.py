"""
Shapefile handling service for processing user uploads.
"""

import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import ee
import geopandas as gpd
from shapely.geometry import mapping

logger = logging.getLogger(__name__)


class ShapefileHandler:
    """Handler for processing shapefile uploads."""

    REQUIRED_EXTENSIONS = {'.shp', '.shx', '.dbf'}
    OPTIONAL_EXTENSIONS = {'.prj', '.cpg', '.sbn', '.sbx', '.xml'}

    def __init__(self, upload_dir: Path):
        """
        Initialize the shapefile handler.

        Args:
            upload_dir: Directory for storing uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def process_upload(
        self,
        file_content: bytes,
        filename: str,
        session_id: str
    ) -> Tuple[gpd.GeoDataFrame, Path]:
        """
        Process an uploaded shapefile (as zip or individual file).

        Args:
            file_content: Raw file content
            filename: Original filename
            session_id: Unique session identifier

        Returns:
            Tuple of (GeoDataFrame, path to extracted files)
        """
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        try:
            if filename.lower().endswith('.zip'):
                return self._process_zip(file_content, session_dir)
            elif filename.lower().endswith('.geojson'):
                return self._process_geojson(file_content, session_dir, filename)
            elif filename.lower().endswith('.shp'):
                raise ValueError(
                    "Please upload a ZIP file containing all shapefile components "
                    "(.shp, .shx, .dbf, and optionally .prj)"
                )
            else:
                raise ValueError(f"Unsupported file format: {filename}")
        except Exception as e:
            # Clean up on error
            shutil.rmtree(session_dir, ignore_errors=True)
            raise

    def _process_zip(
        self,
        file_content: bytes,
        session_dir: Path
    ) -> Tuple[gpd.GeoDataFrame, Path]:
        """Process a zipped shapefile."""
        zip_path = session_dir / "upload.zip"

        # Save zip file
        with open(zip_path, 'wb') as f:
            f.write(file_content)

        # Extract
        extract_dir = session_dir / "extracted"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find .shp file
        shp_files = list(extract_dir.rglob("*.shp"))
        if not shp_files:
            raise ValueError("No .shp file found in the uploaded ZIP")

        shp_path = shp_files[0]

        # Validate components
        self._validate_shapefile_components(shp_path)

        # Read with geopandas
        gdf = gpd.read_file(shp_path)

        # Ensure CRS is set (default to WGS84 if missing)
        if gdf.crs is None:
            logger.warning("No CRS found in shapefile, assuming WGS84 (EPSG:4326)")
            gdf = gdf.set_crs("EPSG:4326")

        # Reproject to WGS84 if needed
        if gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")

        return gdf, extract_dir

    def _process_geojson(
        self,
        file_content: bytes,
        session_dir: Path,
        filename: str
    ) -> Tuple[gpd.GeoDataFrame, Path]:
        """Process a GeoJSON file."""
        geojson_path = session_dir / filename

        with open(geojson_path, 'wb') as f:
            f.write(file_content)

        gdf = gpd.read_file(geojson_path)

        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")

        return gdf, session_dir

    def _validate_shapefile_components(self, shp_path: Path) -> None:
        """Validate that all required shapefile components exist."""
        base_path = shp_path.with_suffix('')
        missing = []

        for ext in self.REQUIRED_EXTENSIONS:
            if not base_path.with_suffix(ext).exists():
                missing.append(ext)

        if missing:
            raise ValueError(
                f"Missing required shapefile components: {', '.join(missing)}. "
                "Please include .shp, .shx, and .dbf files."
            )

    @staticmethod
    def gdf_to_ee_geometry(gdf: gpd.GeoDataFrame) -> ee.Geometry:
        """
        Convert a GeoDataFrame to an Earth Engine Geometry.

        Args:
            gdf: GeoDataFrame to convert

        Returns:
            Earth Engine Geometry
        """
        # Dissolve all geometries into one
        dissolved = gdf.dissolve()

        # Get the geometry as GeoJSON
        geojson = mapping(dissolved.geometry.values[0])

        # Convert to EE geometry
        return ee.Geometry(geojson)

    @staticmethod
    def gdf_to_ee_feature_collection(gdf: gpd.GeoDataFrame) -> ee.FeatureCollection:
        """
        Convert a GeoDataFrame to an Earth Engine FeatureCollection.

        Args:
            gdf: GeoDataFrame to convert

        Returns:
            Earth Engine FeatureCollection
        """
        features = []
        for idx, row in gdf.iterrows():
            geom = ee.Geometry(mapping(row.geometry))
            props = {k: v for k, v in row.items() if k != 'geometry'}
            # Convert non-serializable types
            props = {k: str(v) if not isinstance(v, (int, float, str, bool, type(None))) else v
                     for k, v in props.items()}
            features.append(ee.Feature(geom, props))

        return ee.FeatureCollection(features)

    @staticmethod
    def calculate_area_km2(gdf: gpd.GeoDataFrame) -> float:
        """
        Calculate the total area of geometries in km².

        Args:
            gdf: GeoDataFrame

        Returns:
            Area in square kilometers
        """
        # Project to a suitable CRS for area calculation
        gdf_projected = gdf.to_crs("EPSG:3857")
        area_m2 = gdf_projected.geometry.area.sum()
        return area_m2 / 1_000_000  # Convert to km²

    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up uploaded files for a session.

        Args:
            session_id: Session identifier
        """
        session_dir = self.upload_dir / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"Cleaned up session: {session_id}")
