// Pause menu. Reuses the Options card (#opts), the hero screen (setHeroUI) and the save slots.
// The game freezes through G.pause (same places as G.opts) plus the sim time scale.

const TABS = 5;

const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

export function attachPause(G) {
  const root = document.getElementById('pause');
  const optsEl = document.getElementById('opts');
  if (!root || !optsEl) return;
  const optsHome = { parent: optsEl.parentNode, next: optsEl.nextSibling };
  let tab = 0;
  let focus = 0;
  let savedScale = 1;

  function canOpen() {
    if (G.title || G.busy || G.dlg || G.log || G.opts || G.heroUI || G.shop || G.picking || G.asking || G.downed) return false;
    if (G.intro && G.intro.active) return false;
    if (G.wheel && G.wheel.state && G.wheel.state().open) return false;
    return true;
  }

  function parkOpts() {
    const pane = document.getElementById('pauseOpts');
    if (!pane) return;
    pane.appendChild(optsEl);
    optsEl.hidden = false;
    optsEl.classList.add('parked');
  }
  function unparkOpts() {
    optsEl.classList.remove('parked');
    const { parent, next } = optsHome;
    if (parent) {
      if (next && next.parentNode === parent) parent.insertBefore(optsEl, next);
      else parent.appendChild(optsEl);
    }
    optsEl.hidden = true;
  }

  function freeze() {
    const ctx = G.ctx;
    if (ctx && ctx.timeScale) { const s = ctx.timeScale(); savedScale = s > 0 ? s : 1; }
    if (ctx && ctx.setTimeScale) ctx.setTimeScale(0);
  }
  function thaw() {
    if (G.ctx && G.ctx.setTimeScale) G.ctx.setTimeScale(savedScale || 1);
  }

  function focusables() {
    const out = [];
    const pane = root.querySelector('.pane:not([hidden])');
    const nodes = [];
    if (pane) pane.querySelectorAll('button').forEach((b) => nodes.push(b));
    root.querySelectorAll('.head button, #pauseFoot button').forEach((b) => nodes.push(b));
    for (const b of nodes) {
      if (b.disabled || b.hidden || b.closest('[hidden]')) continue;
      if (!b.offsetParent) continue;   // display:none (the parked options header)
      out.push(b);
    }
    return out;
  }
  function paintFocus() {
    root.querySelectorAll('.pf').forEach((el) => el.classList.remove('pf'));
    const list = focusables();
    if (!list.length) return;
    if (focus < 0) focus = list.length - 1;
    if (focus >= list.length) focus = 0;
    list[focus].classList.add('pf');
    try { list[focus].scrollIntoView({ block: 'nearest' }); } catch (e) { /* old webview */ }
  }
  function pressFocus() {
    const list = focusables();
    const el = list[focus];
    if (el) el.click();
  }

  function fillChar() {
    const pane = document.getElementById('pauseChar'); if (!pane) return;
    const S = G.S || {}, C = G.combat, PR = G.PR;
    const hp = Math.ceil(S.hp ?? (C && C.maxHp ? C.maxHp() : 0));
    const max = C && C.maxHp ? C.maxHp() : hp;
    const st = C ? Math.ceil(C.st || 0) : 0;
    const maxSt = C && C.maxSt ? C.maxSt() : st;
    const stats = (PR && PR.STATS && S.stats) ? PR.STATS.map((stt) => `${esc(stt.name)} ${S.stats[stt.id] ?? 0}`).join(' · ') : '';
    const inv = S.inv || {};
    const bits = Object.keys(inv).filter((id) => inv[id] > 0).slice(0, 8).map((id) => {
      const nm = (G.ITEMS && G.ITEMS[id] && G.ITEMS[id].name) || id;
      return `${esc(nm)} ×${inv[id]}`;
    });
    const bagN = (S.bag || []).length;
    pane.innerHTML = `<h4>Character</h4>
      <p class="sum"><b>Lv ${esc(S.lv || 1)}</b> · HP ${hp}/${max} · stamina ${st}/${maxSt} · gold ${S.gold || 0}</p>
      ${stats ? `<p class="sum">${stats}</p>` : ''}
      <p class="sum">Gear in the bag: ${bagN}${(S.bag || []).slice(0, 4).map((it) => it && it.name ? ` · ${esc(it.name)}` : '').join('')}</p>
      <p class="sum">${bits.length ? bits.join(' · ') : 'Pack is empty.'}</p>
      <div class="rowbtns"><button class="wbtn sm" data-act="hero">Open hero screen</button><button class="wbtn sm" data-act="gear">Gear + bag</button></div>`;
  }
  function fillSpells() {
    const pane = document.getElementById('pauseSpells'); if (!pane) return;
    const S = G.S || {};
    let sl = Array.isArray(S.slots) ? S.slots.slice(0, 4) : (G.slots ? G.slots().slice(0, 4) : []);
    while (sl.length < 4) sl.push(null);
    const name = (id) => (id && G.spellName ? esc(G.spellName(id)) : '— empty —');
    const known = G.knownSpells ? G.knownSpells() : (S.spells || []);
    const tree = (G.PR && G.PR.TREES && G.PR.TREES[S.cls]) || [];
    const learned = tree.filter((n) => S.skills && S.skills[n.id]);
    pane.innerHTML = `<h4>Spells &amp; Skills</h4>
      <p class="sum">${[0, 1, 2, 3].map((i) => `<b>Slot ${i + 1}</b> ${name(sl[i])}`).join('<br>')}</p>
      <p class="sum">Known: ${known.length ? known.map((id) => name(id)).join(' · ') : 'none yet'}</p>
      <p class="sum">Skills: ${learned.length ? learned.map((n) => esc(n.name)).join(' · ') : 'none yet'}</p>
      <div class="rowbtns"><button class="wbtn sm" data-act="spells">Spellbook</button><button class="wbtn sm" data-act="skills">Skills</button></div>`;
  }
  function fillSave() {
    const pane = document.getElementById('pauseSave'); if (!pane) return;
    const slots = [1, 2, 3].map((n) => {
      const info = G.slotInfo ? G.slotInfo(n) : null;
      const label = info ? `Load slot ${n}: ${esc(info.hero)} Lv ${esc(info.lv)}${n === G.slot ? ' · last' : ''}` : `Slot ${n}: empty`;
      return `<button class="wbtn sm" data-act="loadslot" data-slot="${n}">${label}</button>`;
    }).join('');
    pane.innerHTML = `<h4>Save / Load / Quit</h4>
      <div class="rowbtns">
        <button class="wbtn sm" data-act="save">Save now</button>
        <button class="wbtn sm" data-act="loadlast">Load last save</button>
        ${slots}
        <button class="wbtn sm" data-act="quit">Quit to title</button>
      </div>
      <p class="sum">Load and quit ask first. Save writes the slot you are playing.</p>`;
  }

  function setTab(i) {
    tab = ((i % TABS) + TABS) % TABS;
    root.querySelectorAll('#pauseTabs button').forEach((b, k) => b.classList.toggle('on', k === tab));
    root.querySelectorAll('.pane').forEach((p, k) => { p.hidden = k !== tab; });
    if (tab === 2) fillChar();
    if (tab === 3) fillSpells();
    if (tab === 4) fillSave();
    focus = 0;
    paintFocus();
  }

  function showPicker() {
    // a v1 save has no class: cont() opens the hero picker, which lives inside the title screen
    const ts = document.getElementById('titlescreen');
    if (ts) ts.hidden = false;
  }
  function openHero(tabN) {
    setPause(false);
    if (tabN != null && G.hui) { G.hui.tab = tabN; G.hui.i = 0; }
    if (G.setHeroUI) G.setHeroUI(true);
  }
  function loadSlot(n) {
    const s = G.readSave ? G.readSave(n) : null;
    if (!s) { if (G.toast) G.toast('That slot is empty.'); return; }
    if (!window.confirm('Load this save? Progress since the last save will be lost.')) return;
    G.slot = n;
    try { localStorage.setItem('hearthmoor-lastslot', String(n)); } catch (e) { /* private mode */ }
    setPause(false);
    if (!s.cls && G.cont) { showPicker(); G.cont(); return; }
    if (G.resume) G.resume(s);
  }
  function act(name, btn) {
    if (name === 'resume') setPause(false);
    else if (name === 'log') { setPause(false); if (G.setLog) G.setLog(true); }
    else if (name === 'hero') openHero(0);
    else if (name === 'gear') openHero(3);
    else if (name === 'spells') openHero(2);
    else if (name === 'skills') openHero(1);
    else if (name === 'save') { if (G.save) G.save(true); }
    else if (name === 'loadlast') {
      const s = G.readSave ? G.readSave() : null;
      if (!s) { if (G.toast) G.toast('No save in this slot.'); return; }
      if (!window.confirm('Load the last save? Progress since then will be lost.')) return;
      setPause(false);
      if (!s.cls) showPicker();
      if (G.cont) G.cont();
    } else if (name === 'loadslot') loadSlot(+(btn && btn.dataset.slot));
    else if (name === 'quit') {
      if (!window.confirm('Save and quit to the title?')) return;
      if (G.save) G.save(true);
      setPause(false);
      location.reload();
    }
  }

  function setPause(open) {
    open = !!open;
    if (open === !!G.pause) { if (open) { setTab(tab); } return; }
    if (open && !canOpen()) return;
    if (open && G.opts && G.setOpts) G.setOpts(false);
    G.pause = open;
    root.hidden = !open;
    const chip = document.getElementById('btnPauseMenu');
    if (chip) chip.classList.toggle('on', open);
    if (open) {
      parkOpts();
      setTab(tab);
      freeze();
    } else {
      unparkOpts();
      thaw();
    }
  }

  function pausePad(name) {
    if (name === 'select') return false;
    if (name === 'y') { openHero(null); return true; }
    if (name === 'lb' || name === 'left') { setTab(tab - 1); return true; }
    if (name === 'rb' || name === 'right') { setTab(tab + 1); return true; }
    if (name === 'up') { focus -= 1; paintFocus(); return true; }
    if (name === 'down') { focus += 1; paintFocus(); return true; }
    if (name === 'a') { pressFocus(); return true; }
    if (name === 'b' || name === 'start') { setPause(false); return true; }
    return true;
  }
  function pauseKey(k) {
    if (k === 'escape') setPause(false);
    else if (k === 'arrowleft') setTab(tab - 1);
    else if (k === 'arrowright') setTab(tab + 1);
    else if (k === 'arrowup') { focus -= 1; paintFocus(); }
    else if (k === 'arrowdown') { focus += 1; paintFocus(); }
    else if (k === 'enter' || k === ' ') pressFocus();
  }

  root.addEventListener('pointerdown', (e) => { if (e.target === root) setPause(false); });
  root.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest('button');
    if (!b || !root.contains(b)) return;
    const tabs = [...root.querySelectorAll('#pauseTabs button')];
    const ti = tabs.indexOf(b);
    if (ti >= 0) setTab(ti);
    if (b.dataset.act) act(b.dataset.act, b);
    const list = focusables();
    const fi = list.indexOf(b);
    if (fi >= 0) { focus = fi; paintFocus(); }
  });

  G.setPause = setPause;
  G.pausePad = pausePad;
  G.pauseKey = pauseKey;
}
