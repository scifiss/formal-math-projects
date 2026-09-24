#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

APP_ROOT="${APP_ROOT:-/app}"
VERIFIER_ROOT="${VERIFIER_ROOT:-$SCRIPT_DIR}"

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

# Reject incomplete proofs and explicit user-defined axioms.
grep -Eq '\b(sorry|admit)\b' "$SUBMISSION" && fail

grep -Eq \
  '^[[:space:]]*(private[[:space:]]+)?axiom[[:space:]]' \
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
    "ReversibleMarkov.reversible_green_identity",
    "ReversibleMarkov.reversible_mass_conservation",
    "ReversibleMarkov.reversible_generator_self_adjoint",
    "ReversibleMarkov.reversible_dirichlet_nonneg",
    "ReversibleMarkov.reversible_energy_nonpos",
]

allowed = {
    "propext",
    "Classical.choice",
    "Quot.sound",
}

for theorem in required:
    depends_pattern = (
        r"'" + re.escape(theorem) +
        r"' depends on axioms:\s*\[([^\]]*)\]"
    )

    no_axioms_pattern = (
        r"'" + re.escape(theorem) +
        r"' does not depend on any axioms"
    )

    match = re.search(depends_pattern, text)

    if match is not None:
        axioms = {
            item.strip()
            for item in match.group(1).split(",")
            if item.strip()
        }

        if not axioms.issubset(allowed):
            print("0")
            raise SystemExit

    elif re.search(no_axioms_pattern, text) is None:
        print("0")
        raise SystemExit

print("1")
PY