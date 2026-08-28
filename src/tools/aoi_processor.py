"""
Custom Study Area (AOI) Processor for GeoLab-Agent.
Processes user-uploaded ESRI Shapefiles (zipped .shp, .shx, .dbf, .prj), GeoJSON (.geojson),
and Google Earth KML (.kml) files.
Extracts spatial extents, calculates planimetric area and perimeters, and prepares boundary layers.
"""

import io
import json
import zipfile
from typing import Dict, Any, Tuple
import geopandas as gpd  # type: ignore
from shapely.geometry import shape, mapping  # type: ignore


def process_uploaded_aoi(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses and standardizes an uploaded vector study area boundary.

    Args:
        file_bytes: Raw binary bytes of the uploaded file.
        filename: Name of the uploaded file (e.g. 'study_area.zip', 'boundary.geojson').

    Returns:
        Dict containing:
            - success: Boolean indicating success.
            - aoi_name: Clean display name of the study area.
            - format: Detected format ('shapefile_zip', 'geojson', 'kml').
            - crs: Coordinate reference system string.
            - bbox: Bounding box [west, south, east, north] in WGS84 EPSG:4326.
            - center: [lat, lon] centroid coordinates.
            - area_km2: Calculated planimetric area in square kilometers.
            - area_ha: Calculated planimetric area in hectares.
            - perimeter_km: Calculated perimeter in kilometers.
            - feature_count: Total polygon features in the dataset.
            - geojson_layer: Standardized GeoJSON FeatureCollection dictionary.
            - error: Error message if parsing fails.
    """
    clean_name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    file_lower = filename.lower()

    try:
        if file_lower.endswith(".zip"):
            # Handle zipped Shapefile archive
            with io.BytesIO(file_bytes) as zip_buffer:
                gdf = gpd.read_file(zip_buffer)
                fmt_detected = "ESRI Shapefile Archive (.zip)"

        elif file_lower.endswith((".geojson", ".json")):
            # Handle GeoJSON
            with io.BytesIO(file_bytes) as json_buffer:
                gdf = gpd.read_file(json_buffer)
                fmt_detected = "OGC GeoJSON Vector (.geojson)"

        elif file_lower.endswith(".kml"):
            # Handle Google Earth KML (requires fiona driver or standard parser)
            try:
                import fiona  # type: ignore
                fiona.drvsupport.supported_drivers["KML"] = "rw"
                with io.BytesIO(file_bytes) as kml_buffer:
                    gdf = gpd.read_file(kml_buffer, driver="KML")
                    fmt_detected = "Google Earth KML Vector (.kml)"
            except Exception:

                # Fallback simple geojson parse if KML driver is absent
                with io.BytesIO(file_bytes) as kml_buffer:
                    gdf = gpd.read_file(kml_buffer)
                    fmt_detected = "KML Vector"
        else:
            return {
                "success": False,
                "error": f"Unsupported vector file extension: '{filename}'. Please upload a zipped Shapefile (.zip), GeoJSON (.geojson), or KML (.kml)."
            }

        if gdf.empty:
            return {
                "success": False,
                "error": "The uploaded vector file contains no geometry features."
            }

        # Reproject to WGS84 (EPSG:4326) if necessary
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # Compute projected area using Cylindrical Equal Area (EPSG:6933) or UTM approximation for accurate metrics
        try:
            gdf_projected = gdf.to_crs(epsg=6933)
            area_m2 = float(gdf_projected.geometry.area.sum())
            perim_m = float(gdf_projected.geometry.length.sum())
        except Exception:
            # Fallback estimation for spherical lat/lon
            bounds = gdf.total_bounds
            width_deg = bounds[2] - bounds[0]
            height_deg = bounds[3] - bounds[1]
            area_m2 = width_deg * 111320 * height_deg * 111320 * 0.7
            perim_m = (width_deg + height_deg) * 2 * 111320

        area_km2 = round(area_m2 / 1_000_000, 2)
        area_ha = round(area_m2 / 10_000, 2)
        perimeter_km = round(perim_m / 1000, 2)

        # Calculate bounding box [west, south, east, north]
        minx, miny, maxx, maxy = gdf.total_bounds
        bbox = [float(minx), float(miny), float(maxx), float(maxy)]

        # Calculate Centroid
        if hasattr(gdf, "union_all"):
            centroid = gdf.union_all().centroid
        else:
            centroid = gdf.unary_union.centroid
        center = [round(float(centroid.y), 5), round(float(centroid.x), 5)]


        # Convert to standardized GeoJSON FeatureCollection
        features = []
        for idx, row in gdf.iterrows():
            props = {
                "id": f"aoi_feat_{idx+1}",
                "name": f"{clean_name} - Feature {idx+1}",
                "layer_type": "custom_aoi_boundary",
                "area_km2": area_km2,
                "perimeter_km": perimeter_km
            }
            # Include original attribute columns if non-spatial and serializable
            for col in gdf.columns:
                if col != "geometry" and col != "layer_type":
                    val = row[col]
                    if isinstance(val, (str, int, float, bool)):
                        props[col] = val
                    else:
                        props[col] = str(val)

            features.append({
                "type": "Feature",
                "properties": props,
                "geometry": mapping(row["geometry"])
            })

        geojson_layer = {
            "type": "FeatureCollection",
            "layer_name": f"Study Area: {clean_name}",
            "layer_type": "custom_aoi_boundary",
            "features": features
        }

        return {
            "success": True,
            "aoi_name": clean_name,
            "format": fmt_detected,
            "crs": "EPSG:4326 (WGS 84)",
            "bbox": bbox,
            "center": center,
            "area_km2": area_km2,
            "area_ha": area_ha,
            "perimeter_km": perimeter_km,
            "feature_count": len(gdf),
            "geojson_layer": geojson_layer,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse vector boundary: {str(e)}"
        }
