// Snow for Cinderhold: Kindle's offer, one emberimp for the three kids, a stock wraith, reward, save/load.
// Kindle stays a follower. Talk is the Muspelheim prompt wrap. muspelheim.js imports alfheim, which
// imports the browser package `three`. The stub is test-only.
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
const { ENEMIES } = await import('../game/heroes.js');
const { KIT: FOLLOW_KIT } = await import('../game/svartalfheim_follow.js');
const { COMP } = await import('../game/svartalfheim_companions.js');
const { KINDLE, Muspelheim } = await import('../game/muspelheim.js');
const {
  installSideQuests, kindle_snow, ember_kids, kindleTalkReady, EMBER_KIDS_AT,
} = await import('../game/side_quests.js');

const SAY_AT_IMPORT = JSON.parse(JSON.stringify(KINDLE.say));
const KIT_AT_IMPORT = JSON.parse(JSON.stringify(FOLLOW_KIT.kindle));

function fresh(extra = {}) {
  return {
    flags: {}, quests: {}, found: {}, inv: {}, met: {}, gems: {},
    ...extra,
    flags: extra.flags || {},
    quests: extra.quests || {},
    found: extra.found || {},
    inv: extra.inv || {},
    gems: extra.gems || {},
  };
}

function mock(S) {
  const g = {
    S, toasts: [], saves: 0, opened: null, dlg: null, qaStill: true,
    toast(m) { g.toasts.push(m); },
    save() { g.saves += 1; },
    give(id, n = 1) { const cur = g.S; cur.inv = cur.inv || {}; cur.inv[id] = (cur.inv[id] || 0) + n; },
    setQuest(id, stage) { const cur = g.S; cur.quests = cur.quests || {}; cur.quests[id] = stage; },
    openDialogue(who, entry) { g.opened = { who, entry }; },
    svart: { follow: { on: false, id: null, sprite: null } },
    harbor: { prompt() { return ''; }, interact() { return false; }, onTap() { return false; } },
    combat: {
      spawned: [], enemies: [],
      maxHp() { return 100; },
      spawnEnemy(sp, poof) { this.spawned.push({ sp, poof }); return { sp }; },
    },
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({
    quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, gems: S.gems, gold: S.gold,
  }));
}

function world(x, z) {
  const added = [];
  const removed = [];
  const npcs = [];
  const follower = { id: 'comp_kindle', role: 'pet_kindle', x: x + 0.4, z: z + 0.2, talkable: undefined, say: null };
  const ctx = {
    added, removed, follower, npcs,
    player: { x, z, y: 0, facing: 'up' },
    scene: { game: {} },
    clock: { t: 0.5 },
    heightAt: () => 0,
    collide: null,
    gamefx: null,
    actors: {
      meta: { roles: { emberimp: true, wraith: true, pet_kindle: true } },
      list: [follower],
      add(spec) { added.push(spec); return spec; },
      remove(a) { removed.push(a); },
    },
    addNpc(spec) {
      const a = { ...spec, x: spec.pos[0], z: spec.pos[1], y: 0 };
      added.push(a);
      npcs.push(a);
      ctx.actors.list.push(a);
      return a;
    },
    removeNpc(a) {
      removed.push(a && a.id);
      const i = npcs.indexOf(a);
      if (i >= 0) npcs.splice(i, 1);
      const j = ctx.actors.list.indexOf(a);
      if (j >= 0) ctx.actors.list.splice(j, 1);
    },
    npc(id) { return npcs.find((a) => a.id === id) || null; },
  };
  return ctx;
}

const START_FRIEND = [
  'Pip, Sizzle and Wick have never seen snow. Not once. Not even a picture of it.',
  'I promised I would take them, but I have to keep the vent warm. Will you?',
  'Mind them near the border. Wraiths like little lights.',
];
const START_WON = [
  'Pip, Sizzle and Wick have never seen snow. Not once. Not even a picture of it.',
  'Your guards will not let them out of Cinderhold without leave. You are the leave. Please?',
  'Mind them near the border. Wraiths like little lights.',
];
const KIDS = [
  'PIP: Is that it? Is the white stuff snow?',
  'SIZZLE: (touches it) IT HISSED AT ME.',
  'WICK: Do it again! Do it again!',
];
const PAY = ['They came back steaming and giggling. I have not heard Cinderhold this loud in years. Here. A rift shard and some cold-fire petals. Ironic, I know.'];
const LEFTOVER = ['Pip wants to go again. Pip will always want to go again.'];

const shell = mock(fresh({ hp: 100 }));
shell.musp = new Muspelheim(shell);
installSideQuests(shell);

