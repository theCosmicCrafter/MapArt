#!/usr/bin/env python
"""Quick test to verify core functionality"""

import os
import sys

print("=== MAP POSTER GENERATOR - QUICK TEST ===\n")

# Test 1: Check directories
print("1. Checking directories...")
dirs = ["themes", "assets/fonts", "assets/textures"]
for d in dirs:
    exists = os.path.exists(d)
    print(f"   {d}/: {'✓' if exists else '✗'}")

# Test 2: Check theme files
print("\n2. Checking themes...")
theme_dir = "themes"
if os.path.exists(theme_dir):
    themes = [f for f in os.listdir(theme_dir) if f.endswith(".json")]
    print(f"   Found {len(themes)} theme files ✓")
else:
    print("   Themes directory not found ✗")

# Test 3: Check font files
print("\n3. Checking fonts...")
font_dir = "assets/fonts"
if os.path.exists(font_dir):
    fonts = [f for f in os.listdir(font_dir) if f.endswith(".ttf")]
    print(f"   Found {len(fonts)} font files ✓")
else:
    print("   Font directory not found ✗")

# Test 4: Check main script
print("\n4. Checking main script...")
if os.path.exists("create_map_poster.py"):
    print("   create_map_poster.py exists ✓")
    # Check syntax
    try:
        with open("create_map_poster.py", "r") as f:
            compile(f.read(), "create_map_poster.py", "exec")
        print("   Syntax valid ✓")
    except Exception as e:
        print(f"   Syntax error: {e} ✗")
else:
    print("   create_map_poster.py not found ✗")

# Test 5: Check Electron files
print("\n5. Checking Electron files...")
files = ["main.js", "preload.js", "ui_hightech.html", "package.json"]
for f in files:
    exists = os.path.exists(f)
    print(f"   {f}: {'✓' if exists else '✗'}")

print("\n=== TEST COMPLETE ===")
print("\nTo run the app:")
print("1. Ensure virtual environment is activated")
print("2. Run: npm start")
print("3. Or use: launch_app.bat")
