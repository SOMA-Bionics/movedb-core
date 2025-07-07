#!/usr/bin/env python3
"""
Version 1.0.0 readiness checker for movedb-core.
This script checks various metrics and requirements for v1.0.0 release.
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, description="", capture_output=True):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=False)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_test_coverage():
    """Check test coverage percentage."""
    print("🧪 Checking test coverage...")
    success, stdout, stderr = run_command("pytest --cov=src/movedb --cov-report=term-missing --quiet")
    
    if success and stdout:
        # Extract coverage percentage
        lines = stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                # Extract percentage from line like "TOTAL    123    45    67%"
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        percentage = int(part[:-1])
                        if percentage >= 90:
                            print(f"  ✅ Coverage: {percentage}% (target: ≥90%)")
                            return True, percentage
                        else:
                            print(f"  ⚠️  Coverage: {percentage}% (target: ≥90%)")
                            return False, percentage
    
    print("  ❌ Could not determine coverage")
    return False, 0

def check_linting():
    """Check linting status."""
    print("🔍 Checking code quality...")
    
    checks = [
        ("Black formatting", "black --check src/ tests/"),
        ("Import sorting", "isort --check-only src/ tests/"),
        ("Flake8 linting", "flake8 src/ tests/"),
    ]
    
    all_passed = True
    for name, cmd in checks:
        success, _, _ = run_command(cmd)
        if success:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_passed = False
    
    return all_passed

def check_documentation():
    """Check documentation completeness."""
    print("📚 Checking documentation...")
    
    docs_files = [
        "README.md",
        "docs/DEVELOPMENT.md",
        "docs/LINTING.md",
        "docs/CONDA_PACKAGING.md",
        "docs/CONDA_FORGE_SUBMISSION.md",
        "docs/ROADMAP_V1.md",
        "docs/INSTALL.md",
        "LICENSE",
    ]
    
    missing = []
    for doc in docs_files:
        if not Path(doc).exists():
            missing.append(doc)
    
    if missing:
        print(f"  ❌ Missing documentation: {', '.join(missing)}")
        return False
    else:
        print("  ✅ Core documentation files present")
        return True

def check_package_structure():
    """Check package structure and imports."""
    print("📦 Checking package structure...")
    
    try:
        # Try importing main modules
        import movedb
        import movedb.core
        import movedb.file_io
        import movedb.utils
        
        print(f"  ✅ Package imports successfully (version: {movedb.__version__})")
        return True, movedb.__version__
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False, None

def check_version_consistency():
    """Check version consistency across files."""
    print("🔢 Checking version consistency...")
    
    # Check pyproject.toml
    pyproject_version = None
    if Path("pyproject.toml").exists():
        with open("pyproject.toml", "r") as f:
            for line in f:
                if line.strip().startswith("version ="):
                    pyproject_version = line.split('"')[1]
                    break
    
    # Check conda recipe
    conda_version = None
    if Path("conda-recipe/meta.yaml").exists():
        with open("conda-recipe/meta.yaml", "r") as f:
            for line in f:
                if "set version =" in line:
                    conda_version = line.split('"')[1]
                    break
    
    # Check package version
    try:
        import movedb
        package_version = movedb.__version__
    except:
        package_version = None
    
    print(f"  📄 pyproject.toml: {pyproject_version}")
    print(f"  🐍 Package: {package_version}")
    print(f"  📦 Conda recipe: {conda_version}")
    
    versions = [v for v in [pyproject_version, package_version, conda_version] if v is not None]
    if len(set(versions)) == 1:
        print("  ✅ All versions consistent")
        return True, versions[0]
    else:
        print("  ❌ Version mismatch detected")
        return False, None

def check_ci_status():
    """Check CI/CD status."""
    print("🔄 Checking CI/CD...")
    
    workflows = [
        ".github/workflows/ci-cd.yml",
        ".github/workflows/tests.yml",
    ]
    
    workflow_files = [w for w in workflows if Path(w).exists()]
    
    if workflow_files:
        print(f"  ✅ CI/CD workflows present: {len(workflow_files)}")
        return True
    else:
        print("  ❌ No CI/CD workflows found")
        return False

def generate_readiness_report():
    """Generate a comprehensive readiness report."""
    print("🎯 movedb-core v1.0.0 Readiness Report")
    print("=" * 50)
    
    results = {}
    
    # Run all checks
    results['package'] = check_package_structure()
    results['versions'] = check_version_consistency()
    results['coverage'] = check_test_coverage()
    results['linting'] = check_linting()
    results['docs'] = check_documentation()
    results['ci'] = check_ci_status()
    
    print("\n📊 Summary")
    print("-" * 20)
    
    # Package structure
    if results['package'][0]:
        current_version = results['package'][1]
        print(f"✅ Package Structure (v{current_version})")
    else:
        print("❌ Package Structure")
        current_version = "unknown"
    
    # Version consistency
    if results['versions'][0]:
        print("✅ Version Consistency")
    else:
        print("❌ Version Consistency")
    
    # Test coverage
    if results['coverage'][0]:
        coverage_pct = results['coverage'][1]
        print(f"✅ Test Coverage ({coverage_pct}%)")
    else:
        coverage_pct = results['coverage'][1]
        print(f"⚠️  Test Coverage ({coverage_pct}%)")
    
    # Code quality
    if results['linting']:
        print("✅ Code Quality")
    else:
        print("❌ Code Quality")
    
    # Documentation
    if results['docs']:
        print("✅ Documentation")
    else:
        print("❌ Documentation")
    
    # CI/CD
    if results['ci']:
        print("✅ CI/CD")
    else:
        print("❌ CI/CD")
    
    # Overall readiness
    print("\n🏁 Overall Readiness")
    print("-" * 20)
    
    passed = sum([
        results['package'][0],
        results['versions'][0],
        results['coverage'][0],
        results['linting'],
        results['docs'],
        results['ci']
    ])
    total = 6
    readiness_pct = (passed / total) * 100
    
    print(f"Ready: {passed}/{total} checks passed ({readiness_pct:.1f}%)")
    
    if readiness_pct >= 90:
        print("🎉 Package is ready for v1.0.0!")
    elif readiness_pct >= 75:
        print("🚀 Package is nearly ready for v1.0.0")
    elif readiness_pct >= 50:
        print("🔧 Package needs work before v1.0.0")
    else:
        print("⚠️  Package needs significant work before v1.0.0")
    
    print("\n📋 Next Steps")
    print("-" * 20)
    
    if not results['linting']:
        print("• Run `make lint-fix` to fix code quality issues")
    
    if not results['coverage'][0]:
        print("• Increase test coverage to ≥90%")
    
    if not results['versions'][0]:
        print("• Fix version inconsistencies")
    
    if readiness_pct >= 90:
        print("• Consider planning v1.0.0 release!")
        print("• Review docs/ROADMAP_V1.md for release planning")
        print("• Run `make prepare-conda-forge` when ready")

if __name__ == "__main__":
    if not Path("pyproject.toml").exists():
        print("❌ Not in movedb-core project directory")
        sys.exit(1)
    
    generate_readiness_report()
