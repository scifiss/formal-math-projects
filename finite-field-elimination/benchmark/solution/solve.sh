#!/usr/bin/env bash
set -eu

APP_ROOT="${APP_ROOT:-/app}"
CERTIFICATE_ROOT="${CERTIFICATE_ROOT:-/opt/certificate}"

mkdir -p "$APP_ROOT"

cp "$CERTIFICATE_ROOT/reference_certificate.json" \
   "$APP_ROOT/certificate.json"
