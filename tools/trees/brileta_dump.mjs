// Print brileta trees as JSON RGBA (base64) for Python. Vendored dist = MIT brileta-sprites (Mark Ayzenshtat).
// usage: node brileta_dump.mjs '[{"seed":3,"size":26,"arch":"deciduous"}]'
import { generateTree } from "./vendor/brileta-dist/trees.js";
const reqs = JSON.parse(process.argv[2] || "[]");
const out = reqs.map((r) => {
  const res = generateTree(r.seed, r.size || 26, r.arch || "deciduous");
  const c = res.canvas;
  return { w: c.width, h: c.height, arch: res.archetype, data: Buffer.from(c.data).toString("base64") };
});
process.stdout.write(JSON.stringify(out));
