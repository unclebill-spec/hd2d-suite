// The Humming Golem: Dagna's idle offer, three Copper Row piles, golem choice, reward, save/load.
// svartalfheim.js is loaded so the real TALK.dagna (forge lines + Forgefire wrap) is what installSideQuests captures.
// It pulls alfheim, which imports the browser package `three`. The stub is test-only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === 'three' || specifier.startsWith('three/')) {
      return {
        url: 'data:text/javascript,' + encodeURIComponent('export default {};\n'),
        shortCircuit: true,
        format: 'module',
      };
    }
    return nextResolve(specifier, context);
  },
});

globalThis.window ??= globalThis;
globalThis.document ??= { getElementById: () => null, head: { appendChild() {} }, body: { appendChild() {}, classList: { add() {}, remove() {} } }, createElement: () => ({ style: {}, appendChild() {}, classList: { add() {} }, getContext: () => ({}) }) };
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.location ??= { search: '' };

const { TALK, QUESTS, ITEMS, markerFor } = await import('../game/data.js');
await import('../game/svartalfheim.js');
const { KIT: FOLLOW_KIT } = await import('../game/svartalfheim_follow.js');
const {
  installSideQuests, dagna_song, RUBBLE_SPOTS, COPPER_GOLEM, rubbleCount,
} = await import('../game/side_quests.js');
const { Collide } = await import('../engine/collide.js');

const IDLE = 'Anvildeep\'s best smith. Also its rudest. Don\'t touch the hammer.';
const START_OPEN = [
  'Hush. Hear that? Under the floor.',
  'That is my grandfather\'s work song. He hummed it at the anvil for sixty years. He has been dead for twelve.',
];
const START_ASK = 'The old tunnel under Copper Row. Come with me. Bring a pick.';
const START_WON = 'The old tunnel is closed by your new orders. I am asking you to open it. Just this once.';
const CHOICE_PAGES = [
  '(Under a fallen beam: a copper golem, old and green at the joints. Its chest glows neon blue. It is humming.)',
  'He built this one. Look, his mark. It has been humming his song down here in the dark all this time.',
  'The forge would pay well for a core like that. I know it would. I am not saying we should.',
];
const FREE_SING = [
  '(Dagna sings, rough and low. The golem stops. Then it sings the next line, and lifts the beam off itself.)',
  'Grandfather. You stubborn old lump.',
];
const CORE_TAKE = [
  '(The humming stops. The neon goes out of its chest. The tunnel is very quiet.)',
  '...Right. Right. It is good metal. He would have said so.',
];
const FREE_PAY = ['He is walking Copper Row now. Smiths keep stopping to listen. Here: my grandfather\'s rune-stone, and the reward the guild owed him.'];
const CORE_PAY = ['I will carry the rest of him home. You keep the core. Do not let Tova sell it.'];
const LEFTOVER = 'Copper Row has a hum to it again. Or a hole where the hum was. Depends which you chose.';
const TRIAL = 'Strike the Great Anvil when the glow is smallest. The anvil talks. Listen.';
const VERDICT = 'Three true. Your arm\'s not bad, for a Midgarder. Tell the Thane I said so. She won\'t believe it.';
const KINDLE = [
  'The Heart\'s lost somewhere. Fine. I can\'t make a new one. But I can make a little one. Enough to hold him.',
  'I need forge-cores. Three. The mines have ember seams, deep down. Bring me three and I\'ll do the rest.',
];
const EGG = 'Take the Heart to the Thane. Hold it like an egg. A hot, angry egg.';
const OFFER = 'Forgefire! Go and hit something. Not me. Something metal.';
const TURNIN = 'Three true strikes and three orders? ...Not bad. I\'ll chalk your name on the board. I might even spell it right.';
const FOUND3 = { sq_rubble1: 1, sq_rubble2: 1, sq_rubble3: 1 };

