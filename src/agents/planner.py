"""
Spatial Planner Agent for GeoLab-Agent.
Analyzes user queries, determines the spatial intent, extracts geographical bounding boxes/city context,
and outputs a sequence of Geospatial and Earth Observation analysis tools.
"""


import os
import json
from typing import Dict, Any, List
from .state import AgentState
from src.tools.geocoder import extract_location_from_text, resolve_location_coordinates

# Available tool registry documentation for the Planner Agent
AVAILABLE_TOOLS = {
    "compute_ndvi_statistics": "Analyzes Sentinel-2 satellite vegetation canopy, green space per capita, and WHO deficit.",
    "compute_lst_heat_island": "Computes Landsat-8/9 thermal surface temperature, SUHI magnitude, and urban thermal hotspots.",
    "compute_walkability_isochrones": "Computes 5/10/15-minute pedestrian network isochrones and 15-Minute City walkability score.",
    "compute_transit_accessibility": "Evaluates public transit stop density, 400m catchment walksheds, and transit deficit gaps.",
    "compute_zoning_vulnerability": "Audits building setback compliance, impervious surface ratio, and informal settlement risk.",
    "compute_flood_hazard_overlay": "Simulates hydrological DEM flow accumulation, inundation depth, and sea level rise surge exposure.",
    "compute_air_quality_index": "Retrieves Sentinel-5P tropospheric NO2 and estimated ground-level PM2.5 pollution corridors.",
    "compute_lulc_change_detection": "Computes multi-temporal land use/land cover (LULC) changes, impervious built-up expansion, and deforestation rates.",
    "compute_sponge_city_runoff": "Calculates SCS-CN direct stormwater runoff depth, retention pond sizing, and sponge city waterlogging vulnerability.",
    "compute_spatial_equity_deficit": "Evaluates 2SFCA spatial accessibility to emergency healthcare, hospital beds deficit, and underserved community clusters."
}



