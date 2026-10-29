#!/usr/bin/env python3
"""Hearthmoor: run the per-area check-scene for many areas, serially (default) or in parallel (--jobs N).

Every area runs the SAME `bin/hd2d check-scene games/hearthmoor --scene-dir areas/<a> --params "area=<a>&qa&spawn=start"`
as before (same thresholds, same shots dir); --jobs only runs several of them at once. check-scene serves each run on
its own random port and writes its own shots/<area>/ folder, so parallel runs do not touch each other.

  python3 tests/check_all.py                       # every built area, one at a time
  python3 tests/check_all.py --jobs 2              # 2 at a time if the box is idle (capped: see --no-cap)
  python3 tests/check_all.py --areas bifrost,temple --tries 2 --logdir /workspace/.hm-logs/cs
  python3 tests/check_all.py --quick temple        # alias for --areas temple

Wrap it in the browser lock like every headless run:  flock /workspace/.hm-logs/browser.lock python3 tests/check_all.py
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


def run_area(a, tries, logdir, lock, lowres=False):
    params = PARAMS.get(a, f"area={a}&qa&spawn=start")
    cmd = [str(SUITE / "bin" / "hd2d"), "check-scene", "games/hearthmoor", "--scene-dir", f"areas/{a}", "--params", params, "--out", f"games/hearthmoor/shots/{a}"] + (["--quick"] if lowres else [])
    res = {"area": a, "pass": False, "tries": 0}
    relaunches = 0
    for t in range(1, tries + 2):
        if t > tries + relaunches:
            break
        t0 = time.time(); log = logdir / f"cs_{a}_{t}.log"
        with open(log, "w") as fh:
            rc = subprocess.call(cmd, cwd=SUITE, stdout=fh, stderr=subprocess.STDOUT)
        res.update(tries=t, rc=rc, seconds=round(time.time() - t0, 1), log=str(log))
        tail = log.read_text(errors="replace").strip().splitlines()[-1:] or [""]
        with lock:
            print(f"[{a}] try {t}: {'PASS' if rc == 0 else 'FAIL'} in {res['seconds']} s  {tail[0][:140]}", flush=True)
        if rc == 3 and relaunches == 0:   # check-scene: browser could not create a WebGL context (box fault): one fresh relaunch
            relaunches = 1; res["webgl_relaunch"] = True
            time.sleep(20)
            continue
        if rc == 0:
            res["pass"] = True
            (logdir / f"cs_{a}.pass").write_text(str(t))
            break
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--areas", default="", help="comma list (default: every built area)")
    ap.add_argument("--quick", default="", help="same as --areas (the per-change check)")
    ap.add_argument("--lowres", action="store_true", help="check-scene --quick (960x540, same checks / pass rules): per-change runs; full size before publish")
    ap.add_argument("--changed", nargs="?", const="main", default="", help="only areas changed vs this git ref (default main): areas/src/<a>.json or areas/<a>/ in git diff")
    ap.add_argument("--jobs", type=int, default=1, help="check-scenes at once (default 1 = serial)")
    ap.add_argument("--no-cap", action="store_true", help="do not cap --jobs by free CPU")
    ap.add_argument("--tries", type=int, default=1, help="tries per area (a retry re-runs the identical check)")
    ap.add_argument("--logdir", default=str(GAME / "tests" / "out" / "check_all"))
    ap.add_argument("--no-preflight", action="store_true", help="skip tests/preflight.sh (syntax + quick startup load)")
    a = ap.parse_args()
    if not a.no_preflight:
        import os
        rc = subprocess.call(["bash", str(GAME / "tests" / "preflight.sh")], env={**os.environ, "HM_IN_BROWSER_LOCK": "1"})   # check_all runs under the browser lock already
        if rc:
            sys.exit(f"check_all: preflight FAILED (rc {rc}); fix it first (or --no-preflight)")
    want = [x.strip() for x in (a.areas or a.quick).split(",") if x.strip()]
    if a.changed:
        names = subprocess.run(["git", "diff", "--name-only", a.changed, "--", "games/hearthmoor/areas"], cwd=SUITE, capture_output=True, text=True, check=True).stdout.split()
        ch = {Path(n).stem if "/areas/src/" in n else n.split("/areas/")[1].split("/")[0] for n in names if "/areas/" in n}
        want = sorted(x for x in ch & set(areas_built()) if x not in want) + want
        if not want:
            print(f"check_all: no area changed vs {a.changed}"); return
    want = want or areas_built()
    missing = [x for x in want if x not in areas_built()]
    if missing:
        sys.exit(f"not built: {missing} (built: {areas_built()})")
    if a.jobs > 1 and not a.no_cap:
        # each SwiftShader check-scene page burns ~5 cores; 3 at once on an 8-core box shared with other agents starved
        # the renderer so far that most areas never reached 6 frames (ready) inside 120 s. Cap by free CPU, never below 1.
        import os
        free = (os.cpu_count() or 1) - os.getloadavg()[0]
        cap = max(1, int(free // 5))
        if cap < a.jobs:
            print(f"check_all: --jobs {a.jobs} capped to {cap} (loadavg {os.getloadavg()[0]:.1f} on {os.cpu_count()} cpus; --no-cap to override)", flush=True)
            a.jobs = cap
    logdir = Path(a.logdir); logdir.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock(); t0 = time.time()
    print(f"check_all: {len(want)} areas, jobs {a.jobs}, tries {a.tries}: {', '.join(want)}", flush=True)
    order = sorted(want, key=lambda x: -(GAME / "areas" / x / "scene.json").stat().st_size)   # bigger scenes first
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        futs = []
        for k, x in enumerate(order):
            futs.append(ex.submit(run_area, x, a.tries, logdir, lock, a.lowres))
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
