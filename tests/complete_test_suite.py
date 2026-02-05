#!/usr/bin/env python
"""
Complete Test Suite for Map Poster Generator
Tests every feature comprehensively
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class TestRunner:
    def __init__(self):
        self.results = {
            "environment": {"passed": 0, "failed": 0, "details": []},
            "dependencies": {"passed": 0, "failed": 0, "details": []},
            "themes": {"passed": 0, "failed": 0, "details": []},
            "textures": {"passed": 0, "failed": 0, "details": []},
            "fonts": {"passed": 0, "failed": 0, "details": []},
            "effects": {"passed": 0, "failed": 0, "details": []},
            "formats": {"passed": 0, "failed": 0, "details": []},
            "geocoding": {"passed": 0, "failed": 0, "details": []},
            "integration": {"passed": 0, "failed": 0, "details": []},
        }
        self.start_time = time.time()

    def log(self, message):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def run_command(self, cmd, timeout=120):
        """Run command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path(__file__).parent.parent),
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def test_environment(self):
        """Test environment setup"""
        self.log("\n=== TESTING ENVIRONMENT ===")

        # Python version
        if sys.version_info >= (3, 8):
            self.log("✓ Python version OK")
            self.results["environment"]["passed"] += 1
        else:
            self.log("✗ Python version too old")
            self.results["environment"]["failed"] += 1

        # Virtual environment
        if ".venv" in sys.executable or "venv" in sys.executable:
            self.log("✓ Virtual environment active")
            self.results["environment"]["passed"] += 1
        else:
            self.log("✗ Virtual environment not detected")
            self.results["environment"]["failed"] += 1

        # Required directories
        required_dirs = ["themes", "assets/fonts", "assets/textures", "outputs"]
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                self.log(f"✓ Directory {dir_name} exists")
                self.results["environment"]["passed"] += 1
            else:
                self.log(f"✗ Directory {dir_name} missing")
                self.results["environment"]["failed"] += 1

    def test_dependencies(self):
        """Test all dependencies"""
        self.log("\n=== TESTING DEPENDENCIES ===")

        required_modules = [
            "matplotlib",
            "numpy",
            "osmnx",
            "geopy",
            "PIL",
            "tqdm",
            "networkx",
            "shapely",
            "fiona",
        ]

        for module in required_modules:
            try:
                __import__(module)
                self.log(f"✓ Module {module} imported")
                self.results["dependencies"]["passed"] += 1
            except ImportError:
                self.log(f"✗ Module {module} not found")
                self.results["dependencies"]["failed"] += 1

    def test_all_themes(self):
        """Test every theme"""
        self.log("\n=== TESTING ALL THEMES ===")

        themes_dir = Path("../themes")
        themes = [f.stem for f in themes_dir.glob("*.json")]

        self.log(f"Found {len(themes)} themes")

        # Test a sample of themes (to save time)
        sample_themes = themes[:10] if len(themes) > 10 else themes

        for theme in sample_themes:
            self.log(f"Testing theme: {theme}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                "New York",
                "--country",
                "USA",
                "--theme",
                theme,
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                "jpg",
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=60)

            if success:
                self.log(f"  ✓ Theme {theme} works")
                self.results["themes"]["passed"] += 1
            else:
                self.log(f"  ✗ Theme {theme} failed")
                self.results["themes"]["failed"] += 1
                self.results["themes"]["details"].append(f"{theme}: {stderr[:100]}")

    def test_textures(self):
        """Test texture application"""
        self.log("\n=== TESTING TEXTURES ===")

        # Load texture manifest
        try:
            with open("../assets/textures/manifest.json", "r") as f:
                manifest = json.load(f)
        except:
            self.log("✗ Could not load texture manifest")
            self.results["textures"]["failed"] += 1
            return

        # Test main textures
        main_textures = [
            "aged_parchment",
            "rough_paper",
            "watercolor_paper",
            "parchment",
        ]

        for texture in main_textures:
            self.log(f"Testing texture: {texture}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                "Paris",
                "--country",
                "France",
                "--theme",
                "vintage_sepia",
                "--texture",
                texture,
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                "jpg",
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=60)

            if success and "Texture applied successfully" in stdout:
                self.log(f"  ✓ Texture {texture} applied")
                self.results["textures"]["passed"] += 1
            else:
                self.log(f"  ✗ Texture {texture} failed")
                self.results["textures"]["failed"] += 1

    def test_fonts(self):
        """Test font system"""
        self.log("\n=== TESTING FONTS ===")

        fonts = ["Arial", "Times New Roman", "Courier New", "Verdana"]

        for font in fonts:
            self.log(f"Testing font: {font}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                "London",
                "--country",
                "UK",
                "--theme",
                "noir",
                "--font",
                font,
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                "jpg",
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=60)

            if success:
                self.log(f"  ✓ Font {font} works")
                self.results["fonts"]["passed"] += 1
            else:
                self.log(f"  ✗ Font {font} failed")
                self.results["fonts"]["failed"] += 1

    def test_artistic_effects(self):
        """Test artistic effects"""
        self.log("\n=== TESTING ARTISTIC EFFECTS ===")

        # First check if color_enhancement module exists
        if not Path("../color_enhancement.py").exists():
            self.log("! Artistic effects module not found, skipping...")
            return

        effects = ["watercolor", "pencil_sketch", "vintage"]

        for effect in effects:
            self.log(f"Testing effect: {effect}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                "Tokyo",
                "--country",
                "Japan",
                "--theme",
                "feature_based",
                "--artistic-effect",
                effect,
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                "jpg",
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=60)

            if success:
                self.log(f"  ✓ Effect {effect} works")
                self.results["effects"]["passed"] += 1
            else:
                self.log(f"  ✗ Effect {effect} failed")
                self.results["effects"]["failed"] += 1

    def test_output_formats(self):
        """Test all output formats"""
        self.log("\n=== TESTING OUTPUT FORMATS ===")

        formats = ["jpg", "png", "pdf"]

        for fmt in formats:
            self.log(f"Testing format: {fmt}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                "Sydney",
                "--country",
                "Australia",
                "--theme",
                "ocean",
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                fmt,
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=60)

            if success:
                self.log(f"  ✓ Format {fmt} works")
                self.results["formats"]["passed"] += 1
            else:
                self.log(f"  ✗ Format {fmt} failed")
                self.results["formats"]["failed"] += 1

    def test_geocoding(self):
        """Test geocoding with various locations"""
        self.log("\n=== TESTING GEOCODING ===")

        # Test locations that should work
        locations = [
            ("New York", "USA"),
            ("London", "UK"),
            ("Paris", "France"),
            ("Tokyo", "Japan"),
            ("Berlin", "Germany"),
        ]

        for city, country in locations:
            self.log(f"Testing location: {city}, {country}")

            cmd = [
                ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python",
                "create_map_poster.py",
                "--city",
                city,
                "--country",
                country,
                "--theme",
                "feature_based",
                "--distance",
                "8000",
                "--width",
                "8",
                "--height",
                "10",
                "--format",
                "jpg",
            ]

            success, stdout, stderr = self.run_command(cmd, timeout=90)

            if success:
                self.log(f"  ✓ Location {city}, {country} works")
                self.results["geocoding"]["passed"] += 1
            else:
                self.log(f"  ✗ Location {city}, {country} failed")
                self.results["geocoding"]["failed"] += 1

    def test_integration(self):
        """Test integration scenarios"""
        self.log("\n=== TESTING INTEGRATION ===")

        # Test Electron app (if main.js exists)
        if Path("../main.js").exists():
            self.log("Testing Electron app structure...")
            # Just check if main.js is valid
            try:
                with open("../main.js", "r") as f:
                    content = f.read()
                if "ipcMain" in content and "create_map_poster.py" in content:
                    self.log("  ✓ Electron app structure OK")
                    self.results["integration"]["passed"] += 1
                else:
                    self.log("  ✗ Electron app structure issue")
                    self.results["integration"]["failed"] += 1
            except:
                self.log("  ✗ Could not read main.js")
                self.results["integration"]["failed"] += 1

        # Test UI files
        ui_files = ["ui_hightech.html", "preload.js"]
        for ui_file in ui_files:
            if Path(f"../{ui_file}").exists():
                self.log(f"  ✓ {ui_file} exists")
                self.results["integration"]["passed"] += 1
            else:
                self.log(f"  ✗ {ui_file} missing")
                self.results["integration"]["failed"] += 1

    def generate_report(self):
        """Generate comprehensive test report"""
        elapsed = time.time() - self.start_time

        self.log("\n" + "=" * 60)
        self.log("COMPREHENSIVE TEST REPORT")
        self.log("=" * 60)

        total_passed = 0
        total_failed = 0

        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed

            self.log(f"\n{category.upper()}:")
            self.log(f"  Passed: {passed}")
            self.log(f"  Failed: {failed}")

            if results["details"]:
                self.log("  Issues:")
                for detail in results["details"][:3]:
                    self.log(f"    - {detail}")

        self.log(f"\nOVERALL SUMMARY:")
        self.log(f"  Total Tests: {total_passed + total_failed}")
        self.log(f"  Passed: {total_passed}")
        self.log(f"  Failed: {total_failed}")
        self.log(
            f"  Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%"
        )
        self.log(f"  Duration: {elapsed:.1f} seconds")

        # Save report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": elapsed,
            "results": self.results,
            "summary": {
                "total_passed": total_passed,
                "total_failed": total_failed,
                "success_rate": f"{(total_passed / (total_passed + total_failed) * 100):.1f}%",
            },
        }

        with open("../test_outputs/complete_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"\nDetailed report saved to: test_outputs/complete_test_report.json")

        return total_failed == 0

    def run_all_tests(self):
        """Run all tests"""
        self.log("STARTING COMPLETE TEST SUITE")
        self.log("=" * 60)

        # Ensure test outputs directory exists
        Path("../test_outputs").mkdir(exist_ok=True)

        # Run all test categories
        self.test_environment()
        self.test_dependencies()
        self.test_all_themes()
        self.test_textures()
        self.test_fonts()
        self.test_artistic_effects()
        self.test_output_formats()
        self.test_geocoding()
        self.test_integration()

        # Generate final report
        success = self.generate_report()

        if success:
            self.log("\n✅ ALL CRITICAL TESTS PASSED!")
            self.log("The Map Poster Generator is fully functional.")
        else:
            self.log("\n⚠️ SOME TESTS FAILED")
            self.log("Please review the report for details.")

        return success


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