function fresh(extra = {}) {
  const e = JSON.parse(JSON.stringify(extra));
  return {
    flags: e.flags || {},
    quests: e.quests || {},
    found: e.found || {},
    inv: e.inv || {},
    met: e.met || {},
    gems: e.gems || {},
    gold: e.gold ?? 0,
    day: e.day,
    forgefire: e.forgefire,
  };
}

function mock(S) {
  const g = {
    S, toasts: [], saves: 0, opened: null,
    toast(m) { g.toasts.push(m); },
    save() { g.saves += 1; },
    give(id, n = 1) { g.S.inv = g.S.inv || {}; g.S.inv[id] = (g.S.inv[id] || 0) + n; },
    setQuest(id, stage) { g.S.quests = g.S.quests || {}; g.S.quests[id] = stage; },
    openDialogue(who, entry) { g.opened = { who, entry }; },
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({
    quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, gold: S.gold, gems: S.gems,
  }));
}

function makeCtx() {
  const npcs = [];
  return {
    npcs,
    player: { x: 1.6, z: 5.0, y: 0.03 },
    heightAt: () => 0,
    scene: { game: {} },
    actors: {
      meta: { roles: { golem: true, sparkgolem: true, forgeconstruct: true, emberimp: true, dagna: true } },
      add() {},
      remove() {},
    },
    addNpc(spec) {
      const a = { ...spec, x: spec.pos[0], z: spec.pos[1] };
      npcs.push(a);
      return a;
    },
    removeNpc(a) {
      const i = npcs.indexOf(a);
      if (i >= 0) npcs.splice(i, 1);
    },
    npc(id) { return npcs.find((a) => a.id === id) || null; },
  };
}

function makeSv(G) {
  return {
    G,
    area: null,
    ctx: null,
    spots: [],
    follow: null,
    spot(o) { this.spots.push({ r: 1.6, show: () => true, ...o }); },
    attach(ctx, area) {
      this.ctx = ctx;
      this.area = area;
      this.spots = [];
      this.follow = { id: 'dagna', sprite: { role: 'dagna' } };
    },
  };
}

const shell = mock(fresh());
shell.combat = { ctx: {}, spawned: [], spawnEnemy(sp, poof) { this.spawned.push({ sp, poof }); } };
shell.svart = makeSv(shell);
installSideQuests(shell);

const scene = JSON.parse(readFileSync(new URL('../areas/svartalfheim/scene.json', import.meta.url), 'utf8'));
const col = new Collide(scene.collision);
const AVOID = [[-3, 7], [-7, 5.8], [4.4, -3.2], [5.6, 5.6], [-0.8, 1.4], [8.6, 7.8], [1.6, 5.0]];

function reached() {
  const cell = scene.collision.cell;
  const x0 = 1.6, z0 = 5.0;
  const h0 = col.canStand(x0, z0, col.height(x0, z0), 0.28);
  const key = (x, z) => `${Math.round(x / cell)}:${Math.round(z / cell)}`;
  const seen = new Set([key(x0, z0)]);
  const q = [[x0, z0, h0]];
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  while (q.length) {
    const [x, z, h] = q.shift();
    for (const [dx, dz] of dirs) {
      const nx = Math.round((x + dx * cell) * 4) / 4;
      const nz = Math.round((z + dz * cell) * 4) / 4;
      const k = key(nx, nz);
      if (seen.has(k)) continue;
      const nh = col.canStand(nx, nz, h, 0.28);
      if (nh == null) continue;
      seen.add(k);
      q.push([nx, nz, nh]);
    }
  }
  return { seen, key, h0 };
}

