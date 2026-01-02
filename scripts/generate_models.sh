#!/bin/bash
# Script to generate Python client from Allure TestOps OpenAPI spec
# Usage: ./scripts/generate_models.sh

set -e

echo "Filtering OpenAPI spec..."
uv run python scripts/filter_openapi.py

echo "Generating Python client from OpenAPI spec..."

# Generate Client
uv run openapi-generator-cli generate \
  -c openapi-generator-config.yaml

echo "✅ Client generated successfully in src/client/generated"

# Fix imports
echo "Fixing imports..."
uv run python scripts/fix_generated_imports.py

echo "✅ Imports fixed."
