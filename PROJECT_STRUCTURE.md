# Map Poster Generator - Project Structure

## Core Application Files

### Main Application
- `create_map_poster.py` - Core map generation engine with all features
- `main.js` - Electron main process (backend)
- `preload.js` - Electron preload script
- `ui_hightech.html` - High-tech UI frontend
- `package.json` - Node.js dependencies
- `requirements.txt` - Python dependencies

### Supporting Modules
- `color_enhancement.py` - Artistic color enhancements
- `add_free_features.py` - Fantasy and 3D terrain generation
- `clear_cache.py` - Cache management utility
- `logging_config.py` - Logging configuration
- `launch_app.bat` - Windows launcher script

### Data Directories
- `assets/` - Textures, fonts, and UI assets
- `themes/` - 43 map theme configurations
- `outputs/` - Generated map posters
- `posters/` - Sample poster gallery
- `cache/` - Coordinate and data cache
- `tests/` - Unit tests

### Documentation
- `README.md` - Main documentation
- `LICENSE` - MIT License
- `docs/` - Additional documentation

### Configuration
- `.gitignore` - Git ignore rules
- `.venv/` - Python virtual environment

## Archived Files
Moved to `archive/` directory:
- `redundant_docs/` - Consolidated documentation (FUNCTIONALITY_STATUS.md, NEW_FEATURES_SUMMARY.md)
- `redundant_launch_files/` - Alternative launch scripts (archived)
- `old_tests/` - Test scripts and results
- `old_docs/` - Outdated documentation
- `temp_files/` - Temporary utility scripts

## Features Implemented

✅ **Core Features**
- Real map generation from OpenStreetMap
- 43 visual themes
- Multiple output formats (PNG, JPG, PDF, SVG)
- Texture application
- Artistic effects
- Color enhancements

✅ **New Features**
- Fantasy map generation (no API required)
- 3D terrain visualization
- Map shapes (circle, triangle)
- Enhanced geocoding with retry logic
- Full UI integration

✅ **Technical**
- API compliance with rate limiting
- Caching for performance
- Error handling and logging
- Cross-platform support

## Running the Application

### Method 1: Using the batch file (Windows)
```batch
launch_app.bat
```

### Method 2: Manual start
```bash
# Activate virtual environment
.venv\Scripts\activate

# Start Electron
npm start
```

### Method 3: Command line interface
```bash
# Basic map
python create_map_poster.py --city "Paris" --country "France"

# Fantasy map with circle shape
python create_map_poster.py --city "Test" --country "Fantasy" --map-style "fantasy" --map-shape "circle"

# Full features
python create_map_poster.py --city "London" --country "UK" --texture "canvas" --artistic-effect "vintage" --map-shape "triangle"
```

## Dependencies

### Python
- osmnx - Street network data
- geopy - Geocoding
- matplotlib - Plotting
- PIL/Pillow - Image processing
- numpy - Numerical operations

### Node.js
- electron - Desktop framework

## Cache System
- Coordinates cached in `cache/coords.json`
- Reduces API calls for repeated locations
- Automatic cleanup with `clear_cache.py`

## Output Directory
All generated maps saved to `outputs/` with timestamped filenames:
```
outputs/
  paris_feature_based_20260124_124949.png
  london_vintage_sepia_20260124_124934.jpg
  test_fantasy_20260124_125024.png
```

## UI Features
- Real-time progress updates
- Theme selection dropdown
- Map style selector (Real/Fantasy/3D)
- Map shape selector (Rectangle/Circle/Triangle)
- Texture and effect controls
- Output format selection
- Persistent settings

## Notes
- Fantasy and 3D modes work offline (no API needed)
- Rate limiting implemented for geocoding (1 request/second)
- All features tested and functional
- Backward compatibility maintained
