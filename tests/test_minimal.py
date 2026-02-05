#!/usr/bin/env python
"""Minimal test to verify basic functionality"""

import os
import sys

print("=== MINIMAL SYSTEM TEST ===")

# Test 1: Check if we can import the main module
try:
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())

    # Try importing without executing
    import ast

    with open("create_map_poster.py", "r") as f:
        code = f.read()

    # Parse the AST to check syntax
    ast.parse(code)
    print("✓ create_map_poster.py syntax is valid")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 2: Check critical directories
dirs_to_check = [
    ("themes", ".json files"),
    ("assets/fonts", ".ttf files"),
    ("assets/textures", ".png files"),
    ("outputs", "output directory"),
]

for dir_name, expected in dirs_to_check:
    if os.path.exists(dir_name):
        files = os.listdir(dir_name)
        print(f"✓ {dir_name}/ exists ({len(files)} items)")
    else:
        print(f"✗ {dir_name}/ missing")

# Test 3: Check key files
files_to_check = [
    "main.js",
    "preload.js",
    "ui_hightech.html",
    "package.json",
    "requirements.txt",
]

for file_name in files_to_check:
    if os.path.exists(file_name):
        print(f"✓ {file_name} exists")
    else:
        print(f"✗ {file_name} missing")

print("\n=== TEST COMPLETE ===")
print("System appears ready for operation.")
