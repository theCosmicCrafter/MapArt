# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

## Quick Install

### Option 1: Using the installer script (Windows)

1. **Batch file:**
   ```cmd
   install_requirements.bat
   ```

2. **PowerShell:**
   ```powershell
   .\install_requirements.ps1
   ```

### Option 2: Manual installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd maptoposter
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   
   - Windows:
     ```cmd
     .venv\Scripts\activate
     ```
   
   - Mac/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

## Optional Dependencies

### ML Colorization Model
For automatic colorization of maps:
```bash
pip install ddcolor @ git+https://github.com/piddnad/DDColor.git
```

### GPU Acceleration (NVIDIA only)
If you have an NVIDIA GPU and want faster processing:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Verify Installation

Run the test script to verify all packages are installed:
```bash
python check_requirements.py
```

Or try listing available themes:
```bash
python create_map_poster.py --list-themes
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   - Make sure you've activated the virtual environment
   - Try reinstalling: `pip install -r requirements.txt`

2. **Rasterio installation fails:**
   - Windows: Install GDAL first: `pip install GDAL`
   - Or use conda: `conda install rasterio -c conda-forge`

3. **OpenCV issues:**
   - Uninstall and reinstall: 
     ```bash
     pip uninstall opencv-python opencv-contrib-python
     pip install opencv-python==4.8.1.78 opencv-contrib-python==4.8.1.78
     ```

4. **Memory errors:**
   - Close other applications
   - Try reducing the map distance parameter
   - Use a smaller poster size

### Platform-Specific Notes

#### Windows
- Use Python from python.org (not Microsoft Store)
- Run Command Prompt as Administrator if needed
- Some packages may require Microsoft Visual C++ Redistributable

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- If using Apple Silicon, use native Python (not Rosetta)

#### Linux
- Install system dependencies first:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev python3-pip libgdal-dev gdal-bin
  
  # Fedora/CentOS
  sudo dnf install python3-devel python3-pip gdal gdal-devel
  ```

## Next Steps

Once installation is complete:

1. **Run the app:**
   ```bash
   npm start
   ```

2. **Or use CLI:**
   ```bash
   python create_map_poster.py --city "Paris" --country "France" --theme noir
   ```

3. **Check the STRUCTURE.md file for project organization**
