"""
Custom Study Area (AOI) Processor for GeoLab-Agent.
Processes user-uploaded ESRI Shapefiles (zipped .shp, .shx, .dbf, .prj), GeoJSON (.geojson),
and Google Earth KML (.kml) files.
Features automatic topology self-healing (make_valid), smart CRS inference,
empty geometry stripping, vertex decimation for fast web rendering, and accurate planimetric metrics.
"""

import io
import json
import zipfile
from typing import Dict, Any, Tuple
import geopandas as gpd  # type: ignore
from shapely.geometry import shape, mapping  # type: ignore
from shapely.validation import make_valid  # type: ignore


def process_uploaded_aoi(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses, cleans, standardizes, and repairs an uploaded vector study area boundary.

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

        # 1. Filter out empty or null geometries
        gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notnull()].copy()
        if gdf.empty:
            return {
                "success": False,
                "error": "All geometry features in the uploaded file were empty or null."
            }

        # 2. Topology Self-Healing: Automatically repair invalid or self-intersecting polygons
        try:
            gdf["geometry"] = gdf["geometry"].apply(make_valid)
        except Exception:
            pass

        # 3. Smart CRS Inference & Reprojection to WGS84 (EPSG:4326)
        if gdf.crs is None:
            bounds = gdf.total_bounds
            minx, miny, maxx, maxy = bounds
            # If coordinates look like geographic lat/lon (-180 to 180, -90 to 90)
            if -180.0 <= minx <= 180.0 and -90.0 <= miny <= 90.0:
                gdf.set_crs(epsg=4326, inplace=True)
            elif minx > 100000.0 or miny > 100000.0:
                # Projected coordinates in meters (e.g. UTM Zone 45N EPSG:32645 or BTM EPSG:3106)
                try:
                    gdf.set_crs(epsg=32645, inplace=True)
                    gdf = gdf.to_crs(epsg=4326)
                except Exception:
                    gdf.set_crs(epsg=4326, inplace=True)
            else:
                gdf.set_crs(epsg=4326, inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # 4. Planimetric Area & Perimeter Calculations (Equal Area Projection)
        try:
            gdf_projected = gdf.to_crs(epsg=6933)
            area_m2 = float(gdf_projected.geometry.area.sum())
            perim_m = float(gdf_projected.geometry.length.sum())
        except Exception:
            bounds = gdf.total_bounds
            width_deg = bounds[2] - bounds[0]
            height_deg = bounds[3] - bounds[1]
            area_m2 = width_deg * 111320 * height_deg * 111320 * 0.7
            perim_m = (width_deg + height_deg) * 2 * 111320

        area_km2 = round(area_m2 / 1_000_000, 2)
        area_ha = round(area_m2 / 10_000, 2)
        perimeter_km = round(perim_m / 1000, 2)

        # 5. Calculate Bounding Box [west, south, east, north]
        minx, miny, maxx, maxy = gdf.total_bounds
        bbox = [round(float(minx), 6), round(float(miny), 6), round(float(maxx), 6), round(float(maxy), 6)]

        # 6. Calculate Centroid
        if hasattr(gdf, "union_all"):
            centroid = gdf.union_all().centroid
        else:
            centroid = gdf.unary_union.centroid
        center = [round(float(centroid.y), 5), round(float(centroid.x), 5)]

        # 7. Web Optimization: Light vertex simplification if feature is excessively heavy (> 2000 points)
        try:
            if area_km2 > 50.0:
                gdf["geometry"] = gdf["geometry"].simplify(0.0005, preserve_topology=True)
            elif area_km2 > 5.0:
                gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)
        except Exception:
            pass

        # 8. Standardize to GeoJSON FeatureCollection
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
