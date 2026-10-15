// [SVARTALFHEIM] The Thane's alliance choice and the quests that hang off it (story 3.1-3.7, 5.2, 5.4, 5.7), on the lead's
// decisions: befriend vs conquer is the player's choice, rival locks mirror (befriend Alfheim first = Svartalfheim locked, and
// the other way round), a locked player may take the contract. Quest text is the story's own.
// Built: the choice + locks + openers + idle lines, Trial of the Anvil (ring-timing beat on the Great Anvil), Giant Footprints /
//   The Banked Fire turn-ins + forge-core seams + Dagna's forging scene (-> Forge-Seal + Lesser Heart), Hired Hammer (contract)
//   end to end, The Clockwork Deep quest (stage 1 text; cogs / flue not built yet).
// Not built: Giant Footprints' clue scenes (Jotunheim areas), The Forge Claim's watch posts + Ilvar duel, the flue thaw, Bifrost's sv_gate.
import { QUESTS, ITEMS, TALK } from './data.js';
import { MERIT } from './factions.js';
import { lockRival, moodUp } from './alfheim.js';

const flags = (S) => (S.flags = S.flags || {});
const F = (S) => S.flags || {};
const ally = (S) => (flags(S).alliance = flags(S).alliance || {});
export const SV = (S) => ((S.flags || {}).alliance || {}).svartalfheim;
export const locked = (S) => ((S.flags || {}).rivals || {}).svartalfheim === 'locked';
const mood = (S) => ((S.flags || {}).realm_mood || {}).svartalfheim || 0;
const found = (S, ids) => ids.filter((k) => (S.found || {})[k]).length;
const gold = (G, n) => { G.S.gold = (G.S.gold || 0) + n; G.toast(`+${n} gold`, 1.8); G.drawBag && G.drawBag(); };
const q = (S, k) => (S.quests || {})[k] || 0;
const met = (k) => (G) => { G.S.met = { ...(G.S.met || {}), [k]: 1 }; };

Object.assign(ITEMS, { speaktube: { name: 'Speaking-tube badge', px: 'glowseed', about: 'Kesh\'s brass badge. A tube runs down the Deep, and he talks through it. Constantly.' } });

