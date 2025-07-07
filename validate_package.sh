#!/bin/bash
# Validation script for movedb-core conda package setup

# Initialize conda if available
if [[ -f ~/miniconda3/etc/profile.d/conda.sh ]]; then
    source ~/miniconda3/etc/profile.d/conda.sh
elif [[ -f ~/anaconda3/etc/profile.d/conda.sh ]]; then
    source ~/anaconda3/etc/profile.d/conda.sh
fi

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MoveDB Core Package Validation ===${NC}"
echo

# Check required files exist
echo -e "${YELLOW}Checking required files...${NC}"
required_files=(
    "pyproject.toml"
    "src/movedb/__init__.py"
    "conda-recipe/meta.yaml"
    "conda-recipe/conda_build_config.yaml"
    "LICENSE"
    "README.md"
    "MANIFEST.in"
    "environment.yml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - MISSING"
        exit 1
    fi
done

echo

# Check Python syntax
echo -e "${YELLOW}Checking Python syntax...${NC}"
python -m py_compile src/movedb/__init__.py
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓${NC} Python syntax is valid"
else
    echo -e "${RED}✗${NC} Python syntax errors found"
    exit 1
fi

echo

# Check if version is consistent
echo -e "${YELLOW}Checking version consistency...${NC}"
version_pyproject=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
version_init=$(grep '^__version__ = ' src/movedb/__init__.py | cut -d '"' -f 2)
version_conda=$(grep '{% set version = ' conda-recipe/meta.yaml | cut -d '"' -f 2)

if [[ "$version_pyproject" == "$version_init" && "$version_init" == "$version_conda" ]]; then
    echo -e "${GREEN}✓${NC} Version consistent across files: $version_pyproject"
else
    echo -e "${RED}✗${NC} Version mismatch:"
    echo "  pyproject.toml: $version_pyproject"
    echo "  __init__.py: $version_init"
    echo "  meta.yaml: $version_conda"
    exit 1
fi

echo

# Check if conda-build is available
echo -e "${YELLOW}Checking conda-build availability...${NC}"
if conda build --version >/dev/null 2>&1; then
    conda_build_version=$(conda build --version 2>/dev/null)
    echo -e "${GREEN}✓${NC} conda-build is available: $conda_build_version"
else
    echo -e "${YELLOW}!${NC} conda-build not found. Install with: conda install conda-build"
    echo "  Debug: conda build --version output:"
    conda build --version 2>&1 || echo "  Command failed"
fi

echo

# Check if we can import the package (if installed)
echo -e "${YELLOW}Checking package import...${NC}"
if python -c "import movedb; print(f'movedb version: {movedb.__version__}')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Package can be imported successfully"
else
    echo -e "${YELLOW}!${NC} Package not installed or import failed"
    echo "  Install with: pip install -e ."
fi

echo

# Summary
echo -e "${GREEN}=== Validation Complete ===${NC}"
echo "Your movedb-core package is ready for conda packaging!"
echo
echo "Next steps:"
echo "1. Run: ./build_conda.sh"
echo "2. Test the built package"
echo "3. Upload to conda-forge or anaconda.org"
echo

exit 0
