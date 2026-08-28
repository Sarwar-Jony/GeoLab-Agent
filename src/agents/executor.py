"""
Geospatial Tool Executor Agent for GeoLab-Agent.
Dynamically executes GIS, Remote Sensing, and Network analysis tools identified by the Planner.
"""


from typing import Dict, Any, List
from .state import AgentState
from ..tools.gee_analytics import compute_ndvi_statistics, compute_lst_heat_island, compute_air_quality_index, compute_lulc_change_detection
from ..tools.network_analytics import compute_walkability_isochrones, compute_transit_accessibility
from ..tools.vector_analytics import compute_zoning_vulnerability, compute_flood_hazard_overlay, compute_sponge_city_runoff, compute_spatial_equity_deficit


TOOL_DISPATCHER = {
    "compute_ndvi_statistics": compute_ndvi_statistics,
    "compute_lst_heat_island": compute_lst_heat_island,
    "compute_air_quality_index": compute_air_quality_index,
    "compute_lulc_change_detection": compute_lulc_change_detection,
    "compute_walkability_isochrones": compute_walkability_isochrones,
    "compute_transit_accessibility": compute_transit_accessibility,
    "compute_zoning_vulnerability": compute_zoning_vulnerability,
    "compute_flood_hazard_overlay": compute_flood_hazard_overlay,
    "compute_sponge_city_runoff": compute_sponge_city_runoff,
    "compute_spatial_equity_deficit": compute_spatial_equity_deficit,
}



def execute_geospatial_tools(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Geospatial Tool Executor.
    Runs each tool in state['tool_sequence'] against state['target_location'].
    """
    location = state.get("target_location", "Khulna")
    tool_sequence = state.get("tool_sequence", [])
    logs = state.get("execution_logs", [])
    
    logs.append(f"⚙️ [Tool Executor] Executing {len(tool_sequence)} geospatial tool(s) for target: '{location}'")
    
    tool_results = []
    collected_metrics = {}
    geojson_layers = []
    center_coords = [22.8456, 89.5403]
    
    for tool_name in tool_sequence:
        func = TOOL_DISPATCHER.get(tool_name)
        if func:
            try:
                logs.append(f"  ▶️ Invoking tool: {tool_name}...")
                res = func(location_name=location)
                tool_results.append(res)
                
                # Merge metrics
                if "metrics" in res:
                    for k, v in res["metrics"].items():
                        collected_metrics[f"{tool_name}__{k}"] = v
                        
                # Collect GeoJSON layer
                if "geojson_layer" in res and res["geojson_layer"]:
                    geojson_layers.append(res["geojson_layer"])
                    
                # Update center coordinates
                if "center_coordinates" in res:
                    center_coords = res["center_coordinates"]
                    
                logs.append(f"  ✅ Tool completed: {res.get('tool', tool_name)}")
            except Exception as e:
                logs.append(f"  ❌ Error executing {tool_name}: {str(e)}")
        else:
            logs.append(f"  ⚠️ Tool '{tool_name}' not found in registry.")

    return {
        "tool_results": tool_results,
        "collected_metrics": collected_metrics,
        "geojson_layers": geojson_layers,
        "center_coordinates": center_coords,
        "execution_logs": logs
    }
