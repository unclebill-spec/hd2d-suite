// Lamps for the Steps: Lumi's night offer, four orbs, last-orb choice, reward, save/load.
// The follower is not a standing NPC. Talk is the Alfheim prompt wrap. Companion barks stay hers.
// alfheim.js imports the browser package `three`. The stub is test-only.
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
const { Lumi, LUMI_BARKS, COMPANIONS } = await import('../game/alfheim_lumi.js');
const { Alfheim } = await import('../game/alfheim.js');
const {
  installSideQuests, lumi_lamplit, ORB_SPOTS, lightOrb, orbCount, lamplitTalkReady,
} = await import('../game/side_quests.js');

const BARKS_AT_IMPORT = JSON.parse(JSON.stringify(LUMI_BARKS));
const ROLE_AT_IMPORT = COMPANIONS.lumi.role;
const TALKS_AT_IMPORT = COMPANIONS.lumi.talks;

function fresh(extra = {}) {
  return {
    flags: {}, quests: {}, found: {}, inv: {}, met: {}, gold: 0,
    ...extra,
    flags: extra.flags || {},
    quests: extra.quests || {},
    found: extra.found || {},
    inv: extra.inv || {},
    met: extra.met || {},
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
  };
  return g;
}

function snap(S) {
  return JSON.parse(JSON.stringify({
    quests: S.quests, found: S.found, flags: S.flags, inv: S.inv, gold: S.gold,
  }));
}

function stepsCtx(t, x, z) {
  const added = [];
  return {
    added,
    player: { x, z, y: 1.2, facing: 'down' },
    clock: { t },
    scene: { game: { alf: { pond: { pos: [6.4, 4.6] } } } },
    heightAt: () => 1.2,
    npc: () => null,
    collide: null,
    effects: null,
    actors: {
      meta: { roles: { lumi: true, wraith: true } },
      add(spec) { added.push(spec); return spec; },
      remove() {},
    },
  };
}

const START_PAGES = [
  'Oh. Oh no. Look at them. Five orbs, and all of them dark!',
  'Those are my cousins. Well, sort of cousins. They are light in glass, I am light in... me. We are basically family.',
  'Something drank them. A wraith, I bet. They love a free meal. Will you help me light them again?',
];
const YES = ['Yes! Touch each one and I will lend a little glow. Watch the wraith. It will not like this at all.'];
const LATER = ['Later. Right. They will just... sit in the dark. Being sad. It is fine.'];
const LAST_PAGES = ['One left! You do it. No, wait. I could do it? No. Yes? I get shy around family.'];
const LUMI_LIT = [
  '(Lumi touches the orb. It blooms neon blue, and so does she, all the way to the edges.)',
  'Oh. Oh, that felt nice. Do not tell anyone I cried. Wisps can cry. A bit. It sparkles.',
];
const HERO_LIT = ['(The last orb catches.) There! Five. Five cousins, all glowing. You are very good at this.'];
const PAY_WON = [
  'They are lit. The elves are watching from behind their shutters. They will not come out while you are here.',
  '...I know why. I am still glad we did it. Here. The Steps keep a little gold for lamplighters.',
];
const PAY_FRIEND = [
  'They are lit! Look at the Steps. Like a river of little moons.',
  'The lamplighters\' box had gold in it. And some glow seeds. Plant them somewhere dark that deserves it.',
];

const shell = mock(fresh({
  day: 0,
  flags: { alf_seen: 1, companions: { lumi: 1 }, alliance: { alfheim: 'befriend' } },
}));
shell.combat = { ctx: {}, out() { return 0; }, spawned: [], spawnEnemy(sp, poof) { this.spawned.push({ sp, poof }); return { sp }; } };
installSideQuests(shell);
shell.alfheim = new Alfheim(shell);