test('quest text is the Story block and runestone already exists', () => {
  assert.equal(QUESTS.sq_copper_song.title, 'The Humming Golem');
  assert.equal(QUESTS.sq_copper_song.giver, 'Dagna Coalbeard');
  assert.equal(QUESTS.sq_copper_song.side, true);
  assert.equal(QUESTS.sq_copper_song.steps[1]({ found: {} }), 'Something under Copper Row hums an old work song. Rubble cleared: 0/3.');
  assert.equal(QUESTS.sq_copper_song.steps[1]({ found: { sq_rubble1: 1, sq_rubble3: 1 } }), 'Something under Copper Row hums an old work song. Rubble cleared: 2/3.');
  assert.equal(QUESTS.sq_copper_song.steps[2], 'An old copper golem, jammed under a beam. It is still humming.');
  assert.equal(QUESTS.sq_copper_song.steps[3](fresh({ flags: { sq_golem: 'free' } })), 'The golem walks Copper Row now, humming.');
  assert.equal(QUESTS.sq_copper_song.steps[3](fresh({ flags: { sq_golem: 'core' } })), 'You took the core. Dagna will not look at the forge for a while.');
  assert.equal(ITEMS.runestone.name, 'Rune-stone');
  assert.equal(ITEMS.golem_core, undefined);
  assert.equal(QUESTS.sq_ember_kids, undefined);
  assert.deepEqual(dagna_song(fresh()).pages, [...START_OPEN, START_ASK]);
  assert.equal(dagna_song(fresh({ flags: { alliance: { svartalfheim: 'conquer' } } })).pages[2], START_WON);
});

test('the side quest starts from idle, including both won lines, and not from trial, kindle, or forgefire', () => {
  const plain = fresh();
  const start = TALK.dagna(plain);
  assert.deepEqual(start.pages, [...START_OPEN, START_ASK]);
  start.then(mock(plain));
  assert.equal(plain.quests.sq_copper_song, 1);

  const won = fresh({ flags: { alliance: { svartalfheim: 'conquer' } } });
  const wonTalk = TALK.dagna(won);
  assert.equal(wonTalk.pages[0], START_OPEN[0]);
  assert.equal(wonTalk.pages[2], START_WON);
  wonTalk.then(mock(won));
  assert.equal(won.quests.sq_copper_song, 1);

  const mid = fresh({ quests: { sq_copper_song: 1 } });
  assert.equal(TALK.dagna(mid).pages[0], IDLE);
  assert.equal(mid.quests.sq_copper_song, 1);

  const trial = fresh({ flags: { alliance: { svartalfheim: 'befriend' } }, quests: { sv_trial: 1 } });
  assert.equal(TALK.dagna(trial).pages[0], TRIAL);
  assert.equal(trial.quests.sq_copper_song, undefined);

  const verdict = fresh({ flags: { alliance: { svartalfheim: 'befriend' }, st_hits: 3 }, quests: { sv_trial: 1 } });
  const vd = TALK.dagna(verdict);
  assert.equal(vd.pages[0], VERDICT);
  vd.then(mock(verdict));
  assert.equal(verdict.quests.sv_trial, 2);
  assert.equal(verdict.quests.sq_copper_song, undefined);

  const kindle = fresh({ flags: { alliance: { svartalfheim: 'befriend' } }, quests: { sv_kindle: 1 } });
  assert.deepEqual(TALK.dagna(kindle).pages, KINDLE);
  assert.equal(kindle.quests.sq_copper_song, undefined);

  const egg = fresh({ flags: { alliance: { svartalfheim: 'befriend' } }, quests: { sv_kindle: 2 } });
  assert.equal(TALK.dagna(egg).pages[0], EGG);

  const ready = fresh({
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { sv_kindle: 1, sq_copper_song: 1 },
    found: FOUND3,
  });
  assert.deepEqual(TALK.dagna(ready).pages, KINDLE);
  assert.equal(ready.quests.sq_copper_song, 1);

  const offer = fresh({
    day: 3,
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { clockdeep: 3 },
  });
  const off = TALK.dagna(offer);
  assert.equal(off.pages[0], OFFER);
  off.then(mock(offer));
  assert.equal(offer.quests.forgefire, 1);
  assert.equal(offer.quests.sq_copper_song, undefined);

  const remind = fresh({
    day: 3,
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { clockdeep: 3, forgefire: 1, sq_copper_song: 2 },
    forgefire: { strikes: 1, orders: 0, fday: 3, given: {} },
    found: FOUND3,
    flagsExtra: null,
  });
  remind.flags.sq_golem = 'free';
  assert.equal(TALK.dagna(remind).pages[0], 'Forgefire! strikes 1/3, orders 0/3. Hit the anvil when the glow is smallest.');
  assert.equal(remind.quests.sq_copper_song, 2);
  assert.equal(remind.gold, 0);

  const turn = fresh({
    day: 3,
    flags: { alliance: { svartalfheim: 'befriend' }, sq_golem: 'free' },
    quests: { clockdeep: 3, forgefire: 1, sq_copper_song: 2 },
    forgefire: { strikes: 3, orders: 3, fday: 3, given: {} },
    found: FOUND3,
  });
  assert.equal(TALK.dagna(turn).pages[0], TURNIN);
  assert.equal(turn.quests.sq_copper_song, 2);
  assert.equal(turn.inv.runestone, undefined);
});

