#!/usr/bin/env bash
set -eu

APP_ROOT="${APP_ROOT:-/app}"
SOLUTION_ROOT="${SOLUTION_ROOT:-/opt/solution}"

cp "$SOLUTION_ROOT/Reference.lean" \
   "$APP_ROOT/Submission.lean"
