#!/usr/bin/env bash
# Build script for creating mcpb bundle for Claude Desktop
# This script vendors dependencies and creates a versioned .mcpb artifact

set -euo pipefail

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Building lucius-mcp version $VERSION"

# Clean previous build artifacts
echo "Cleaning previous build artifacts..."
rm -rf dist/*.mcpb build/mcpb-bundle-* 2>/dev/null || true
mkdir -p dist

MANIFEST_DIR="deployment/mcpb"
SERVER_TYPES=("uv" "python")

# Check if mcpb is installed
if ! command -v mcpb &> /dev/null; then
    echo "ERROR: mcpb CLI not found. Please install it with: npm install -g @anthropic-ai/mcpb"
    exit 1
fi

for server_type in "${SERVER_TYPES[@]}"; do
    manifest_source="$MANIFEST_DIR/manifest.${server_type}.json"
    if [ ! -f "$manifest_source" ]; then
        echo "ERROR: $manifest_source not found"
        exit 1
    fi

    bundle_dir="build/mcpb-bundle-${server_type}"
    mkdir -p "$bundle_dir"

    # Copy necessary files to bundle directory
    echo "Copying project files to bundle ($server_type)..."
    cp -r src "$bundle_dir/"
    cp pyproject.toml "$bundle_dir/"
    cp uv.lock "$bundle_dir/"
    cp "$manifest_source" "$bundle_dir/manifest.json"
    cp README.md "$bundle_dir/"

    if [ "$server_type" = "python" ]; then
        cat > "$bundle_dir/.mcpbignore" <<'EOF'
__pycache__/
*.pyc
EOF
        mkdir -p "$bundle_dir/server/lib"
        uv export --frozen --no-hashes -o "$bundle_dir/server/requirements.txt"
        uv pip install --no-deps --requirement "$bundle_dir/server/requirements.txt" --target "$bundle_dir/server/lib"
    else
        cp .mcpbignore "$bundle_dir/"
    fi

    # Update manifest version from pyproject.toml
    MANIFEST_PATH="$bundle_dir/manifest.json"
    python3 - "$MANIFEST_PATH" "$VERSION" <<'PY'
import json
import sys

path, version = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)

data["version"] = version

with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

    # Copy icon if it exists
    if [ -f "icon.png" ]; then
        cp icon.png "$bundle_dir/"
    fi

    # Create .mcpb bundle using mcpb CLI
    echo "Creating .mcpb bundle ($server_type)..."
    cd "$bundle_dir"

    # Pack the bundle
    mcpb pack

    # Move the created bundle to dist with versioned name
    BUNDLE_FILE=$(ls *.mcpb 2>/dev/null || echo "")
    if [ -z "$BUNDLE_FILE" ]; then
        echo "ERROR: No .mcpb file was created"
        exit 1
    fi

    # Rename to include version and server type
    VERSIONED_NAME="lucius-mcp-${VERSION}-${server_type}.mcpb"
    mv "$BUNDLE_FILE" "../../dist/$VERSIONED_NAME"

    cd ../..
    rm -rf "$bundle_dir"
    echo "✅ Successfully created dist/$VERSIONED_NAME"
    echo ""
done
