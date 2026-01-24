# Advanced Mapping APIs and Techniques Research 2026

## Table of Contents
1. [Free Map APIs](#free-map-apis)
2. [Historical Mapping Resources](#historical-mapping-resources)
3. [Fantasy Map Generation](#fantasy-map-generation)
4. [Elevation and 3D Texturing](#elevation-and-3d-texturing)
5. [Implementation Recommendations](#implementation-recommendations)

---

## Free Map APIs

### 1. OpenStreetMap (OSM) - Currently Used
- **API**: Overpass API
- **Features**: Complete global map data, roads, buildings, water features
- **Usage**: Already implemented via OSMnx
- **Limitations**: No historical data, modern styling only

### 2. Mapbox
- **Free Tier**: 50,000 API calls/month
- **Features**: 
  - Static maps API with custom styles
  - Terrain and elevation data
  - Satellite imagery
  - Historical map styles
- **APIs**: 
  - Mapbox Static Images API
  - Mapbox Terrain-RGB v2
  - Mapbox Elevation API
- **Documentation**: https://docs.mapbox.com/

### 3. Stadia Maps
- **Free Tier**: 250,000 API calls/month
- **Features**:
  - Multiple map styles (including vintage)
  - Stamen Terrain, Watercolor, Toner
  - High-quality cartography
- **APIs**: 
  - Static Maps API
  - Tiles API
- **Documentation**: https://stadiamaps.com/

### 4. Thunderforest
- **Free Tier**: Limited requests
- **Features**:
  - Landscape (terrain shading)
  - Outdoors (hiking trails)
  - Transport, Transport Dark
  - Neighbourhood, Pioneer
- **Documentation**: https://www.thunderforest.com/docs/

### 5. HERE Maps
- **Free Tier**: 250,000 transactions/month
- **Features**:
  - Satellite imagery
  - Traffic flow
  - Public transit routes
  - Truck routing
- **Documentation**: https://developer.here.com/

---

## Historical Mapping Resources

### 1. David Rumsey Map Collection
- **URL**: https://www.davidrumsey.com/
- **Features**: 131,000+ historical maps
- **API**: No direct API, but maps available for download
- **Time Period**: 16th-21st centuries
- **Integration**: Can download and overlay historical maps

### 2. OldMapsOnline
- **URL**: https://www.oldmapsonline.org/
- **Features**: Search across 400,000+ historical maps
- **API**: OGC WMS/WFS services available
- **Integration**: Can georeference and overlay historical maps

### 3. New York Public Library Map Warper
- **URL**: https://maps.nypl.org/warper/
- **Features**: 20,000+ georeferenced historical maps
- **API**: RESTful API available
- **Usage**: Can download warped historical maps as tiles

### 4. British Library Georeferencer
- **URL**: https://www.bl.uk/projects/georeferencer
- **Features**: Historical maps with georeferencing
- **API**: IIIF (International Image Interoperability Framework)
- **Integration**: Can fetch historical map tiles

### 5. USGS Historical Topographic Maps
- **URL**: https://ngmdb.usgs.gov/topotv/
- **Features**: US historical topo maps (1884-2006)
- **API**: The National Map services
- **Coverage**: United States only

---

## Fantasy Map Generation

### 1. Azgaar's Fantasy Map Generator
- **URL**: https://azgaar.github.io/Fantasy-Map-Generator/
- **Features**:
  - Procedural world generation
  - Rivers, mountains, biomes
  - Medieval style
  - Export to JSON/SVG
- **API**: Can export map data as JSON
- **GitHub**: https://github.com/Azgaar/Fantasy-Map-Generator

### 2. Wonderdraft
- **Commercial**: $30 USD
- **Features**: Professional fantasy map creation
- **Integration**: Export as PNG/JPG, can import custom assets

### 3. Inkarnate
- **Free Tier**: Limited features
- **Features**: Browser-based fantasy map maker
- **API**: No API, manual creation only

### 4. Donjon
- **URL**: https://donjon.bin.sh/
- **Features**:
  - Random world/region/city generators
  - D&D focused
  - JSON export available
- **Integration**: Can generate and import map data

### 5. Perilous Shores
- **URL**: https://perilous-shores.appspot.com/
- **Features**: Hex-based fantasy maps
- **Export**: PNG/SVG

---

## Elevation and 3D Texturing

### 1. NASA SRTM (Shuttle Radar Topography Mission)
- **Resolution**: 30m (SRTMGL1) or 90m (SRTM3)
- **Coverage**: 80% of Earth's land surface
- **APIs**:
  - Google Earth Engine
  - AWS Open Data
  - USGS EarthExplorer
- **Usage**: 
  ```python
  import elevation
  elevation.clip(bounds, output='dem.tif')
  ```

### 2. ALOS World 3D
- **Resolution**: 30m
- **Provider**: JAXA (Japan Aerospace Exploration Agency)
- **Coverage**: Global
- **API**: OpenTopography

### 3. EU-DEM
- **Resolution**: 30m
- **Coverage**: Europe
- **Provider**: Copernicus

### 4. 3D Texturing Techniques (Not 3D Rendering)

#### Hill Shading
```python
from matplotlib.colors import LightSource
ls = LightSource(azdeg=315, altdeg=45)
shaded = ls.shade(dem, cmap='terrain')
```

#### Slope Shading
```python
import numpy as np
x, y = np.gradient(dem)
slope = np.degrees(np.arctan(np.sqrt(x**2 + y**2)))
aspect = np.degrees(np.arctan2(-x, y))
```

#### Contour Lines
```python
from matplotlib import pyplot as plt
plt.contour(dem, levels=20, colors='black', alpha=0.3)
plt.contourf(dem, levels=20, cmap='terrain', alpha=0.5)
```

#### Texture Overlay with Elevation
```python
# Combine elevation with texture
elevation_texture = np.dstack([dem, dem, dem])
elevation_texture = (elevation_texture - elevation_texture.min()) / (elevation_texture.max() - elevation_texture.min())
combined = texture * (0.7 + 0.3 * elevation_texture)
```

---

## Implementation Recommendations

### Phase 1: Immediate Enhancements

1. **Add Mapbox Integration**
   - Sign up for free tier
   - Implement terrain shading
   - Add satellite imagery option
   - Use Mapbox Static API for alternative maps

2. **Elevation Data Integration**
   ```python
   import elevation
   import rasterio
   
   def get_elevation_data(bounds):
       # Download DEM for bounds
       elevation.clip(bounds, output='temp.tif')
       with rasterio.open('temp.tif') as src:
           return src.read(1)
   ```

3. **Enhanced Texturing with Elevation**
   - Combine textures with hill shading
   - Add contour line overlays
   - Implement slope-based coloring

### Phase 2: Historical Maps

1. **Historical Map Overlay**
   ```python
   def apply_historical_overlay(base_map, historical_map, opacity=0.5):
       # Georeference and blend
       return (base_map * (1-opacity) + historical_map * opacity)
   ```

2. **API Integration**
   - NYPL Map Warper API
   - British Library IIIF
   - David Rumsey downloads

### Phase 3: Fantasy Maps

1. **Azgaar Integration**
   - Fetch generated world data
   - Convert to poster format
   - Apply fantasy styling

2. **Custom Fantasy Elements**
   - Hand-drawn textures
   - Fantasy labels and symbols
   - Medieval color palettes

### Code Examples

#### Elevation-Based Texturing
```python
def apply_elevation_texture(ax, dem, texture_img):
    # Create elevation-based alpha mask
    elevation_norm = (dem - dem.min()) / (dem.max() - dem.min())
    
    # Apply texture with elevation variation
    ax.imshow(texture_img, extent=bounds, alpha=0.3 + 0.4 * elevation_norm)
    
    # Add hill shading
    ls = LightSource(azdeg=315, altdeg=45)
    hillshade = ls.hillshade(dem, vert_exag=10)
    ax.imshow(hillshade, extent=bounds, cmap='gray', alpha=0.3)
```

#### Multiple Texture Layers
```python
def layer_textures(ax, base_texture, aging_texture, stain_texture):
    # Base paper texture
    ax.imshow(base_texture, alpha=0.8)
    
    # Aging effects
    ax.imshow(aging_texture, alpha=0.4)
    
    # Stains and decay
    ax.imshow(stain_texture, alpha=0.2)
```

---

## Resources and Links

### Data Sources
- SRTM Downloader: https://dwtkns.com/srtm30m/
- OpenTopography: https://opentopography.org/
- EarthExplorer: https://earthexplorer.usgs.gov/

### Python Libraries
- `rasterio`: Geospatial raster data
- `elevation`: SRTM data download
- `pyproj`: Coordinate transformations
- `matplotlib.colors`: Color manipulation
- `scipy.ndimage`: Image processing

### Inspiration
- Ancient Maps Gallery: https://www.ancientmaps.com/
- Cartographers' Guild: https://www.cartographersguild.com/
- Reddit r/MapPorn: https://reddit.com/r/MapPorn

---

## Next Steps

1. **Test Mapbox API** - Get API key and test terrain features
2. **Download Sample DEM** - Test elevation-based texturing
3. **Explore Historical APIs** - Test NYPL and British Library
4. **Prototype Fantasy Integration** - Test Azgaar data import

This research provides a roadmap for expanding the map poster generator with advanced features while maintaining the 2D artistic aesthetic.
