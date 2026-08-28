"""
Multi-Format Geospatial & Municipal Exporter Hub for GeoLab-Agent.
Generates:
1. OGC KML (.kml) for Google Earth Pro & 3D Web GIS
2. GeoJSON (.geojson) for QGIS, ArcGIS, and WebGIS
3. Georeferenced GeoTIFF (.tif) for Remote Sensing analysis
4. Tabular Metrics CSV (.csv) for statistical software
5. Printable Municipal Brief (.html / PDF)
6. Academic Markdown Brief (.md)
7. 1-Click Master GIS Research Package (.zip) containing all above assets
"""

import io
import json
import zipfile
from typing import Dict, Any, List, Tuple
from .raster_exporter import generate_geotiff_raster


def convert_geojson_to_kml(geojson_dict: Dict[str, Any], title: str = "GeoLab-Agent Spatial Layers") -> str:
    """
    Converts a standard GeoJSON FeatureCollection into valid OGC KML 2.2 XML
    for 3D visualization in Google Earth Pro and Google Earth Web.
    """
    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        f'  <name>{title}</name>',
        '  <open>1</open>',
        '  <Style id="polyStyle">',
        '    <LineStyle><color>ff0284c7</color><width>2</width></LineStyle>',
        '    <PolyStyle><color>7f0284c7</color></PolyStyle>',
        '  </Style>',
        '  <Style id="heatStyle">',
        '    <LineStyle><color>ffe74c3c</color><width>2</width></LineStyle>',
        '    <PolyStyle><color>7fe74c3c</color></PolyStyle>',
        '  </Style>',
        '  <Style id="greenStyle">',
        '    <LineStyle><color>ff2ecc71</color><width>2</width></LineStyle>',
        '    <PolyStyle><color>7f2ecc71</color></PolyStyle>',
        '  </Style>',
        '  <Style id="waterStyle">',
        '    <LineStyle><color>ff3498db</color><width>2</width></LineStyle>',
        '    <PolyStyle><color>7f3498db</color></PolyStyle>',
        '  </Style>'
    ]

    for feat in geojson_dict.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        feat_name = props.get("name") or props.get("zone_name") or props.get("id") or "Spatial Feature"
        
        # Build HTML table for balloon description in Google Earth
        desc_rows = [f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in props.items()]
        desc_html = f"<h3>{feat_name}</h3><table border='1' cellpadding='4' cellspacing='0'>{''.join(desc_rows)}</table>"

        # Style selection
        style_ref = "#polyStyle"
        layer_type = props.get("layer_type", "")
        if "heat" in layer_type or "lst" in layer_type:
            style_ref = "#heatStyle"
        elif "green" in layer_type or "ndvi" in layer_type:
            style_ref = "#greenStyle"
        elif "flood" in layer_type or "runoff" in layer_type:
            style_ref = "#waterStyle"

        kml_lines.append('  <Placemark>')
        kml_lines.append(f'    <name>{feat_name}</name>')
        kml_lines.append(f'    <description><![CDATA[{desc_html}]]></description>')
        kml_lines.append(f'    <styleUrl>{style_ref}</styleUrl>')

        geom_type = geom.get("type", "")
        if geom_type == "Polygon":
            kml_lines.append('    <Polygon>')
            kml_lines.append('      <extrude>1</extrude>')
            kml_lines.append('      <altitudeMode>clampToGround</altitudeMode>')
            kml_lines.append('      <outerBoundaryIs><LinearRing><coordinates>')
            for ring in geom.get("coordinates", []):
                coord_strs = [f"{pt[0]},{pt[1]},0" for pt in ring]
                kml_lines.append("        " + " ".join(coord_strs))
            kml_lines.append('      </coordinates></LinearRing></outerBoundaryIs>')
            kml_lines.append('    </Polygon>')
            
        elif geom_type == "Point":
            coords = geom.get("coordinates", [0, 0])
            kml_lines.append('    <Point>')
            kml_lines.append(f'      <coordinates>{coords[0]},{coords[1]},0</coordinates>')
            kml_lines.append('    </Point>')

        elif geom_type == "MultiPolygon":
            kml_lines.append('    <MultiGeometry>')
            for poly in geom.get("coordinates", []):
                kml_lines.append('      <Polygon><outerBoundaryIs><LinearRing><coordinates>')
                for ring in poly:
                    coord_strs = [f"{pt[0]},{pt[1]},0" for pt in ring]
                    kml_lines.append("        " + " ".join(coord_strs))
                kml_lines.append('      </coordinates></LinearRing></outerBoundaryIs></Polygon>')
            kml_lines.append('    </MultiGeometry>')

        kml_lines.append('  </Placemark>')

    kml_lines.append('</Document>')
    kml_lines.append('</kml>')
    return "\n".join(kml_lines)


