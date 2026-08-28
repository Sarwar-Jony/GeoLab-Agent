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
        import rasterio  # type: ignore
        from rasterio.io import MemoryFile  # type: ignore


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
                self.assertGreaterEqual(ds.shape[0], 100)
                self.assertGreaterEqual(ds.shape[1], 100)
                arr = ds.read(1)

                self.assertIsNotNone(arr)
                self.assertGreater(arr.max(), 0.0)

        # Test Sponge Runoff raster export
        sponge_bytes, sponge_fn, sponge_meta = generate_geotiff_raster("Chittagong", "sponge_runoff")
        self.assertIn("SpongeCity_Runoff", sponge_fn)
        self.assertGreater(len(sponge_bytes), 1000)

        # Test all extended raster indices
        extended_indices = ["ndwi", "ndbi", "dem", "slope", "aspect", "bsi", "evi", "lst", "flood_depth", "lulc"]
        for idx in extended_indices:
            b_data, f_name, r_meta = generate_geotiff_raster("Dhaka", idx)
            self.assertTrue(f_name.endswith(".tif"))
            self.assertGreater(len(b_data), 1000)
            self.assertEqual(r_meta["crs"], "EPSG:4326 (WGS 84)")
            self.assertIn("dimensions", r_meta)


    def test_exporter_hub_kml_and_zip(self):
        from src.tools.exporter_hub import convert_geojson_to_kml, generate_master_zip_package, generate_printable_html

        sample_res = {
            "target_location": "Sylhet",
            "identified_domain": "Urban Heat & Canopy",
            "policy_report_markdown": "# Sylhet Brief",
            "collected_metrics": {"compute_ndvi_statistics__mean_ndvi": 0.35},
            "geojson_layers": [{
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {"name": "Sylhet Core", "layer_type": "ndvi"},
                    "geometry": {"type": "Polygon", "coordinates": [[[91.8, 24.8], [91.9, 24.8], [91.9, 24.9], [91.8, 24.9], [91.8, 24.8]]]}
                }]
            }]
        }

        # KML Test
        kml_out = convert_geojson_to_kml(sample_res["geojson_layers"][0], "Sylhet Test")
        self.assertIn("<kml", kml_out)
        self.assertIn("<Placemark>", kml_out)
        self.assertIn("<Polygon>", kml_out)

        # HTML Test
        html_out = generate_printable_html(sample_res)
        self.assertIn("<!DOCTYPE html>", html_out)
        self.assertIn("Sylhet", html_out)

        # Master ZIP Package Test
        zip_bytes, zip_fn = generate_master_zip_package(sample_res)
        self.assertTrue(zip_fn.endswith(".zip"))
        self.assertGreater(len(zip_bytes), 5000)

    def test_process_uploaded_aoi(self):
        from src.tools.aoi_processor import process_uploaded_aoi
        import json

        # 1. Test GeoJSON upload processing
        sample_geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"name": "Sundarbans Sector 1", "zone": "Protected Mangrove"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[89.4, 21.8], [89.7, 21.8], [89.7, 22.1], [89.4, 22.1], [89.4, 21.8]]]
                }
            }]
        }
        geojson_bytes = json.dumps(sample_geojson).encode("utf-8")
        parsed = process_uploaded_aoi(geojson_bytes, "sundarbans_aoi.geojson")

        self.assertTrue(parsed["success"])
        self.assertEqual(parsed["aoi_name"], "Sundarbans Aoi")
        self.assertGreater(parsed["area_km2"], 0)
        self.assertEqual(parsed["feature_count"], 1)
        self.assertEqual(len(parsed["bbox"]), 4)
        self.assertEqual(len(parsed["center"]), 2)

    def test_flow_accumulation_and_custom_bbox(self):
        # Test Flow Accumulation with custom uploaded bounding box
        custom_bbox = [89.4, 21.8, 89.7, 22.1]
        tif_bytes, tif_fn, tif_meta = generate_geotiff_raster(
            target_location="Sundarbans",
            raster_type="flow_accumulation",
            custom_bbox=custom_bbox
        )
        self.assertTrue(tif_fn.endswith(".tif"))
        self.assertIn("Flow_Accumulation", tif_fn)
        self.assertGreater(len(tif_bytes), 1000)
        self.assertEqual(tif_meta["bounds"]["west"], 89.4)
        self.assertEqual(tif_meta["bounds"]["north"], 22.1)
        self.assertIn("stats", tif_meta)
        self.assertGreater(tif_meta["stats"]["max"], tif_meta["stats"]["min"])

    def test_detailed_index_analytics(self):
        from src.tools.index_analytics import compute_detailed_index_analytics

        # Test NDVI detailed analytics
        ndvi_res = compute_detailed_index_analytics("ndvi", "Khulna")
        self.assertEqual(ndvi_res["raster_type"], "ndvi")
        self.assertEqual(len(ndvi_res["kpis"]), 4)
        self.assertIn("stats", ndvi_res)
        self.assertGreater(len(ndvi_res["detailed_synthesis"]), 50)
        self.assertGreater(len(ndvi_res["policy_recommendations"]), 0)

        # Test LST detailed analytics
        lst_res = compute_detailed_index_analytics("lst", "Dhaka")
        self.assertEqual(lst_res["raster_type"], "lst")
        self.assertEqual(len(lst_res["kpis"]), 4)
        self.assertIn("stats", lst_res)

        # Test LULC detailed analytics with class distribution
        lulc_res = compute_detailed_index_analytics("lulc", "Sylhet")
        self.assertEqual(lulc_res["raster_type"], "lulc")
        self.assertEqual(len(lulc_res["distribution"]), 5)


if __name__ == "__main__":
    unittest.main()





