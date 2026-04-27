#!/usr/bin/env bash
set -euo pipefail

LOG_PATH="/Users/loantr/DevProject/RentManager/.cursor/debug-734dd4.log"
mkdir -p "$(dirname "${LOG_PATH}")"
NOW_MS="$(python3 -c 'import time; print(int(time.time()*1000))')"

# #region agent log
echo "{\"sessionId\":\"734dd4\",\"runId\":\"pre-push-run\",\"hypothesisId\":\"H1\",\"location\":\"scripts/pre-push.sh:8\",\"message\":\"Pre-push script started\",\"data\":{\"pwd\":\"$(pwd)\"},\"timestamp\":${NOW_MS}}" >> "${LOG_PATH}"
# #endregion

if [ ! -f "webAdmin/package-lock.json" ]; then
  NOW_MS="$(python3 -c 'import time; print(int(time.time()*1000))')"
  # #region agent log
  echo "{\"sessionId\":\"734dd4\",\"runId\":\"pre-push-run\",\"hypothesisId\":\"H2\",\"location\":\"scripts/pre-push.sh:14\",\"message\":\"Missing frontend lockfile\",\"data\":{\"path\":\"webAdmin/package-lock.json\"},\"timestamp\":${NOW_MS}}" >> "${LOG_PATH}"
  # #endregion
  echo "pre-push: missing webAdmin/package-lock.json"
  exit 1
fi

NOW_MS="$(python3 -c 'import time; print(int(time.time()*1000))')"
# #region agent log
echo "{\"sessionId\":\"734dd4\",\"runId\":\"pre-push-run\",\"hypothesisId\":\"H3\",\"location\":\"scripts/pre-push.sh:23\",\"message\":\"Pre-push script completed\",\"data\":{\"lockfile\":true},\"timestamp\":${NOW_MS}}" >> "${LOG_PATH}"
# #endregion

echo "pre-push checks passed"
