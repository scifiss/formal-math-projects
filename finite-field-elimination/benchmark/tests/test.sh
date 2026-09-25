#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="${APP_ROOT:-/app}"
LOG_DIR="${LOG_DIR:-/logs/verifier}"

mkdir -p "$LOG_DIR"
mkdir -p /logs/verifier

STDOUT_FILE="$(mktemp)"
STDERR_FILE="$(mktemp)"

cleanup() {
  rm -f "$STDOUT_FILE" "$STDERR_FILE"
}

trap cleanup EXIT

python3 "$SCRIPT_DIR/verifier.py" \
  "$APP_ROOT/certificate.json" \
  >"$STDOUT_FILE" 2>"$STDERR_FILE" || true

{
  cat "$STDOUT_FILE"
  cat "$STDERR_FILE"
} > "$LOG_DIR/verifier.log"

RESULT="$(
  awk '/^[01]$/ { result=$0 } END { print result }' \
    "$STDOUT_FILE"
)"

if [ "$RESULT" = "1" ]; then
  REWARD=1
  OUTCOME="passed"
else
  REWARD=0
  OUTCOME="failed"
fi

# Required verifier reward artifact.
printf '%s\n' "$REWARD" > /logs/verifier/reward.txt

python3 - "$LOG_DIR/ctrf-report.json" "$REWARD" "$OUTCOME" <<'PY'
import json
import sys

path, reward, outcome = sys.argv[1], sys.argv[2], sys.argv[3]

report = {
    "results": {
        "tool": {
            "name": "finite-field-elimination-verifier",
            "version": "1.0",
        },
        "summary": {
            "tests": 1,
            "passed": int(reward == "1"),
            "failed": int(reward != "1"),
        },
        "tests": [
            {
                "name": "exact finite-field elimination certificate",
                "status": outcome,
            }
        ],
    }
}

with open(path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")
PY

exit 0
