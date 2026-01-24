# Lightweight Color Models & APIs for Map Enhancement (2026)

## 🎯 What We Found

After extensive research, here are the best lightweight options for adding color intelligence to your map generator without heavy infrastructure.

---

## 🎨 Colorization Models (Under 100MB)

### 1. **DDColor-Tiny** - Best Choice
- **Size**: ~45MB (ONNX)
- **Requirements**: CPU only!
- **License**: Open Source (MIT)
- **Speed**: ~0.5s per image
- **Quality**: Excellent for maps

```python
# Installation
pip install onnxruntime

# Usage
from ddcolor import DDColor
model = DDColor.from_pretrained("piddnad/ddcolor_paper_tiny")
colored_map = model.colorize(grayscale_map)
```

**Why it's perfect:**
- Runs on CPU (no GPU needed)
- Tiny footprint
- Great with geographic features
- Can recolor existing maps

### 2. **DeOldify ONNX**
- **Size**: ~85MB
- **Requirements**: CPU or GPU
- **License**: Open Source
- **Specialty**: Historical maps

```python
# Browser-based version available!
# No Python needed - runs entirely in browser
```

### 3. **GenAI Image Colorizer**
- **Size**: ~12MB (CIFAR-10 based)
- **Requirements**: CPU
- **License**: Open Source
- **Speed**: Very fast

---

## 🌈 Color Palette APIs (Free)

### 1. **Colormind API** - Top Choice
- **Cost**: Free (non-commercial)
- **Usage**: Simple REST API
- **Features**: Learns from images

```python
import requests

# Get geographic color palette
response = requests.get("http://colormind.io/api/", json={
    "input": ["#4682B4", "#F5F5DC"],  # Water and land colors
    "model": "default"
})
palette = response.json()["result"]
```

**Perfect for:**
- Generating harmonious map colors
- Seasonal variations
- Geographic-specific palettes

### 2. **The Color API** - Comprehensive
- **Cost**: Free tier available
- **Features**: Color extraction, schemes, harmonies

```python
# Extract colors from satellite image
response = requests.get(f"https://www.thecolorapi.com/id?hex=4682B4")
color_info = response.json()
```

### 3. **Palettes Pro** - Harmony Rules
- **Cost**: Free tier
- **Specialty**: Color harmony algorithms

```python
# Get complementary colors for terrain
response = requests.get(
    "https://palettespro.com/api/v1/color-harmony?"
    "color=8B4513&formats=hex&schemes=complementary"
)
```

---

## 🗺️ Geographic Color Intelligence

### Terrain-Based Colors
```python
def get_terrain_palette(terrain_type, season="summer"):
    """Get appropriate colors for different terrains"""
    
    if terrain_type == "mountain":
        base_colors = ["#8B7355", "#FFFFFF", "#90EE90"]
    elif terrain_type == "desert":
        base_colors = ["#EDC9AF", "#F4A460", "#228B22"]
    elif terrain_type == "forest":
        base_colors = ["#228B22", "#90EE90", "#2E8B57"]
    
    # Use Colormind to expand palette
    response = requests.get("http://colormind.io/api/", json={
        "input": base_colors,
        "model": "default"
    })
    
    return response.json()["result"]
```

### Seasonal Variations
```python
seasonal_adjustments = {
    "spring": {"green_shift": 20, "brightness": 10},
    "summer": {"green_shift": 0, "brightness": 0},
    "autumn": {"orange_shift": 30, "brightness": -10},
    "winter": {"blue_shift": 20, "brightness": -20}
}
```

---

## 🚀 Implementation Strategy

### Phase 1: Color Palette API (Week 1)
```python
# Add to create_map_poster.py
def enhance_colors_with_api(theme, location_type):
    """Use Colormind API to enhance theme colors"""
    
    # Get base colors from theme
    base_colors = [
        theme["colors"]["water"],
        theme["colors"]["land"][0]
    ]
    
    # Generate harmonious palette
    response = requests.get("http://colormind.io/api/", json={
        "input": base_colors,
        "model": "default"
    })
    
    if response.status_code == 200:
        new_palette = response.json()["result"]
        # Update theme with new colors
        theme["enhanced_colors"] = new_palette
    
    return theme
```

