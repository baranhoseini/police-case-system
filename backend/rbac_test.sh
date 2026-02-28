#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://127.0.0.1:8000/api}"
EMAIL="${EMAIL:-rbac_test_$(date +%s)@test.com}"
USER="${USER:-rbac_test_$(date +%s)}"
PHONE="${PHONE:-0912$(date +%s | tail -c 8)}"
NID="${NID:-$(date +%s | tail -c 10)}"
PASS="${PASS:-Passw0rd!!}"

echo "BASE=$BASE"
echo "USER=$USER"
echo "EMAIL=$EMAIL"
echo "PHONE=$PHONE"
echo "NID=$NID"
echo

pyjson() {
  python3 -c "import json,sys; print(json.loads(sys.argv[1]).get(sys.argv[2], ''))" "$1" "$2"
}

pyjson_path() {
  # usage: pyjson_path "$json" "user.roles"
  python3 - <<'PY' "$1" "$2"
import json,sys
obj=json.loads(sys.argv[1])
path=sys.argv[2].split(".")
cur=obj
for p in path:
  if isinstance(cur, dict):
    cur=cur.get(p)
  else:
    cur=None
print(cur)
PY
}

http_code() {
  # usage: http_code METHOD URL [DATA]
  local method="$1"
  local url="$2"
  local data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "$data"
  else
    curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
      -H "Authorization: Bearer $TOKEN"
  fi
}

echo "1) Register (may return 400 if already exists, that's ok)..."
REG_BODY=$(cat <<JSON
{"username":"$USER","first_name":"Demo","last_name":"User","email":"$EMAIL","phone":"$PHONE","national_id":"$NID","password":"$PASS"}
JSON
)

REG_RES=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register/" -H "Content-Type: application/json" -d "$REG_BODY")
REG_JSON="$(echo "$REG_RES" | head -n 1)"
REG_CODE="$(echo "$REG_RES" | tail -n 1)"

echo "HTTP $REG_CODE"
echo "$REG_JSON"
echo

if [[ "$REG_CODE" == "201" || "$REG_CODE" == "200" ]]; then
  USER_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "$REG_JSON")
else
  echo "Register did not create a user (maybe already exists). We'll still try login."
  USER_ID=""
fi

echo "2) Login..."
LOGIN_BODY=$(cat <<JSON
{"identifier":"$EMAIL","password":"$PASS"}
JSON
)

LOGIN_JSON=$(curl -s -X POST "$BASE/auth/login/" -H "Content-Type: application/json" -d "$LOGIN_BODY")
echo "$LOGIN_JSON" | python3 -c "import json,sys; json.loads(sys.stdin.read()); print('Login JSON OK')" >/dev/null

TOKEN=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['access'])" "$LOGIN_JSON")
REFRESH=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['refresh'])" "$LOGIN_JSON")

echo "Login OK. Token starts with: ${TOKEN:0:15}..."
echo

echo "3) /me (must include roles + primary_role)..."
ME_JSON=$(curl -s "$BASE/auth/me/" -H "Authorization: Bearer $TOKEN")
echo "$ME_JSON"
echo

ROLES=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('roles'))" "$ME_JSON")
PRIMARY=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('primary_role'))" "$ME_JSON")

if [[ "$ROLES" == "None" || -z "$ROLES" ]]; then
  echo "❌ ERROR: /me response missing roles. Fix backend MeView serializer."
  exit 1
fi

if [[ "$PRIMARY" == "None" || -z "$PRIMARY" ]]; then
  echo "❌ ERROR: /me response missing primary_role. Fix backend serializer."
  exit 1
fi

echo "✅ /me has roles and primary_role."
echo

# If we didn't capture USER_ID from register, read it from /me
if [[ -z "$USER_ID" ]]; then
  USER_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "$ME_JSON")
fi
echo "Using user_id=$USER_ID"
echo

assign_role() {
  local role="$1"
  echo "Assign role: $role"
  local payload="{\"user_id\":$USER_ID,\"role_name\":\"$role\"}"
  local res_code
  res_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/rbac/assign-role/" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "$payload")
  echo "assign-role HTTP $res_code"
  if [[ "$res_code" != "200" && "$res_code" != "201" ]]; then
    echo "❌ assign-role failed for $role"
    exit 1
  fi
  ME_JSON=$(curl -s "$BASE/auth/me/" -H "Authorization: Bearer $TOKEN")
  echo "/me => roles=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('roles'))" "$ME_JSON") primary=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('primary_role'))" "$ME_JSON")"
  echo
}

echo "4) Role assignment tests..."
# pick a representative set. You can add more roles if you want.
ROLES_TO_TEST=("Base user" "Police Officer" "Patrol Officer" "Detective" "Sergent" "Captain" "Chief" "Judge" "Administrator" "Corenary" "Complainant" "Witness")

for r in "${ROLES_TO_TEST[@]}"; do
  assign_role "$r"
done

echo "5) Endpoint accessibility smoke test per role"
echo "We will assign each role, then test key endpoints with HTTP status codes."
echo

# Endpoints list (method, url)
# These should exist in your project based on url patterns: /auth, /rbac, /rewards, /suspects, etc.
declare -a TESTS=(
  "GET $BASE/auth/me/"
  "GET $BASE/rbac/roles/"
  "GET $BASE/suspects/"
  "GET $BASE/rewards/"
  "GET $BASE/schema/"
  "GET $BASE/docs/"
)

# Some POST tests (may require extra fields; keep to lightweight endpoints)
# rbac assign-role already tested.
declare -a POST_TESTS=(
  # example: create a reward tip might require fields; skipping to avoid false failures.
)

for r in "${ROLES_TO_TEST[@]}"; do
  assign_role "$r"
  echo "== Role: $r =="
  for t in "${TESTS[@]}"; do
    method=$(echo "$t" | awk '{print $1}')
    url=$(echo "$t" | awk '{print $2}')
    code=$(http_code "$method" "$url")
    echo "$method $url -> HTTP $code"
  done
  echo
done

echo "✅ RBAC test finished."
echo "If you see unexpected 403/401 for endpoints that should be allowed, tell me the role + endpoint and I’ll tell you what to adjust in backend permissions."
