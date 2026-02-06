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
   git clone https://github.com/theCosmicCrafter/MapArt.git
   cd MapArt
   ```

2. **Automated Setup (Windows)**
   Simply run the setup script to install all dependencies and create required folders:
   ```bash
   setup.bat
   ```

3. **Manual Setup**
   If you prefer manual installation:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   npm install
   ```

4. **Launch the application**
   Double-click `launch_app.bat` or run:
   ```bash
   npm start
   ```

## 📖 Usage Guide

### Basic Usage

1. **Enter Location**: Type city name (e.g., "Paris", "New York, USA")
2. **Select Theme**: Choose from 43+ available themes
3. **Adjust Settings**:
   - Distance: Map radius in meters
   - Dimensions: Width and height in inches
   - Format: Output file format
   - Font: Text font family
   - Texture: Paper texture overlay
   - Artistic Effect: Style transformation
   - Color Enhancement: Color optimization
4. **Generate**: Click "Execute Pulse" to create your poster. Track progress via the AQ (Active Queue) counter in the header.

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
MapArt/
├── assets/
│   ├── fonts/          # Roboto font family
│   ├── textures/       # 100+ High-resolution paper textures
│   └── posters/        # Pre-generated preview examples
├── themes/             # 43+ custom theme JSON files
├── outputs/            # Generated posters (ignored by Git)
├── logs/               # Application logs (ignored by Git)
├── map_providers/      # Specialized layer logic (Rail, Sea, Star, etc.)
├── create_map_poster.py    # Main Python logic
├── main.js             # Electron main process
├── ui_hightech.html    # High-tech Pulse UI
├── color_enhancement.py    # Artistic processing & enhancement
├── input_validation.py # Coordinate and input safety
└── setup.bat           # Automated environment setup
```

### Custom Themes

Create your own theme by adding a JSON file to the `themes/` directory:

```json
{
  "name": "My Custom Theme",
  "bg": "#FFFFFF",
  "text": "#000000",
  "road_primary": "#1A1A1A",
  "water": "#C0C0C0",
  "parks": "#F0F0F0"
}
```

## 📊 Performance & Optimization

1. **Smart Cache**: The system caches OSM data to speed up subsequent generations of the same area.
2. **Metadata Injection**: All generated PNGs include embedded metadata: Artist (**CosmicCrafter**), Coordinates, Theme, and Software details.
3. **Queue System**: Supports multiple concurrent jobs with real-time progress monitoring.

## 🔍 Troubleshooting

**NumPy Version Conflict**
If you see error related to NumPy 2.0: `pip install "numpy<2.0"`

**Generation Fails**
- Check internet connection (required for initial OSM data fetch)
- Verify city/country spelling
- Check `logs/` for detailed error reports

## 📄 License & Credits

This project is licensed under the MIT License.

### Acknowledgments
- **Inspiration**: This project was inspired by [originalankur/maptoposter](https://github.com/originalankur/maptoposter) but has since evolved into a standalone project with unique UI, layer logic, and artistic features.
- **OpenStreetMap**: For global map data.
- **OSMnx**: street network analysis.
- **Electron**: desktop framework.

**Made with ❤️ by [CosmicCrafter](https://github.com/theCosmicCrafter)**
