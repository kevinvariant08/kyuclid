// Summarises review/decisions.jsonl into a short paragraph for the generator's prompt (task 06).
//   node scripts/rejection-digest.mjs
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DEFAULT_ROOT = fileURLToPath(new URL("..", import.meta.url));
const MAX_NOTES = 5;
const NOTE_CHARS = 160;

// The standard's failure list, read from its section 6 table so it can't drift: [{ code, label }].
export function failureList(root = DEFAULT_ROOT) {
  const file = root + "/docs/problem-standard.md";
  const text = existsSync(file) ? readFileSync(file, "utf8") : "";
  const list = [...text.matchAll(/^\| \*\*(B\d+)\*\* \| ([^|]+?) \|/gm)].map((m) => ({ code: m[1], label: m[2] }));
  return [...list, { code: "other", label: "Other (say why in the note)" }];
}

export function readDecisions(root = DEFAULT_ROOT) {
  const file = root + "/review/decisions.jsonl";
  if (!existsSync(file)) return [];
  return readFileSync(file, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

export function digest(decisions, failures) {
  const rejected = decisions.filter((d) => d.decision === "reject");
  if (!rejected.length) return `No drafts have been rejected yet (${decisions.length} reviewed).`;
  const label = Object.fromEntries(failures.map((f) => [f.code, f.label]));
  const counts = new Map();
  for (const d of rejected) for (const c of d.reason) counts.set(c, (counts.get(c) || 0) + 1);
  const top = [...counts].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))
    .map(([c, n]) => `${c === "other" ? "other" : `${c} ${(label[c] || "").toLowerCase()}`} (${n})`.replace(" ()", ""));
  const notes = rejected.filter((d) => d.note).slice(-MAX_NOTES).map((d) => `"${d.note.replace(/\s+/g, " ").slice(0, NOTE_CHARS)}"`);
  let out = `The reviewer rejected ${rejected.length} of ${decisions.length} reviewed drafts. Reasons, most common first: ${top.join("; ")}. Avoid these.`;
  if (notes.length) out += ` Recent reviewer notes: ${notes.join(" ")}`;
  return out;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  console.log(digest(readDecisions(), failureList()));
}
