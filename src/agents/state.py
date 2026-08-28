"""
State definition for GeoLab-Agent Multi-Agent Workflow.
"""


from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    # User input query
    user_query: str
    
    # Planner outputs
    target_location: str
    identified_domain: str  # e.g., 'Urban Heat & Environment', '15-Minute City & Mobility', 'Flood & Coastal Resilience', 'Comprehensive Planning'
    tool_sequence: List[str]  # e.g., ['compute_ndvi_statistics', 'compute_lst_heat_island']
    execution_plan_rationale: str
    
    # Geospatial Tool Executor outputs
    tool_results: List[Dict[str, Any]]
    collected_metrics: Dict[str, Any]
    geojson_layers: List[Dict[str, Any]]
    center_coordinates: List[float]
    execution_logs: List[str]
    
    # Urban Policy Critic outputs
    policy_report_markdown: str
    academic_summary: str
    key_recommendations: List[str]
    compliance_verdict: str