Object.assign(QUESTS, {
  sv_trial: { title: 'Trial of the Anvil', giver: 'Forge-Thane Ragna Copperbraid', story: true, steps: {
    1: (S) => { const n = F(S).st_hits || 0; return n < 3 ? `Strike the Great Anvil true, three times, while Dagna judges (E / A on the glow). ${n}/3` : 'Hear Dagna\'s verdict.'; },
    2: 'Tell the Thane what Dagna said.',
    3: 'Anvildeep will hear you out. Dagna says your arm is \'not bad, for a Midgarder\'.' } },
  sv_name: { title: 'Giant Footprints', giver: 'Forge-Thane Ragna Copperbraid', story: true, steps: {
    1: (S) => { const f = F(S);
      if (!f.sn_prints) return 'Look at the giant footprints in the Heart Vault.';
      if (!f.sn_lock) return 'Ask Sereth Gloamweave to read the frost on the vault lock with her rune-lens.';
      if (!f.sn_mould) return 'Search the slag pits in the Amethyst Mines. Kesh says something odd turned up there.';
      return 'Bring the boot mould to Sereth\'s rune-lens.'; },
    2: 'Tell the Thane what the lens shows.',
    3: 'The giants never came. Someone cold wore giant boots and laid a false trail north. The Heart is still somewhere close.' } },
  sv_kindle: { title: 'The Banked Fire', giver: 'Dagna Coalbeard', story: true, steps: {
    1: (S) => { const n = found(S, ['fc_1', 'fc_2', 'fc_3']); return n < 3 ? `Dig three forge-cores from the Amethyst Mines' ember seams. ${n}/3` : 'Bring the forge-cores to Dagna\'s side forge.'; },
    2: 'Watch Dagna forge the Lesser Heart, then take it to the Thane.',
    3: 'The Lesser Heart beats in a copper cage. It won\'t last forever, but it\'ll hold a demon. Dagna\'s coming with you.' } },
  sv_take: { title: 'The Forge Claim', giver: 'Forge-Thane Ragna Copperbraid', story: true, steps: {
    1: (S) => { const f = F(S), n = found(S, ['fk_p1', 'fk_p2', 'fk_p3']);
      if (n < 3) return `Break the Hushed's watch posts around the Great Forge. ${n}/3`;
      if (!f.fk_ilvar) return 'Captain Ilvar Hushblade carries the Forge-Seal. Take it from him.';
      return 'Open the Deep\'s lift with the Forge-Seal.'; },
    2: 'Open the Deep\'s lift with the Forge-Seal.',
    3: 'The lift is yours. Below it lies the Clockwork Deep, and the fire that feeds Anvildeep.' } },
  sv_hire: { title: 'Hired Hammer', giver: 'Gatewright Halvard Ness', story: true, steps: {
    1: (S) => { const f = F(S);
      if (!f.sh_terms) return 'Hear the Thane\'s terms. She won\'t ally with an elf-friend, but she\'ll pay one.';
      if (!f.sh_kesh) return 'Find Kesh, the mine-runner the Thane hired as your guide, on Copper Row.';
      return 'Take the Forge-Seal and the Thane\'s Lesser Heart down the Deep\'s lift.'; },
    2: 'Collect your pay from the Thane.',
    3: 'The demon\'s bound and you\'ve been paid. Anvildeep owes you nothing, and says so.' } },
  clockdeep: { title: 'The Clockwork Deep', giver: 'Forge-Thane Ragna Copperbraid', story: true, steps: {
    1: (S) => { const f = F(S), n = found(S, ['cd_cog1', 'cd_cog2', 'cd_cog3']);
      if (n < 3) return `Restart the Deep's three drive cogs (gear puzzles). ${n}/3`;
      if (!f.cd_boss) return 'Descend to the Binding Forge. Something is pulling at its chains.';
      if (!f.cd_bound && !f.cd_taken) return SV(S) === 'conquer' ? 'Gorrak\'s fire is failing. Search the Binding Forge.' : 'Set the Lesser Heart in the Binding Forge (E / A).';
      return 'Something glows under the rime in the flue. Thaw it (a spell) and take it.'; },
    2: (S) => (SV(S) === 'conquer' ? 'Leave Svartalfheim with the Anvil-Heart.' : 'Bring the Anvil-Heart home to the Thane.'),
    3: (S) => (SV(S) === 'conquer' ? 'The Anvil-Heart is yours. Anvildeep\'s forges are going cold, one by one.'
      : SV(S) === 'befriend' ? 'The Heart is home, Gorrak is bound and the Great Forge roars. Anvildeep calls you friend.' : 'Gorrak is bound again. Anvildeep paid you, and showed you the door.') } },
});

