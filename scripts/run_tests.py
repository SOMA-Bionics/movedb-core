#!/usr/bin/env python3
"""
Simple test runner for movedb-core development.
This script sets up the environment and runs tests with sensible defaults.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    if description:
        print(f"🔧 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_environment():
    """Check if we're in a conda environment with required dependencies."""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if not conda_env:
        print("⚠️  Warning: No conda environment detected")
        print("Consider activating a conda environment with the required dependencies")
        return True  # Don't fail, just warn
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✅ Running in conda environment: {conda_env}")
        return True
    except ImportError:
        print(f"⚠️  Warning: pytest not available in environment '{conda_env}'")
        print("Make sure you have pytest installed: conda install pytest")
        return False

def check_package_installed():
    """Check if the package is installed in development mode."""
    try:
        import movedb
        print(f"✅ Package installed: movedb version {movedb.__version__}")
        return True
    except ImportError:
        print("❌ Package not installed. Run: pip install -e .")
        return False

def main():
    """Main test runner."""
    print("🧪 MoveDB Core Test Runner")
    print("=" * 40)
    
    # Check environment (warn but don't fail)
    env_ok = check_environment()
    
    # Check package installation (this is critical)
    if not check_package_installed():
        sys.exit(1)
    
    # If environment check failed, warn but continue
    if not env_ok:
        print("⚠️  Environment issues detected, but continuing...")
    
    # Parse command line arguments
    test_args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not test_args:
        print("🚀 Running all tests with coverage...")
        cmd = "pytest --cov=src/movedb --cov-report=term-missing --cov-report=html -v"
    else:
        print(f"🚀 Running tests with custom arguments: {' '.join(test_args)}")
        cmd = f"pytest {' '.join(test_args)}"
    
    success = run_command(cmd, "Running pytest")
    
    if success:
        print("\n✅ Tests completed successfully!")
        if not test_args:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