test('quest text is the Story block and glowseed already exists', () => {
  assert.equal(QUESTS.sq_lamplit.title, 'Lamps for the Steps');
  assert.equal(QUESTS.sq_lamplit.giver, 'Lumi');
  assert.equal(QUESTS.sq_lamplit.side, true);
  assert.equal(QUESTS.sq_lamplit.steps[1]({ found: {} }), 'A wraith drank the light from five orbs on the Glimmer Steps. Orbs lit: 0/5.');
  assert.equal(QUESTS.sq_lamplit.steps[1]({ found: { sq_orb1: 1, sq_orb3: 1 } }), 'A wraith drank the light from five orbs on the Glimmer Steps. Orbs lit: 2/5.');
  assert.equal(QUESTS.sq_lamplit.steps[2], 'One orb left. Lumi is hovering beside it, very nervous.');
  assert.equal(QUESTS.sq_lamplit.steps[3](fresh()), 'Five orbs burn neon blue. Lumi will not stop talking about it.');
  assert.equal(QUESTS.sq_lamplit.steps[3](fresh({ flags: { alliance: { alfheim: 'conquer' } } })), 'Five orbs burn. The elves shut their shutters as you pass.');
  assert.equal(QUESTS.sq_ember_kids, undefined);
  assert.equal(QUESTS.sq_copper_song.title, 'The Humming Golem');
  assert.deepEqual(ORB_SPOTS.map((s) => s.id), ['sq_orb1', 'sq_orb2', 'sq_orb3', 'sq_orb4']);
  assert.deepEqual(ORB_SPOTS.map((s) => s.pos), [[-2.6, -0.4], [2.6, -0.4], [-6.4, -3.8], [6.4, -3.8]]);
  assert.equal(ITEMS.glowseed.name, 'Glow seed');
  assert.equal(ENEMIES.wraith.name, 'Cold-fire wraith');
  assert.equal(ENEMIES.wraith.shy, true);
  assert.equal(TALK.lumi, lumi_lamplit);
  assert.deepEqual(lumi_lamplit(fresh()).pages, START_PAGES);
});

test('start choice lights the quest; Later does not', () => {
  const S = fresh({ flags: { alliance: { alfheim: 'befriend' }, companions: { lumi: 1 } } });
  const G = mock(S);
  const start = lumi_lamplit(S);
  assert.deepEqual(start.pages, START_PAGES);
  const later = start.choice.options.find((o) => o.label === 'Later, Lumi.');
  const yes = start.choice.options.find((o) => o.label === 'Let\'s light them.');
  assert.equal(later.cancel, true);
  assert.deepEqual(later.pick(G).pages, LATER);
  assert.equal(S.quests.sq_lamplit, undefined);
  assert.deepEqual(yes.pick(G).pages, YES);
  assert.equal(S.quests.sq_lamplit, 1);
  assert.equal(lumi_lamplit(S).choice, undefined);
});

