#!/usr/bin/env python
"""Final test to verify everything works"""

import subprocess
import sys
import os

print("=== FINAL SYSTEM TEST ===\n")

# Test 1: Python with virtual environment
print("1. Testing Python script with virtual environment...")
try:
    result = subprocess.run(
        [".venv\\Scripts\\python.exe", "create_map_poster.py", "--list-themes"],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
    )

    if result.returncode == 0:
        themes = result.stdout.strip().split("\n")
        print(f"   ✓ Script runs successfully")
        print(f"   ✓ Output contains {len([t for t in themes if t])} lines")
    else:
        print(f"   ✗ Script failed with return code {result.returncode}")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Test 2: Check if we can import modules
print("\n2. Testing module imports...")
modules = ["matplotlib", "numpy", "osmnx", "geopandas", "PIL"]
for module in modules:
    try:
        __import__(module)
        print(f"   ✓ {module}")
    except ImportError as e:
        print(f"   ✗ {module}: {e}")

# Test 3: Verify all arguments are defined
print("\n3. Checking argument definitions...")
with open("create_map_poster.py", "r") as f:
    content = f.read()

required_args = [
    "--font",
    "--texture",
    "--artistic-effect",
    "--color-enhancement",
    "--format",
    "--state",
]

for arg in required_args:
    if arg in content:
        print(f"   ✓ {arg} defined")
    else:
        print(f"   ✗ {arg} missing")

# Test 4: Check output directory
print("\n4. Checking output directory...")
if os.path.exists("outputs"):
    print(f"   ✓ outputs/ exists")
    count = len(os.listdir("outputs"))
    print(f"   Contains {count} files")
else:
    print(f"   ⚠ outputs/ will be created on first run")

print("\n=== TEST COMPLETE ===")
print("\nTo run the app:")
print("1. npm start")
print("2. Or double-click launch_app.bat")
