#!/bin/sh
set -e

echo "==> Waiting for PostgreSQL to be ready..."

python3 - <<'EOF'
import os, sys, time

url = os.environ["DATABASE_URL"]
# Add connect_timeout to avoid hanging
if "?" in url:
    url_with_timeout = url + "&connect_timeout=3"
else:
    url_with_timeout = url + "?connect_timeout=3"

import psycopg2

for attempt in range(1, 31):
    try:
        conn = psycopg2.connect(url_with_timeout)
        conn.close()
        print(f"PostgreSQL is ready (attempt {attempt})")
        sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt}/30: {e}", flush=True)
        time.sleep(2)

print("ERROR: PostgreSQL did not become ready in time")
sys.exit(1)
EOF

echo ""
echo "==> Running tests..."
exec python3 -m pytest tests/ -v --tb=short
