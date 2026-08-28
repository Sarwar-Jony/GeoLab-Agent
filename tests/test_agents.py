"""
Unit Tests for GeoLab-Agent Multi-Agent Workflow.
"""

import unittest
from src.agents.workflow import run_geolab_workflow
from src.agents.planner import plan_spatial_workflow
from src.agents.state import AgentState



class TestMultiAgentWorkflow(unittest.TestCase):

    def test_planner_spatial_intent(self):
        state: AgentState = {
            "user_query": "Audit urban heat island and green space canopy for Khulna",
            "target_location": "",
            "identified_domain": "",
            "tool_sequence": [],
            "execution_plan_rationale": "",
            "tool_results": [],
            "collected_metrics": {},
            "geojson_layers": [],
            "center_coordinates": [],
            "execution_logs": [],
            "policy_report_markdown": "",
            "academic_summary": "",
            "key_recommendations": [],
            "compliance_verdict": ""
        }
        res = plan_spatial_workflow(state)
        self.assertEqual(res["target_location"], "Khulna")
        self.assertIn("compute_ndvi_statistics", res["tool_sequence"])
        self.assertIn("compute_lst_heat_island", res["tool_sequence"])

    def test_end_to_end_workflow(self):
        query = "Evaluate 15-minute walkability and transit access for Dhaka"
        res = run_geolab_workflow(query)
        self.assertEqual(res["target_location"], "Dhaka")
        self.assertGreater(len(res["tool_results"]), 0)
        self.assertGreater(len(res["geojson_layers"]), 0)
        self.assertIn("📑", res["policy_report_markdown"])
        self.assertGreater(len(res["execution_logs"]), 0)

    def test_lulc_change_agent_workflow(self):
        query = "Analyze urban sprawl and land use change dynamics for Khulna"
        res = run_geolab_workflow(query)
        self.assertEqual(res["target_location"], "Khulna")
        self.assertIn("compute_lulc_change_detection", res["tool_sequence"])
        self.assertGreater(len(res["tool_results"]), 0)

    def test_sponge_city_agent_workflow(self):
        query = "Simulate sponge city stormwater runoff and drainage retention for Chittagong"
        res = run_geolab_workflow(query)
        self.assertEqual(res["target_location"], "Chittagong")
        self.assertIn("compute_sponge_city_runoff", res["tool_sequence"])

    def test_arbitrary_search_sylhet(self):
        query = "Audit urban vegetative canopy cover and thermal microclimate for Sylhet"
        res = run_geolab_workflow(query)
        self.assertEqual(res["target_location"], "Sylhet")
        self.assertAlmostEqual(res["center_coordinates"][0], 24.8949, places=2)
        self.assertAlmostEqual(res["center_coordinates"][1], 91.8687, places=2)
        self.assertGreater(len(res["tool_results"]), 0)

    def test_arbitrary_search_coxs_bazar(self):
        query = "Simulate sponge city stormwater runoff for Cox's Bazar"
        res = run_geolab_workflow(query)
        self.assertIn("Cox", res["target_location"])
        self.assertAlmostEqual(res["center_coordinates"][0], 21.4272, places=2)
        self.assertGreater(len(res["tool_results"]), 0)

    def test_arbitrary_search_tokyo(self):
        query = "Perform 15-minute city walkability audit for Tokyo"
        res = run_geolab_workflow(query)
        self.assertEqual(res["target_location"], "Tokyo")
        self.assertAlmostEqual(res["center_coordinates"][0], 35.6762, places=2)
        self.assertGreater(len(res["tool_results"]), 0)




if __name__ == "__main__":
    unittest.main()

