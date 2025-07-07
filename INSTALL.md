#!/bin/bash
# Installation instructions for movedb-core

echo "=== MoveDB Core Installation Guide ==="
echo

echo "1. CREATE CONDA ENVIRONMENT (Recommended)"
echo "   conda env create -f environment.yml"
echo "   conda activate movedb-core-dev"
echo

echo "2. INSTALL FOR DEVELOPMENT"
echo "   pip install -e ."
echo

echo "3. BUILD CONDA PACKAGE"
echo "   ./build_conda.sh"
echo

echo "4. INSTALL CONDA PACKAGE LOCALLY"
echo "   conda install dist/conda/noarch/movedb-core-0.1.0-*.tar.bz2"
echo

echo "5. UPLOAD TO CONDA-FORGE (requires conda-forge membership)"
echo "   # Follow conda-forge documentation"
echo "   # https://conda-forge.org/docs/maintainer/adding_pkgs.html"
echo

echo "6. UPLOAD TO ANACONDA.ORG (alternative)"
echo "   anaconda upload dist/conda/noarch/movedb-core-0.1.0-*.tar.bz2"
echo

echo "7. RUN TESTS"
echo "   pytest tests/"
echo

echo "=== Prerequisites ==="
echo "- conda or miniconda installed"
echo "- conda-build installed: conda install conda-build"
echo "- anaconda-client (optional): conda install anaconda-client"