function boot(S, x, z, kindle = false) {
  shell.S = S;
  shell.dlg = null;
  shell.opened = null;
  shell.toasts = [];
  shell.saves = 0;
  if (!shell.combat) shell.combat = mock(S).combat;
  shell.combat.spawned = [];
  shell.combat.enemies = [];
  const ctx = world(x, z);
  shell.svart.follow = kindle
    ? { on: true, id: 'kindle', sprite: ctx.follower }
    : { on: false, id: null, sprite: null };
  shell.musp.attach(ctx, 'muspelheim');
  return ctx;
}

test('quest text is the Story block and coldpetal already exists', () => {
  assert.equal(QUESTS.sq_ember_kids.title, 'Snow for Cinderhold');
  assert.equal(QUESTS.sq_ember_kids.giver, 'Kindle');
  assert.equal(QUESTS.sq_ember_kids.side, true);
  assert.equal(QUESTS.sq_ember_kids.steps[1], 'Lead Pip, Sizzle and Wick to the frost border.');
  assert.equal(QUESTS.sq_ember_kids.steps[2], 'Keep the wraiths off them. They are small, and very excited.');
  assert.equal(QUESTS.sq_ember_kids.steps[3], 'They saw snow. It hissed. They have not stopped laughing.');
  assert.equal(QUESTS.sq_copper_song.title, 'The Humming Golem');
  assert.equal(ITEMS.coldpetal.name, 'Cold-fire petal');
  assert.equal(ITEMS.rift_shard, undefined);
  assert.equal(ENEMIES.wraith.name, 'Cold-fire wraith');
  assert.equal(ENEMIES.wraith.shy, true);
  assert.equal(TALK.kindle, kindle_snow);
  assert.equal(TALK.ember_kids, ember_kids);
  assert.deepEqual(kindle_snow(fresh()).pages, START_FRIEND);
  assert.equal(kindle_snow(fresh()).choice, undefined);
  assert.deepEqual(kindle_snow(fresh({ flags: { alliance: { muspelheim: 'conquer' } } })).pages, START_WON);
});

test('start talk has no choice and sets stage 1; kids talk sets stage 2', () => {
  const S = fresh();
  const G = mock(S);
  const start = kindle_snow(S);
  assert.equal(start.choice, undefined);
  assert.deepEqual(start.pages, START_FRIEND);
  start.then(G);
  assert.equal(S.quests.sq_ember_kids, 1);
  assert.deepEqual(kindle_snow(S).pages, LEFTOVER);
  assert.equal(kindle_snow(S).then, undefined);

  const kids = ember_kids(S);
  assert.deepEqual(kids.pages, KIDS);
  assert.equal(kids.choice, undefined);
  kids.then(G);
  assert.equal(S.quests.sq_ember_kids, 2);
  assert.deepEqual(ember_kids(S).pages, ['PIP: Hi!']);
});

test('reward is one rift shard and two coldpetal, then the leftover line', () => {
  const S = fresh({ quests: { sq_ember_kids: 2 }, inv: { coldpetal: 1, tonic: 4 }, gems: { rift_shard: 2 } });
  const G = mock(S);
  const pay = kindle_snow(S);
  assert.deepEqual(pay.pages, PAY);
  pay.then(G);
  assert.equal(S.gems.rift_shard, 3);
  assert.equal(S.inv.coldpetal, 3);
  assert.equal(S.inv.tonic, 4);
  assert.equal(S.quests.sq_ember_kids, 3);
  assert.deepEqual(kindle_snow(S).pages, LEFTOVER);
  assert.equal(kindle_snow(S).then, undefined);
  assert.deepEqual(ember_kids(S).pages, ['PIP: Hi!']);

  const empty = fresh({ quests: { sq_ember_kids: 2 } });
  const g2 = mock(empty);
  kindle_snow(empty).then(g2);
  assert.equal(empty.gems.rift_shard, 1);
  assert.equal(empty.inv.coldpetal, 2);
  assert.equal(empty.quests.sq_ember_kids, 3);
});

test('save and load keeps the stage, the shard, the petals, and the wraith flag', () => {
  const S = fresh({
    flags: { alliance: { muspelheim: 'befriend' }, sq_ember_wraith: 1 },
    quests: { sq_ember_kids: 2 },
    inv: { coldpetal: 1, tonic: 2 },
    gems: { rift_shard: 4 },
    gold: 9,
  });
  const loaded = fresh(JSON.parse(JSON.stringify(snap(S))));
  assert.equal(loaded.quests.sq_ember_kids, 2);
  assert.equal(loaded.flags.sq_ember_wraith, 1);
  assert.equal(loaded.gems.rift_shard, 4);
  assert.equal(loaded.inv.tonic, 2);
  assert.deepEqual(kindle_snow(loaded).pages, PAY);
  const G = mock(loaded);
  kindle_snow(loaded).then(G);
  const again = fresh(JSON.parse(JSON.stringify(snap(loaded))));
  assert.equal(again.quests.sq_ember_kids, 3);
  assert.equal(again.gems.rift_shard, 5);
  assert.equal(again.inv.coldpetal, 3);
  assert.equal(again.inv.tonic, 2);
  assert.equal(again.gold, 9);
  assert.equal(again.flags.sq_ember_wraith, 1);
  assert.deepEqual(kindle_snow(again).pages, LEFTOVER);
  assert.equal(QUESTS.sq_ember_kids.steps[3], 'They saw snow. It hissed. They have not stopped laughing.');
});

