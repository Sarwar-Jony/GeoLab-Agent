"""
LangGraph Multi-Agent Orchestrator for GeoLab-Agent.
Connects Spatial Planner, Geospatial Tool Executor, and Urban Policy Critic into a cyclic/linear state graph.
"""

import sys
import json
from typing import Dict, Any

# Ensure UTF-8 output on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .state import AgentState
from .planner import plan_spatial_workflow
from .executor import execute_geospatial_tools
from .critic import synthesize_urban_policy

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def _build_langgraph_workflow():
    """Builds and compiles the LangGraph Multi-Agent State Machine."""
    builder = StateGraph(AgentState)
    
    # Add Agent Nodes
    builder.add_node("planner", plan_spatial_workflow)
    builder.add_node("executor", execute_geospatial_tools)
    builder.add_node("critic", synthesize_urban_policy)
    
    # Add Edges
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "critic")
    builder.add_edge("critic", END)
    
    return builder.compile()


# Compiled Graph instance if langgraph is installed
if LANGGRAPH_AVAILABLE:
    graph_app = _build_langgraph_workflow()
else:
    graph_app = None


def run_geolab_workflow(user_query: str) -> Dict[str, Any]:
    """
    Main entry point for executing the GeoLab-Agent Multi-Agent pipeline.
    Accepts natural language user query, returns complete state dictionary with logs,
    metrics, GeoJSON layers, and final policy report.
    """
    initial_state: AgentState = {
        "user_query": user_query,
        "target_location": "Khulna",
        "identified_domain": "",
        "tool_sequence": [],
        "execution_plan_rationale": "",
        "tool_results": [],
        "collected_metrics": {},
        "geojson_layers": [],
        "center_coordinates": [22.8456, 89.5403],
        "execution_logs": [f"🚀 [Orchestrator] Initiating GeoLab-Agent Pipeline..."],
        "policy_report_markdown": "",
        "academic_summary": "",
        "key_recommendations": [],
        "compliance_verdict": ""
    }
    
    if LANGGRAPH_AVAILABLE and graph_app:
        final_state = graph_app.invoke(initial_state)
    else:
        # Graceful sequential fallback if langgraph package is still loading
        s1 = {**initial_state, **plan_spatial_workflow(initial_state)}
        s2 = {**s1, **execute_geospatial_tools(s1)}
        final_state = {**s2, **synthesize_urban_policy(s2)}
        
    return final_state


# Backwards compatibility alias
run_urbangeo_workflow = run_geolab_workflow


if __name__ == "__main__":
    query = "Analyze urban heat island intensity and green space canopy deficit for Khulna city"
    if len(sys.argv) > 1 and sys.argv[1] != "--test":
        query = " ".join(sys.argv[1:])
        
    print(f"\n==========================================")
    print(f"🌍 GeoLab-Agent Test Execution")
    print(f"Query: {query}")
    print(f"==========================================\n")
    
    result = run_geolab_workflow(query)
    
    print("\n--- Execution Logs ---")
    for log in result["execution_logs"]:
        print(log)
        
    print("\n--- Collected Spatial Metrics ---")
    for k, v in result["collected_metrics"].items():
        print(f"  {k}: {v}")
        
    print("\n--- Executive Policy Brief Snippet ---")
    print(result["policy_report_markdown"][:600] + "...\n[Full Report Truncated for CLI View]\n")

