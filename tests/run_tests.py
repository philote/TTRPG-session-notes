#!/usr/bin/env python3
"""
Simple test runner script for TTRPG Session Notes tests.
Can be run directly or used with pytest.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run all unit tests using unittest."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main entry point."""
    print("Running TTRPG Session Notes test suite...")
    print("-" * 50)
    
    success = run_unit_tests()
    
    print("-" * 50)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)