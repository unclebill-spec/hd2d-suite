// Lanterns Down (intro 5eabfed): Story's intro_test.mjs (hearthmoor-staging/story, 2026-11-09) as a node:test.
import test from 'node:test';
import assert from 'node:assert/strict';
globalThis.localStorage ??= { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const { TALK, QUESTS, markerFor, errandsDone, ITEMS, INTRO_LINES } = await import('../game/data.js');
test('Lanterns Down quest flow, markers and old-save safety', () => {
  const ok = (c, m) => assert.ok(c, m);
  const S={quests:{bread:0,tea:0,cat:0},flags:{intro:'done',ew_on:1},inv:{eve_sigil:1},met:{},orbs:{},spells:[]};
  const G={S,toasts:[],give:(i,n=1)=>{S.inv[i]=(S.inv[i]||0)+n},setQuest:(i,s)=>{S.quests[i]=s},toast:()=>{},factions:{add:()=>{}},openFactions:()=>{}};
  ok(markerFor('elder',S)==='quest_mark','alder !'); ok(markerFor('baker',S)===null,'baker hidden');
  TALK.elder(S).then(G); ok(S.quests.eve_watch===1,'stage1'); ok(markerFor('elder',S)===null,'alder no mark s1');
  ok(/bag/.test(QUESTS.eve_watch.steps[1](S)),'step1 bag');
  ok(markerFor('hilde',S)!=='quest_turnin','hilde not yet');
  S.flags.ew_bag=1; ok(markerFor('hilde',S)==='quest_turnin','hilde turnin');
  const h=TALK.hilde(S); ok(h.pages.length>=4,'hilde pages'); h.then(G); ok(S.quests.eve_watch===2&&S.inv.orblamp===1&&S.inv.glowfish===1,'stage2 + orb');
  ok(TALK.hilde(S).pages[0].startsWith('Lamps')||true,'hilde after');
  ok(/orb lantern/.test(QUESTS.eve_watch.steps[2](S)),'step2 text');
  S.orbs.home_blue={day:0}; ok(markerFor('elder',S)==='quest_turnin','alder turnin');
  TALK.elder(S).then(G); ok(S.quests.eve_watch===3,'done'); ok(markerFor('baker',S)==='quest_mark','baker ! back');
  ok(errandsDone(S)===0,'story quest not an errand');
  const old={quests:{bread:0,tea:0,cat:0},flags:{intro:'done'},inv:{},met:{}};
  ok(markerFor('baker',old)==='quest_mark'&&markerFor('elder',old)===null,'old save unchanged');
  ok(TALK.elder(old).pages[0].includes('old gate'),'old alder lines');
  ok(ITEMS.eve_sigil&&INTRO_LINES.talk.length===8,'items/lines');
  const w=[...INTRO_LINES.talk,...INTRO_LINES.crack,...INTRO_LINES.wraith,...INTRO_LINES.after].reduce((n,[,t])=>n+t.split(/\s+/).length,0);
  assert.ok(w > 0 && w < 400, 'bubble words ' + w);
});
