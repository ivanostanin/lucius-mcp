#!/bin/bash
# Script to generate Python client from Allure TestOps OpenAPI spec
# Usage: ./scripts/generate_testops_api_client.sh

set -e

echo "Filtering OpenAPI spec..."
uv run python scripts/filter_openapi.py

echo "Cleaning up generated client..."
rm -rf src/client/generated

echo "Generating Python client from OpenAPI spec..."
uv run openapi-generator-cli generate \
    --ignore-file-override=scripts/.openapi-generator-ignore \
    -c ./scripts/openapi-generator-config.yaml

mv src/client/generated_README.md src/client/generated/README.md

echo "✅ Client generated successfully in src/client/generated"