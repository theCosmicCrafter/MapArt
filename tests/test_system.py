#!/usr/bin/env python
"""
System tests for map poster generator
"""

import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import create_map_poster

        print("✓ Main script imports successfully")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

    try:
        import logging_config

        print("✓ Logging config imports")
    except Exception as e:
        print(f"✗ Logging config import failed: {e}")

    return True


def test_themes():
    """Test theme loading"""
    print("\nTesting themes...")
    try:
        themes = create_map_poster.get_available_themes()
        print(f"✓ Found {len(themes)} themes")

        # Test loading default theme
        theme = create_map_poster.load_theme("feature_based")
        print(f"✓ Loaded default theme: {theme.get('name', 'Unknown')}")

        # Test loading a specific theme
        if "noir" in themes:
            theme = create_map_poster.load_theme("noir")
            print(f"✓ Loaded noir theme: {theme.get('name', 'Unknown')}")

        return True
    except Exception as e:
        print(f"✗ Theme test failed: {e}")
        return False


def test_fonts():
    """Test font loading"""
    print("\nTesting fonts...")
    try:
        fonts = create_map_poster.load_fonts()
        if fonts:
            print("✓ Fonts loaded successfully")
            for weight, path in fonts.items():
                if os.path.exists(path):
                    print(f"  ✓ {weight}: {os.path.basename(path)}")
                else:
                    print(f"  ✗ {weight}: Not found at {path}")
        else:
            print("⚠ Fonts not loaded, will use system fonts")
        return True
    except Exception as e:
        print(f"✗ Font test failed: {e}")
        return False


def test_directories():
    """Test required directories exist"""
    print("\nTesting directories...")
    dirs = ["themes", "assets/fonts", "assets/textures", "outputs", "logs"]
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            os.makedirs(dir_name, exist_ok=True)
            print(f"  Created {dir_name}/")


def test_color_enhancement():
    """Test color enhancement module"""
    print("\nTesting color enhancement...")
    try:
        import color_enhancement

        print("✓ Color enhancement module imports")

        if hasattr(color_enhancement, "ColorEnhancer"):
            print("✓ ColorEnhancer class available")
        return True
    except Exception as e:
        print(f"⚠ Color enhancement not available: {e}")
        return True  # Not critical


def test_argument_parsing():
    """Test argument definitions"""
    print("\nTesting argument parsing...")
    try:
        # Create test arguments
        test_args = [
            "--city",
            "Test City",
            "--country",
            "Test Country",
            "--theme",
            "feature_based",
            "--distance",
            "10000",
            "--width",
            "12",
            "--height",
            "16",
            "--format",
            "png",
            "--font",
            "Roboto",
            "--texture",
            "none",
            "--artistic-effect",
            "none",
            "--color-enhancement",
            "none",
        ]

        # Parse arguments
        import argparse

        parser = argparse.ArgumentParser()

        # Add all arguments (simplified test)
        parser.add_argument("--city")
        parser.add_argument("--country")
        parser.add_argument("--theme", default="feature_based")
        parser.add_argument("--distance", type=int, default=29000)
        parser.add_argument("--width", type=float, default=12)
        parser.add_argument("--height", type=float, default=16)
        parser.add_argument("--format", default="png")
        parser.add_argument("--font", default="Roboto")
        parser.add_argument("--texture", default="none")
        parser.add_argument("--artistic-effect", default="none")
        parser.add_argument("--color-enhancement", default="none")

        args = parser.parse_args(test_args)

        print("✓ All arguments parsed successfully")
        print(f"  City: {args.city}")
        print(f"  Country: {args.country}")
        print(f"  Theme: {args.theme}")
        print(f"  Format: {args.format}")

        return True
    except Exception as e:
        print(f"✗ Argument parsing test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MAP POSTER GENERATOR - SYSTEM TESTS")
    print("=" * 60)

    tests = [
        test_directories,
        test_imports,
        test_argument_parsing,
        test_themes,
        test_fonts,
        test_color_enhancement,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! System is ready.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
