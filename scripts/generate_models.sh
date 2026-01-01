#!/bin/bash
# Script to generate Pydantic v2 models from Allure TestOps OpenAPI spec
# Usage: ./scripts/generate_models.sh

set -e

echo "Generating Pydantic models from OpenAPI spec..."

uv run datamodel-codegen \
  --input openapi/allure-testops-service/report-service.json \
  --output src/client/models/_generated.py \
  --output-model-type pydantic_v2.BaseModel \
  --use-standard-collections \
  --use-union-operator \
  --target-python-version 3.12 \
  --use-annotated \
  --use-field-description \
  --strict-nullable \
  --collapse-root-models \
  --field-constraints

echo "✅ Models generated successfully in src/client/models/_generated.py"