// ---------------------------------------------------------------- the Thane (5.2)
const choiceEntry = (S) => {
  const pages = [];
  if (locked(S)) pages.push('Brokk tells me you\'re the elves\' friend. Bold, coming here.');
  else if (mood(S) >= 1) pages.push('Brokk tells me you put the light-ears in their place. Sit. Have some ale. Then we talk.');
  pages.push('A Midgarder in my hall. Sit, or stand. Don\'t touch the anvil.',
    'Our Heart is stolen. The giants walked it out of my vault on midsummer night. My forge is cooling. My city shakes.',
    'So, Midgarder. Will you help Anvildeep, or are you here to pick our bones like everyone else?');
  if (S.cls === 'cinderknight') pages.splice(pages.length - 1, 0, 'Ember-blood. You\'ll feel the Deep before you see it. So will what\'s down there.');
  const befriend = (pre) => (G) => { ally(G.S).svartalfheim = 'befriend'; G.toast('Svartalfheim: befriended', 2.2); lockRival(G.S, 'alfheim');
    if (mood(G.S) >= 1) { G.setQuest('sv_trial', 3); G.factions.add('embassy', MERIT.sv_trial, 'sv_trial'); G.setQuest('sv_name', 1); } else G.setQuest('sv_trial', 1);
    return { pages: [...(pre ? [pre] : []), 'Then prove your arm first. Dagna will judge. She judges everyone. She judged me once. I lost.', '(Svartalfheim is your friend now. Its rival, Alfheim, will not stand with you as well.)'] }; };
  const opts = [];
  if (S.cls === 'seer') opts.push({ label: 'Your vault was opened by frost, not giants. I\'ve seen the hand.', pick: befriend('...Frost? Hm. My grandmother said the old ones had a word for folk like you. \'Annoying.\' Go on.') });
  opts.push(locked(S) ? { label: '(Locked. You stand with Alfheim.)', pick: () => ({ pages: ['(Locked. You stand with Alfheim.)'] }) }
                      : { label: 'I\'ll help. Let me find your Heart.', pick: befriend() },
    { label: 'Anvildeep will answer for the Temple tongs.', pick: (G) => { ally(G.S).svartalfheim = 'conquer'; G.toast('Svartalfheim: conquered', 2.2); G.setQuest('sv_take', 1); moodUp(G.S, 'alfheim');
        return { pages: ['...Tongs. You come for my fire over tongs. Then you\'ll meet the Hushed before you meet the Deep.', '(Svartalfheim stands against you now. The dwarves will remember. They write everything down.)'] }; } });
  if (locked(S)) opts.push({ label: 'Then hire me.', pick: (G) => { flags(G.S).sv_contract = 1; G.setQuest('sv_hire', 1); G.setQuest('clockdeep', 1);
      return { pages: ['An elf-friend, for hire. Ha. Fine. Gold\'s gold, and my Deep is waking.', 'Here\'s the seal, and a Lesser Heart my smiths forged. Kesh will guide you. Don\'t come back for tea.'],
               then: (G2) => { G2.give('forge_seal', 1); G2.give('lesser_heart', 1); flags(G2.S).sh_terms = 1; } }; } });
  opts.push({ label: 'I\'m only passing through.', cancel: true, pick: () => ({ pages: ['Then pass quickly. The floor\'s been known to move.'] }) });
  return { pages, choice: { id: 'alliance_svartalfheim', options: opts } };
};
const say1 = (line, then) => ({ pages: [line], then });
const thane = (S) => {
  const f = F(S), a = SV(S);
  if (!a && !f.sv_contract) return choiceEntry(S);
  const night = false;
  if (a === 'befriend') {
    if (q(S, 'sv_trial') === 2) return { pages: ['Dagna says your arm is not bad. From Dagna, that is a parade.', 'Anvildeep will hear you out.'], then: (G) => { G.setQuest('sv_trial', 3); G.factions.add('embassy', MERIT.sv_trial, 'sv_trial'); gold(G, 20); flags(G.S).sv_trusted = 1; G.setQuest('sv_name', 1); } };
    if (q(S, 'sv_name') === 2) return { pages: ['Frost-iron boots. Little straps. So my vault was robbed by someone who wanted a war.', 'And I nearly gave them one. Put down the spears, all of you! Make pans. We\'ll need pans for the apology feast.',
        'And if the trail north was a lie, my Heart\'s still under this mountain somewhere. First, the Deep. Talk to Dagna.'],
      then: (G) => { G.setQuest('sv_name', 3); G.factions.add('embassy', MERIT.sv_name, 'sv_name'); gold(G, 40); const ff = flags(G.S); ff.sv_cleared = 1; ff.sv_decoy = 1;
        G.S.evidence = { ...(G.S.evidence || {}), svartalfheim: 'boot_mould' }; if ((G.S.inv || {}).orri_letter) G.factions.add('embassy', MERIT.orri, 'orri'); G.setQuest('sv_kindle', 1); } };
    if (q(S, 'sv_kindle') === 2) return { pages: ['A Lesser Heart. Dagna, you clever, stubborn thing. It\'ll hold him a while.', 'Gorrak Ironmaw. Our oldest shame. A demon the first smiths bound in iron to keep our forge lit.',
        'Without the Heart the binding cools, and he wakes. Here\'s the Forge-Seal. Bind him again. Don\'t let him talk you round.'],
      then: (G) => { G.setQuest('sv_kindle', 3); G.factions.add('embassy', MERIT.sv_kindle, 'sv_kindle'); gold(G, 60); G.give('forge_seal', 1); G.setQuest('clockdeep', 1); flags(G.S).companions = { ...(flags(G.S).companions || {}), dagna: 1 }; } };
    return say1(f.cd_bound ? 'He watches the festival from the forge mouth now. Gorrak. Grumbling. I find I don\'t mind.' : night ? 'Night shift.' : 'The forge breathes. When it breathes, I breathe. Simple folk, dwarves.');
  }
  if (a === 'conquer') return say1(f.cd_taken ? 'You took his fire. Look around. Every cold chimney is yours.' : 'Say it and go. The forges can\'t hear you. They\'ve gone quiet.');
  if (f.sv_contract) {
    if (q(S, 'sv_hire') === 2) return { pages: ['The demon\'s bound. The Deep is quiet. Here is your coin. Count it.', 'You\'ve been paid. Don\'t take it personally. We remember who your friends are.'],
      then: (G) => { G.setQuest('sv_hire', 3); G.factions.add('gate', MERIT.contract, 'contract'); gold(G, 250); flags(G.S).sv_resolved = 'contract'; G.setQuest('clockdeep', 3); } };
    return say1(q(S, 'sv_hire') === 3 ? 'You\'ve been paid. Don\'t take it personally. We remember who your friends are.' : 'The Deep is down the lift behind the Great Forge. Kesh will walk you in. Try to come back.');
  }
  return say1('Still deciding? The mountain isn\'t. It shakes either way.');
};

