#!/usr/bin/env bash
set -euo pipefail

TEST_USER="${TEST_USER:-testuser1}"
TEST_PASS="${TEST_PASS:-TestPass123!}"
TEST_EMAIL="${TEST_EMAIL:-testuser1@example.com}"

docker compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='$TEST_USER', defaults={'email': '$TEST_EMAIL'})
if created:
    u.set_password('$TEST_PASS')
    u.is_staff = True
    u.is_superuser = True
    u.save()
print('OK', u.username, 'created=' + str(created))
"