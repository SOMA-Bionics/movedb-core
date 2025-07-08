#!/bin/bash
# setup_opensim_env.sh
# Script to create a Python environment compatible with OpenSim

set -e

echo "Setting up OpenSim-compatible environment for movedb-core..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first"
    exit 1
fi

# Create environment with Python 3.12 (latest supported by OpenSim)
ENV_NAME="movedb-opensim"
echo "Creating conda environment: $ENV_NAME"

conda create -n $ENV_NAME python=3.12 -y

echo "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

echo "Installing movedb-core..."
pip install movedb-core

echo "Installing OpenSim..."
conda install -c opensim-org opensim -y

echo "Testing installation..."
python -c "
import movedb
print('✅ movedb-core imported successfully')
print('Version:', movedb.__version__)

# Test OpenSim availability
try:
    from movedb.file_io.opensim_exporters import OPENSIM_AVAILABLE
    if OPENSIM_AVAILABLE:
        print('✅ OpenSim available - all features enabled')
    else:
        print('❌ OpenSim not detected')
except Exception as e:
    print('❌ Error testing OpenSim:', e)
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To use this environment:"
echo "  conda activate $ENV_NAME"
echo ""
echo "To deactivate:"
echo "  conda deactivate"
echo ""
echo "Environment details:"
conda list | grep -E "(python|opensim|movedb)"