def generate_printable_html(res_data: Dict[str, Any]) -> str:
    """Generates an executive municipal briefing in clean, printable HTML."""
    loc = res_data.get("target_location", "City")
    dom = res_data.get("identified_domain", "Urban Spatial Planning")
    md_content = res_data.get("policy_report_markdown", "")
    coords = res_data.get("center_coordinates", [22.8456, 89.5403])
    import html
    escaped_md = html.escape(md_content)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GeoLab-Agent Municipal Planning Brief - {loc}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 40px auto; padding: 20px; }}
        .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 15px; margin-bottom: 25px; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin-bottom: 20px; font-size: 13px; }}
        h1, h2, h3 {{ color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #f1f5f9; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 12px; color: #64748b; text-align: center; }}
        @media print {{ .no-print {{ display: none; }} body {{ margin: 10px; }} }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px;">
        <button onclick="window.print()" style="background:#0284c7; color:white; border:none; padding:10px 20px; font-weight:bold; border-radius:6px; cursor:pointer;">🖨️ Print / Save as PDF</button>
    </div>
    <div class="header">
        <span class="badge">GEOLAB POLICY BRIEF</span>
        <h1>🌍 GeoLab-Agent Spatial Investigation: {loc}</h1>
        <p><strong>Department of Urban and Regional Planning (URP), KUET</strong></p>
    </div>
    <div class="meta-box">
        <strong>Domain:</strong> {dom} &nbsp;|&nbsp; 
        <strong>Coordinates:</strong> {coords[0]:.4f}° N, {coords[1]:.4f}° E &nbsp;|&nbsp;
        <strong>Compliance Status:</strong> {res_data.get('compliance_verdict', 'Standard Audit')}
    </div>
    <div class="content">
        <pre style="white-space: pre-wrap; font-family: inherit; font-size: 14px;">{escaped_md}</pre>
    </div>
    <div class="footer">
        Generated by Autonomous Multi-Agent GeoAI Engine (GeoLab-Agent) | Department of Urban & Regional Planning, Khulna University of Engineering & Technology (KUET)
    </div>
</body>
</html>"""


def generate_master_zip_package(result_dict: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Bundles all spatial layers, rasters, tabular metrics, and municipal reports
    into a single 1-click Master Research Package (.zip).
    """
    loc_name = result_dict.get("target_location", "City")
    loc_clean = loc_name.replace(" ", "_")
    zip_filename = f"GeoLab_Master_Package_{loc_clean}.zip"

    # 1. GeoJSON Layer Package
    combined_geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": []
    }
    for layer in result_dict.get("geojson_layers", []):
        if "features" in layer:
            combined_geojson["features"].extend(layer["features"])
    geojson_str = json.dumps(combined_geojson, indent=2)

    # 2. Google Earth KML
    kml_str = convert_geojson_to_kml(combined_geojson, title=f"GeoLab-Agent - {loc_name}")

    # 3. CSV Metrics Table
    import csv
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(["Tool_and_Metric", "Observed_Value"])
    for k, v in result_dict.get("collected_metrics", {}).items():
        writer.writerow([k, str(v)])
    csv_str = csv_buf.getvalue()

    # 4. GeoTIFF Raster
    geotiff_bytes, tif_name, _ = generate_geotiff_raster(
        target_location=loc_name,
        raster_type="auto",
        metrics=result_dict.get("collected_metrics", {})
    )

    # 5. HTML Report
    html_str = generate_printable_html(result_dict)

    # 6. Markdown Report
    md_str = result_dict.get("policy_report_markdown", "")

    # 7. Data Dictionary README
    readme_text = f"""========================================================================
GeoLab-Agent: Autonomous Multi-Agent GeoAI Research Package
Target Study Area: {loc_name}
Institution: Department of Urban & Regional Planning, KUET
========================================================================

CONTENTS IN THIS ARCHIVE:
1. {loc_clean}_Layers.geojson          -> OGC GeoJSON vector layers (QGIS, ArcGIS, Mapbox)
2. {loc_clean}_GoogleEarth.kml        -> 3D satellite visualization for Google Earth Pro
3. {tif_name}                         -> 32-bit floating-point GeoTIFF (WGS84 EPSG:4326)
4. {loc_clean}_Metrics.csv            -> Geospatial and physical indicators table
5. {loc_clean}_Municipal_Report.html  -> Printable executive brief with KUET URP styling
6. {loc_clean}_Policy_Brief.md        -> Academic Markdown policy synthesis report

COORDINATE REFERENCE SYSTEM:
EPSG:4326 - WGS 84 (Geographic Lat/Lon)

SOFTWARE COMPATIBILITY:
- QGIS 3.x+ (Drag and drop GeoJSON and GeoTIFF)
- ArcGIS Pro / ArcMap (Add Data -> GeoJSON/KML/GeoTIFF)
- Google Earth Pro (File -> Open -> KML)
- R, Python, Pandas, GeoPandas, Rasterio

Generated automatically by GeoLab-Agent (KUET URP).
========================================================================
"""

    # Build ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{loc_clean}_Layers.geojson", geojson_str)
        zf.writestr(f"{loc_clean}_GoogleEarth.kml", kml_str)
        zf.writestr(tif_name, geotiff_bytes)
        zf.writestr(f"{loc_clean}_Metrics.csv", csv_str)
        zf.writestr(f"{loc_clean}_Municipal_Report.html", html_str)
        zf.writestr(f"{loc_clean}_Policy_Brief.md", md_str)
        zf.writestr("README_DATA_DICTIONARY.txt", readme_text)

    return zip_buffer.getvalue(), zip_filename
