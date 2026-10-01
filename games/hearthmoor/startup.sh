#!/usr/bin/env bash
# Hearthmoor preview: static server on 0.0.0.0:8080 (open http://<box>:8080/ ; phones on the same network work too).
cd "$(dirname "$0")"
PORT="${PORT:-8080}"
echo "Hearthmoor on http://0.0.0.0:${PORT}/  (Ctrl+C to stop)"
exec python3 -m http.server "$PORT" --bind 0.0.0.0
