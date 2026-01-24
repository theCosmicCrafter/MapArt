# Map Poster Generator

A sophisticated Electron application that generates beautiful, customizable map posters for any city in the world. Built with Python backend for map processing and Electron for the modern UI.

![Map Poster Generator](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Electron](https://img.shields.io/badge/Electron-30.0+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **City Map Generation**: Create stunning posters for any city worldwide
- **43 Unique Themes**: From minimalist noir to vibrant watercolor styles
- **Customizable Dimensions**: Support for various poster sizes (inches)
- **Multiple Output Formats**: PNG, JPG, JPEG, SVG, and PDF support
- **High Resolution**: 300 DPI output for print-quality posters

### Advanced Features
- **Font Selection**: Choose from Roboto font family (Bold, Regular, Light)
- **Paper Textures**: 50+ authentic paper textures for artistic effect
- **Artistic Effects**: Watercolor, pencil sketch, oil painting, vintage
- **Color Enhancements**: 
  - Intelligent palette optimization
  - Geographic color schemes
  - Seasonal variations (Summer, Autumn, Winter, Spring)
- **Distance Control**: Adjust map radius from 4km to 20km
- **State/Province Support**: Optional region specification

### Technical Features
- **Modern UI**: Sleek high-tech interface with theme switching
- **Real-time Progress**: Live progress updates during generation
- **Error Handling**: Comprehensive error reporting and logging
- **Cache System**: Intelligent caching for faster repeat generations
- **OpenStreetMap Integration**: Up-to-date map data from OSM

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16.0 or higher
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/maptoposter.git
   cd maptoposter
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   npm install
   ```

5. **Launch the application**
   ```bash
   npm start
   ```
   
   Or simply double-click `launch_app.bat` on Windows

## 📖 Usage Guide

### Basic Usage

1. **Enter Location**: Type city name (e.g., "Paris", "New York, USA")
2. **Select Theme**: Choose from 43 available themes
3. **Adjust Settings**:
   - Distance: Map radius in meters
   - Dimensions: Width and height in inches
   - Format: Output file format
   - Font: Text font family
   - Texture: Paper texture overlay
   - Artistic Effect: Style transformation
   - Color Enhancement: Color optimization
4. **Generate**: Click "Execute Pulse" to create your poster

### Advanced Options

#### Command Line Interface
Generate posters directly from command line:

```bash
python create_map_poster.py --city "Tokyo" --country "Japan" --theme noir --distance 10000 --width 12 --height 16 --format png
```

#### Available Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--city` | `-c` | City name | Required |
| `--country` | `-C` | Country name | Required |
| `--state` | `-s` | State/province | Optional |
| `--theme` | `-t` | Theme name | feature_based |
| `--distance` | `-d` | Map radius (meters) | 29000 |
| `--width` | `-W` | Poster width (inches) | 12 |
| `--height` | `-H` | Poster height (inches) | 16 |
| `--format` | `-f` | Output format | png |
| `--font` | | Font family | Roboto |
| `--texture` | | Paper texture | none |
| `--artistic-effect` | | Artistic style | none |
| `--color-enhancement` | | Color optimization | none |

#### Theme Examples

```bash
# Iconic grid patterns
python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000
python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000

# Waterfront cities
python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000

# Radial patterns
python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000
python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000
```

## 🎨 Themes Gallery

### Minimalist Themes
- **Noir**: Classic black and white elegance
- **Blueprint**: Technical drawing style
- **Monochrome Blue**: Sophisticated blue tones

### Vibrant Themes
- **Sunset**: Warm sunset gradients
- **Ocean**: Deep ocean blues
- **Copper Patina**: Metallic copper tones

### Artistic Themes
- **Watercolor**: Soft watercolor effect
- **Japanese Ink**: Traditional sumi-e style
- **Vintage Sepia**: Aged parchment look

### Geographic Themes
- **Arctic Aurora**: Northern lights inspiration
- **Desert Oasis**: Warm desert palette
- **Forest Enchanted**: Deep forest greens

## 🔧 Configuration

### File Structure

```
maptoposter/
├── assets/
│   ├── fonts/          # Roboto font family
│   └── textures/       # 50+ paper textures
├── themes/             # 43 theme JSON files
├── outputs/            # Generated posters
├── logs/               # Application logs
├── tests/              # Test suite
├── docs/               # Documentation
├── create_map_poster.py    # Main Python script
├── main.js             # Electron main process
├── preload.js          # Electron preload script
├── ui_hightech.html    # Main UI
├── color_enhancement.py    # Color processing
└── logging_config.py  # Logging configuration
```

### Custom Themes

Create your own theme by adding a JSON file to the `themes/` directory:

```json
{
  "name": "My Custom Theme",
  "description": "A beautiful custom theme",
  "bg": "#FFFFFF",
  "text": "#000000",
  "gradient_color": "#FFFFFF",
  "water": "#C0C0C0",
  "parks": "#F0F0F0",
  "road_motorway": "#0A0A0A",
  "road_primary": "#1A1A1A",
  "road_secondary": "#2A2A2A",
  "road_tertiary": "#3A3A3A",
  "road_residential": "#4A4A4A",
  "road_default": "#3A3A3A"
}
```

### Custom Textures

Add PNG textures to `assets/textures/`:
- Recommended size: 2048x2048 pixels
- Format: PNG with transparency
- Categories: base, specialty, artistic, edges, stains

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python tests/comprehensive_test.py

# Run specific tests
python tests/test_system.py
python tests/test_quick.py
```

Test categories:
- Environment setup
- Dependency verification
- File structure validation
- Python script functionality
- Argument parsing
- Theme system
- Font system
- Texture system
- Electron app
- Integration tests

## 📊 Performance

### System Requirements

**Minimum:**
- Python 3.8
- Node.js 16.0
- 4GB RAM
- 1GB free disk space

**Recommended:**
- Python 3.10+
- Node.js 18.0+
- 8GB RAM
- 2GB free disk space

### Performance Tips

1. **Use Cache**: Enable caching for faster repeat generations
2. **Optimize Distance**: Smaller distances generate faster
3. **Choose Format**: SVG/PDF for vector, PNG/JPG for raster
4. **Texture Impact**: Textures add processing time

## 🔍 Troubleshooting

### Common Issues

**NumPy Version Conflict**
```bash
# Downgrade NumPy for compatibility
pip install "numpy<2.0"
```

**Font Not Found**
- Ensure Roboto fonts are in `assets/fonts/`
- Check font file permissions

**Theme Loading Error**
- Verify JSON syntax in theme file
- Check file is in `themes/` directory

**Generation Fails**
- Check internet connection (OSM data)
- Verify city name spelling
- Check logs in `logs/` directory

### Debug Mode

Enable debug logging:
```python
# In create_map_poster.py
logger.setLevel(logging.DEBUG)
```

Check logs:
```bash
tail -f logs/map_poster.log
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

### Code Style

- Python: Follow PEP 8
- JavaScript: Use ESLint configuration
- HTML: Follow HTML5 standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenStreetMap**: For map data
- **OSMnx**: Python library for street networks
- **Matplotlib**: Plotting library
- **Electron**: Cross-platform desktop framework
- ** Google Fonts



**Made with ❤️ by CosmicCrafter**
