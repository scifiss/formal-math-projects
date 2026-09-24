#!/usr/bin/env bash
set -u

APP_ROOT="${APP_ROOT:-/app}"
VERIFIER_ROOT="${VERIFIER_ROOT:-/opt/verifier}"

SUBMISSION="$APP_ROOT/Submission.lean"
OLEAN="$APP_ROOT/.lake/build/lib/lean/Submission.olean"
LOG="$(mktemp)"

cleanup() {
  rm -f "$LOG" "$OLEAN"
}

trap cleanup EXIT

fail() {
  printf '0\n'
  exit 0
}

[[ -f "$SUBMISSION" ]] || fail

# Reject incomplete proofs and explicit user axioms.
grep -Eq '\b(sorry|admit)\b' "$SUBMISSION" && fail
grep -Eq '^[[:space:]]*(private[[:space:]]+)?axiom[[:space:]]' \
  "$SUBMISSION" && fail

mkdir -p "$(dirname "$OLEAN")"

cd "$APP_ROOT" || fail

rm -f "$OLEAN"

lake env lean \
  -o "$OLEAN" \
  "$SUBMISSION" >"$LOG" 2>&1 || fail

timeout 180 lake env lean \
  "$VERIFIER_ROOT/Verifier.lean" >>"$LOG" 2>&1 || fail

python3 - "$LOG" <<'PY'
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()

required = [
    "CyclicFourier.cyclicDFT_cyclicConvolution",
]

allowed = {"propext", "Classical.choice", "Quot.sound"}

for theorem in required:
    pattern = (
        r"'" + re.escape(theorem) +
        r"' depends on axioms:\s*\[([^\]]*)\]"
    )

    match = re.search(pattern, text)

    if match is None:
        print("0")
        raise SystemExit

    axioms = {
        item.strip()
        for item in match.group(1).split(",")
        if item.strip()
    }

    if not axioms.issubset(allowed):
        print("0")
        raise SystemExit

print("1")
PY