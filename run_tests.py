#!/usr/bin/env python3
"""Test runner for shopping service"""

import subprocess
import sys

def run_shopping_tests():
    """Run shopping service tests"""
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/shopping/test_service.py", 
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_shopping_tests()
    sys.exit(0 if success else 1)