// ---------------------------------------------------------------- Dagna (5.4) and Kesh (5.7)
const dagna = (S) => {
  const f = F(S), a = SV(S);
  if (a === 'befriend' && q(S, 'sv_trial') === 1) return (f.st_hits || 0) >= 3
    ? { pages: ['Three true. Your arm\'s not bad, for a Midgarder. Tell the Thane I said so. She won\'t believe it.'], then: (G) => G.setQuest('sv_trial', 2) }
    : say1('Strike the Great Anvil when the glow is smallest. The anvil talks. Listen.');
  if (a === 'befriend' && q(S, 'sv_kindle') === 1) {
    if (found(S, ['fc_1', 'fc_2', 'fc_3']) >= 3) return { pages: ['(Dagna hammers the three cores into one. Sparks fly up like stars. The lump begins to beat.)', 'There. A Lesser Heart. Ugly. It works. I\'m coming with you. Somebody has to hold the hammer properly.'],
      then: (G) => { G.setQuest('sv_kindle', 2); G.give('lesser_heart', 1); if ((G.S.inv || {}).forge_core) G.take('forge_core', G.S.inv.forge_core); } };
    return { pages: ['The Heart\'s lost somewhere. Fine. I can\'t make a new one. But I can make a little one. Enough to hold him.', 'I need forge-cores. Three. The mines have ember seams, deep down. Bring me three and I\'ll do the rest.'] };
  }
  if (a === 'befriend' && q(S, 'sv_kindle') === 2) return say1('Take the Heart to the Thane. Hold it like an egg. A hot, angry egg.');
  return say1('Anvildeep\'s best smith. Also its rudest. Don\'t touch the hammer.');
};
const kesh = (S) => {
  const f = F(S), a = SV(S);
  if (f.sv_contract && f.sh_terms && !f.sh_kesh) return { pages: ['I\'m Kesh! The Thane hired me to walk you down. Here, a speaking-tube badge. I talk, you groan. It works.'], then: (G) => { flags(G.S).sh_kesh = 1; G.give('speaktube', 1); } };
  const first = !(S.met || {}).kesh;
  if (a === 'conquer') return say1('The carts don\'t run anymore. Nothing runs. The forge went out. Did you do that?');
  return { pages: [first ? 'I\'m Kesh! I run the carts. Well, the carts run. I hang on. Want a ride? It\'s free. Mostly.' : q(S, 'sv_name') === 1 ? 'Something weird in the slag pits. Big iron shoes. I didn\'t touch them. Much.' : 'Cave orbs follow you if you stand still. I stood still for an hour once. I had nine.'], then: met('kesh') };
};
Object.assign(TALK, { thane, dagna, kesh });

