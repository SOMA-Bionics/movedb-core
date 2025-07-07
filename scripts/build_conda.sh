#!/bin/bash
# Build script for movedb-core conda package

# Initialize conda if available
if [[ -f ~/miniconda3/etc/profile.d/conda.sh ]]; then
    source ~/miniconda3/etc/profile.d/conda.sh
elif [[ -f ~/anaconda3/etc/profile.d/conda.sh ]]; then
    source ~/anaconda3/etc/profile.d/conda.sh
fi

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building movedb-core conda package...${NC}"

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/
rm -rf dist/
rm -rf src/movedb.egg-info/

# Build the conda package
echo -e "${YELLOW}Building conda package...${NC}"
conda build conda-recipe --output-folder dist/conda

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Conda package build successful!${NC}"
    echo -e "${GREEN}Package location: $(find dist/conda -name '*.tar.bz2' -o -name '*.conda')${NC}"
else
    echo -e "${RED}✗ Conda package build failed!${NC}"
    exit 1
fi

# Optionally install the package locally
read -p "Install the package locally? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installing package locally...${NC}"
    PACKAGE_PATH=$(find dist/conda -name '*.tar.bz2' -o -name '*.conda' | head -1)
    conda install "$PACKAGE_PATH" -y
    echo -e "${GREEN}✓ Package installed locally!${NC}"
fi

echo -e "${GREEN}Build process completed!${NC}"
