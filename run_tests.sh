#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Backend API Tests ==="
cd "$ROOT_DIR/backend"
if [ -f venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi
python manage.py test submissions -v 2

echo ""
echo "=== Frontend Build / Type Verification ==="
cd "$ROOT_DIR/frontend"
npm run build

echo ""
echo "✅ All checks passed."