test('Kindle companion lines, kit, and follower sprite stay as they are', () => {
  const src = readFileSync(new URL('../game/side_quests.js', import.meta.url), 'utf8');
  assert.equal(src.includes('talkable'), false);
  assert.equal(src.includes('.say'), false);
  assert.equal(src.includes('pet_kindle'), false);
  assert.equal(src.includes('KINDLE'), false);
  assert.equal(KINDLE.say.first, "I'll go first. I'm warm. You're squishy.");
  assert.equal(KINDLE.say.rude, "That one's rude. Burn it.");
  assert.equal(KINDLE.say.bead, 'Cold bead. Keep it. It\'s nice.');
  assert.equal(KINDLE.say.emberBorn, 'You smell like home.');
  assert.equal(KINDLE.say.faint, '(Kindle curls into a coal. She will be back at the waystone.)');
  assert.deepEqual(KINDLE.say, SAY_AT_IMPORT);
  assert.equal(FOLLOW_KIT.kindle.role, 'pet_kindle');
  assert.deepEqual(FOLLOW_KIT.kindle, KIT_AT_IMPORT);
  assert.equal(COMP.kindle, 'Kindle');
  assert.equal(QUESTS.mp_kindle.title, 'A Spark for Kindle');
  TALK.kindle = kindle_snow;
  assert.deepEqual(KINDLE.say, SAY_AT_IMPORT);
  assert.deepEqual(FOLLOW_KIT.kindle, KIT_AT_IMPORT);
  assert.equal(FOLLOW_KIT.kindle.role, 'pet_kindle');

  const ctx = boot(fresh(), -4.6, 4.6, true);
  shell.musp.update(0.05);
  shell.musp.prompt();
  shell.musp.interact();
  assert.equal(ctx.follower.talkable, undefined);
  assert.equal(ctx.follower.say, null);
  assert.equal(ctx.follower.role, 'pet_kindle');
  assert.equal(ctx.follower.id, 'comp_kindle');
  assert.equal(ctx.added.some((a) => a.role === 'pet_kindle' || a.id === 'comp_kindle'), false);
  assert.deepEqual(KINDLE.say, SAY_AT_IMPORT);
  assert.deepEqual(FOLLOW_KIT.kindle, KIT_AT_IMPORT);
});

