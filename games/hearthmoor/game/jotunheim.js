// [JOTUNHEIM] STUB. Registers the Jotunheim realm with the game (G.jot) so the real module can fill it in later. Story:
// /workspace/hearthmoor-staging/story/jotunheim.md; plan and status: JOTUNHEIM_PROGRESS.md. Nothing here changes any existing area or
// behaviour: no areas are built yet (hold until /workspace/hearthmoor-staging/art/jotunheim/READY.txt exists), so AREAS_JOT stays empty.
// To go live: build the specs (areas/src/<id>.json), move the ids from JOT_PLANNED into AREAS_JOT / AREA_NAMES_JOT, then fill in
// ENEMIES / XP / MERIT / QUESTS / TALK / MARKER_HOOKS / ITEMS / SHOPS / WAYS / GATES (the Bifrost arch moves from `sealed` to `portals`).
export const JOT_PLANNED = {   // id -> display name (story 2.1); `barrow` (B1-B4) + `barrow2` (B5-B9) are the dungeon, two areas like clockdeep
  jotunheim: 'Stonehollow', jt_hall: 'Hall of Hearthstones', rimecaves: 'The Rime Caves', barrow: "The Titan's Barrow", barrow2: "The Titan's Barrow: the Throne",
};
export const AREAS_JOT = {};        // id -> 'areas/<id>/' (filled when the areas are built; merged into game.js's area path map)
export const AREA_NAMES_JOT = {};   // id -> display name (merged into game.js's AREA_NAME)
export const JOT_AREAS = Object.keys(JOT_PLANNED);

export class Jotunheim {
  constructor(G) { this.G = G; this.ctx = null; this.area = null; this.planned = JOT_PLANNED; }
  attach(ctx, area) { this.detach(); if (!AREAS_JOT[area]) return; this.ctx = ctx; this.area = area; }
  detach() { this.ctx = null; this.area = null; }
  update(dt) { /* nothing to do until the realm has areas */ }
  qa() { return { realm: 'jotunheim', stub: true, built: Object.keys(AREAS_JOT), planned: JOT_AREAS, area: this.area }; }
}