test('four orbs, then both last-orb picks, then both rewards', () => {
  const base = fresh({
    flags: { alliance: { alfheim: 'befriend' }, companions: { lumi: 1 } },
    quests: { sq_lamplit: 1 },
    found: {},
  });
  const G = mock(base);
  assert.equal(lightOrb(G, 'sq_orb1'), 1);
  assert.equal(lightOrb(G, 'sq_orb2'), 2);
  assert.equal(lightOrb(G, 'sq_orb3'), 3);
  assert.equal(base.quests.sq_lamplit, 1);
  assert.equal(lumi_lamplit(base).choice, undefined);
  assert.deepEqual(lumi_lamplit(base).pages, ['Five cousins. I visit them sometimes.']);
  assert.equal(lightOrb(G, 'sq_orb4'), 4);
  assert.equal(orbCount(base), 4);
  assert.equal(base.quests.sq_lamplit, 1);
  assert.deepEqual(G.toasts.filter((t) => t.startsWith('Orb ')), ['Orb 1/5', 'Orb 2/5', 'Orb 3/5', 'Orb 4/5']);
  assert.equal(G.toasts.at(-1), 'The light pushes the wraith back.');
  assert.equal(G.combat, undefined);

  const last = lumi_lamplit(base);
  assert.deepEqual(last.pages, LAST_PAGES);
  const byLumi = last.choice.options.find((o) => o.label === 'You light it, Lumi.');
  const byHero = last.choice.options.find((o) => o.label === 'I\'ve got it.');

  const lit = fresh(snap(base));
  const gLit = mock(lit);
  assert.deepEqual(byLumi.pick(gLit).pages, LUMI_LIT);
  assert.equal(lit.flags.sq_lumi_lit, 1);
  assert.equal(lit.quests.sq_lamplit, 2);

  const hero = fresh(snap(base));
  const gHero = mock(hero);
  assert.deepEqual(byHero.pick(gHero).pages, HERO_LIT);
  assert.equal(hero.flags.sq_lumi_lit, undefined);
  assert.equal(hero.quests.sq_lamplit, 2);

  const friend = lumi_lamplit(hero);
  assert.deepEqual(friend.pages, PAY_FRIEND);
  friend.then(gHero);
  assert.equal(hero.gold, 60);
  assert.equal(hero.inv.glowseed, 2);
  assert.equal(hero.quests.sq_lamplit, 3);
  assert.deepEqual(lumi_lamplit(hero).pages, ['Five cousins. I visit them sometimes.']);

  const wonS = fresh(snap(lit));
  wonS.flags.alliance = { alfheim: 'conquer' };
  const gWon = mock(wonS);
  const won = lumi_lamplit(wonS);
  assert.deepEqual(won.pages, PAY_WON);
  won.then(gWon);
  assert.equal(wonS.gold, 60);
  assert.equal(wonS.inv.glowseed, 2);
  assert.equal(wonS.quests.sq_lamplit, 3);
  assert.equal(QUESTS.sq_lamplit.steps[3](wonS), 'Five orbs burn. The elves shut their shutters as you pass.');
  assert.deepEqual(lumi_lamplit(wonS).pages, ['I still feel a bit brighter since I lit that orb. Is that silly?']);
  assert.deepEqual(lumi_lamplit(lit).pages, PAY_FRIEND);
});

test('save and load keeps orbs, the wisp flag, gold and seeds', () => {
  const S = fresh({
    flags: { alliance: { alfheim: 'befriend' }, companions: { lumi: 1 }, sq_lumi_lit: 1 },
    quests: { sq_lamplit: 2 },
    found: { sq_orb1: 1, sq_orb2: 1, sq_orb3: 1, sq_orb4: 1 },
    inv: { glowseed: 1, tonic: 2 },
    gold: 10,
  });
  const loaded = fresh(JSON.parse(JSON.stringify(snap(S))));
  assert.equal(loaded.quests.sq_lamplit, 2);
  assert.equal(orbCount(loaded), 4);
  assert.equal(loaded.flags.sq_lumi_lit, 1);
  assert.equal(loaded.inv.tonic, 2);
  assert.deepEqual(lumi_lamplit(loaded).pages, PAY_FRIEND);
  const G = mock(loaded);
  lumi_lamplit(loaded).then(G);
  const again = fresh(JSON.parse(JSON.stringify(snap(loaded))));
  assert.equal(again.quests.sq_lamplit, 3);
  assert.equal(again.gold, 70);
  assert.equal(again.inv.glowseed, 3);
  assert.equal(again.inv.tonic, 2);
  assert.equal(QUESTS.sq_lamplit.steps[1](again), 'A wraith drank the light from five orbs on the Glimmer Steps. Orbs lit: 4/5.');
  assert.deepEqual(lumi_lamplit(again).pages, ['I still feel a bit brighter since I lit that orb. Is that silly?']);
});