test('three rubble, then both golem picks, then both rewards, then leftover and save/load', () => {
  const base = fresh({ quests: { sq_copper_song: 1 }, found: FOUND3, gold: 5 });
  assert.equal(rubbleCount(base), 3);
  const choice = dagna_song(base);
  assert.deepEqual(choice.pages, CHOICE_PAGES);
  assert.equal(choice.choice.id, 'sq_golem');
  const freeOpt = choice.choice.options.find((o) => o.label === 'Sing the second verse with it.');
  const coreOpt = choice.choice.options.find((o) => o.label === 'Take the core for the forge.');

  const freeS = fresh(snap(base));
  const gFree = mock(freeS);
  assert.deepEqual(freeOpt.pick(gFree).pages, FREE_SING);
  assert.equal(freeS.flags.sq_golem, 'free');
  assert.equal(freeS.quests.sq_copper_song, 2);
  assert.equal(freeS.gems.golem_core, undefined);
  assert.equal(freeS.gold, 5);
  assert.deepEqual(TALK.dagna(freeS).pages, FREE_PAY);
  TALK.dagna(freeS).then(gFree);
  assert.equal(freeS.quests.sq_copper_song, 3);
  assert.equal(freeS.inv.runestone, 1);
  assert.equal(freeS.gold, 85);
  assert.equal(freeS.gems.golem_core, undefined);
  assert.deepEqual(TALK.dagna(freeS).pages, [LEFTOVER]);
  assert.equal(QUESTS.sq_copper_song.steps[3](freeS), 'The golem walks Copper Row now, humming.');

  const loaded = fresh(JSON.parse(JSON.stringify(snap(freeS))));
  assert.equal(loaded.quests.sq_copper_song, 3);
  assert.equal(loaded.flags.sq_golem, 'free');
  assert.equal(loaded.found.sq_rubble2, 1);
  assert.equal(loaded.inv.runestone, 1);
  assert.equal(loaded.gold, 85);
  assert.deepEqual(dagna_song(loaded).pages, [LEFTOVER]);

  const coreS = fresh(snap(base));
  coreS.gold = 40;
  const gCore = mock(coreS);
  assert.deepEqual(coreOpt.pick(gCore).pages, CORE_TAKE);
  assert.equal(coreS.flags.sq_golem, 'core');
  assert.equal(coreS.quests.sq_copper_song, 2);
  assert.equal(coreS.gems.golem_core, 1);
  assert.equal(coreS.inv.runestone, undefined);
  assert.equal(coreS.gold, 40);
  assert.deepEqual(dagna_song(coreS).pages, CORE_PAY);
  const parked = fresh(JSON.parse(JSON.stringify(snap(coreS))));
  assert.equal(parked.quests.sq_copper_song, 2);
  assert.equal(parked.gems.golem_core, 1);
  assert.equal(parked.gold, 40);
  dagna_song(parked).then(mock(parked));
  assert.equal(parked.quests.sq_copper_song, 3);
  assert.equal(parked.inv.runestone, undefined);
  assert.equal(parked.gold, 40);
  assert.equal(parked.gems.golem_core, 1);
  assert.deepEqual(TALK.dagna(parked).pages, [LEFTOVER]);
  assert.equal(QUESTS.sq_copper_song.steps[3](parked), 'You took the core. Dagna will not look at the forge for a while.');
});

