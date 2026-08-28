"""
Interactive Geospatial Map Rendering Engine using Folium and Leaflet.
Renders multi-layer GeoJSON layers, choropleths, thermal contours, isochrones,
and georeferenced multi-spectral raster overlays (NDVI, NDWI, DEM, Slope, LST, Flow Accumulation, LULC)
on cartographic base maps.
"""

import io
import base64
from typing import List, Dict, Any, Optional
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.image as mpimg  # type: ignore
import rasterio  # type: ignore

try:
    import folium  # type: ignore
    from folium.plugins import Fullscreen, MeasureControl  # type: ignore
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from src.tools.raster_exporter import generate_geotiff_raster, AVAILABLE_RASTER_TYPES


# Colormap mapping for all 13 remote sensing and terrain indices
RASTER_COLORMAPS = {
    "lulc": "tab10",
    "ndvi": "RdYlGn",
    "ndwi": "YlGnBu",
    "ndbi": "YlOrRd",
    "dem": "terrain",
    "slope": "magma",
    "aspect": "twilight",
    "flow_accumulation": "PuBu",
    "bsi": "YlOrBr",
    "evi": "YlGn",
    "lst": "plasma",
    "sponge_runoff": "coolwarm",
    "flood_depth": "Blues",
}


def build_interactive_folium_map(
    center_coords: List[float] = [22.8456, 89.5403],
    zoom_start: int = 13,
    geojson_layers: Optional[List[Dict[str, Any]]] = None,
    active_raster_type: Optional[str] = None,
    target_location: str = "Khulna",
    metrics: Optional[Dict[str, Any]] = None,
    custom_bbox: Optional[List[float]] = None
):
    """
    Builds a multi-layered, dark-themed or satellite interactive Folium map with dynamic GeoJSON layers
    and georeferenced raster image overlays.
    """
    if not FOLIUM_AVAILABLE:
        return {
            "type": "FoliumMapFallback",
            "center": center_coords,
            "zoom": zoom_start,
            "layers_count": len(geojson_layers) if geojson_layers else 0,
            "status": "Folium library not loaded, raw layer metadata available."
        }

    # Create base map with CartoDB DarkMatter for a sleek, modern GeoAI aesthetic
    m = folium.Map(
        location=center_coords,
        zoom_start=zoom_start,
        tiles="CartoDB dark_matter",
        name="Dark Matter (Modern GeoAI)",
        control_scale=True,
    )
    
    # Add Esri World Imagery (Satellite) alternative base layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite Imagery",
        overlay=False,
        control=True
    ).add_to(m)

    # Add OpenStreetMap alternative base layer
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap Standard",
        overlay=False,
        control=True
    ).add_to(m)

    # Add Georeferenced Raster Image Overlay if requested
    if active_raster_type and active_raster_type in AVAILABLE_RASTER_TYPES:
        try:
            tif_bytes, tif_name, tif_meta = generate_geotiff_raster(
                target_location=target_location,
                raster_type=active_raster_type,
                metrics=metrics or {},
                custom_bbox=tuple(custom_bbox) if custom_bbox else None
            )
            
            with rasterio.open(io.BytesIO(tif_bytes)) as ds:
                arr = ds.read(1).astype(float)
                bounds = ds.bounds
                west, south, east, north = bounds.left, bounds.bottom, bounds.right, bounds.top

            # Colormapping
            cmap_name = RASTER_COLORMAPS.get(active_raster_type, "viridis")
            cmap = plt.get_cmap(cmap_name)

            if active_raster_type == "lulc":
                # Discrete classification coloring (1:Water, 2:Forest, 3:Agri, 4:Urban, 5:Bare)
                rgba_img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
                color_map = {
                    1: [0, 119, 190, 220],   # Water (Blue)
                    2: [27, 94, 32, 220],    # Forest (Dark Green)
                    3: [139, 195, 74, 220],  # Agri (Light Green)
                    4: [211, 47, 47, 230],   # Built-up (Red)
                    5: [215, 204, 200, 210]  # Bare (Tan)
                }
                for class_val, rgba in color_map.items():
                    mask = (arr == class_val)
                    rgba_img[mask] = rgba
            else:
                vmin = np.nanmin(arr)
                vmax = np.nanmax(arr)
                if vmax == vmin:
                    vmax += 1.0
                norm_arr = np.clip((arr - vmin) / (vmax - vmin), 0.0, 1.0)
                rgba_img = (cmap(norm_arr) * 255).astype(np.uint8)
                # Set vibrant visibility opacity
                rgba_img[:, :, 3] = 205

            buf = io.BytesIO()
            mpimg.imsave(buf, rgba_img, format="png")
            b64_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

            raster_display_name = AVAILABLE_RASTER_TYPES[active_raster_type]["name"]
            folium.raster_layers.ImageOverlay(
                image=b64_url,
                bounds=[[south, west], [north, east]],
                opacity=0.82,
                name=f"🛰️ {raster_display_name}",
                interactive=True,
                cross_origin=False,
                zindex=2
            ).add_to(m)

            # Fit map to bounds so user immediately sees the visual raster overlay
            m.fit_bounds([[south, west], [north, east]])

        except Exception:
            pass

    # Marker for city center
    folium.Marker(
        location=center_coords,
        popup=f"<b>Analysis Center: {target_location}</b>",
        tooltip="Analysis Center",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Vector layers rendering
    if geojson_layers:
        for layer in geojson_layers:
            layer_type = layer.get("layer_type", "default")
            
            # Styling based on GeoAI layer type
            if layer_type == "custom_aoi_boundary":
                layer_name = "📁 Study Area Boundary"
                def style_fn(feature):
                    return {
                        "fillColor": "#38bdf8",
                        "color": "#0284c7",
                        "weight": 3,
                        "fillOpacity": 0.15,
                        "dashArray": "5, 5"
                    }
            elif layer_type == "isochrones":
                layer_name = "🚶 15-Min Walkability Isochrones"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("fill_color", "#3498db"),
                        "color": props.get("fill_color", "#3498db"),
                        "weight": 2,
                        "fillOpacity": 0.3
                    }
            elif layer_type == "thermal_hotspots":
                layer_name = "🔥 Landsat LST Thermal Hotspots"
                def style_fn(feature):
                    return {
                        "fillColor": "#e74c3c",
                        "color": "#c0392b",
                        "weight": 2,
                        "fillOpacity": 0.55
                    }
            elif layer_type == "ndvi_deficit":
                layer_name = "🌳 Sentinel-2 Canopy Deficit Zones"
                def style_fn(feature):
                    return {
                        "fillColor": "#27ae60",
                        "color": "#2ecc71",
                        "weight": 2,
                        "fillOpacity": 0.45
                    }
            elif layer_type == "flood_hazard":
                layer_name = "🌊 Coastal & Flood Hazard Zones"
                def style_fn(feature):
                    return {
                        "fillColor": "#2980b9",
                        "color": "#3498db",
                        "weight": 2,
                        "fillOpacity": 0.5
                    }
            elif layer_type == "vulnerability_zones":
                layer_name = "⚠️ Zoning & Socio-Spatial Vulnerability"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("stroke_color", "#f39c12"),
                        "color": props.get("stroke_color", "#f39c12"),
                        "weight": 2,
                        "fillOpacity": 0.4
                    }
            elif layer_type == "lulc_change":
                layer_name = "🔄 Multi-Temporal LULC & Sprawl Conversions"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("stroke_color", "#e67e22"),
                        "color": props.get("stroke_color", "#e67e22"),
                        "weight": 2,
                        "fillOpacity": 0.5
                    }
            elif layer_type == "sponge_city_runoff":
                layer_name = "💧 Sponge City & Stormwater Retention Sites"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("stroke_color", "#0ea5e9"),
                        "color": props.get("stroke_color", "#0ea5e9"),
                        "weight": 2,
                        "fillOpacity": 0.55
                    }
            elif layer_type == "spatial_equity_deficit":
                layer_name = "🏥 Spatial Equity & Healthcare Deficit Wards"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("stroke_color", "#e11d48"),
                        "color": props.get("stroke_color", "#e11d48"),
                        "weight": 2,
                        "fillOpacity": 0.5
                    }
            else:
                layer_name = f"📍 {layer_type.capitalize()} Layer"
                def style_fn(feature):
                    return {"fillColor": "#9b59b6", "color": "#8e44ad", "weight": 2, "fillOpacity": 0.4}

            # Add GeoJSON layer with popups
            folium.GeoJson(
                layer,
                name=layer_name,
                style_function=style_fn,
                tooltip=folium.GeoJsonTooltip(
                    fields=[k for k in layer["features"][0]["properties"].keys() if k not in ["stroke_color", "fill_color", "fill_opacity"]] if layer.get("features") else [],
                    aliases=[f"{k.replace('_', ' ').capitalize()}: " for k in layer["features"][0]["properties"].keys() if k not in ["stroke_color", "fill_color", "fill_opacity"]] if layer.get("features") else [],
                    style="background-color: #1e293b; color: #f8fafc; font-family: Inter, sans-serif; font-size: 12px; padding: 8px; border-radius: 6px;"
                ) if layer.get("features") else None
            ).add_to(m)

    # Add useful Leaflet map plugins
    Fullscreen(position="topright").add_to(m)
    MeasureControl(position="topleft").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    
    return m
