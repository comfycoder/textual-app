#!/usr/bin/env bash
# Regenerate the typed OpenAPI client from api/openapi.yaml.
# Run after pulling spec changes or modifying api/openapi.yaml locally.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f api/openapi.yaml ]]; then
    echo "Error: api/openapi.yaml not found." >&2
    exit 1
fi

# --meta none: don't generate a separate setup.py / pyproject; just the modules.
# --overwrite: replace existing files.
openapi-python-client generate \
    --path api/openapi.yaml \
    --output-path src/your_cli/client \
    --overwrite \
    --meta none

echo "Client regenerated at src/your_cli/client/"
