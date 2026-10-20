#!/usr/bin/env bash
# Heavy-job queue (opt-in for every bot on this box): run "$@" at nice 10 holding one of TWO lock slots, so at most 2 heavy jobs
# (smokes, check_all, builds, art installs) run at once; a third waits for a free slot. Never kills anything.
#   tools/heavy.sh flock /workspace/.hm-logs/browser.lock python3 games/hearthmoor/tests/smoke.py --segments C
# Slots: /workspace/.hm-logs/heavy.lock.1 and heavy.lock.2 (= `nice -n 10 flock /workspace/.hm-logs/heavy.lock.N "$@"`).
D=/workspace/.hm-logs; mkdir -p "$D"
[ $# -gt 0 ] || { echo "usage: tools/heavy.sh CMD [ARGS...]" >&2; exit 64; }
waited=0
while :; do
  for s in 1 2; do
    nice -n 10 flock -n -E 200 "$D/heavy.lock.$s" "$@"; rc=$?
    [ $rc = 200 ] || exit $rc   # 200 = that slot is busy (the command never ran); anything else is the command's own exit code
  done
  [ $waited = 0 ] && echo "heavy.sh: both slots busy, waiting..." >&2; waited=1
  sleep 5   # queue pacing while both slots are held
done
