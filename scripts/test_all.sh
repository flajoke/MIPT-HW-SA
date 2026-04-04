#!/usr/bin/env bash
set -euo pipefail

AUTH_BASE_URL="${AUTH_BASE_URL:-http://localhost:8000}"
MESSAGE_BASE_URL="${MESSAGE_BASE_URL:-http://localhost:8001}"
EMAIL="${EMAIL:-user@example.com}"
PASSWORD="${PASSWORD:-StrongPass123!}"
JWT_SECRET="${JWT_SECRET:-super-secret-change-me}"
JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}"

function print_result() {
  local title="$1"
  local code="$2"
  echo "[$title] HTTP $code"
}

register_code=$(curl -s -o /tmp/register.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
print_result "register valid" "$register_code"

duplicate_code=$(curl -s -o /tmp/duplicate.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
print_result "register duplicate email" "$duplicate_code"

bad_email_code=$(curl -s -o /tmp/bad_email.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong-email","password":"StrongPass123!"}')
print_result "register invalid email" "$bad_email_code"

weak_password_code=$(curl -s -o /tmp/weak.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"weak@example.com","password":"12345"}')
print_result "register weak password" "$weak_password_code"

login_body=$(mktemp)
login_code=$(curl -s -o "$login_body" -w "%{http_code}" -X POST "$AUTH_BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
print_result "login valid" "$login_code"
TOKEN=$(python3 - <<PY
import json
from pathlib import Path
p = Path('$login_body')
print(json.loads(p.read_text())['token'])
PY
)

wrong_email_login_code=$(curl -s -o /tmp/wrong_email_login.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"nouser@example.com","password":"StrongPass123!"}')
print_result "login wrong email" "$wrong_email_login_code"

wrong_password_login_code=$(curl -s -o /tmp/wrong_password_login.out -w "%{http_code}" -X POST "$AUTH_BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"WrongPass123!\"}")
print_result "login wrong password" "$wrong_password_login_code"

message_code=$(curl -s -o /tmp/message.out -w "%{http_code}" -X POST "$MESSAGE_BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"hello from script"}')
print_result "message valid token" "$message_code"

bad_signature_token="${TOKEN%?}x"
bad_signature_code=$(curl -s -o /tmp/bad_sig.out -w "%{http_code}" -X POST "$MESSAGE_BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $bad_signature_token" \
  -d '{"message":"bad signature"}')
print_result "message invalid signature" "$bad_signature_code"

expired_token=$(python3 - <<PY
from datetime import datetime, timedelta, timezone
import jwt
payload = {"user_id": 1, "exp": datetime.now(timezone.utc) - timedelta(minutes=5)}
print(jwt.encode(payload, "$JWT_SECRET", algorithm="$JWT_ALGORITHM"))
PY
)
expired_code=$(curl -s -o /tmp/expired.out -w "%{http_code}" -X POST "$MESSAGE_BASE_URL/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $expired_token" \
  -d '{"message":"expired token"}')
print_result "message expired token" "$expired_code"

echo "Done. Expected codes: 201, 400, 400, 400, 200, 401, 401, 201, 400, 401"
