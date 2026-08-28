# 📖 GeoLab-Agent: Comprehensive User Manual & Feature Guide
**Autonomous Multi-Agent GeoAI Platform for Spatial Planning & Earth Observation**  
**Created & Developed by [Sarwar Jony](https://github.com/Sarwar-Jony)**  
*Department of Urban and Regional Planning (URP), Khulna University of Engineering & Technology (KUET)*

---

## 📑 Table of Contents
1. [🌟 System Overview & Purpose](#-system-overview--purpose)
2. [⚡ Complete List of Existing Features](#-complete-list-of-existing-features)
3. [🚀 Step-by-Step User Walkthrough](#-step-by-step-user-walkthrough)
   - [Step 1: Select Analysis Product](#step-1-select-analysis-product)
   - [Step 2: Define Study Area (Search vs Upload)](#step-2-define-study-area-search-vs-upload)
   - [Step 3: Explore Interactive Visual Map](#step-3-explore-interactive-visual-map)
   - [Step 4: Interpret Dynamic Detailed Analytics](#step-4-interpret-dynamic-detailed-analytics)
   - [Step 5: Export to GIS & Municipal Reports](#step-5-export-to-gis--municipal-reports)
4. [🛰️ 13 Remote Sensing & Terrain Analysis Suite](#️-13-remote-sensing--terrain-analysis-suite)
5. [🧪 Digital Twin 'What-If' Simulation Guide](#-digital-twin-what-if-simulation-guide)
6. [💡 Tips for QGIS, ArcGIS Pro & Shapefile Preparation](#-tips-for-qgis-arcgis-pro--shapefile-preparation)
7. [❓ Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🌟 System Overview & Purpose

**GeoLab-Agent** is an open-source, multi-agent GeoAI web platform that bridges the gap between Earth Observation satellite data (Sentinel-2, Landsat-9, DEM), topological street networks, and urban municipal policy making.

Instead of manually preprocessing satellite data across complex software, any student, researcher, or urban planner can:
1. Select an analysis product (e.g. NDVI, LST, Slope, LULC).
2. Choose any study area globally (by search query or custom Shapefile upload).
3. Instantly view interactive visual maps and dynamic physical metrics.
4. Export publication-ready georeferenced GeoTIFFs (`.tif`) and GIS layers for QGIS and ArcGIS Pro.

---

## ⚡ Complete List of Existing Features

### 1. 🛰️ 13-in-1 Earth Observation & Terrain Products
- **🔄 LULC:** 5-Class Land Use / Land Cover (Water, Forest, Agriculture, Built-up, Bare Soil).
- **🌿 NDVI:** Sentinel-2 Vegetative Canopy & Green Space Deficit ($m^2/\text{capita}$).
- **💧 NDWI:** Sentinel-2 Water Bodies, Wetlands & Monsoon Retention ($m^3$).
- **🏢 NDBI:** Sentinel-2/Landsat Built-up Concrete Density & Urban Sprawl.
- **🏔️ DEM:** NASADEM / SRTM 30m Digital Elevation Topography ($m$).
- **📐 Slope:** Topographical Terrain Slope Gradient ($0^\circ - 90^\circ$).
- **🧭 Aspect:** Solar Azimuth & Terrain Slope Compass Orientation ($0^\circ - 360^\circ$).
- **🌊 Flow Accumulation:** Hydrological Stream Network & Drainage Convergence.
- **🏜️ BSI:** Sentinel-2 Bare Soil & Land Degradation Index.
- **🌾 EVI:** Sentinel-2 Enhanced Vegetation Index & Biomass Health.
- **🔥 LST:** Landsat-9 Land Surface Temperature & Heat Island Anomaly ($^\circ\text{C}$).
- **💧 SCS-CN Runoff:** USDA NRCS Stormwater Surface Runoff Depth ($mm$) and Volume ($m^3$).
- **🌊 Coastal Flood:** Hydrodynamic 25-Year Surge Inundation Grid ($m$).

### 2. 🗺️ Interactive Visual Map Studio
- **High-Performance Native Canvas:** Rendered with Leaflet and Folium web components for 100% reliable viewing.
- **Scientific Colormaps:** Specific palettes tailored to each index (e.g. `RdYlGn` for NDVI, `magma` for LST, `terrain` for DEM, `PuBu` for NDWI).
- **Multi-Base Layer Control:** Switch between *Dark Matter*, *CartoDB Positron*, *Satellite Imagery*, and *OpenStreetMap*.
- **Full-Screen / Split Layout Toggle:** Switch between 50/50 Analytics+Map or 100% Full-Width Visual Studio.

### 3. 📁 Universal Study Area Definition (Search & Vector Upload)
- **Global Search Bar:** Geocode any city, ward, upazila, district, or landmark worldwide.
- **Vector Boundary Uploader:** Drag-and-drop ESRI Shapefiles (`.zip` containing `.shp, .shx, .dbf, .prj`), OGC GeoJSON (`.geojson`), and Google Earth KML (`.kml`).
- **Self-Healing Geometry:** Automatically heals invalid or self-intersecting polygons with `shapely.make_valid`.
- **Smart CRS Fallback:** Automatically infers WGS84 or UTM/BTM if the `.prj` projection is missing.
- **Planimetric Metrics:** Computes exact planimetric area in $km^2$ and hectares, perimeter ($km$), and centroid.

### 4. 📊 Product-Tailored Dynamic Analytics
- **4 Specialized KPI Cards:** Dynamically update to reflect the specific physics, benchmarks, and units of the chosen product.
- **Statistical Range Panel:** Shows Min, Max, Mean, Median (P50), and Standard Deviation ($\pm\sigma$).
- **Scientific Spatial Synthesis:** Multi-paragraph technical interpretation of observations.
- **Actionable Municipal Policy Plan:** Priority short-term and long-term recommendations.

### 5. 🧪 Digital Twin "What-If" Policy Simulator
- Interactive sliders for:
  - 🌳 Urban Tree Canopy Target (+%)
  - 🏢 Cool Roof Albedo Retrofit (%)
  - 🚶 New Transit & Pedestrian Nodes
  - 💧 Sponge Retention Detention Basin (+ha)
- Real-time recalculation of SUHI Heat Reduction ($\Delta^\circ\text{C}$), Green Space per Capita ($m^2$), 15-Minute Walkability, and Abated Stormwater ($m^3$).

### 6. 💾 Multi-Format GIS & Municipal Export Hub
- **📦 1-Click Master Archive (.zip):** Includes GeoJSON, KML, GeoTIFF, CSV metrics, HTML Brief, and Markdown Report.
- **🛰️ Georeferenced GeoTIFF (.tif):** 32-bit floating-point raster with embedded Affine Transform and WGS84 CRS for QGIS and ArcGIS Pro.
- **🗺️ Vector Layers (.geojson):** Standardized OGC FeatureCollections.
- **🌐 Google Earth 3D (.kml):** Native 3D visualization.
- **📄 Printable Municipal Brief (.html):** Academic layout with institutional header.
- **📊 Tabular Indicators (.csv):** Spreadsheet table for Excel, R, Python, and SPSS.

---

## 🚀 Step-by-Step User Walkthrough

### Step 1: Select Analysis Product
1. Look at the top control bar under **"Step 1: Select Analysis Product"** (or in the left sidebar).
2. Click the dropdown and select the product you wish to investigate (e.g. `🌿 Sentinel-2 NDVI`, `🔥 Landsat-9 LST`, or `📐 Slope`).

### Step 2: Define Study Area (Search vs Upload)
You have two options:
* **Option A: 🌐 Search Any Place Worldwide:**
  - Type the name of any location (e.g. `Khulna`, `Sylhet`, `Sundarbans`, `Dhaka`, `London`, `Tokyo`, `Cox's Bazar`).
  - Click **"🚀 Analyze"**.
* **Option B: 📁 Upload Custom Study Area:**
  - Switch the radio toggle to **"📁 Upload Shapefile/GeoJSON"**.
  - Drag and drop your `.zip` (containing `.shp, .shx, .dbf, .prj`), `.geojson`, or `.kml`.
  - Click **"🚀 Run Analysis on Custom AOI"**.

### Step 3: Explore Interactive Visual Map
- The interactive map automatically zooms to the bounding box of your study area.
- The colormapped satellite layer for the selected index is layered directly on top of the terrain.
- Use the top-right layer switcher to switch between **Dark Matter**, **Satellite Imagery**, and **OpenStreetMap**.
- Switch layout between **"Split View"** and **"Full-Width Visual Map"** using the layout radio button.

### Step 4: Interpret Dynamic Detailed Analytics
- Observe the **4 KPI Cards** at the top of Tab 1.
- In the left column under **"📊 Detailed Analytics"**:
  - Review the **Min / Max / Mean / Median / Std Dev** statistical summary.
  - Read the **Spatial Scientific Synthesis** for academic research papers.
  - Review the **Municipal Policy Recommendations** for master plan formulation.

### Step 5: Export to GIS & Municipal Reports
- Directly click **"📥 Download GeoTIFF (.tif)"** inside Tab 1 for immediate GIS mapping.
- Or navigate to **"💾 GIS & Municipal Export Hub"** (Tab 4) to download:
  - 📦 1-Click Complete Master Zip
  - 🗺️ GeoJSON Vector Layers
  - 🌐 Google Earth 3D KML
  - 📊 CSV Metrics Spreadsheet
  - 📄 Printable HTML Brief

---

## 🛰️ 13 Remote Sensing & Terrain Analysis Suite

| Index Name | Sensor Platform | Formula / Model | Typical Values | Primary GIS Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **🔄 LULC** | Sentinel-2 MSI | Multi-band Random Forest / CNN | Classes 1 to 5 | Land cover change, urban sprawl & zoning audits |
| **🌿 NDVI** | Sentinel-2 MSI | $\frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$ | $-0.2$ to $+0.85$ | Urban canopy health & WHO 9 $m^2$ green space audit |
| **💧 NDWI** | Sentinel-2 MSI | $\frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$ | $-0.5$ to $+0.7$ | Wetland delineation & waterlogging detention mapping |
| **🏢 NDBI** | Sentinel-2 / Landsat | $\frac{\text{SWIR} - \text{NIR}}{\text{SWIR} + \text{NIR}}$ | $-0.4$ to $+0.6$ | Impervious surface mapping & concrete heat retention |
| **🏔️ DEM** | NASADEM / SRTM | 30m Global Radar Topography | Meters ($m$) | Lowland flood susceptibility & drainage gravity modeling |
| **📐 Slope** | NASADEM Derived | $\arctan\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}$ | Degrees ($0^\circ - 90^\circ$) | Runoff velocity, landslide hazard & constructability |
| **🧭 Aspect** | NASADEM Derived | $\arctan2\left(-\frac{\partial z}{\partial y}, \frac{\partial z}{\partial x}\right)$ | Degrees ($0^\circ - 360^\circ$) | Solar radiation exposure & passive architectural design |
| **🌊 Flow Accumulation**| Topographic D8 | Single/Multiple Flow Direction | Accumulated Cells | Stream channel networks & drainage bottleneck analysis |
| **🏜️ BSI** | Sentinel-2 MSI | $\frac{(\text{SWIR}+\text{Red}) - (\text{NIR}+\text{Blue})}{(\text{SWIR}+\text{Red}) + (\text{NIR}+\text{Blue})}$ | $-0.3$ to $+0.5$ | Topsoil erosion, dust emission & vacant land infill |
| **🌾 EVI** | Sentinel-2 MSI | $2.5 \times \frac{\text{NIR} - \text{Red}}{\text{NIR} + 6\text{Red} - 7.5\text{Blue} + 1}$ | $0.0$ to $+1.0$ | Forest canopy biomass & carbon sequestration tracking |
| **🔥 LST** | Landsat-9 TIRS-2 | $\frac{T_B}{1 + (\lambda T_B / \rho)\ln\varepsilon}$ | Celsius ($^\circ\text{C}$) | Surface Urban Heat Island (SUHI) & heat stress zones |
| **💧 SCS-CN Runoff** | USDA NRCS Hydrology| $Q = \frac{(P - 0.2S)^2}{P + 0.8S}$ | Millimeters ($mm$) | Stormwater runoff depth & sponge retention sizing |
| **🌊 Coastal Flood** | Hydrodynamic Model | 25-Year Surge Stage Hydrograph | Water Depth ($m$) | Coastal dyke heights & 50m riparian buffer setbacks |

---

## 🧪 Digital Twin 'What-If' Simulation Guide

1. Navigate to **Tab 2: 🧪 Digital Twin 'What-If' Sandbox**.
2. Adjust policy intervention sliders:
   - **Urban Tree Canopy (+%):** Simulates vegetative evapotranspiration cooling.
   - **Cool Roof Albedo (%):** Simulates high-reflectance commercial roofing.
   - **New Transit Nodes:** Expands 15-minute pedestrian accessibility.
   - **Sponge Detention Area (+ha):** Models stormwater volume retention.
3. Observe live metric recalculations:
   - Real-time **Surface Heat Island (SUHI) Cooling ($\Delta^\circ\text{C}$)**.
   - Updated **Green Space per Capita ($m^2$)**.
   - Improved **15-Minute City Walkability Score**.
   - Total **Stormwater Runoff Abated ($m^3$)**.

---

## 💡 Tips for QGIS, ArcGIS Pro & Shapefile Preparation

### Importing GeoTIFFs into QGIS:
1. Open **QGIS** (v3.x or later).
2. Go to `Layer` $\rightarrow$ `Add Layer` $\rightarrow$ `Add Raster Layer...`.
3. Select the downloaded `.tif` file (e.g. `GeoLab_Khulna_NDVI.tif`).
4. Right-click layer $\rightarrow$ `Properties` $\rightarrow$ `Symbology`:
   - Change *Render type* to **Singleband pseudocolor**.
   - Choose a scientific color ramp (e.g., `RdYlGn` for NDVI, `Magma` for LST, `Blues` for NDWI).
   - Click `Apply`.

### Preparing Shapefiles for Upload:
- Ensure your `.zip` file contains at least:
  - `boundary.shp` (Geometry features)
  - `boundary.shx` (Shape positional index)
  - `boundary.dbf` (Attribute database)
  - `boundary.prj` *(Optional, system auto-detects WGS84/UTM if missing)*
- Compress the files directly into the root of the `.zip` archive (not inside a nested folder).

---

## ❓ Troubleshooting & FAQ

#### Q1: Can I upload a study area outside Bangladesh?
**Yes!** GeoLab-Agent supports global analysis for any continent, country, city, or watershed on Earth.

#### Q2: What should I do if my shapefile has self-intersecting boundaries?
**Nothing!** GeoLab-Agent includes built-in topology self-healing (`shapely.make_valid`) that automatically fixes broken rings and intersections.

#### Q3: Is there a file size limit for vector uploads?
For optimal web performance, vector boundary files under **50 MB** are recommended. Large geometries (> 2,000 vertices) are automatically decimated for smooth browser rendering.

---

## 🏛️ Citation & Developer Info
If you use GeoLab-Agent in your academic research, journal papers, or graduate theses, please cite:

```bibtex
@software{geolab_agent_2026,
  author = {Sarwar Jony and GeoLab Research Team},
  title = {GeoLab-Agent: Autonomous Multi-Agent GeoAI Platform for Urban Spatial Planning and Earth Observation},
  year = {2026},
  publisher = {Sarwar Jony / Department of Urban and Regional Planning (URP), Khulna University of Engineering & Technology (KUET)},
  url = {https://github.com/Sarwar-Jony/GeoLab-Agent}
}
```
