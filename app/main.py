"""
GeoLab-Agent: Autonomous Multi-Agent GeoAI Web Platform.
Built with Streamlit, Folium, and LangGraph.
"""

import os
import sys
import json
from pathlib import Path


# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()

from src.agents.workflow import run_geolab_workflow
from src.tools.map_renderer import build_interactive_folium_map
from src.tools.raster_exporter import generate_geotiff_raster
from src.tools.exporter_hub import convert_geojson_to_kml, generate_printable_html, generate_master_zip_package



# Page Configuration
st.set_page_config(
    page_title="GeoLab-Agent | Autonomous GeoAI Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom High-End Modern GeoAI Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Glassmorphism */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d1117 0%, #030712 100%);
        color: #f3f4f6;
    }

    /* Metric Cards */
    .metric-box {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #38bdf8;
    }

    /* Agent Status Pill */
    .agent-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Tab and Button Polish */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None
if "current_query" not in st.session_state:
    st.session_state.current_query = "Analyze urban heat island intensity and green space canopy deficit for Khulna city"

# Sidebar Branding & Control Panel
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 2.2rem;">🌍</span>
        <div>
            <h2 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #f8fafc;">GeoLab-Agent</h2>
            <p style="margin: 0; font-size: 0.75rem; color: #38bdf8; font-weight: 600;">Autonomous GeoAI & Spatial LLM Platform</p>
        </div>
    </div>

    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Curated Research Scenarios")
    
    scenarios = {
        "🌿 Khulna: Heat Island & Green Space Canopy": "Analyze urban heat island intensity and green space canopy deficit for Khulna city",
        "🚶 Dhaka: 15-Minute City & Walkability": "Perform 15-minute city walkability isochrone and transit access audit for Dhaka",
        "💧 Cox's Bazar: Sponge City & Coastal Stormwater": "Simulate sponge city stormwater runoff and drainage retention for Cox's Bazar",
        "🌲 Sylhet: Urban Green Canopy & Microclimate": "Audit urban vegetative canopy cover and thermal microclimate for Sylhet",
        "🏥 Rangpur: Healthcare Spatial Equity & 2SFCA": "Audit spatial equity and healthcare clinic accessibility deficit for Rangpur",
        "🌊 Chittagong: Coastal Flood & Tidal Hazard": "Simulate 25-year flood inundation and zoning setback vulnerability for Chittagong",
        "🔄 Rajshahi: Multi-Temporal LULC & Urban Sprawl": "Analyze urban sprawl and land use change dynamics for Rajshahi",
        "🏭 Mymensingh: Atmospheric Air Pollution (NO2/PM2.5)": "Evaluate atmospheric air pollution and industrial emission corridors for Mymensingh",
        "🌐 Tokyo: Global 15-Minute Walkability Benchmark": "Perform 15-minute city walkability isochrone and transit access audit for Tokyo",
        "🏙️ London: Comprehensive Multi-Criteria Urban Audit": "Conduct a comprehensive urban planning and environmental resilience audit for London"
    }
    
    selected_scenario = st.selectbox("Select a benchmark scenario:", list(scenarios.keys()))
    if st.button("🚀 Load & Run Scenario", use_container_width=True):
        st.session_state.current_query = scenarios[selected_scenario]
        st.session_state.agent_result = run_geolab_workflow(scenarios[selected_scenario])
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ System Configuration")
    api_status = "🟢 Active (Configured)" if os.environ.get("GEMINI_API_KEY") else "🟡 Synthetic / Sandbox Mode"
    st.caption(f"**LLM Engine:** Gemini 2.5 Flash ({api_status})")
    st.caption("**Geocoding:** Universal OSM Nominatim & Curated Registry")
    st.caption("**Earth Observation:** Sentinel-2, Landsat-9, Sentinel-5P")
    st.caption("**Network Engine:** OSMnx & Graph Theory")
    st.caption("**Hydrology:** SCS-CN Sponge City Model")
    st.caption("**Institution:** KUET Urban & Regional Planning (URP)")
    
    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.72rem; color: #64748b; text-align: center;'>"
        "Designed for Academic Publications & Graduate Research Fellowships<br>"
        "Developed by KUET URP Researchers"
        "</div>", 
        unsafe_allow_html=True
    )

