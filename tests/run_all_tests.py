#!/usr/bin/env python
"""
Test runner for Map Poster Generator
Run all tests and generate a report
"""

import os
import sys
import subprocess
import time
from datetime import datetime


def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'=' * 50}")
    print(f"Running {test_file}")
    print("=" * 50)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False


def main():
    """Run all tests"""
    print("MAP POSTER GENERATOR - TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # List of test files
    tests = [
        "test_quick.py",
        "test_system.py",
        "test_minimal.py",
        "comprehensive_test.py",
    ]

    results = []

    for test in tests:
        test_path = os.path.join(os.path.dirname(__file__), test)
        if os.path.exists(test_path):
            success = run_test(test_path)
            results.append((test, success))
        else:
            print(f"\n⚠️  Test file not found: {test}")
            results.append((test, False))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {test}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed! System is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
