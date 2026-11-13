"""pure-python self-test of smoke.seal_reward_ok (no browser, no game): python3 tests/test_smoke_seal_reward.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke import seal_reward_ok  # noqa: E402


# (a) a05e92d: ground kept wave gold 4/5/5/6 and two Commons; the Epic was already in the bag.
ground_a = [
    {"gold": 4, "rar": None},
    {"gold": 5, "rar": None},
    {"gold": 5, "rar": None},
    {"gold": 6, "rar": None},
    {"gold": 0, "rar": 0},
    {"gold": 0, "rar": 0},
]
assert any(d.get("rar") is not None and d["rar"] >= 2 for d in ground_a) is False
assert seal_reward_ok(2, ground_a, {"won": True, "drops": [], "pending": []}, [2], 0) == (True, True)

# (b) Epic exists only in the synchronous post-close drop list (ground + bag do not have it).
ground_b = [{"gold": 0, "rar": 0}, {"gold": 0, "rar": 0}]
snap_b = {"won": True, "drops": [{"gold": 8, "gem": None, "rar": 2}], "pending": []}
assert seal_reward_ok(2, ground_b, snap_b, [], 0) == (True, True)

# (c) Epic only as a deferred dropItem floor (loot.js may store minRar, not a rolled item).
ground_c = [{"gold": 4, "rar": 0}, {"gold": 0, "rar": 0}]
snap_c = {"won": True, "drops": [], "pending": [{"gold": 0, "gem": None, "rar": None, "minRar": 2}]}
assert seal_reward_ok(2, ground_c, snap_c, [0], 0) == (True, True)
# the wrapper's real pending shape: drop() pushed {item:{rar}} and the snapshot copied rar.
snap_c_item = {"won": True, "drops": [], "pending": [{"gold": 0, "gem": None, "rar": 2, "minRar": None}]}
assert seal_reward_ok(2, [{"gold": 0, "rar": 0}], snap_c_item, [], 0)[1] is True

# (d) nothing >= Epic anywhere: the rarity check must still fail. A Rare floor is not Epic.
ground_d = [{"gold": 4, "rar": 0}, {"gold": 0, "rar": 0}]
snap_d = {"won": True, "drops": [{"gold": 0, "rar": 0}], "pending": []}
assert seal_reward_ok(2, ground_d, snap_d, [0, 0], 4)[1] is False
assert seal_reward_ok(2, ground_d, {"won": True, "drops": [], "pending": [{"gold": 0, "rar": None, "minRar": 1}]}, [0], 0)[1] is False

# (e) minor tier (need 0): gold alone counts; no gold and a zero delta does not.
assert seal_reward_ok(0, [{"gold": 5, "rar": None}], None, [], 0)[0] is True
assert seal_reward_ok(0, [{"gold": 5, "rar": 0}], None, [], 0) == (True, True)  # Common meets need 0 (rar 0 is not "missing")
assert seal_reward_ok(0, [], {"drops": [], "pending": []}, [], 0)[0] is False
assert seal_reward_ok(0, [{"gold": 0, "rar": None}], {"drops": [{"gold": 0}], "pending": [{"gold": 0, "rar": None, "minRar": None}]}, [], 0)[0] is False
assert seal_reward_ok(0, [], None, [], 8)[0] is True  # picked into S.gold, nothing left on the ground
assert seal_reward_ok(0, [], {"drops": [], "pending": [{"gold": 3, "rar": None, "minRar": 0}]}, [], 0) == (True, True)

print("seal_reward_ok self-test: 5 cases ok")
