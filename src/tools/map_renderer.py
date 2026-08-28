"""
Interactive Geospatial Map Rendering Engine using Folium and Leaflet.
Renders multi-layer GeoJSON layers, choropleths, thermal contours, and isochrones on cartographic base maps.
"""

from typing import List, Dict, Any, Optional
try:
    import folium
    from folium.plugins import Fullscreen, MeasureControl
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False



def build_interactive_folium_map(
    center_coords: List[float] = [22.8456, 89.5403],
    zoom_start: int = 13,
    geojson_layers: Optional[List[Dict[str, Any]]] = None
):
    """
    Builds a multi-layered, dark-themed or satellite interactive Folium map with dynamic GeoJSON layers.
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

    # Marker for city center
    folium.Marker(
        location=center_coords,
        popup="<b>Urban Core Analysis Center</b>",
        tooltip="Analysis Origin",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    if geojson_layers:
        for layer in geojson_layers:
            layer_type = layer.get("layer_type", "default")
            
            # Styling based on GeoAI layer type
            if layer_type == "isochrones":
                layer_name = "🚶 15-Min Walkability Isochrones"
                def style_fn(feature):
                    props = feature.get("properties", {})
                    return {
                        "fillColor": props.get("fill_color", "#3498db"),
                        "color": props.get("fill_color", "#3498db"),
                        "weight": 2,
                        "fillOpacity": props.get("fill_opacity", 0.3)
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
                    fields=[k for k in layer["features"][0]["properties"].keys() if k != "stroke_color"] if layer.get("features") else [],
                    aliases=[f"{k.replace('_', ' ').capitalize()}: " for k in layer["features"][0]["properties"].keys() if k != "stroke_color"] if layer.get("features") else [],
                    style="background-color: #1e293b; color: #f8fafc; font-family: Inter, sans-serif; font-size: 12px; padding: 8px; border-radius: 6px;"
                ) if layer.get("features") else None
            ).add_to(m)

    # Add useful Leaflet map plugins
    Fullscreen(position="topright").add_to(m)
    MeasureControl(position="topleft").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    
    return m