test('Lumi companion barks, joined, and the follower sprite stay as they are', () => {
  const src = readFileSync(new URL('../game/side_quests.js', import.meta.url), 'utf8');
  assert.equal(src.includes('talkable'), false);
  assert.equal(src.includes('.say'), false);
  assert.deepEqual(LUMI_BARKS, BARKS_AT_IMPORT);
  assert.equal(LUMI_BARKS.night, 'Night! Finally. Days are too bright. I can\'t see myself.');
  assert.deepEqual(LUMI_BARKS.follow, ['Ting! Left, left, no, your other left.', 'I like your boots. They\'re very... stompy.']);
  assert.equal(LUMI_BARKS.pond, 'Hello, frogs! (The frogs sing back. Lumi glows a little brighter.)');
  assert.equal(LUMI_BARKS.combat, 'Bright and sharp! I\'ll light them up for you!');
  assert.equal(COMPANIONS.lumi.role, 'companion_lumi');
  assert.equal(COMPANIONS.lumi.talks, true);
  assert.equal(COMPANIONS.lumi.role, ROLE_AT_IMPORT);
  assert.equal(COMPANIONS.lumi.talks, TALKS_AT_IMPORT);
  assert.equal(TALK.lumi, lumi_lamplit);

  assert.equal(new Lumi({ S: { flags: {} } }).joined(), false);
  assert.equal(new Lumi({ S: { flags: { companions: { lumi: 1 }, alliance: { alfheim: 'conquer' } } } }).joined(), false);
  assert.equal(new Lumi({ S: { flags: { companions: { lumi: 1 }, alliance: { alfheim: 'befriend' } } } }).joined(), true);
  assert.deepEqual(LUMI_BARKS, BARKS_AT_IMPORT);

  const none = fresh({ flags: { alf_seen: 1 } });
  shell.S = none;
  const day = stepsCtx(0.5, 1.6, 4.4);
  shell.alfheim.attach(day, 'alfheim');
  assert.equal(shell.alfheim.lumi.on, false);
  assert.equal(day.added.some((a) => a.id === 'lumi'), false);
  for (const id of ['sq_orb1', 'sq_orb2', 'sq_orb3', 'sq_orb4']) {
    assert.equal(shell.alfheim.spots.find((s) => s.id === id).show(), false);
  }
  assert.equal(shell.alfheim.prompt(), '');
  assert.equal(shell.alfheim.interact(), false);
  assert.equal(markerFor('lumi', none), null);

  shell.S = fresh({
    day: 0,
    flags: { alf_seen: 1, companions: { lumi: 1 }, alliance: { alfheim: 'befriend' } },
  });
  const night = stepsCtx(0.9, 0, 0);
  shell.alfheim.attach(night, 'alfheim');
  const bodies = night.added.filter((a) => a.id === 'lumi');
  assert.equal(bodies.length, 1);
  assert.equal(bodies[0].talkable, undefined);
  assert.equal(bodies[0].say, undefined);
  assert.equal(shell.alfheim.lumi.sprite.talkable, undefined);
  assert.equal(shell.alfheim.lumi.sprite.say, undefined);
  assert.equal(shell.alfheim.lumi.on, true);
  assert.deepEqual(LUMI_BARKS, BARKS_AT_IMPORT);
  assert.equal(new Lumi(shell).joined(), true);
});

