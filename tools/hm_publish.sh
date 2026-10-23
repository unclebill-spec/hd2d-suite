#!/usr/bin/env bash
# Auto-publish watcher (Hearthmoor): wait for every listed .done marker, and if all contain 0, publish <branch> to main + live.
#   setsid nohup tools/hm_publish.sh <branch> /workspace/.hm-logs/x.done [y.done ...] > /workspace/.hm-logs/publish_<branch>.log 2>&1 < /dev/null &
# Steps: CHANGELOG.md / AGENTS.md committed -> build.write_pwa() + make_zip() (via tools/heavy.sh) -> commit -> tools/secret_scan.sh +
# tools/checks/extra_secret_patterns.sh + gitleaks (abort on any finding) -> ff-only merge into main -> push main + branch -> poll the live sw.js until its cache id matches local (<= 10 min).
# Writes one line to /workspace/.hm-logs/publish_<branch>.result and RESUME.md. Any non-zero marker / failed step stops it with the reason.
set -uo pipefail
L=/workspace/.hm-logs; REPO="$(cd "$(dirname "$0")/.." && pwd)"
LIVE=https://unclebill-spec.github.io/hd2d-suite/games/hearthmoor/sw.js
B="${1:?usage: hm_publish.sh <branch> <done-marker...>}"; shift
[ $# -gt 0 ] || { echo "need at least one .done marker"; exit 64; }
RES="$L/publish_${B//\//_}.result"; rm -f "$RES"
ts() { date '+%H:%M'; }
finish() { echo "$1"; echo "$1" > "$RES"; echo "- publish $B $(ts): $1" >> "$L/RESUME.md"; exit "${2:-1}"; }
echo "hm_publish $B: waiting for $*"
for m in "$@"; do while [ ! -e "$m" ]; do sleep 20; done; done   # marker pacing (files written by detached jobs)
for m in "$@"; do v=$(tr -d '[:space:]' < "$m"); [ "$v" = 0 ] || finish "STOPPED: marker $m = '$v' (not 0)"; done
cd "$REPO" || finish "STOPPED: no repo $REPO"
[ "$(git rev-parse --abbrev-ref HEAD)" = "$B" ] || finish "STOPPED: checkout is on $(git rev-parse --abbrev-ref HEAD), not $B"
git add CHANGELOG.md AGENTS.md && { git diff --cached --quiet || git commit -qm "docs: CHANGELOG / AGENTS for $B"; } || finish "STOPPED: commit of CHANGELOG/AGENTS failed"
( cd games/hearthmoor && "$REPO/tools/heavy.sh" python3 -c 'import build; build.write_pwa(); build.make_zip()' ) || finish "STOPPED: pwa/zip build failed"
git add games/hearthmoor/sw.js games/hearthmoor.zip && { git diff --cached --quiet || git commit -qm "hearthmoor: PWA + zip for $B"; } || finish "STOPPED: pwa commit failed"
[ -z "$(git status --porcelain --untracked-files=no)" ] || finish "STOPPED: uncommitted tracked changes: $(git status --porcelain --untracked-files=no | head -3 | tr '\n' ' ')"
"$REPO/tools/checks/extra_secret_patterns.sh" "$REPO" || finish "STOPPED: extra secret pattern finding / error (nothing pushed)"
"$REPO/tools/secret_scan.sh" || finish "STOPPED: secret scan (rg + extra patterns + gitleaks) finding / error (nothing pushed)"
git fetch -q origin main || finish "STOPPED: git fetch failed"
git checkout -q main && git merge -q --ff-only origin/main && git merge -q --ff-only "$B" || { git checkout -q "$B"; finish "STOPPED: ff-merge of $B into main failed"; }
H=$(git rev-parse --short HEAD)
git push -q origin main || { git checkout -q "$B"; finish "STOPPED: push main failed (main is $H locally)"; }
git checkout -q "$B"; git push -q origin "$B" || finish "STOPPED: push $B failed (main $H pushed)"
want=$(rg -o "hearthmoor-v1-[0-9a-f]+" games/hearthmoor/sw.js | head -1)
for i in $(seq 1 40); do
  got=$(curl -fsS "$LIVE?cb=$(date +%s)" 2>/dev/null | rg -o "hearthmoor-v1-[0-9a-f]+" | head -1)
  [ "$got" = "$want" ] && finish "OK: main $H live ($want)" 0
  sleep 15   # Pages deploy polling
done
finish "STOPPED: pushed main $H but live sw.js is '$got', not $want after 10 min"
