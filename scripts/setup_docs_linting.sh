#!/bin/bash
# Setup script for documentation linting tools

set -e

echo "Setting up documentation linting tools..."

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first:"
    echo "   - On macOS: brew install node"
    echo "   - On Ubuntu: sudo apt install nodejs npm"
    echo "   - Or use conda: conda install nodejs"
    exit 1
fi

# Install markdownlint globally
echo "📝 Installing markdownlint-cli..."
npm install -g markdownlint-cli

# Verify installation
if command -v markdownlint &> /dev/null; then
    echo "✅ markdownlint installed successfully!"
    echo ""
    echo "Available commands:"
    echo "  make lint-docs     - Check documentation"
    echo "  make lint-docs-fix - Auto-fix issues"
    echo "  make lint          - Check all code and docs"
else
    echo "❌ markdownlint installation failed"
    exit 1
fi

echo ""
echo "🚀 Documentation linting is ready!"
echo "Run 'make lint-docs' to check your documentation."
