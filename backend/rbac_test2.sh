#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8000/api}"
ADMIN_IDENTIFIER="${ADMIN_IDENTIFIER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-Admin12345!}"

TEST_EMAIL="${TEST_EMAIL:-role_tester@test.com}"
TEST_USER="${TEST_USER:-role_tester}"
TEST_PASS="${TEST_PASS:-Passw0rd!!}"
TEST_PHONE="${TEST_PHONE:-09129990000}"
TEST_NID="${TEST_NID:-9990001111}"

echo "1) Admin login..."
ADMIN_LOGIN=$(curl -s -X POST "$BASE/auth/login/" -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$ADMIN_IDENTIFIER\",\"password\":\"$ADMIN_PASS\"}")
ADMIN_TOKEN=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['access'])" "$ADMIN_LOGIN")
echo "Admin OK"

echo "2) Create test user (ignore if exists)..."
curl -s -o /dev/null -X POST "$BASE/auth/register/" -H "Content-Type: application/json" \
  -d "{\"username\":\"$TEST_USER\",\"first_name\":\"Role\",\"last_name\":\"Tester\",\"email\":\"$TEST_EMAIL\",\"phone\":\"$TEST_PHONE\",\"national_id\":\"$TEST_NID\",\"password\":\"$TEST_PASS\"}" || true
echo "User OK"

echo "3) Test user login..."
TEST_LOGIN=$(curl -s -X POST "$BASE/auth/login/" -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASS\"}")
TEST_TOKEN=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['access'])" "$TEST_LOGIN")
TEST_USER_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['user']['id'])" "$TEST_LOGIN")
echo "test user_id=$TEST_USER_ID"

assign() {
  role="$1"
  echo "Assign: $role"
  curl -s -X POST "$BASE/rbac/assign-role/" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":$TEST_USER_ID,\"role_name\":\"$role\"}" >/dev/null
  curl -s "$BASE/auth/me/" -H "Authorization: Bearer $TEST_TOKEN"
  echo
}

echo "4) /me before:"
curl -s "$BASE/auth/me/" -H "Authorization: Bearer $TEST_TOKEN"
echo; echo

echo "5) Assign roles and re-check /me:"
for r in Citizen Officer Patrol Detective Sergent Captain Chief Judge Admin Coroner; do
  assign "$r"
done

echo "DONE ✅"
