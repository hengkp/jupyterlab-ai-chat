#!/bin/bash

# JupyterLab AI Chat Extension - Development Installation Script
echo "🚀 Installing JupyterLab AI Chat Extension..."

# Check if we're in a conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  Warning: No conda environment detected. Consider activating one first."
fi

# Install development dependencies first
echo "📦 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e .

# Enable server extension
echo "🔧 Enabling server extension..."
jupyter serverextension enable --py jupyterlab_ai_chat --sys-prefix

# Check if jupyter is available
if ! command -v jupyter &> /dev/null; then
    echo "❌ Error: jupyter command not found. Please install JupyterLab first:"
    echo "   pip install jupyterlab"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Build the extension using npm (fallback if jlpm not available)
echo "🔨 Building extension..."
if command -v jlpm &> /dev/null; then
    npm run build
else
    echo "⚠️  jlpm not found, using npm directly..."
    npx tsc
    jupyter labextension build .
fi

# Install lab extension in development mode
echo "🧪 Installing lab extension in development mode..."
jupyter labextension develop . --overwrite

# Build JupyterLab
echo "🏗️  Building JupyterLab..."
jupyter lab build

echo "✅ Installation complete!"
echo ""
echo "🎯 To start JupyterLab:"
echo "   jupyter lab"
echo ""
echo "🎯 To watch for changes during development:"
echo "   npm run watch"
echo ""
echo "🎯 For Ubuntu 22.04 deployment:"
echo "   jupyter lab --ip=0.0.0.0 --no-browser" 