// ---------------------------------------------------------------- spots (the Great Anvil's ring beat, the ember seams) + QA
export const SEAMS = [['fc_1', [-8.0, 2.4]], ['fc_2', [7.4, -4.0]], ['fc_3', [3.0, -7.6]]];
export const ANVIL = [0.0, -3.2];
export class SvStory {
  constructor(sv) { this.sv = sv; this.G = sv.G; this.t = 0; this.t0 = 0; this.auto = false; }
  get ctx() { return this.sv.ctx; }
  attach(area) {
    const sv = this.sv, G = this.G, S = G.S;
    if (area === 'forge_hall') sv.spot({ pos: ANVIL, r: 1.9, label: 'strike the Great Anvil (E / A)', show: () => SV(S) === 'befriend' && q(S, 'sv_trial') === 1 && (F(S).st_hits || 0) < 3, act: () => this.strike() });
    if (area === 'glowmines') for (const [id, pos] of SEAMS) sv.spot({ pos, r: 1.8, label: 'dig a forge-core from the ember seam (E / A)', show: () => q(S, 'sv_kindle') === 1 && !(S.found || {})[id], act: () => this.core(id) });
    this.auto = (G.qs || new URLSearchParams(location.search)).get('anvil') === 'auto';
  }
  strike() {
    const G = this.G, f = flags(G.S), ph = (this.t - this.t0) % 2.0, hit = this.auto || (ph >= 1.4 && ph <= 1.95);
    if (hit) { f.st_hits = (f.st_hits || 0) + 1; G.toast(['Dagna: "Hm. Not bad."', 'Dagna: "That one sang. Do it again."', 'Dagna: "Three true."'][Math.min(2, f.st_hits - 1)] + ` (${f.st_hits}/3)`, 2.2); const c = this.ctx; if (c && c.effects) c.effects.spawn('ember_pop', ANVIL[0], c.heightAt(...[ANVIL[0], ANVIL[1]]) + 0.6, ANVIL[1]); }
    else G.toast(['Dagna: "You hit it like you owe it money."', 'Dagna: "Wait for the glow. The anvil talks. Listen."'][Math.floor(this.t) % 2], 2.2);
  }
  core(id) { const G = this.G; G.S.found = { ...(G.S.found || {}), [id]: 1 }; G.give('forge_core', 1); G.toast(`Forge-core ${found(G.S, ['fc_1', 'fc_2', 'fc_3'])}/3`, 1.8); }
  update(dt, area) {
    const c = this.ctx; this.t += dt;
    if (area === 'forge_hall' && c && c.effects && SV(this.G.S) === 'befriend' && q(this.G.S, 'sv_trial') === 1 && (F(this.G.S).st_hits || 0) < 3 && Math.hypot(c.player.x - ANVIL[0], c.player.z - ANVIL[1]) < 6) {
      const ph = (this.t - this.t0) % 2.0;
      if (ph < dt) c.effects.spawn('rune_circle', ANVIL[0], c.heightAt(ANVIL[0], ANVIL[1]) + 0.05, ANVIL[1]);   // the glow ring pulses every 2 s; true strike = E / A as it shrinks (1.4-1.95 s)
    }
  }
  qaPreset(qv) {   // ?svq=befriend|conquer|hire|kindle
    const S = this.G.S, f = flags(S); S.found = S.found || {}; S.quests = S.quests || {};
    if (qv === 'befriend') { ally(S).svartalfheim = 'befriend'; lockRival(S, 'alfheim'); S.quests.sv_trial = 1; }
    if (qv === 'kindle') { ally(S).svartalfheim = 'befriend'; lockRival(S, 'alfheim'); S.quests.sv_trial = 3; S.quests.sv_name = 3; S.quests.sv_kindle = 1; f.sv_cleared = 1; }
    if (qv === 'conquer') { ally(S).svartalfheim = 'conquer'; S.quests.sv_take = 1; }
    if (qv === 'hire') { lockRival(S, 'svartalfheim'); }
  }
}
