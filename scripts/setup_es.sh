#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source .env

echo "Creating blr-rentals index..."
curl -s -X PUT "${ES_URL}/blr-rentals" \
  -H "Authorization: ApiKey ${ES_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @ingest/mappings/blr_rentals.json

echo ""
echo "Verifying ELSER endpoint..."
curl -s -X GET "${ES_URL}/_inference/.elser-2-elasticsearch" \
  -H "Authorization: ApiKey ${ES_API_KEY}"

echo ""
echo "Setup complete."
