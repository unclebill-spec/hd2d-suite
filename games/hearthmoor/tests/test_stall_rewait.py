"""pure-python self-test of smoke.stall_rewait (no browser, no game): python3 tests/test_stall_rewait.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke import stall_rewait  # noqa: E402


class TO(Exception):
    pass


def case(frames_now, rewait_ok, f_start=10):
    logs, dumps = [], []

    def w():
        if not rewait_ok:
            raise TO("again")
    try:
        r = stall_rewait(w, lambda: frames_now, f_start, lambda a, b: dumps.append((a, b)), logs.append, "pred")
    except TO:
        r = "raised"
    return r, dumps, logs


assert case(10, True)[0] == "recovered" and case(10, True)[1] == [(10, 10)] and "STALL-WARN" in case(10, True)[2][0]
assert case(10, False)[0] == "raised" and "STALL-FAIL" in case(10, False)[2][0]
assert case(15, True) == (None, [], [])          # frames ticking: a real timeout, no re-wait
assert case(None, True) == (None, [], [])        # counter unreadable: no re-wait
print("stall_rewait self-test: 4 cases ok")