def plan_spatial_workflow(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Spatial Planner Agent.
    Decomposes natural language query into an actionable GIS pipeline with dynamic global geocoding.
    """
    user_query = state.get("user_query", "").strip()
    logs = state.get("execution_logs", [])
    logs.append(f"🧠 [Planner Agent] Analyzing spatial intent for query: '{user_query}'")

    # Try calling Google Gemini API if key is set
    gemini_key = os.environ.get("GEMINI_API_KEY")
    plan_result = None

    if gemini_key:
        try:
            import importlib
            genai_mod = importlib.import_module("google.genai")
            client = genai_mod.Client(api_key=gemini_key)

            prompt = f"""You are the Lead Geospatial AI Planner for GeoLab-Agent.

Your job is to read the user's spatial planning query and determine:
1. target_location (City or Region name, e.g., 'Sylhet', 'Khulna', 'Cox's Bazar', 'London', 'Tokyo')
2. identified_domain (e.g., 'Urban Heat & Microclimate', '15-Minute City & Mobility', 'Coastal Flood Resilience', 'Air Quality & Environmental Health', 'Sponge City Hydrology', 'Comprehensive Urban Audit')
3. tool_sequence (Array of tool names chosen strictly from: {list(AVAILABLE_TOOLS.keys())})
4. execution_plan_rationale (Brief justification in 1-2 sentences)

User Query: "{user_query}"

Respond ONLY with valid JSON in this format:
{{
  "target_location": "Khulna",
  "identified_domain": "Urban Heat & Microclimate",
  "tool_sequence": ["compute_ndvi_statistics", "compute_lst_heat_island"],
  "execution_plan_rationale": "Evaluating vegetative canopy deficit and surface heat island intensity to identify urban cooling intervention zones."
}}"""

            # Retry loop with exponential backoff for transient rate limits
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )
                    parsed = json.loads(response.text)
                    if "tool_sequence" in parsed and parsed["tool_sequence"]:
                        plan_result = parsed
                        logs.append(f"✅ [Planner Agent] LLM Reasoning Success. Domain: {plan_result.get('identified_domain')}")
                        break
                except Exception as ex:
                    if attempt == 0:
                        import time
                        time.sleep(1.5)
                    else:
                        raise ex
        except Exception as e:
            logs.append(f"⚠️ [Planner Agent] Gemini API call fallback triggered: {str(e)[:100]}")


    # Robust Universal Spatial Heuristic Fallback
    if not plan_result:
        q_lower = user_query.lower()
        
        # Universal Location Extraction
        extracted_loc = extract_location_from_text(user_query)
        
        # Determine tools and domain
        tools = []
        if any(w in q_lower for w in ["sponge", "runoff", "stormwater", "retention", "scs"]):
            domain = "Sponge City & Urban Stormwater Hydrology"
            tools = ["compute_sponge_city_runoff", "compute_flood_hazard_overlay"]
            rationale = "Computing SCS-CN direct runoff volumes and sizing distributed bioswales and retention infrastructure."
        elif any(w in q_lower for w in ["lulc", "sprawl", "expansion", "land use", "land cover", "deforestation", "growth", "temporal"]):
            domain = "Multi-Temporal LULC & Urban Sprawl Dynamics"
            tools = ["compute_lulc_change_detection", "compute_ndvi_statistics"]
            rationale = "Analyzing multi-epoch satellite imagery to quantify impervious built-up expansion and vegetative canopy loss."
        elif any(w in q_lower for w in ["equity", "hospital", "clinic", "healthcare", "emergency", "injustice", "disparity"]):
            domain = "Spatial Equity & Healthcare Accessibility"
            tools = ["compute_spatial_equity_deficit", "compute_walkability_isochrones"]
            rationale = "Evaluating 2SFCA spatial accessibility to critical emergency medical infrastructure and identifying underserved wards."
        elif any(w in q_lower for w in ["heat", "temperature", "lst", "thermal", "cooling", "canopy", "green", "ndvi", "tree"]):
            domain = "Urban Heat & Vegetative Canopy Audit"
            tools = ["compute_ndvi_statistics", "compute_lst_heat_island"]
            rationale = "Coupling Sentinel-2 vegetation indices with Landsat thermal infrared bands to identify urban heat island cores."
        elif any(w in q_lower for w in ["walk", "15-minute", "isochrone", "transit", "mobility", "transport", "pedestrian"]):
            domain = "15-Minute City & Multi-Modal Mobility"
            tools = ["compute_walkability_isochrones", "compute_transit_accessibility"]
            rationale = "Calculating network isochrones and transit walksheds to assess pedestrian accessibility."
        elif any(w in q_lower for w in ["flood", "waterlog", "drainage", "sea level", "cyclone", "surge"]):
            domain = "Hydrological Flood & Coastal Hazard"
            tools = ["compute_flood_hazard_overlay", "compute_zoning_vulnerability"]
            rationale = "Analyzing elevation flow accumulation models and zoning setback vulnerability."
        elif any(w in q_lower for w in ["air", "pollution", "pm2.5", "no2", "emission", "smog"]):
            domain = "Atmospheric Air Quality & Environmental Exposure"
            tools = ["compute_air_quality_index", "compute_ndvi_statistics"]
            rationale = "Retrieving Sentinel-5P tropospheric column densities and assessing vegetative buffer mitigation."
        else:
            domain = "Comprehensive Multi-Criteria Urban Audit"
            tools = ["compute_ndvi_statistics", "compute_lst_heat_island", "compute_walkability_isochrones", "compute_flood_hazard_overlay", "compute_lulc_change_detection"]
            rationale = "Comprehensive spatial synthesis covering vegetation canopy, thermal resilience, walkability, flood hazards, and urban sprawl."

        plan_result = {
            "target_location": extracted_loc,
            "identified_domain": domain,
            "tool_sequence": tools,
            "execution_plan_rationale": rationale
        }
        logs.append(f"ℹ️ [Planner Agent] Spatial Domain Identified: {domain} for {extracted_loc}")

    # Dynamic Universal Geocoding
    target_loc = plan_result.get("target_location", "Khulna")
    geo_info = resolve_location_coordinates(target_loc)
    center_coords = [geo_info["lat"], geo_info["lon"]]
    
    logs.append(f"📍 [Planner Agent] Geocoded Location: {geo_info['display_name']} ({geo_info['lat']}° N, {geo_info['lon']}° E) [{geo_info['source']}]")

    return {
        "target_location": geo_info["location_name"],
        "identified_domain": plan_result["identified_domain"],
        "tool_sequence": plan_result["tool_sequence"],
        "execution_plan_rationale": plan_result["execution_plan_rationale"],
        "center_coordinates": center_coords,
        "execution_logs": logs
    }

