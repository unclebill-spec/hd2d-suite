"""pure-python self-test of smoke.can_wear / wearable_chest_index (no browser, no game): python3 tests/test_smoke_gear_wear.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke import can_wear, wearable_chest_index  # noqa: E402


# (a) official try 1: Stormborn rolled "Twilight Plate Coat" (plate). Enter toasts "Can't wear".
assert can_wear("stormborn", {"slot": "chest", "name": "Twilight Plate Coat", "at": "plate"}) is False
assert can_wear("stormborn", {"slot": "chest", "name": "Twilight Plate Coat"}) is False  # name-only, at missing

# (b) official try 2: "Starlit Leather Jerkin" (leather) is wearable; max HP went 120→127.
assert can_wear("stormborn", {"slot": "chest", "name": "Starlit Leather Jerkin", "at": "leather"}) is True
assert can_wear("stormborn", {"slot": "chest", "name": "Starlit Leather Jerkin"}) is True

# (c) Stormborn (chain) wears chain and cloth, not only leather.
assert can_wear("stormborn", {"slot": "chest", "name": "Moss Mail", "at": "chain"}) is True
assert can_wear("stormborn", {"slot": "chest", "name": "Chain Hauberk"}) is True
assert can_wear("stormborn", {"slot": "chest", "name": "Wool Cloth Robe", "at": "cloth"}) is True
assert can_wear("stormborn", {"slot": "chest", "name": "Wool Cloth Robe"}) is True

# (d) skip a leading unwearable plate chest; a bag of only that plate chest is -1.
bag = [
    {"slot": "chest", "name": "Twilight Plate Coat", "at": "plate"},
    {"slot": "helm", "name": "Starlit Leather Helm", "at": "leather"},
    {"slot": "chest", "name": "Starlit Leather Jerkin", "at": "leather"},
]
assert wearable_chest_index("stormborn", bag) == 2
bag_chain = [
    {"slot": "chest", "name": "Twilight Plate Coat"},
    {"slot": "chest", "name": "Moss Mail", "at": "chain"},
]
assert wearable_chest_index("stormborn", bag_chain) == 1
assert wearable_chest_index("stormborn", [{"slot": "chest", "name": "Twilight Plate Coat", "at": "plate"}]) == -1
assert wearable_chest_index("stormborn", [{"slot": "chest", "name": "Twilight Plate Coat"}]) == -1

# (e) Seer (cloth) refuses leather, chain and plate; Runeguard (plate) wears plate.
assert can_wear("seer", {"slot": "chest", "name": "Starlit Leather Jerkin", "at": "leather"}) is False
assert can_wear("seer", {"slot": "chest", "name": "Moss Mail", "at": "chain"}) is False
assert can_wear("seer", {"slot": "chest", "name": "Twilight Plate Coat", "at": "plate"}) is False
assert can_wear("seer", {"slot": "chest", "name": "Wool Cloth Robe", "at": "cloth"}) is True
assert can_wear("runeguard", {"slot": "chest", "name": "Twilight Plate Coat", "at": "plate"}) is True
# no armor type (weapons, or a name with no cue) is wearable, same as !it.at in loot.js
assert can_wear("stormborn", {"slot": "primary", "name": "Iron Sword"}) is True
assert can_wear("seer", None) is True

print("can_wear/wearable_chest_index self-test: 5 cases ok")
