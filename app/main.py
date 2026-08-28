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
        "🔄 Khulna: Multi-Temporal LULC & Urban Sprawl": "Analyze urban sprawl and land use change dynamics for Khulna",
        "💧 Chittagong: Sponge City & Stormwater Runoff": "Simulate sponge city stormwater runoff and drainage retention for Chittagong",
        "🏥 Dhaka: Healthcare Spatial Equity & 2SFCA": "Audit spatial equity and healthcare clinic accessibility deficit for Dhaka",
        "🌊 Chittagong: Coastal Flood & Tidal Hazard": "Simulate 25-year flood inundation and zoning setback vulnerability for Chittagong",
        "🏭 Khulna: Industrial Air Pollution (NO2/PM2.5)": "Evaluate atmospheric air pollution and industrial emission corridors for Khulna",
        "🏙️ Rajshahi: Comprehensive Multi-Criteria Audit": "Conduct a comprehensive urban planning and environmental resilience audit for Rajshahi"
    }
    
    selected_scenario = st.selectbox("Select a benchmark scenario:", list(scenarios.keys()))
    if st.button("Load Scenario"):
        st.session_state.current_query = scenarios[selected_scenario]

    st.markdown("---")
    st.markdown("### ⚙️ System Configuration")
    api_status = "🟢 Active (Configured)" if os.environ.get("GEMINI_API_KEY") else "🟡 Synthetic / Sandbox Mode"
    st.caption(f"**LLM Engine:** Gemini 2.5 Flash ({api_status})")
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
            Natural Language Multi-Agent Orchestration for Earth Observation, Urban Resilience, and Policy Synthesis
        </p>
    </div>
    <div>
        <span class="agent-pill">🤖 LangGraph Multi-Agent Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Query Input Bar
with st.container():
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "Enter your Spatial Planning or Remote Sensing query:",
            value=st.session_state.current_query,
            placeholder="e.g., Audit urban heat island intensity and pedestrian accessibility for Khulna...",
            label_visibility="collapsed"
        )
    with col_btn:
        run_btn = st.button("🚀 Run Agent", use_container_width=True)

# Execute Workflow on Button Click or Initial Run
if run_btn or st.session_state.agent_result is None:
    with st.spinner("🤖 Multi-Agent Engine orchestrating GEE, OSMnx, Hydrology, and Policy Critic..."):
        st.session_state.agent_result = run_geolab_workflow(user_query)


result = st.session_state.agent_result

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

# Helper function to generate printable HTML report
def generate_html_report(res_data: dict) -> str:
    loc = res_data.get("target_location", "City")
    dom = res_data.get("identified_domain", "Urban Spatial Planning")
    md_content = res_data.get("policy_report_markdown", "")
    import html
    escaped_md = html.escape(md_content)
    
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GeoLab-Agent Municipal Planning Brief - {loc}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 40px auto; padding: 20px; }}
        .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 15px; margin-bottom: 25px; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        h1, h2, h3 {{ color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #f1f5f9; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 12px; color: #64748b; text-align: center; }}
        @media print {{ .no-print {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px;">
        <button onclick="window.print()" style="background:#0284c7; color:white; border:none; padding:10px 20px; font-weight:bold; border-radius:6px; cursor:pointer;">🖨️ Print / Save as PDF</button>
    </div>
    <div class="header">
        <span class="badge">GEOLAB POLICY BRIEF</span>
        <h1>🌍 GeoLab-Agent Spatial Investigation: {loc}</h1>
        <p><strong>Department of Urban and Regional Planning (URP), KUET</strong> | Domain: <em>{dom}</em></p>
    </div>
    <div class="content">
        <pre style="white-space: pre-wrap; font-family: inherit;">{escaped_md}</pre>
    </div>
    <div class="footer">
        Generated by Autonomous Multi-Agent GeoAI Engine (GeoLab-Agent) | Built for KUET URP Research & Municipal Planners
    </div>
</body>
</html>"""

    return html_doc

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
        st.markdown("#### 💾 Multi-Format GIS & Report Exporter")
        st.caption("Export your autonomous spatial analytics directly into desktop GIS (QGIS, ArcGIS Pro) and municipal formats.")
        
        loc_name = result.get('target_location', 'City')
        
        # 1. GeoJSON Bundle
        combined_geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": []
        }
        for layer in result.get("geojson_layers", []):
            if "features" in layer:
                combined_geojson["features"].extend(layer["features"])
                
        st.download_button(
            label="📥 Download GeoJSON Layer Package (.geojson)",
            data=json.dumps(combined_geojson, indent=2),
            file_name=f"GeoLab_{loc_name}_Layers.geojson",
            mime="application/geo+json",
            use_container_width=True
        )
        
        # 2. CSV Metrics Table
        import io, csv
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Tool_and_Metric", "Observed_Value"])
        for k, v in result.get("collected_metrics", {}).items():
            writer.writerow([k, str(v)])
            
        st.download_button(
            label="📊 Download Geospatial Metrics Table (.csv)",
            data=csv_buffer.getvalue(),
            file_name=f"GeoLab_{loc_name}_Metrics.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # 3. HTML Municipal Brief
        html_report_data = generate_html_report(result)
        st.download_button(
            label="📄 Download Printable Municipal Report (.html)",
            data=html_report_data,
            file_name=f"GeoLab_Brief_{loc_name}.html",
            mime="text/html",
            use_container_width=True
        )
        
        # 4. Markdown Report
        st.download_button(
            label="📑 Download Policy Brief (.md)",
            data=result.get("policy_report_markdown", ""),
            file_name=f"GeoLab_Report_{loc_name}.md",
            mime="text/markdown",
            use_container_width=True
        )


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