test('kids stand only at stage 1, spots keep E / A, and no marker sits on kindle', () => {
  const quiet = boot(fresh(), -4.6, 4.6, false);
  assert.equal(quiet.npc('ember_kids'), null);
  assert.equal(shell.musp.prompt(), '');
  assert.equal(kindleTalkReady(shell.musp), false);
  assert.equal(shell.musp.interact(), false);

  const start = boot(fresh(), -4.6, 4.6, true);
  assert.equal(start.npc('ember_kids'), null);
  assert.equal(kindleTalkReady(shell.musp), true);
  assert.equal(shell.musp.prompt(), 'Talk to Kindle (E / A)');
  assert.equal(shell.harbor.prompt(), 'Talk to Kindle (E / A)');
  assert.equal(shell.musp.interact(), true);
  assert.equal(shell.opened.who.id, 'kindle');
  assert.equal(shell.opened.who.name, 'Kindle');
  assert.deepEqual(shell.opened.entry.pages, START_FRIEND);
  shell.opened.entry.then(shell);
  assert.equal(shell.S.quests.sq_ember_kids, 1);
  assert.equal(shell.combat.spawned.length, 0);
  shell.musp.update(0.05);
  const kid = start.npc('ember_kids');
  assert.equal(kid.role, 'emberimp');
  assert.equal(kid.id, 'ember_kids');
  assert.equal(kid.name, 'Pip, Sizzle and Wick');
  assert.equal(kid.behavior, 'idle');
  assert.equal(kid.talkable, true);
  assert.equal(kid.say, undefined);
  assert.ok(!kid.ai);
  assert.deepEqual(kid.pos, EMBER_KIDS_AT);
  assert.equal(kindleTalkReady(shell.musp), false);
  assert.equal(shell.musp.prompt(), '');
  assert.equal(shell.combat.spawned.length, 1);
  const sp = shell.combat.spawned[0];
  assert.equal(sp.poof, true);
  assert.equal(sp.sp.id, 'sq_ember_wraith');
  assert.equal(sp.sp.role, 'wraith');
  assert.equal(sp.sp.once, true);
  assert.ok(Math.hypot(sp.sp.pos[0] - EMBER_KIDS_AT[0], sp.sp.pos[1] - EMBER_KIDS_AT[1]) >= 1.2);
  assert.ok(Math.hypot(sp.sp.pos[0] - start.player.x, sp.sp.pos[1] - start.player.z) >= 0.9);
  assert.ok(shell.toasts.includes('The kids hide behind you.'));
  shell.musp.update(0.05);
  assert.equal(shell.combat.spawned.length, 1);

  ember_kids(shell.S).then(shell);
  assert.equal(shell.S.quests.sq_ember_kids, 2);
  shell.musp.update(0.05);
  assert.equal(start.npc('ember_kids'), null);
  assert.equal(shell.musp.prompt(), 'Talk to Kindle (E / A)');
  shell.opened = null;
  shell.musp.interact();
  assert.deepEqual(shell.opened.entry.pages, PAY);
  shell.opened.entry.then(shell);
  assert.equal(shell.S.quests.sq_ember_kids, 3);
  assert.equal(shell.S.gems.rift_shard, 1);
  assert.equal(shell.S.inv.coldpetal, 2);
  assert.equal(shell.musp.prompt(), 'Talk to Kindle (E / A)');
  shell.opened = null;
  shell.musp.interact();
  assert.deepEqual(shell.opened.entry.pages, LEFTOVER);
  assert.equal(shell.opened.entry.then, undefined);

  shell.dlg = { open: true };
  assert.equal(kindleTalkReady(shell.musp), false);
  assert.equal(shell.musp.prompt(), '');
  shell.dlg = null;

  const stones = boot(fresh({ quests: { mp_walk: 1 } }), 0, 4.4, true);
  assert.equal(stones.npc('ember_kids'), null);
  assert.equal(shell.musp.prompt(), "the Warden's Stones (E / A)");
  shell.opened = null;
  assert.equal(shell.musp.interact(), true);
  assert.equal(shell.opened.who.id, 'mw_hint');
  assert.equal(shell.opened.who.name, "The Warden's Stones");

  const far = boot(fresh({ quests: { sq_ember_kids: 1 } }), 8, -7, true);
  const border = far.npc('ember_kids');
  assert.equal(border.role, 'emberimp');
  assert.equal(border.id, 'ember_kids');
  shell.musp.update(0.05);
  assert.equal(shell.combat.spawned.length, 0);
  assert.equal(shell.toasts.includes('The kids hide behind you.'), false);
  far.player.x = EMBER_KIDS_AT[0];
  far.player.z = EMBER_KIDS_AT[1];
  shell.musp.update(0.05);
  assert.equal(shell.combat.spawned.length, 1);
  assert.equal(shell.S.flags.sq_ember_wraith, 1);

  const held = shell.combat;
  shell.combat = null;
  const bare = boot(fresh({ quests: { sq_ember_kids: 1 } }), -5.9, 1.8, false);
  assert.doesNotThrow(() => shell.musp.update(0.05));
  assert.equal(bare.npc('ember_kids').id, 'ember_kids');
  ember_kids(shell.S).then(shell);
  assert.equal(shell.S.quests.sq_ember_kids, 2);
  shell.combat = held;

  const later = boot(fresh({ quests: { sq_ember_kids: 2 } }), -4.6, 4.6, true);
  assert.equal(later.npc('ember_kids'), null);
  const done = boot(fresh({ quests: { sq_ember_kids: 3 } }), -4.6, 4.6, true);
  assert.equal(done.npc('ember_kids'), null);

  shell.S = fresh({ quests: { sq_ember_kids: 1 } });
  const hall = world(0, 0);
  shell.svart.follow = { on: true, id: 'kindle', sprite: hall.follower };
  shell.musp.attach(hall, 'mp_hall');
  assert.equal(hall.npc('ember_kids'), null);
  assert.equal(kindleTalkReady(shell.musp), false);

  for (const stage of [0, 1, 2, 3]) {
    const S = fresh({ quests: stage ? { sq_ember_kids: stage } : {} });
    assert.equal(markerFor('kindle', S), null);
    assert.equal(markerFor('ember_kids', S), null);
    assert.equal(markerFor('comp_kindle', S), null);
  }

  const replaced = new Muspelheim(shell);
  shell.musp = replaced;
  const ctx = boot(fresh(), -4.6, 4.6, true);
  assert.equal(ctx.npc('ember_kids'), null);
  assert.equal(shell.musp.prompt(), 'Talk to Kindle (E / A)');
  assert.equal(ctx.follower.talkable, undefined);
  assert.equal(ctx.follower.say, null);
});
