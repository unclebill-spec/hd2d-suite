// node --test tests/codex.mjs : lore codex unlocks from existing save state
import test from 'node:test';
import assert from 'node:assert/strict';
import { CODEX, isUnlocked, unlockedEntries } from '../game/codex.js';

const KINDS = new Set(['always', 'alliance', 'flags', 'met', 'merit', 'quests']);
const byUnlock = (unlock) => CODEX.find((e) => e.unlock === unlock);
const byId = (id) => CODEX.find((e) => e.id === id);

test('27 entries, unique ids, non-empty title and text, six unlock kinds', () => {
  assert.equal(CODEX.length, 27);
  const ids = CODEX.map((e) => e.id);
  assert.equal(new Set(ids).size, 27);
  for (const e of CODEX) {
    assert.equal(typeof e.title, 'string');
    assert.ok(e.title.length > 0, e.id);
    assert.equal(typeof e.text, 'string');
    assert.ok(e.text.length > 0, e.id);
    const kind = String(e.unlock).split('.')[0];
    assert.ok(KINDS.has(kind), e.unlock);
  }
});

test('isUnlocked is true and false for each kind', () => {
  const always = byUnlock('always');
  assert.equal(isUnlocked({}, always), true);
  assert.equal(isUnlocked({ flags: {} }, always), true);

  const alf = byUnlock('alliance.alfheim');
  assert.equal(isUnlocked({ flags: { alliance: { alfheim: 'befriend' } } }, alf), true);
  assert.equal(isUnlocked({ flags: { alliance: { alfheim: 'conquer' } } }, alf), true);
  assert.equal(isUnlocked({ flags: { alliance: { alfheim: 'contract' } } }, alf), true);
  assert.equal(isUnlocked({ flags: { alliance: { alfheim: '' } } }, alf), false);
  assert.equal(isUnlocked({ flags: { alliance: {} } }, alf), false);
  assert.equal(isUnlocked({}, alf), false);

  const revealed = byId('realm_niflheim');
  assert.equal(revealed.unlock, 'flags.veyra_revealed');
  assert.equal(isUnlocked({ flags: { veyra_revealed: 1 } }, revealed), true);
  assert.equal(isUnlocked({ flags: { veyra_revealed: 0 } }, revealed), false);
  assert.equal(isUnlocked({ flags: {} }, revealed), false);

  const hel = byId('realm_helheim');
  assert.equal(isUnlocked({ flags: { hel: 'kind' } }, hel), true);
  assert.equal(isUnlocked({ flags: { hel: 'defiant' } }, hel), true);
  assert.equal(isUnlocked({ flags: { hel: '' } }, hel), false);

  const lumi = byId('lumi');
  assert.equal(lumi.unlock, 'flags.companions.lumi');
  assert.equal(isUnlocked({ flags: { companions: { lumi: 1 } } }, lumi), true);
  assert.equal(isUnlocked({ flags: { companions: {} } }, lumi), false);
  assert.equal(isUnlocked({ flags: {} }, lumi), false);

  const nettle = byId('boss_nettlecrown');
  assert.equal(isUnlocked({ flags: { vh_nettle: 'spared' } }, nettle), true);
  assert.equal(isUnlocked({ flags: { vh_nettle: 'ended' } }, nettle), true);
  assert.equal(isUnlocked({ flags: {} }, nettle), false);

  const hilde = byUnlock('met.hilde');
  assert.equal(isUnlocked({ met: { hilde: 1 } }, hilde), true);
  assert.equal(isUnlocked({ met: {} }, hilde), false);
  assert.equal(isUnlocked({}, hilde), false);

  const gnome = byUnlock('merit.gnome');
  assert.equal(isUnlocked({ merit: { gnome: 1 } }, gnome), true);
  assert.equal(isUnlocked({ merit: { gnome: 40 } }, gnome), true);
  assert.equal(isUnlocked({ merit: { gnome: 0 } }, gnome), false);
  assert.equal(isUnlocked({}, gnome), false);

  const rotwood = byUnlock('quests.rotwood');
  assert.equal(isUnlocked({ quests: { rotwood: 3 } }, rotwood), true);
  assert.equal(isUnlocked({ quests: { rotwood: 2 } }, rotwood), false);
  assert.equal(isUnlocked({ quests: { rotwood: 1 } }, rotwood), false);
  assert.equal(isUnlocked({}, rotwood), false);

  const verdant = byUnlock('quests.verdant');
  assert.equal(isUnlocked({ quests: { verdant: 3 } }, verdant), true);
  assert.equal(isUnlocked({ quests: { verdant: 3 } }, byId('boss_hjortur')), true);
  assert.equal(isUnlocked({ quests: {} }, verdant), false);
});

test('empty save never throws and unlocks only always', () => {
  const S = {};
  assert.deepEqual(unlockedEntries(S).map((e) => e.id), ['realm_midgard']);
  for (const e of CODEX) {
    assert.equal(isUnlocked(S, e), e.unlock === 'always');
    assert.equal(isUnlocked(null, e), e.unlock === 'always');
    assert.equal(isUnlocked(undefined, e), e.unlock === 'always');
  }
  assert.doesNotThrow(() => unlockedEntries(null));
  assert.doesNotThrow(() => unlockedEntries());
  const broken = { flags: null, met: null, merit: null, quests: null };
  assert.doesNotThrow(() => unlockedEntries(broken));
  assert.deepEqual(unlockedEntries(broken).map((e) => e.id), ['realm_midgard']);
});
