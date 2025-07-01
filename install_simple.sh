#!/bin/bash

# Simplified JupyterLab AI Chat Extension Installation
echo "🚀 Installing JupyterLab AI Chat Extension (Simple Mode)..."

# Check if we're in a conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  Warning: No conda environment detected. Consider activating one first."
fi

# Install JupyterLab if not present
if ! command -v jupyter &> /dev/null; then
    echo "📦 Installing JupyterLab..."
    pip install jupyterlab
fi

# Install core Python dependencies
echo "📦 Installing core dependencies..."
pip install -r requirements-dev.txt

# Install the package using simplified setup
echo "📦 Installing package (Python-only)..."
python setup_simple.py develop

# Enable server extension
echo "🔧 Enabling server extension..."
jupyter serverextension enable --py jupyterlab_ai_chat --sys-prefix

echo "✅ Basic installation complete!"
echo ""
echo "🎯 To start JupyterLab:"
echo "   jupyter lab"
echo ""
echo "⚠️  Note: This is a simplified installation without the frontend extension."
echo "   For full functionality, run ./install_dev.sh after installing development dependencies." 