test('Dagna\'s idle, trial, kindle, follower, and marks stay put', () => {
  const src = readFileSync(new URL('../game/side_quests.js', import.meta.url), 'utf8');
  assert.equal(src.includes('talkable'), false);
  assert.equal(src.includes('.say'), false);
  assert.equal((src.match(/TALK\.dagna\s*=/g) || []).length, 1);
  assert.equal(FOLLOW_KIT.dagna.role, 'dagna');

  const idle = fresh({ quests: { sq_copper_song: 1 }, found: { sq_rubble1: 1 } });
  assert.equal(TALK.dagna(idle).pages[0], IDLE);
  assert.equal(markerFor('dagna', fresh()), null);
  assert.equal(markerFor('dagna', fresh({ quests: { sq_copper_song: 0 } })), null);
  assert.equal(markerFor('dagna', fresh({ quests: { sq_copper_song: 1 } })), null);
  assert.equal(markerFor('dagna', fresh({ quests: { sq_copper_song: 1 }, found: FOUND3 })), null);

  const fest = fresh({
    day: 3,
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { clockdeep: 3 },
  });
  assert.equal(markerFor('dagna', fest), 'quest_mark');

  const trial = fresh({
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { sv_trial: 1, sq_copper_song: 2 },
    found: FOUND3,
  });
  assert.equal(TALK.dagna(trial).pages[0], TRIAL);
  const kindle = fresh({
    flags: { alliance: { svartalfheim: 'befriend' } },
    quests: { sv_kindle: 2, sq_copper_song: 2 },
  });
  assert.equal(TALK.dagna(kindle).pages[0], EGG);
});

