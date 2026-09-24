#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LOG_DIR="/logs/verifier"
REWARD_FILE="$LOG_DIR/reward.txt"
CTRF_FILE="$LOG_DIR/ctrf-report.json"

mkdir -p /logs/verifier

CORE_OUTPUT="$("$SCRIPT_DIR/verify_core.sh" 2>&1)"

printf '%s\n' "$CORE_OUTPUT" >"$LOG_DIR/verifier.log"

CORE_RESULT="$(
  printf '%s\n' "$CORE_OUTPUT" |
  awk '/^[01]$/ { result=$0 } END { print result }'
)"

if [ "$CORE_RESULT" = "1" ]; then
    REWARD=1
    OUTCOME="passed"
else
    REWARD=0
    OUTCOME="failed"
fi

printf '%s\n' "$REWARD" > /logs/verifier/reward.txt

python3 - "$CTRF_FILE" "$REWARD" "$OUTCOME" <<'PY'
import json
import sys

path, reward, outcome = sys.argv[1], sys.argv[2], sys.argv[3]

report = {
    "results": {
        "tool": {
            "name": "cyclic-fourier-verifier",
            "version": "1.0"
        },
        "summary": {
            "tests": 1,
            "passed": int(reward == "1"),
            "failed": int(reward != "1")
        },
        "tests": [{
            "name": "Lean cyclic Fourier convolution submission",
            "status": outcome
        }]
    }
}

with open(path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
PY

exit 0