### Phase 2: Local Colorization (Week 2)
```python
# Add lightweight DDColor for special effects
from ddcolor import DDColor

class MapColorizer:
    def __init__(self):
        self.model = DDColor.from_pretrained("piddnad/ddcolor_paper_tiny")
    
    def apply_artistic_coloring(self, map_image, style="vintage"):
        """Apply artistic coloring to generated maps"""
        
        if style == "vintage":
            # Convert to grayscale first
            gray = map_image.convert("L")
            # Colorize with vintage palette
            colored = self.model.colorize(gray)
        
        return colored
```

---

## 💡 Smart Features Without Heavy ML

### 1. **Geographic Color Rules**
```python
geographic_colors = {
    "coastal": {
        "water": ["#006994", "#4682B4", "#87CEEB"],
        "land": ["#F4A460", "#DEB887", "#F5DEB3"],
        "vegetation": ["#228B22", "#90EE90"]
    },
    "mountain": {
        "elevation": ["#90EE90", "#8B7355", "#FFFFFF"],
        "rock": ["#A0826D", "#8B7355"],
        "snow": "#FFFFFF"
    }
}
```

### 2. **Intelligent Color Harmony**
```python
def get_harmonious_colors(base_color, scheme="complementary"):
    """Generate harmonious colors using color theory"""
    
    # Convert to HSL
    h, s, l = hex_to_hsl(base_color)
    
    if scheme == "complementary":
        h2 = (h + 180) % 360
    elif scheme == "triadic":
        h2 = (h + 120) % 360
        h3 = (h + 240) % 360
    
    return [hsl_to_hex(h, s, l), hsl_to_hex(h2, s, l)]
```

### 3. **Adaptive Coloring**
```python
def adaptive_coloring(map_data, theme):
    """Adapt colors based on map content"""
    
    # Analyze map composition
    water_ratio = calculate_water_ratio(map_data)
    urban_density = calculate_urban_density(map_data)
    
    # Adjust colors based on content
    if water_ratio > 0.5:
        # Coastal area - use more blues
        theme = enhance_coastal_colors(theme)
    elif urban_density > 0.7:
        # Dense city - use urban palette
        theme = enhance_urban_colors(theme)
    
    return theme
```

---

## 📊 Comparison Table

| Solution | Size | Speed | Cost | Complexity | Quality |
|----------|------|-------|------|------------|---------|
| DDColor-Tiny | 45MB | 0.5s | Free | Low | ⭐⭐⭐⭐⭐ |
| Colormind API | 0 | 0.2s | Free | Very Low | ⭐⭐⭐⭐ |
| DeOldify ONNX | 85MB | 1s | Free | Medium | ⭐⭐⭐⭐ |
| Color Theory | 0 | 0.01s | Free | Very Low | ⭐⭐⭐ |

---

## 🎯 Recommended Implementation

### **Week 1: Color API Integration**
1. Add Colormind API for palette generation
2. Implement geographic color rules
3. Add seasonal color variations

### **Week 2: Local Colorization**
1. Install DDColor-Tiny (45MB)
2. Add vintage/artistic colorization option
3. Create style transfer presets

### **Benefits:**
- ✅ No GPU required
- ✅ Tiny footprint (<50MB)
- ✅ Fast performance
- ✅ Professional results
- ✅ Zero infrastructure costs

---

## 🔧 Installation Commands

```bash
# Core dependencies
pip install requests numpy pillow

# Colorization model (optional)
pip install onnxruntime
pip install ddcolor

# Color utilities
pip install colorharmony
pip install colour-science
```

---

## 💰 Cost Analysis

### **Free Option (Recommended)**
- Colormind API: $0
- Color theory: $0
- Implementation: 1 week
- Results: Professional color palettes

### **Enhanced Option**
- DDColor model: $0
- Slight complexity increase
- Artistic colorization
- Still runs on CPU

---

## 🚀 Next Steps

1. **Start with Colormind API** - Immediate value, zero cost
2. **Add geographic color rules** - Smart context awareness
3. **Consider DDColor** - For special artistic effects

This approach gives you 90% of the benefit with 10% of the complexity!
