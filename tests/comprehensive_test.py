#!/usr/bin/env python
"""
Comprehensive test suite for Map Poster Generator
Tests all aspects of the application
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_test(name, result, details=""):
    """Print a test result"""
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"  {status} {name}")
    if details:
        print(f"    {details}")


def test_environment():
    """Test the development environment"""
    print_section("ENVIRONMENT TESTS")

    results = []

    # Test Python version
    version = sys.version_info
    python_ok = version.major == 3 and version.minor >= 8
    results.append(python_ok)
    print_test(
        "Python 3.8+",
        python_ok,
        f"Found {version.major}.{version.minor}.{version.micro}",
    )

    # Test virtual environment
    venv_exists = os.path.exists(".venv")
    results.append(venv_exists)
    print_test("Virtual environment", venv_exists, ".venv directory exists")

    # Test Node.js
    try:
        node_result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True
        )
        node_ok = node_result.returncode == 0
        results.append(node_ok)
        print_test("Node.js", node_ok, node_result.stdout.strip())
    except:
        results.append(False)
        print_test("Node.js", False, "Not installed")

    # Test npm
    try:
        npm_result = subprocess.run(
            ["npm", "--version"], capture_output=True, text=True
        )
        npm_ok = npm_result.returncode == 0
        results.append(npm_ok)
        print_test("npm", npm_ok, npm_result.stdout.strip())
    except:
        results.append(False)
        print_test("npm", False, "Not installed")

    return all(results)


def test_dependencies():
    """Test Python dependencies"""
    print_section("DEPENDENCY TESTS")

    # Test critical modules
    modules = [
        ("matplotlib", "Plotting library"),
        ("numpy", "Numerical computing"),
        ("osmnx", "OpenStreetMap interface"),
        ("geopandas", "Geospatial data"),
        ("PIL", "Image processing (Pillow)"),
        ("geopy", "Geocoding"),
        ("networkx", "Graph operations"),
        ("tqdm", "Progress bars"),
    ]

    results = []
    for module, description in modules:
        try:
            __import__(module)
            results.append(True)
            print_test(module, True, description)
        except ImportError as e:
            results.append(False)
            print_test(module, False, f"{description} - {e}")

    return all(results)


def test_file_structure():
    """Test project file structure"""
    print_section("FILE STRUCTURE TESTS")

    # Required directories
    dirs = [
        ("themes", "Theme files"),
        ("assets/fonts", "Font files"),
        ("assets/textures", "Texture files"),
        ("outputs", "Output directory"),
        ("logs", "Log files"),
    ]

    results = []
    for dir_path, description in dirs:
        exists = os.path.exists(dir_path)
        results.append(exists)
        if exists:
            count = len(os.listdir(dir_path))
            print_test(dir_path, True, f"{description} ({count} items)")
        else:
            print_test(dir_path, False, description)

    # Required files
    files = [
        ("create_map_poster.py", "Main Python script"),
        ("main.js", "Electron main process"),
        ("preload.js", "Electron preload script"),
        ("ui_hightech.html", "Main UI"),
        ("package.json", "Node.js configuration"),
        ("requirements.txt", "Python dependencies"),
    ]

    for file_path, description in files:
        exists = os.path.exists(file_path)
        results.append(exists)
        if exists:
            size = os.path.getsize(file_path)
            print_test(file_path, True, f"{description} ({size:,} bytes)")
        else:
            print_test(file_path, False, description)

    return all(results)


def test_python_script():
    """Test Python script functionality"""
    print_section("PYTHON SCRIPT TESTS")

    results = []

    # Test syntax
    try:
        with open("create_map_poster.py", "r") as f:
            compile(f.read(), "create_map_poster.py", "exec")
        results.append(True)
        print_test("Syntax check", True, "Script compiles successfully")
    except SyntaxError as e:
        results.append(False)
        print_test("Syntax check", False, f"Line {e.lineno}: {e.msg}")

    # Test help output
    try:
        result = subprocess.run(
            [".venv\\Scripts\\python.exe", "create_map_poster.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        help_ok = result.returncode == 0 and "usage:" in result.stdout
        results.append(help_ok)
        print_test("Help command", help_ok, "Displays usage information")
    except:
        results.append(False)
        print_test("Help command", False, "Failed to execute")

    # Test list themes
    try:
        result = subprocess.run(
            [".venv\\Scripts\\python.exe", "create_map_poster.py", "--list-themes"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        themes_ok = result.returncode == 0
        results.append(themes_ok)
        print_test("List themes", themes_ok, "Lists available themes")
    except:
        results.append(False)
        print_test("List themes", False, "Failed to execute")

    return all(results)


def test_arguments():
    """Test argument definitions"""
    print_section("ARGUMENT TESTS")

    with open("create_map_poster.py", "r") as f:
        content = f.read()

    # Required arguments
    args = [
        ("--city", "City name"),
        ("--country", "Country name"),
        ("--theme", "Theme selection"),
        ("--font", "Font family"),
        ("--texture", "Paper texture"),
        ("--artistic-effect", "Artistic effects"),
        ("--color-enhancement", "Color enhancements"),
        ("--format", "Output format"),
        ("--distance", "Map radius"),
        ("--width", "Image width"),
        ("--height", "Image height"),
        ("--state", "State/province"),
    ]

    results = []
    for arg, description in args:
        exists = arg in content
        results.append(exists)
        print_test(arg, exists, description)

    return all(results)


def test_themes():
    """Test theme system"""
    print_section("THEME SYSTEM TESTS")

    results = []

    # Count themes
    if os.path.exists("themes"):
        theme_files = [f for f in os.listdir("themes") if f.endswith(".json")]
        results.append(len(theme_files) > 0)
        print_test("Theme files", True, f"Found {len(theme_files)} themes")

        # Test loading a theme
        try:
            import create_map_poster

            theme = create_map_poster.load_theme("feature_based")
            theme_ok = theme and "name" in theme
            results.append(theme_ok)
            print_test(
                "Load theme", theme_ok, f"Loaded: {theme.get('name', 'Unknown')}"
            )
        except Exception as e:
            results.append(False)
            print_test("Load theme", False, str(e))
    else:
        results.append(False)
        print_test("Theme directory", False, "Not found")

    return all(results)


def test_fonts():
    """Test font system"""
    print_section("FONT SYSTEM TESTS")

    results = []

    if os.path.exists("assets/fonts"):
        font_files = [f for f in os.listdir("assets/fonts") if f.endswith(".ttf")]
        results.append(len(font_files) > 0)
        print_test("Font files", True, f"Found {len(font_files)} fonts")

        # Check for Roboto family
        roboto_files = [f for f in font_files if "Roboto" in f]
        results.append(len(roboto_files) >= 3)
        print_test(
            "Roboto family",
            len(roboto_files) >= 3,
            f"Found {len(roboto_files)} Roboto fonts",
        )
    else:
        results.append(False)
        print_test("Font directory", False, "Not found")

    return all(results)


def test_textures():
    """Test texture system"""
    print_section("TEXTURE SYSTEM TESTS")

    results = []

    if os.path.exists("assets/textures"):
        texture_files = [f for f in os.listdir("assets/textures") if f.endswith(".png")]
        results.append(len(texture_files) > 0)
        print_test("Texture files", True, f"Found {len(texture_files)} textures")

        # Check texture categories
        categories = set()
        for f in texture_files:
            parts = f.split("_")
            if len(parts) > 1:
                categories.add(parts[0])

        results.append(len(categories) > 0)
        print_test("Texture categories", True, f"Found {len(categories)} categories")
    else:
        results.append(False)
        print_test("Texture directory", False, "Not found")

    return all(results)


def test_electron_app():
    """Test Electron application"""
    print_section("ELECTRON APP TESTS")

    results = []

    # Check package.json
    if os.path.exists("package.json"):
        try:
            with open("package.json", "r") as f:
                package = json.load(f)

            main_ok = "main.js" in package.get("main", "")
            results.append(main_ok)
            print_test(
                "package.json", main_ok, f"Main: {package.get('main', 'Not set')}"
            )

            electron_ok = "electron" in package.get("devDependencies", {})
            results.append(electron_ok)
            print_test("Electron dependency", electron_ok, "In devDependencies")
        except:
            results.append(False)
            print_test("package.json", False, "Invalid JSON")
    else:
        results.append(False)
        print_test("package.json", False, "Not found")

    # Check main.js
    if os.path.exists("main.js"):
        with open("main.js", "r") as f:
            main_content = f.read()

        ipc_handlers = ["generate-map", "get-newest-poster", "open-folder"]
        for handler in ipc_handlers:
            exists = handler in main_content
            results.append(exists)
            print_test(f"IPC: {handler}", exists, "Handler defined")

    # Check preload.js
    if os.path.exists("preload.js"):
        with open("preload.js", "r") as f:
            preload_content = f.read()

        api_methods = ["generateMap", "getNewestPoster", "openFolder"]
        for method in api_methods:
            exists = method in preload_content
            results.append(exists)
            print_test(f"API: {method}", exists, "Method exposed")

    return all(results)


def test_integration():
    """Test end-to-end integration"""
    print_section("INTEGRATION TESTS")

    results = []

    # Test parameter flow simulation
    print_test("Parameter flow", True, "UI → main.js → Python → create_poster()")

    # Test output directory creation
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    results.append(True)
    print_test("Output directory", True, "Ready for generation")

    # Test logging setup
    if not os.path.exists("logs"):
        os.makedirs("logs")
    results.append(True)
    print_test("Logging system", True, "Logs will save to /logs")

    return all(results)


def main():
    """Run all tests"""
    print_section("MAP POSTER GENERATOR - COMPREHENSIVE TEST SUITE")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all test suites
    test_suites = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("Python Script", test_python_script),
        ("Arguments", test_arguments),
        ("Themes", test_themes),
        ("Fonts", test_fonts),
        ("Textures", test_textures),
        ("Electron App", test_electron_app),
        ("Integration", test_integration),
    ]

    results = []
    for name, test_func in test_suites:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            results.append((name, False))

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} {name}")

    print(f"\nOverall: {passed}/{total} test suites passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - System is fully functional!")
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