# Main Application Layout
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div>
        <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #f8fafc;">Autonomous Spatial Planning & GeoAI Studio</h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Search any city, district, or region worldwide to orchestrate Earth Observation, Urban Resilience, and Policy Analytics
        </p>
    </div>
    <div>
        <span class="agent-pill">🤖 LangGraph Multi-Agent Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Universal Spatial Search Bar
with st.container():
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "Search any place or enter a Spatial Planning query:",
            value=st.session_state.current_query,
            placeholder="Search any place, e.g., 'Sylhet heat island', 'Cox\'s Bazar runoff', 'Rangpur 15-min walkability', 'Tokyo resilience'...",
            label_visibility="collapsed"
        )
    with col_btn:
        run_btn = st.button("🔍 Search & Run", use_container_width=True)

# Execute Workflow on Button Click or Initial Default Load
if run_btn:
    with st.spinner("🤖 Multi-Agent Engine geocoding location and orchestrating GEE, OSMnx, Hydrology..."):
        st.session_state.agent_result = run_geolab_workflow(user_query)
elif st.session_state.agent_result is None:
    with st.spinner("🤖 Initializing GeoAI Spatial Engine..."):
        st.session_state.agent_result = run_geolab_workflow(st.session_state.current_query)

result = st.session_state.agent_result


# Location & Spatial Intelligence Badge
if result:
    loc_display = result.get("target_location", "City")
    dom_display = result.get("identified_domain", "Urban Planning")
    coords_display = result.get("center_coordinates", [22.8456, 89.5403])
    lat_str = f"{coords_display[0]:.4f}° N" if coords_display[0] >= 0 else f"{abs(coords_display[0]):.4f}° S"
    lon_str = f"{coords_display[1]:.4f}° E" if coords_display[1] >= 0 else f"{abs(coords_display[1]):.4f}° W"
    
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 10px 16px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <span style="color: #38bdf8; font-weight: 700; font-size: 0.95rem;">📍 Target Location:</span>
            <strong style="color: #f8fafc; font-size: 1.05rem; margin-left: 6px;">{loc_display}</strong>
            <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 8px;">({lat_str}, {lon_str})</span>
        </div>
        <div>
            <span style="color: #38bdf8; font-weight: 700; font-size: 0.95rem;">🔬 Domain:</span>
            <span style="color: #e2e8f0; font-size: 0.9rem; margin-left: 6px; background: rgba(56, 189, 248, 0.15); padding: 3px 8px; border-radius: 4px;">{dom_display}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Top KPI Summary Cards
if result and result.get("collected_metrics"):
    metrics = result["collected_metrics"]
    st.markdown("### 📊 Key Diagnostic Geospatial Indicators")
    
    cols = st.columns(4)
    # Card 1: Domain
    with cols[0]:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Target City & Domain</div>
            <div class="metric-value" style="font-size: 1.15rem;">{result.get('target_location')}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">{result.get('identified_domain', '')[:30]}...</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Card 2: Primary Ecological / Thermal / LULC Metric
    with cols[1]:
        if "compute_lulc_change_detection__built_up_expansion_percentage" in metrics:
            val = metrics["compute_lulc_change_detection__built_up_expansion_percentage"]
            lbl = "Built-up Expansion"
            sub = "LULC Multi-Epoch (10-Yr)"
        elif "compute_ndvi_statistics__green_space_per_capita_m2" in metrics:
            val = f"{metrics['compute_ndvi_statistics__green_space_per_capita_m2']} m²"
            lbl = "Green Space / Capita"
            sub = "Sentinel-2 Canopy"
        elif "compute_lst_heat_island__suhi_intensity_delta_celsius" in metrics:
            val = str(metrics["compute_lst_heat_island__suhi_intensity_delta_celsius"])
            lbl = "SUHI Heat Delta"
            sub = "Landsat-9 TIRS"
        else:
            val = "N/A"
            lbl = "Environmental Indicator"
            sub = "Remote Sensing"
            
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{lbl}</div>
            <div class="metric-value">{val}</div>
            <div style="font-size: 0.75rem; color: #38bdf8; margin-top: 4px;">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 3: Mobility / Hydrology / Equity
    with cols[2]:
        if "compute_sponge_city_runoff__direct_surface_runoff_depth" in metrics:
            m_val = metrics["compute_sponge_city_runoff__direct_surface_runoff_depth"]
            m_lbl = "SCS Direct Runoff"
            m_sub = "Sponge City Model"
        elif "compute_spatial_equity_deficit__population_outside_15min_emergency_walkshed" in metrics:
            m_val = metrics["compute_spatial_equity_deficit__population_outside_15min_emergency_walkshed"]
            m_lbl = "Underserved Pop."
            m_sub = "2SFCA Healthcare Mismatch"
        elif "compute_walkability_isochrones__15_min_walkability_index" in metrics:
            m_val = metrics["compute_walkability_isochrones__15_min_walkability_index"]
            m_lbl = "15-Min Walkability"
            m_sub = "OSMnx Graph Catchment"
        else:
            m_val = metrics.get('compute_flood_hazard_overlay__simulated_inundated_area_pct', '31.4%')
            m_lbl = "Flood Inundation"
            m_sub = "DEM Flow Accumulation"

        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{m_lbl}</div>
            <div class="metric-value">{m_val}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">{m_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 4: Compliance Status
    with cols[3]:
        verdict = result.get("compliance_verdict", "Strategic Intervention Required")
        st.markdown(f"""
        <div class="metric-box" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="metric-title">Planning Compliance</div>
            <div class="metric-value" style="font-size: 1.05rem; color: #f87171;">{verdict}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">URP / WHO Standard Audit</div>
        </div>
        """, unsafe_allow_html=True)

