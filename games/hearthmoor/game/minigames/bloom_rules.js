// game/minigames/bloom_rules.js: Bloomtide harvest + dance rules (Vanaheim Stage C). Pure: no DOM, no save, no randomness.
// Each game is one timing tap: tap when the cue meets its mark. Unit tested by tests/test_bloom_rules.mjs.
export const WINDOW = { perfect: 70, good: 150 };          // ms either side of a cue's beat
export const POINTS = { perfect: 100, good: 50, miss: 0 };

// harvest: 8 glow-caps ripen one after another (a ring closes on the cap); 5 picked to win
// dance: 12 steps on Liss's beat, 96 BPM, after a 4-beat count-in; 8 steps to win
export const GAMES = {
  harvest: { title: 'Glow-cap Harvest', cues: 8, need: 5, lead: 1100, start: 1600, gaps: [1400, 1200, 1500, 1000, 1300, 1100, 1400, 1200] },
  dance: { title: 'Spring Dance', cues: 12, need: 8, lead: 1600, bpm: 96, countIn: 4 },
};

// cue times in ms from the game's start
export function chart(kind) {
  const g = GAMES[kind]; if (!g) throw new Error(`bloom: unknown game ${kind}`);
  if (kind === 'harvest') { const t = []; let at = g.start; for (let i = 0; i < g.cues; i++) { t.push(at); at += g.gaps[i % g.gaps.length]; } return t; }
  const beat = 60000 / g.bpm; return Array.from({ length: g.cues }, (_, i) => Math.round((g.countIn + i) * beat));
}

// grade one tap: |offset| <= perfect -> perfect, <= good -> good, else miss
export function judge(offsetMs) {
  const d = Math.abs(offsetMs);
  return d <= WINDOW.perfect ? 'perfect' : d <= WINDOW.good ? 'good' : 'miss';
}

// a tap at time t against the chart's open cues (judged[i] undefined): the nearest open cue inside the good window gets it.
// Returns { i, grade, off } or null (a stray tap: no cue near, no penalty).
export function tapAt(times, judged, t) {
  let best = -1, bd = Infinity;
  for (let i = 0; i < times.length; i++) { if (judged[i]) continue; const d = Math.abs(t - times[i]); if (d < bd) { bd = d; best = i; } }
  if (best < 0 || bd > WINDOW.good) return null;
  return { i: best, grade: judge(t - times[best]), off: t - times[best] };
}

// cues whose good window has passed at time t without a tap become misses
export function expire(times, judged, t) {
  const out = [];
  for (let i = 0; i < times.length; i++) if (!judged[i] && t > times[i] + WINDOW.good) { judged[i] = 'miss'; out.push(i); }
  return out;
}

export function score(kind, grades) {
  const g = GAMES[kind], hits = grades.filter((x) => x === 'perfect' || x === 'good').length;
  const pts = grades.reduce((s, x) => s + (POINTS[x] || 0), 0);
  return { score: pts, hits, perfect: grades.filter((x) => x === 'perfect').length, need: g.need, of: g.cues, won: hits >= g.need, max: g.cues * POINTS.perfect };
}
