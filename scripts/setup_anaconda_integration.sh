#!/bin/bash

# setup_anaconda_integration.sh
# Helper script to set up Anaconda.org integration for GitHub Actions

set -e

echo "🔧 Setting up Anaconda.org integration for GitHub Actions"
echo "======================================================="

# Check if running in GitHub repository
if [ ! -d ".git" ]; then
    echo "❌ Error: This script must be run from the root of a git repository"
    exit 1
fi

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Please install GitHub CLI first: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "❌ Error: You are not logged in to GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is available and authenticated"

# Get repository information
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(basename "$REPO_URL" .git)
echo "📦 Repository: $REPO_NAME"

# Get Anaconda.org username
echo ""
echo "🔑 Anaconda.org Setup"
echo "===================="
read -p "Enter your Anaconda.org username: " ANACONDA_USER

if [ -z "$ANACONDA_USER" ]; then
    echo "❌ Error: Anaconda.org username cannot be empty"
    exit 1
fi

# Get API token
echo ""
echo "Please go to https://anaconda.org and:"
echo "1. Log in to your account"
echo "2. Go to Account Settings → Access → API tokens"
echo "3. Create a new token with 'api:write' scope"
echo "4. Copy the token (you'll only see it once)"
echo ""
read -s -p "Enter your Anaconda.org API token: " ANACONDA_API_TOKEN
echo ""

if [ -z "$ANACONDA_API_TOKEN" ]; then
    echo "❌ Error: API token cannot be empty"
    exit 1
fi

# Set GitHub secrets
echo ""
echo "🔐 Setting GitHub repository secrets..."

# Set ANACONDA_USER secret
if gh secret set ANACONDA_USER --body "$ANACONDA_USER"; then
    echo "✅ ANACONDA_USER secret set successfully"
else
    echo "❌ Failed to set ANACONDA_USER secret"
    exit 1
fi

# Set ANACONDA_API_TOKEN secret
if gh secret set ANACONDA_API_TOKEN --body "$ANACONDA_API_TOKEN"; then
    echo "✅ ANACONDA_API_TOKEN secret set successfully"
else
    echo "❌ Failed to set ANACONDA_API_TOKEN secret"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo "Your repository is now configured for automatic conda package uploads:"
echo ""
echo "📦 Package uploads will happen automatically when:"
echo "   • You push a git tag (e.g., v1.0.0) → Main channel"
echo "   • You push to main branch → Development channel (--label dev)"
echo ""
echo "📥 Users can install your package with:"
echo "   conda install -c $ANACONDA_USER movedb-core           # Stable releases"
echo "   conda install -c $ANACONDA_USER -c dev movedb-core    # Development versions"
echo ""
echo "🔍 Monitor your packages at: https://anaconda.org/$ANACONDA_USER/movedb-core"
echo ""
echo "Next steps:"
echo "1. Commit and push your changes"
echo "2. Create a release tag: git tag v1.0.0 && git push origin v1.0.0"
echo "3. Watch GitHub Actions build and upload your package!"
