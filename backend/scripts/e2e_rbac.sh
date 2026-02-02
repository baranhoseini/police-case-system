#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"

USERNAME="melina"
PASSWORD="melina12345678"

echo "==> Logging in as $USERNAME ..."
LOGIN_JSON=$(curl -s -X POST "$BASE_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

# Extract access token without python/jq:
# Finds: "access":"<TOKEN>"
ACCESS=$(echo "$LOGIN_JSON" | sed -n 's/.*"access":"\([^"]*\)".*/\1/p')

if [[ -z "$ACCESS" ]]; then
  echo "ERROR: Could not extract access token."
  echo "Login response was:"
  echo "$LOGIN_JSON"
  exit 1
fi

echo "==> Access token acquired (hidden)."

echo "==> GET /api/rbac/roles/"
curl -s "$BASE_URL/api/rbac/roles/" \
  -H "Authorization: Bearer $ACCESS" | tee /tmp/rbac_roles.json
echo

echo "==> Assigning Admin role to user_id=2"
curl -s -X POST "$BASE_URL/api/rbac/assign-role/" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "role_name": "Admin"}'
echo

echo "==> Done."
