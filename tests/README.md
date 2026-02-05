# Tests Directory

This directory contains the test suite for the Map Poster Generator.

## Test Files

### Quick Tests
- **test_quick.py** - Fast verification of core components
- **test_minimal.py** - Basic syntax and structure checks

### System Tests
- **test_system.py** - Comprehensive component testing
- **comprehensive_test.py** - Full end-to-end testing

### Utilities
- **test_system.bat** - Windows batch file for running tests
- **run_all_tests.py** - Python test runner with reporting

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Individual Tests
```bash
python tests/test_quick.py
python tests/test_system.py
python tests/comprehensive_test.py
```

### Windows Batch File
```cmd
cd tests
test_system.bat
```

## Test Categories

1. **Environment Tests**
   - Python version
   - Virtual environment
   - Node.js and npm

2. **Dependency Tests**
   - Module imports
   - Package versions

3. **File Structure Tests**
   - Directory existence
   - File permissions
   - Asset availability

4. **Functionality Tests**
   - Argument parsing
   - Theme loading
   - Font system
   - Texture system

5. **Integration Tests**
   - Electron app
   - IPC communication
   - End-to-end flow

## Troubleshooting

If tests fail:
1. Check Python version (3.8+)
2. Verify virtual environment is activated
3. Ensure all dependencies are installed
4. Check file permissions
5. Review logs in the main directory