test('spots, the pond, and Lumi share E / A in the right order', () => {
  shell.S = fresh({
    day: 0,
    flags: { alf_seen: 1, companions: { lumi: 1 }, alliance: { alfheim: 'befriend' } },
    quests: {},
    found: {},
  });
  shell.opened = null;
  shell.combat.spawned = [];
  const ctx = stepsCtx(0.91, 0, 0);
  shell.alfheim.attach(ctx, 'alfheim');
  assert.equal(lamplitTalkReady(shell.alfheim), true);
  assert.equal(shell.alfheim.prompt(), 'Talk to Lumi (E / A)');
  assert.equal(shell.alfheim.interact(), true);
  assert.equal(shell.opened.who.id, 'lumi');
  assert.deepEqual(shell.opened.entry.pages, START_PAGES);
  shell.dlg = { open: true };
  assert.equal(lamplitTalkReady(shell.alfheim), false);
  assert.equal(shell.alfheim.prompt(), '');
  shell.dlg = null;

  ctx.clock.t = 0.5;
  assert.equal(shell.alfheim.prompt(), '');
  ctx.clock.t = 0.8;
  assert.equal(shell.alfheim.prompt(), '');
  ctx.clock.t = 0.25;
  assert.equal(shell.alfheim.prompt(), '');
  ctx.clock.t = 0.1;
  assert.equal(shell.alfheim.prompt(), 'Talk to Lumi (E / A)');
  shell.S.flags.alliance = {};
  assert.equal(shell.alfheim.prompt(), '');
  shell.S.flags.alliance = { alfheim: 'befriend' };

  shell.opened.entry.choice.options.find((o) => o.label === 'Let\'s light them.').pick(shell);
  assert.equal(shell.S.quests.sq_lamplit, 1);
  ctx.clock.t = 0.9;
  ctx.player.x = 0;
  ctx.player.z = 0;
  assert.equal(lamplitTalkReady(shell.alfheim), false);
  assert.equal(shell.alfheim.prompt(), '');
  for (const s of ORB_SPOTS) assert.equal(shell.alfheim.spots.find((x) => x.id === s.id).show(), true);
  ctx.clock.t = 0.5;
  for (const s of ORB_SPOTS) assert.equal(shell.alfheim.spots.find((x) => x.id === s.id).show(), false);
  ctx.clock.t = 0.9;

  ctx.player.x = 6.4;
  ctx.player.z = 4.6;
  const pond = shell.alfheim.prompt();
  assert.match(pond, /Ferrin's glow-pool/);
  assert.notEqual(pond, 'Talk to Lumi (E / A)');
  shell.opened = null;
  assert.equal(shell.alfheim.interact(), true);
  assert.equal(shell.opened.who.id, 'pond');

  ctx.player.x = -2.6;
  ctx.player.z = -0.8;
  assert.equal(shell.alfheim.prompt(), 'a dark orb, west steps (E / A)');
  assert.equal(shell.alfheim.spots.filter((s) => s.show() && Math.hypot(ctx.player.x - s.pos[0], ctx.player.z - s.pos[1]) < (s.r || 1.4)).length, 1);
  shell.opened = null;
  shell.toasts = [];
  assert.equal(shell.alfheim.interact(), true);
  assert.equal(shell.opened.who.id, 'sq_orb1');
  assert.match(shell.opened.entry.pages[0], /neon blue/);
  shell.opened.entry.then(shell);
  assert.equal(shell.S.found.sq_orb1, 1);
  assert.equal(shell.alfheim.spots.find((s) => s.id === 'sq_orb1').show(), false);
  assert.deepEqual(shell.toasts, ['Orb 1/5']);
  assert.equal(shell.combat.spawned.length, 0);

  for (const [id, x, z] of [['sq_orb2', 2.6, -0.8], ['sq_orb3', -6.4, -3.0], ['sq_orb4', 6.4, -3.0]]) {
    ctx.player.x = x;
    ctx.player.z = z;
    shell.opened = null;
    shell.alfheim.interact();
    shell.opened.entry.then(shell);
    assert.equal(shell.S.found[id], 1);
  }
  assert.equal(orbCount(shell.S), 4);
  assert.equal(shell.S.quests.sq_lamplit, 1);
  assert.equal(shell.combat.spawned.length, 1);
  const sp = shell.combat.spawned[0];
  assert.equal(sp.poof, true);
  assert.equal(sp.sp.id, 'sq_lamplit_wraith');
  assert.equal(sp.sp.role, 'wraith');
  assert.equal(sp.sp.once, true);
  assert.equal(sp.sp.def, undefined);
  assert.ok(Math.hypot(sp.sp.pos[0] - ctx.player.x, sp.sp.pos[1] - ctx.player.z) >= 0.8);
  assert.ok(Math.hypot(sp.sp.pos[0] - 6.4, sp.sp.pos[1] - (-3.8)) < 2.6);
  assert.ok(shell.toasts.includes('Orb 4/5'));
  assert.ok(shell.toasts.includes('The light pushes the wraith back.'));

  ctx.clock.t = 0.5;
  ctx.player.x = 0;
  ctx.player.z = 0;
  for (const s of ORB_SPOTS) assert.equal(shell.alfheim.spots.find((x) => x.id === s.id).show(), false);
  assert.equal(shell.alfheim.prompt(), 'Talk to Lumi (E / A)');
  shell.opened = null;
  shell.alfheim.interact();
  assert.deepEqual(shell.opened.entry.pages, LAST_PAGES);
  assert.equal(markerFor('lumi', shell.S), null);

  const court = stepsCtx(0.1, 0, 0);
  shell.alfheim.attach(court, 'lumen_court');
  assert.equal(shell.alfheim.spots.some((s) => s.id && String(s.id).startsWith('sq_orb')), false);
  assert.equal(shell.alfheim.prompt(), '');
  assert.equal(lamplitTalkReady(shell.alfheim), false);
});
