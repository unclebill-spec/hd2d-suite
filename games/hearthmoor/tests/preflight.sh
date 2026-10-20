#!/usr/bin/env bash
# Hearthmoor preflight (~10-30 s): catch syntax + startup errors before a long smoke / check_all.
#  1. node --check on every game/*.js and engine/*.js, as an .mjs copy (node --check on a .js ES module silently passes)
#  2. one headless page load of index.html (title screen ready): any pageerror / console.error (TDZ, ReferenceError, 404 import) fails
# Usage: bash games/hearthmoor/tests/preflight.sh [--no-load]
# The page load takes /workspace/.hm-logs/browser.lock itself unless HM_IN_BROWSER_LOCK=1 (smoke.py / check_all.py set it: they run under that lock already).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; GAME="$(dirname "$HERE")"
t0=$(date +%s); fail=0
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
n=0
for f in "$GAME"/game/*.js "$GAME"/engine/*.js; do
  n=$((n+1)); c="$tmp/$(basename "$(dirname "$f")")_$(basename "${f%.js}").mjs"; cp "$f" "$c"
  if ! out=$(node --check "$c" 2>&1); then echo "preflight: SYNTAX $f"; echo "$out" | head -8; fail=1; fi
done
echo "preflight: node --check $n files: $([ $fail = 0 ] && echo ok || echo FAIL)"
[ $fail = 0 ] || exit 1
[ "${1:-}" = "--no-load" ] && exit 0
load() { python3 "$HERE/preflight_load.py"; }
if [ "${HM_IN_BROWSER_LOCK:-}" = 1 ]; then load; rc=$?
else mkdir -p /workspace/.hm-logs; flock /workspace/.hm-logs/browser.lock python3 "$HERE/preflight_load.py"; rc=$?; fi
echo "preflight: $([ $rc = 0 ] && echo PASS || echo FAIL) in $(( $(date +%s) - t0 )) s"
exit $rc
