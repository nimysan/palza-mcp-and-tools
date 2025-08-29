#!/usr/bin/env python3
"""Generate test structure visualization."""

import os
import json
from pathlib import Path


def generate_test_tree():
    """Generate test structure tree."""
    test_dir = Path("tests")
    tree = {}
    
    for root, dirs, files in os.walk(test_dir):
        root_path = Path(root)
        current = tree
        
        # Build nested structure
        for part in root_path.parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add files
        for file in files:
            if file.endswith('.py'):
                current[file] = "test_file"
    
    return tree


def print_tree(tree, indent=0):
    """Print tree structure."""
    for key, value in tree.items():
        print("  " * indent + f"├── {key}")
        if isinstance(value, dict):
            print_tree(value, indent + 1)


def main():
    """Main function."""
    print("📊 Test Structure Visualization")
    print("=" * 40)
    
    tree = generate_test_tree()
    print_tree(tree)
    
    print("\n📈 Available Reports:")
    print("- HTML Coverage Report: htmlcov/index.html")
    print("- Test Report: reports/report.html")
    print("- JSON Report: reports/report.json")
    
    print("\n🚀 Quick Commands:")
    print("- Run tests: uv run pytest")
    print("- Open coverage: open htmlcov/index.html")
    print("- Open test report: open reports/report.html")


if __name__ == "__main__":
    main()
