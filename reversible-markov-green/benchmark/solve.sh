#!/usr/bin/env bash
set -eu

APP_ROOT="${APP_ROOT:-/app}"
PROOF_ROOT="${PROOF_ROOT:-/opt/proof}"

cp "$PROOF_ROOT/GreenIdentity.lean" \
   "$APP_ROOT/Submission.lean"
