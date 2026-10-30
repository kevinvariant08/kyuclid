// Writes data/index.json, the compact manifest the problem list loads.
// Full problems load on demand from data/problems/<id>.json.
//   node scripts/build-index.mjs
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const ROOT = fileURLToPath(new URL("..", import.meta.url));
export const PROBLEMS_DIR = ROOT + "data/problems/";
export const INDEX_FILE = ROOT + "data/index.json";

export const problemFiles = () => readdirSync(PROBLEMS_DIR).filter((f) => f.endsWith(".json")).sort();

// One manifest entry. `author` and `source` are extra to the brief's field list:
// the list shows "by <author>" or the source, and search covers the source.
export function entry(p) {
  const e = { id: p.id, title: p.title, kyu: p.kyu, topic: p.topic, subtopics: p.subtopics, type: p.type, status: p.status, author: p.provenance.author };
  if (p.provenance.source) e.source = p.provenance.source;
  e.stats = p.stats;
  return e;
}

// Easiest first, then by id, so the order never depends on the file system.
export const order = (a, b) => b.kyu - a.kyu || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);

export function buildIndex(problems) {
  return problems.map(entry).sort(order);
}

// One problem per line keeps diffs readable.
export const serialise = (index) => "[\n" + index.map((e) => JSON.stringify(e)).join(",\n") + "\n]\n";

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const problems = problemFiles().map((f) => JSON.parse(readFileSync(PROBLEMS_DIR + f, "utf8")));
  const index = buildIndex(problems);
  writeFileSync(INDEX_FILE, serialise(index));
  console.log(`Wrote data/index.json: ${index.length} problems.`);
}