test('rubble and the golem stay hidden at stage 0, then the third pile brings the beam', () => {
  const { seen, key, h0 } = reached();
  assert.notEqual(h0, null);
  const spots = [...RUBBLE_SPOTS.map((s) => s.pos), COPPER_GOLEM.pos];
  for (const p of spots) {
    assert.notEqual(col.canStand(p[0], p[1], col.height(p[0], p[1]), 0.28), null, p.join(','));
    assert.equal(seen.has(key(p[0], p[1])), true, p.join(','));
    for (const n of AVOID) assert.ok(Math.hypot(p[0] - n[0], p[1] - n[1]) >= 3, p.join(',') + ' near ' + n.join(','));
  }
  for (let i = 0; i < RUBBLE_SPOTS.length; i++) {
    for (let j = i + 1; j < RUBBLE_SPOTS.length; j++) {
      const a = RUBBLE_SPOTS[i].pos, b = RUBBLE_SPOTS[j].pos;
      assert.ok(Math.hypot(a[0] - b[0], a[1] - b[1]) >= 2.4);
    }
  }
  const last = RUBBLE_SPOTS[2].pos;
  assert.ok(Math.hypot(COPPER_GOLEM.pos[0] - last[0], COPPER_GOLEM.pos[1] - last[1]) < 2.5);
  assert.equal(COPPER_GOLEM.role, 'golem');

  shell.S = fresh();
  shell.combat.spawned = [];
  shell.toasts = [];
  const quiet = makeCtx();
  shell.svart.attach(quiet, 'svartalfheim');
  for (const id of ['sq_rubble1', 'sq_rubble2', 'sq_rubble3', 'sq_golem']) {
    const spot = shell.svart.spots.find((s) => s.id === id);
    assert.ok(spot);
    assert.equal(spot.r, 1.2);
    assert.equal(spot.show(), false);
  }
  assert.equal(quiet.npc('sq_golem'), null);
  assert.equal(shell.combat.spawned.length, 0);
  assert.equal(shell.svart.follow.id, 'dagna');
  assert.equal(shell.svart.follow.sprite.role, 'dagna');
  assert.equal(shell.svart.follow.sprite.talkable, undefined);
  assert.equal(shell.svart.follow.sprite.say, undefined);

  shell.svart.attach(makeCtx(), 'forge_hall');
  assert.equal(shell.svart.spots.some((s) => s.id && String(s.id).startsWith('sq_')), false);

  shell.S = fresh({ quests: { sq_copper_song: 1 } });
  shell.combat.spawned = [];
  shell.toasts = [];
  shell.saves = 0;
  shell.opened = null;
  const ctx = makeCtx();
  shell.svart.attach(ctx, 'svartalfheim');
  assert.equal(ctx.npc('sq_golem'), null);
  assert.equal(shell.svart.spots.find((s) => s.id === 'sq_golem').show(), false);
  assert.equal(shell.combat.spawned.length, 0);
  for (const id of ['sq_rubble1', 'sq_rubble2', 'sq_rubble3']) {
    const spot = shell.svart.spots.find((s) => s.id === id);
    assert.equal(spot.show(), true);
    spot.act();
    assert.equal(shell.opened.who.id, id);
    shell.opened.entry.then(shell);
    assert.equal(shell.S.found[id], 1);
    assert.equal(spot.show(), false);
  }
  assert.equal(rubbleCount(shell.S), 3);
  assert.equal(shell.S.quests.sq_copper_song, 1);
  assert.deepEqual(shell.toasts.filter((t) => t.startsWith('Rubble ')), ['Rubble 1/3', 'Rubble 2/3', 'Rubble 3/3']);
  assert.ok(shell.toasts.includes('Fire elementals spark in the cracks.'));
  assert.ok(shell.toasts.includes('Something under the beam is humming.'));
  assert.equal(shell.saves, 3);
  assert.equal(shell.combat.spawned.length, 1);
  assert.equal(shell.combat.spawned[0].poof, true);
  assert.equal(shell.combat.spawned[0].sp.role, 'emberimp');
  assert.equal(shell.combat.spawned[0].sp.once, true);
  assert.equal(shell.combat.spawned[0].sp.id, 'sq_copper_imp');
  const body = ctx.npc('sq_golem');
  assert.equal(body.role, 'golem');
  assert.equal(body.talkable, undefined);
  assert.equal(body.say, undefined);
  assert.deepEqual(body.pos, COPPER_GOLEM.pos);
  const beam = shell.svart.spots.find((s) => s.id === 'sq_golem');
  assert.equal(beam.show(), true);
  shell.opened = null;
  beam.act();
  assert.equal(shell.opened.who.id, 'dagna');
  assert.equal(shell.opened.who.name, 'Dagna Coalbeard');
  assert.deepEqual(shell.opened.entry.pages, CHOICE_PAGES);
  const picked = shell.opened.entry.choice.options.find((o) => o.label === 'Sing the second verse with it.');
  assert.deepEqual(picked.pick(shell).pages, FREE_SING);
  assert.equal(shell.S.flags.sq_golem, 'free');
  assert.equal(shell.S.quests.sq_copper_song, 2);
  assert.equal(shell.S.gems.golem_core, undefined);
  assert.equal(ctx.npc('sq_golem'), null);
  assert.equal(beam.show(), false);

  const again = makeCtx();
  shell.svart.attach(again, 'svartalfheim');
  assert.equal(again.npc('sq_golem'), null);
  assert.equal(shell.svart.spots.find((s) => s.id === 'sq_golem').show(), false);
  assert.equal(shell.combat.spawned.length, 1);
});
