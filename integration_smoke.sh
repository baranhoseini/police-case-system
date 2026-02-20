#!/usr/bin/env bash
set -euo pipefail

BE="http://127.0.0.1:8000"
FE="http://127.0.0.1:5174" # change if your Vite prints a different port

echo "== Check servers reachable =="
curl -fsS "$BE/api/schema/?format=json" >/dev/null && echo "Backend OK"
curl -fsS "$FE" >/dev/null && echo "Frontend OK"

echo "== Register + login =="
TS="$(date +%s)"
USERNAME="user$TS"
EMAIL="user$TS@example.com"
PHONE="0912$((TS % 10000000))"
NID="$((1000000000 + (TS % 899999999)))"
PASS="Passw0rd!123"

curl -fsS -X POST "$BE/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\":\"$USERNAME\",
    \"first_name\":\"Test\",
    \"last_name\":\"User\",
    \"email\":\"$EMAIL\",
    \"phone\":\"$PHONE\",
    \"national_id\":\"$NID\",
    \"password\":\"$PASS\"
  }" >/dev/null

LOGIN=$(curl -fsS -X POST "$BE/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$USERNAME\",\"password\":\"$PASS\"}")

ACCESS=$(echo "$LOGIN" | sed -n 's/.*"access":"\([^"]*\)".*/\1/p')
if [ -z "$ACCESS" ]; then
  echo "ERROR: access token missing"
  echo "$LOGIN"
  exit 1
fi
AUTHH="Authorization: Bearer $ACCESS"
echo "Auth OK ($USERNAME)"

echo "== Create case =="
CASE_JSON=$(curl -fsS -X POST "$BE/api/cases/" -H "$AUTHH" -H "Content-Type: application/json" -d "{\"title\":\"Auto Case $TS\"}")
CASE_ID=$(echo "$CASE_JSON" | sed -n 's/.*"id":[ ]*\([0-9][0-9]*\).*/\1/p')
[ -n "$CASE_ID" ] || (echo "ERROR: case id missing: $CASE_JSON" && exit 1)
echo "Case OK (id=$CASE_ID)"

echo "== Create evidence (ID_DOC) =="
EVID_JSON=$(curl -fsS -X POST "$BE/api/evidence/" -H "$AUTHH" -H "Content-Type: application/json" -d "{
  \"case\": $CASE_ID,
  \"title\": \"ID evidence\",
  \"evidence_type\": \"ID_DOC\",
  \"id_fields\": {\"passport\":\"123\"}
}")
echo "$EVID_JSON" | python3 -m json.tool | head -n 25

echo "== Verify evidence list types =="
RESP_FILE="$(mktemp)"
HTTP_CODE=$(curl -sS -o "$RESP_FILE" -w "%{http_code}" -H "$AUTHH" "$BE/api/evidence/")

echo "Evidence list HTTP $HTTP_CODE"
head -c 120 "$RESP_FILE"; echo

# Must be JSON and 200
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: evidence list not 200"
  cat "$RESP_FILE"
  exit 1
fi

python3 - <<'PY' < "$RESP_FILE"
import json,sys
data=json.load(sys.stdin)
items=data.get("results", data)
assert isinstance(items, list), f"Expected list, got {type(items)}"
if items:
    e=items[0]
    assert isinstance(e.get("image_urls", []), list), "image_urls not list"
    assert isinstance(e.get("media_urls", []), list), "media_urls not list"
    assert isinstance(e.get("id_fields", {}), dict), "id_fields not object"
print("OK: evidence JSON fields have correct types")
PY

echo "== Check OpenAPI includes endpoints FE needs =="
SCHEMA=$(curl -fsS "$BE/api/schema/?format=json")
python3 - <<PY
import json,sys
s=json.loads(sys.stdin.read())
paths=s.get("paths",{})
need=["/api/auth/register/","/api/auth/login/","/api/cases/","/api/evidence/"]
missing=[p for p in need if p not in paths]
assert not missing, f"Missing endpoints: {missing}"
print("OK: schema includes core endpoints")
PY
<<<"$SCHEMA"

echo
echo "✅ Integration contract smoke PASSED"
echo "Tip: screenshot this output for submission evidence."
