#!/usr/bin/env bash
# Build script for creating mcpb bundle for Claude Desktop
# This script vendors dependencies and creates a versioned .mcpb artifact

set -euo pipefail

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Building lucius-mcp version $VERSION"

# Clean previous build artifacts
echo "Cleaning previous build artifacts..."
rm -rf dist/*.mcpb build/mcpb-bundle 2>/dev/null || true
mkdir -p dist build/mcpb-bundle

# Copy necessary files to bundle directory
echo "Copying project files to bundle..."
cp -r src build/mcpb-bundle/
cp pyproject.toml build/mcpb-bundle/
cp uv.lock build/mcpb-bundle/
cp manifest.json build/mcpb-bundle/
cp README.md build/mcpb-bundle/

# Copy icon if it exists
if [ -f "icon.png" ]; then
    cp icon.png build/mcpb-bundle/
fi

# Create .mcpb bundle using mcpb CLI
echo "Creating .mcpb bundle..."
cd build/mcpb-bundle

# Check if mcpb is installed
if ! command -v mcpb &> /dev/null; then
    echo "ERROR: mcpb CLI not found. Please install it with: npm install -g @anthropic-ai/mcpb"
    exit 1
fi

# Pack the bundle
mcpb pack

# Move the created bundle to dist with versioned name
BUNDLE_FILE=$(ls *.mcpb 2>/dev/null || echo "")
if [ -z "$BUNDLE_FILE" ]; then
    echo "ERROR: No .mcpb file was created"
    exit 1
fi

# Rename to include version
VERSIONED_NAME="lucius-mcp-${VERSION}.mcpb"
mv "$BUNDLE_FILE" "../../dist/$VERSIONED_NAME"

cd ../..
echo "✅ Successfully created dist/$VERSIONED_NAME"