# Main Two-Column Layout: Left (Policy, What-If, Export, Logs) | Right (Interactive Folium Map)

col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    tab_report, tab_whatif, tab_export, tab_logs, tab_tools = st.tabs([
        "📑 Policy Brief", 
        "🧪 'What-If' Simulation", 
        "💾 GIS Export", 
        "🔍 Agent Logs", 
        "⚙️ Executed GIS Tools"
    ])
    
    with tab_report:
        st.markdown(result.get("policy_report_markdown", "*No report generated.*"))
        
    with tab_whatif:
        st.markdown("#### 🧪 Digital Twin 'What-If' Policy Sandbox")
        st.caption("Interactively simulate policy interventions and view instant recalculated microclimate & mobility metrics.")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            tree_boost = st.slider("🌳 Urban Canopy Target (+%):", min_value=0, max_value=50, value=20, step=5)
            cool_roof = st.slider("🏢 Cool Roof Albedo Retrofit (%):", min_value=0, max_value=100, value=40, step=10)
        with sim_col2:
            transit_stops = st.slider("🚶 New Transit & Pedestrian Nodes:", min_value=0, max_value=10, value=4, step=1)
            sponge_ha = st.slider("💧 Sponge Detention Area (+ha):", min_value=0, max_value=30, value=12, step=2)

        # Compute dynamic live simulation deltas
        base_temp_delta = float(str(result.get("collected_metrics", {}).get("compute_lst_heat_island__suhi_intensity_delta_celsius", "+3.8°C")).replace("°C", "").replace("+", ""))
        temp_reduction = round((tree_boost * 0.055) + (cool_roof * 0.022), 2)
        new_temp_delta = round(max(0.5, base_temp_delta - temp_reduction), 2)
        
        base_green = float(result.get("collected_metrics", {}).get("compute_ndvi_statistics__green_space_per_capita_m2", 3.8))
        new_green = round(base_green * (1.0 + (tree_boost / 100.0)), 2)
        
        base_walk = float(str(result.get("collected_metrics", {}).get("compute_walkability_isochrones__15_min_walkability_index", "68.5/100")).split("/")[0])
        new_walk = min(100.0, round(base_walk + (transit_stops * 3.2), 1))
        
        runoff_abated_m3 = int(sponge_ha * 10000 * 0.065 * 1000)

        st.markdown("##### 📈 Simulated Impact Assessment:")
        
        res_cols = st.columns(2)
        with res_cols[0]:
            st.metric(
                label="🌡️ Surface Heat Island (SUHI)",
                value=f"+{new_temp_delta} °C",
                delta=f"-{temp_reduction} °C Cooling"
            )
            st.metric(
                label="🌳 Green Space / Capita",
                value=f"{new_green} m²",
                delta=f"+{round(new_green - base_green, 2)} m²"
            )
        with res_cols[1]:
            st.metric(
                label="🚶 15-Minute Walkability Score",
                value=f"{new_walk} / 100",
                delta=f"+{round(new_walk - base_walk, 1)} pts"
            )
            st.metric(
                label="💧 Stormwater Runoff Abated",
                value=f"{runoff_abated_m3:,} m³",
                delta="Flood Mitigation Capacity"
            )

    with tab_export:
        st.markdown("#### 💾 Multi-Format GIS & Data Export Hub")
        st.caption("Export your autonomous spatial analytics directly into desktop GIS (QGIS, ArcGIS Pro), Google Earth, and municipal formats.")
        
        loc_name = result.get('target_location', 'City')
        metrics_dict = result.get('collected_metrics', {})
        
        # 0. Featured Master Package (1-Click Download All)
        master_zip_bytes, master_zip_name = generate_master_zip_package(result)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.25), rgba(14, 165, 233, 0.1)); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 8px; padding: 14px 18px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h5 style="margin: 0; font-size: 1.05rem; color: #f8fafc;">📦 Complete Master GIS Research Package (.zip)</h5>
                    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #94a3b8;">
                        Includes GeoJSON Layers, Google Earth KML, GeoTIFF Raster, CSV Metrics, HTML Brief, Policy Markdown & Data Dictionary.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label=f"📦 Download 1-Click Master Archive ({master_zip_name})",
            data=master_zip_bytes,
            file_name=master_zip_name,
            mime="application/zip",
            use_container_width=True
        )

        st.markdown("---")
        
        # Section 1: Vector & 3D Geodata
        st.markdown("##### 🗺️ 1. Vector & 3D Spatial Layers")
        vec_col1, vec_col2 = st.columns(2)
        
        # Combined GeoJSON
        combined_geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": []
        }
        for layer in result.get("geojson_layers", []):
            if "features" in layer:
                combined_geojson["features"].extend(layer["features"])
                
        with vec_col1:
            st.download_button(
                label="📥 Download GeoJSON Layers (.geojson)",
                data=json.dumps(combined_geojson, indent=2),
                file_name=f"GeoLab_{loc_name}_Layers.geojson",
                mime="application/geo+json",
                use_container_width=True
            )
            st.caption("Compatible with **QGIS**, **ArcGIS Pro**, **Mapbox**, & **Leaflet**.")
            
        with vec_col2:
            kml_content = convert_geojson_to_kml(combined_geojson, title=f"GeoLab - {loc_name}")
            st.download_button(
                label="🌐 Download Google Earth 3D (.kml)",
                data=kml_content,
                file_name=f"GeoLab_{loc_name}_GoogleEarth.kml",
                mime="application/vnd.google-earth.kml+xml",
                use_container_width=True
            )
            st.caption("Direct 3D satellite visualization in **Google Earth Pro & Web**.")

        st.markdown("---")
        
        # Section 2: Georeferenced GeoTIFF Raster Export
        st.markdown("##### 🛰️ 2. Georeferenced Satellite GeoTIFF Raster (.tif)")
        st.caption("Standard 32-bit float GeoTIFF with embedded WGS84 (EPSG:4326) CRS & Affine Transform for QGIS, ArcGIS Pro, and Google Earth Engine.")
        
        default_idx = 0
        if any("lst_heat_island" in k for k in metrics_dict.keys()):
            default_idx = 1
        elif any("sponge_city" in k for k in metrics_dict.keys()):
            default_idx = 2
        elif any("flood_hazard" in k for k in metrics_dict.keys()):
            default_idx = 3
        elif any("lulc_change" in k for k in metrics_dict.keys()):
            default_idx = 4

        raster_options = [
            "🌿 Sentinel-2 NDVI Canopy Index (Float32, -1 to +1)",
            "🔥 Landsat-9 Land Surface Temperature (LST °C)",
            "💧 SCS-CN Sponge City Direct Surface Runoff (mm)",
            "🌊 DEM 25-Year Coastal / Deltaic Flood Inundation (m)",
            "🔄 Multi-Temporal LULC Classification (Categorical Classes)"
        ]

        raster_opt = st.selectbox(
            "Select Raster Band to Export:",
            raster_options,
            index=default_idx
        )
        
        raster_type_map = {
            "🌿 Sentinel-2 NDVI Canopy Index (Float32, -1 to +1)": "ndvi",
            "🔥 Landsat-9 Land Surface Temperature (LST °C)": "lst",
            "💧 SCS-CN Sponge City Direct Surface Runoff (mm)": "sponge_runoff",
            "🌊 DEM 25-Year Coastal / Deltaic Flood Inundation (m)": "flood_depth",
            "🔄 Multi-Temporal LULC Classification (Categorical Classes)": "lulc"
        }
        
        selected_raster_type = raster_type_map[raster_opt]
        geotiff_bytes, geotiff_filename, raster_meta = generate_geotiff_raster(
            target_location=loc_name,
            raster_type=selected_raster_type,
            metrics=metrics_dict
        )
        
        st.info(f"**Selected Raster:** `{geotiff_filename}` | **CRS:** {raster_meta['crs']} | **Grid:** {raster_meta['dimensions']} | **Size:** {round(raster_meta['byte_size'] / 1024, 1)} KB | **Band Unit:** {raster_meta['units']}")
        
        st.download_button(
            label=f"📥 Download {geotiff_filename} (.tif)",
            data=geotiff_bytes,
            file_name=geotiff_filename,
            mime="image/tiff",
            use_container_width=True
        )

        st.markdown("---")
        
        # Section 3: Tabular Indicators & Policy Reports
        st.markdown("##### 📊 3. Tabular Metrics & Municipal Reports")
        tab_col1, tab_col2, tab_col3 = st.columns(3)
        
        with tab_col1:
            import io, csv
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["Tool_and_Metric", "Observed_Value"])
            for k, v in metrics_dict.items():
                writer.writerow([k, str(v)])
                
            st.download_button(
                label="📊 Metrics Table (.csv)",
                data=csv_buffer.getvalue(),
                file_name=f"GeoLab_{loc_name}_Metrics.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("For Python, R, SPSS, Excel.")
            
        with tab_col2:
            html_report_data = generate_printable_html(result)
            st.download_button(
                label="📄 Municipal Brief (.html)",
                data=html_report_data,
                file_name=f"GeoLab_Brief_{loc_name}.html",
                mime="text/html",
                use_container_width=True
            )
            st.caption("Printable report with KUET URP layout.")
            
        with tab_col3:
            st.download_button(
                label="📑 Policy Synthesis (.md)",
                data=result.get("policy_report_markdown", ""),
                file_name=f"GeoLab_Report_{loc_name}.md",
                mime="text/markdown",
                use_container_width=True
            )
            st.caption("Structured text for research papers.")




    with tab_logs:
        st.markdown("#### Multi-Agent Execution Trace")
        for log in result.get("execution_logs", []):
            if "❌" in log:
                st.error(log)
            elif "⚠️" in log:
                st.warning(log)
            elif "✅" in log:
                st.success(log)
            elif "🧠" in log or "🚀" in log or "📊" in log or "⚙️" in log:
                st.info(log)
            else:
                st.write(log)
                
    with tab_tools:
        st.markdown("#### Tool Output Registry")
        for res in result.get("tool_results", []):
            with st.expander(f"🛠️ {res.get('tool', 'Geospatial Tool')}"):
                st.json(res)

with col_right:
    st.markdown("### 🗺️ Interactive Multi-Layer Geospatial Map")
    
    # Build folium map from agent state
    center = result.get("center_coordinates", [22.8456, 89.5403])
    layers = result.get("geojson_layers", [])
    
    map_obj = build_interactive_folium_map(
        center_coords=center,
        zoom_start=13,
        geojson_layers=layers
    )
    
    # Render map
    if hasattr(map_obj, "get_root"):
        st_folium(map_obj, width="100%", height=620, returned_objects=[])
    else:
        st.info("🗺️ Multi-Layer Map Layer Metadata Available.")
        st.json(map_obj)
    
    st.caption("💡 *Tip: Use the top-right layer switch on the map to toggle between Dark Matter, Satellite Imagery, Thermal Hotspots, LULC Changes, Sponge Basins, and 15-Minute Isochrone Walksheds.*")


