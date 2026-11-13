"""pure-python self-test of smoke.dmgnum_ok (no browser, no game): python3 tests/test_smoke_dmgnum.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke import dmgnum_ok  # noqa: E402


# (a) official a04cf1c try 1: HP fell 120→84, the floater had already expired.
assert dmgnum_ok(120, 84, 0) is True

# (b) official a04cf1c try 2: HP fell 120→75, the floater had already expired.
assert dmgnum_ok(120, 75, 0) is True

# (c) HP unchanged and no floater: the swing did not land.
assert dmgnum_ok(120, 120, 0) is False

# (d) HP drop and a floater still in #fxlayer.
assert dmgnum_ok(120, 84, 1) is True

# (e) floater still visible while the HP sample lags; missing HP / nums satisfy neither side.
assert dmgnum_ok(120, 120, 2) is True
assert dmgnum_ok(None, None, 0) is False
assert dmgnum_ok("120", 84, None) is False
assert dmgnum_ok(120, None, 0) is False

print("dmgnum_ok self-test: 5 cases ok")
