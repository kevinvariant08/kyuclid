// Checks every problem against schema/problem.schema.json, plus the rules a schema can't express:
// file name matches id, ids unique, rubrics total 7, figures exist and are safe to inline, subtopics are in
// the taxonomy, and data/index.json is up to date. Exits non-zero on any failure.
//   node scripts/validate.mjs
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import Ajv2020 from "ajv/dist/2020.js";
import { ROOT, PROBLEMS_DIR, INDEX_FILE, problemFiles, buildIndex } from "./build-index.mjs";

const errors = [];
const fail = (where, msg) => errors.push(`${where}: ${msg}`);

const schema = JSON.parse(readFileSync(ROOT + "schema/problem.schema.json", "utf8"));
const ajv = new Ajv2020({ allErrors: true, strict: true, strictRequired: false });
const validate = ajv.compile(schema);

// Subtopics are free-form slugs until task 03 publishes data/taxonomy.json.
let taxonomy = null;
if (existsSync(ROOT + "data/taxonomy.json")) {
  const t = JSON.parse(readFileSync(ROOT + "data/taxonomy.json", "utf8"));
  const slugs = [...(t.techniques || []), ...(t.configurations || [])].map((x) => (typeof x === "string" ? x : x.id));
  taxonomy = new Set(slugs);
}

// The schema's "not" rules forbid a field given another field's value. Ajv only says "must NOT be valid",
// so name the field here.
function forbidden(p, at) {
  if (at === "/provenance") {
    const pr = p.provenance;
    if (pr.kind === "classical") return `"pipeline_run" is only for generated original problems`;
    return `only classical problems have ${["source", "book"].filter((k) => k in pr).map((k) => `"${k}"`).join(" or ")}`;
  }
  if (p.type === "answer") return `answer problems have no "rubric"`;
  return `proof problems have no ${["answer_hash", "answer_format"].filter((k) => k in p).map((k) => `"${k}"`).join(" or ")}`;
}

// Ajv's messages, minus the "must match then/else schema" lines that only repeat the real error.
function describe(err, p) {
  if (err.keyword === "if") return null;
  const at = err.instancePath || "(top level)";
  if (err.keyword === "additionalProperties") return `${at}: unknown field "${err.params.additionalProperty}"`;
  if (err.keyword === "enum") return `${at}: must be one of ${err.params.allowedValues.map((v) => JSON.stringify(v)).join(", ")}`;
  if (err.keyword === "required") return `${at}: missing required field "${err.params.missingProperty}"`;
  if (err.keyword === "not") return `${at}: ${forbidden(p, err.instancePath)}`;
  return `${at}: ${err.message}`;
}

// What pipeline/figures produces. CI has no TeX, so it checks the committed SVG rather than rebuilding it.
const PAINT = new Set(["none", "currentColor", "var(--fig-accent,currentColor)"]);
function svgProblems(svg, name) {
  const out = [];
  if (!svg.startsWith("<svg")) out.push("doesn't start with <svg");
  if (/<script|<foreignObject|<image|\son\w+=|https?:\/\/(?!www\.w3\.org)/.test(svg)) out.push("holds active or external content");
  for (const m of svg.matchAll(/\b(?:stroke|fill)='([^']*)'/g)) if (!PAINT.has(m[1])) { out.push(`has the colour ${m[1]}, which won't follow the theme`); break; }
  for (const m of svg.matchAll(/\bid='([^']*)'/g)) if (!m[1].startsWith(name + "-")) { out.push(`has the id ${m[1]}, which could clash when inlined`); break; }
  return out;
}

function checkSolutionFigures(p, where) {
  const paragraphs = p.solution.split(/\n\s*\n/).length;
  for (const f of p.solution_figures || []) {
    const path = f.src.split("?")[0];
    const name = path.slice("figures/".length, -".svg".length);
    if (!new RegExp(`^${p.id}-solution(-\\d+)?$`).test(name)) { fail(where, `${f.src} should be named ${p.id}-solution[-n].svg`); continue; }
    if (f.after_paragraph > paragraphs) fail(where, `${path} comes after paragraph ${f.after_paragraph}, but the solution has ${paragraphs}`);
    if (!existsSync(ROOT + path)) { fail(where, `figure ${path} does not exist`); continue; }
    if (!existsSync(ROOT + path.replace(/\.svg$/, ".tex"))) fail(where, `${path} has no .tex source beside it`);
    const svg = readFileSync(ROOT + path, "utf8");
    const version = createHash("sha256").update(svg.replace(/\r\n/g, "\n")).digest("hex").slice(0, 8);
    if (!f.src.endsWith("?v=" + version)) fail(where, `${f.src} is stale: the file's version is ${version}. Run: python -m pipeline.figures attach`);
    for (const problem of svgProblems(svg, name)) fail(where, `${path} ${problem}`);
  }
}

const problems = [];
const seen = new Map();
for (const f of problemFiles()) {
  const where = "data/problems/" + f;
  let p;
  try { p = JSON.parse(readFileSync(PROBLEMS_DIR + f, "utf8")); }
  catch (e) { fail(where, `not valid JSON (${e.message})`); continue; }

  if (!validate(p)) {
    for (const msg of new Set(validate.errors.map((e) => describe(e, p)).filter(Boolean))) fail(where, msg);
    continue;
  }
  problems.push(p);

  if (f !== p.id + ".json") fail(where, `id is "${p.id}", so the file must be named ${p.id}.json`);
  if (seen.has(p.id)) fail(where, `duplicate id "${p.id}", also used by ${seen.get(p.id)}`);
  else seen.set(p.id, where);

  if (p.rubric) {
    const total = p.rubric.reduce((s, r) => s + r.marks, 0);
    if (total !== 7) fail(where, `rubric marks total ${total}, not 7`);
  }
  if (p.figure && !existsSync(ROOT + p.figure)) fail(where, `figure ${p.figure} does not exist`);
  checkSolutionFigures(p, where);
  if (taxonomy) for (const s of p.subtopics) if (!taxonomy.has(s)) fail(where, `subtopic "${s}" is not in data/taxonomy.json`);
}

// Compare parsed JSON, not bytes, so line endings don't matter.
if (errors.length === 0) {
  let current = null;
  try { current = JSON.parse(readFileSync(INDEX_FILE, "utf8")); } catch {}
  if (JSON.stringify(current) !== JSON.stringify(buildIndex(problems))) {
    fail("data/index.json", current ? "out of date. Run: node scripts/build-index.mjs" : "missing or unreadable. Run: node scripts/build-index.mjs");
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  console.error(`\n${errors.length} error${errors.length > 1 ? "s" : ""}.`);
  process.exit(1);
}
console.log(`OK: ${problems.length} problems valid, data/index.json up to date.`);
