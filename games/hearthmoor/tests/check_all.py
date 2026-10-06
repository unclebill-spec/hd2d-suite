#!/usr/bin/env python3
"""Hearthmoor: run the per-area check-scene for many areas, serially (default) or in parallel (--jobs N).

Every area runs the SAME `bin/hd2d check-scene games/hearthmoor --scene-dir areas/<a> --params "area=<a>&qa&spawn=start"`
as before (same thresholds, same shots dir); --jobs only runs several of them at once. check-scene serves each run on
its own random port and writes its own shots/<area>/ folder, so parallel runs do not touch each other.

  python3 tests/check_all.py                       # every built area, one at a time
  python3 tests/check_all.py --jobs 3              # 3 at a time (2-3 on a loaded 8-core box)
  python3 tests/check_all.py --areas bifrost,temple --tries 2 --logdir /workspace/.hm-logs/cs
  python3 tests/check_all.py --quick temple        # alias for --areas temple

Wrap it in the browser lock like every headless run:  flock /workspace/.hm-logs/browser.lock python3 tests/check_all.py --jobs 3
Exit code 0 only when every area passed. A summary is written to <logdir>/check_all.json.
"""
import argparse
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
SUITE = GAME.parents[1]
PARAMS = {}   # per-area overrides of the check-scene params (default: area=<a>&qa&spawn=start)


def areas_built():
    return sorted(p.parent.name for p in (GAME / "areas").glob("*/scene.json"))


def run_area(a, tries, logdir, lock):
    params = PARAMS.get(a, f"area={a}&qa&spawn=start")
    cmd = [str(SUITE / "bin" / "hd2d"), "check-scene", "games/hearthmoor", "--scene-dir", f"areas/{a}", "--params", params, "--out", f"games/hearthmoor/shots/{a}"]
    res = {"area": a, "pass": False, "tries": 0}
    for t in range(1, tries + 1):
        t0 = time.time(); log = logdir / f"cs_{a}_{t}.log"
        with open(log, "w") as fh:
            rc = subprocess.call(cmd, cwd=SUITE, stdout=fh, stderr=subprocess.STDOUT)
        res.update(tries=t, rc=rc, seconds=round(time.time() - t0, 1), log=str(log))
        tail = log.read_text(errors="replace").strip().splitlines()[-1:] or [""]
        with lock:
            print(f"[{a}] try {t}: {'PASS' if rc == 0 else 'FAIL'} in {res['seconds']} s  {tail[0][:140]}", flush=True)
        if rc == 0:
            res["pass"] = True
            (logdir / f"cs_{a}.pass").write_text(str(t))
            break
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--areas", default="", help="comma list (default: every built area)")
    ap.add_argument("--quick", default="", help="same as --areas (the per-change check)")
    ap.add_argument("--jobs", type=int, default=1, help="check-scenes at once (default 1 = serial)")
    ap.add_argument("--tries", type=int, default=1, help="tries per area (a retry re-runs the identical check)")
    ap.add_argument("--logdir", default=str(GAME / "tests" / "out" / "check_all"))
    a = ap.parse_args()
    want = [x.strip() for x in (a.areas or a.quick).split(",") if x.strip()] or areas_built()
    missing = [x for x in want if x not in areas_built()]
    if missing:
        sys.exit(f"not built: {missing} (built: {areas_built()})")
    logdir = Path(a.logdir); logdir.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock(); t0 = time.time()
    print(f"check_all: {len(want)} areas, jobs {a.jobs}, tries {a.tries}: {', '.join(want)}", flush=True)
    order = sorted(want, key=lambda x: -(GAME / "areas" / x / "scene.json").stat().st_size)   # bigger scenes first
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        futs = []
        for k, x in enumerate(order):
            futs.append(ex.submit(run_area, x, a.tries, logdir, lock))
            if a.jobs > 1 and k < a.jobs:
                time.sleep(3)   # stagger the browser launches a little on a loaded box
        out = [f.result() for f in futs]
    out.sort(key=lambda r: want.index(r["area"]))
    ok = all(r["pass"] for r in out)
    summary = {"pass": ok, "jobs": a.jobs, "seconds": round(time.time() - t0, 1), "areas": out}
    (logdir / "check_all.json").write_text(json.dumps(summary, indent=1))
    print(f"check_all: {'PASS' if ok else 'FAIL'} {sum(r['pass'] for r in out)}/{len(out)} areas in {summary['seconds']} s (jobs {a.jobs})", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
