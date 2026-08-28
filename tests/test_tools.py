"""
Unit Tests for GeoLab-Agent Geospatial Tools.
"""


import unittest
from src.tools.gee_analytics import compute_ndvi_statistics, compute_lst_heat_island, compute_air_quality_index, compute_lulc_change_detection
from src.tools.network_analytics import compute_walkability_isochrones, compute_transit_accessibility
from src.tools.vector_analytics import compute_zoning_vulnerability, compute_flood_hazard_overlay, compute_sponge_city_runoff, compute_spatial_equity_deficit
from src.tools.map_renderer import build_interactive_folium_map


class TestGeospatialTools(unittest.TestCase):

    def test_ndvi_statistics(self):
        res = compute_ndvi_statistics("Khulna")
        self.assertEqual(res["status"], "success")
        self.assertIn("metrics", res)
        self.assertIn("mean_ndvi", res["metrics"])
        self.assertIn("geojson_layer", res)
        self.assertEqual(res["geojson_layer"]["type"], "FeatureCollection")

    def test_lst_heat_island(self):
        res = compute_lst_heat_island("Dhaka")
        self.assertEqual(res["status"], "success")
        self.assertIn("suhi_intensity_delta_celsius", res["metrics"])
        self.assertIn("geojson_layer", res)

    def test_air_quality_index(self):
        res = compute_air_quality_index("Chittagong")
        self.assertEqual(res["status"], "success")
        self.assertIn("estimated_ground_pm25_ug_m3", res["metrics"])

    def test_walkability_isochrones(self):
        res = compute_walkability_isochrones("Khulna", trip_times=[5, 10, 15])
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["geojson_layer"]["features"]), 3)
        self.assertIn("15_min_walkability_index", res["metrics"])

    def test_transit_accessibility(self):
        res = compute_transit_accessibility("Rajshahi")
        self.assertEqual(res["status"], "success")
        self.assertIn("transit_coverage_ratio_400m", res["metrics"])

    def test_zoning_vulnerability(self):
        res = compute_zoning_vulnerability("Khulna")
        self.assertEqual(res["status"], "success")
        self.assertIn("mean_vulnerability_index", res["metrics"])

    def test_flood_hazard_overlay(self):
        res = compute_flood_hazard_overlay("Chittagong", return_period_years=25)
        self.assertEqual(res["status"], "success")
        self.assertIn("simulated_inundated_area_pct", res["metrics"])

    def test_lulc_change_detection(self):
        res = compute_lulc_change_detection("Khulna", base_year=2016, target_year=2026)
        self.assertEqual(res["status"], "success")
        self.assertIn("built_up_expansion_percentage", res["metrics"])
        self.assertIn("vegetation_canopy_loss_km2", res["metrics"])
        self.assertEqual(res["geojson_layer"]["layer_type"], "lulc_change")

    def test_sponge_city_runoff(self):
        res = compute_sponge_city_runoff("Khulna", rainfall_mm=100.0, curve_number=85)
        self.assertEqual(res["status"], "success")
        self.assertIn("direct_surface_runoff_depth", res["metrics"])
        self.assertIn("required_retention_capacity_m3", res["metrics"])
        self.assertEqual(res["geojson_layer"]["layer_type"], "sponge_city_runoff")

    def test_spatial_equity_deficit(self):
        res = compute_spatial_equity_deficit("Dhaka")
        self.assertEqual(res["status"], "success")
        self.assertIn("population_outside_15min_emergency_walkshed", res["metrics"])
        self.assertEqual(res["geojson_layer"]["layer_type"], "spatial_equity_deficit")

    def test_folium_map_rendering(self):
        ndvi_res = compute_ndvi_statistics("Khulna")
        lulc_res = compute_lulc_change_detection("Khulna")
        sponge_res = compute_sponge_city_runoff("Khulna")
        equity_res = compute_spatial_equity_deficit("Khulna")
        m = build_interactive_folium_map(
            center_coords=[22.8456, 89.5403],
            geojson_layers=[
                ndvi_res["geojson_layer"],
                lulc_res["geojson_layer"],
                sponge_res["geojson_layer"],
                equity_res["geojson_layer"]
            ]
        )
        self.assertIsNotNone(m)


if __name__ == "__main__":
    unittest.main()

