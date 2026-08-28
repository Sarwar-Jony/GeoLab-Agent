"""
Unit Tests for GeoLab-Agent Geospatial Tools.
"""


import unittest
from src.tools.gee_analytics import compute_ndvi_statistics, compute_lst_heat_island, compute_air_quality_index, compute_lulc_change_detection
from src.tools.network_analytics import compute_walkability_isochrones, compute_transit_accessibility
from src.tools.vector_analytics import compute_zoning_vulnerability, compute_flood_hazard_overlay, compute_sponge_city_runoff, compute_spatial_equity_deficit
from src.tools.map_renderer import build_interactive_folium_map
from src.tools.raster_exporter import generate_geotiff_raster



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

    def test_geotiff_raster_export(self):
        import rasterio
        from rasterio.io import MemoryFile

        # Test NDVI raster export
        data_bytes, filename, meta = generate_geotiff_raster("Khulna", "ndvi")
        self.assertTrue(filename.endswith(".tif"))
        self.assertGreater(len(data_bytes), 1000)
        self.assertEqual(meta["crs"], "EPSG:4326 (WGS 84)")
        
        # Verify valid GeoTIFF readable by rasterio
        with MemoryFile(data_bytes) as memfile:
            with memfile.open() as ds:
                self.assertEqual(ds.crs.to_string(), "EPSG:4326")
                self.assertEqual(ds.count, 1)
                self.assertEqual(ds.shape, (150, 150))
                arr = ds.read(1)
                self.assertIsNotNone(arr)
                self.assertGreater(arr.max(), 0.0)

        # Test Sponge Runoff raster export
        sponge_bytes, sponge_fn, sponge_meta = generate_geotiff_raster("Chittagong", "sponge_runoff")
        self.assertIn("SpongeCity_Runoff", sponge_fn)
        self.assertGreater(len(sponge_bytes), 1000)


if __name__ == "__main__":
    unittest.main()


