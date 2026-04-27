#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "webAdmin/package-lock.json" ]; then
  echo "pre-push: missing webAdmin/package-lock.json"
  exit 1
fi

echo "pre-push checks passed"
