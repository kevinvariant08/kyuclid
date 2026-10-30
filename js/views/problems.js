// The problem list. It needs only data/index.json, and it stays fast at any size by drawing one page of rows.
// All filter state lives in the URL hash (lib/hash.js): edits rewrite the hash with replaceState, which doesn't
// fire hashchange, so typing in the search box never re-renders the view or loses focus.
import { $, esc, statusTag, sourceLine, authorOf } from "../lib/ui.js";
import { badge, TOPICS, LADDER } from "../lib/ranks.js";
import { S, myKyu } from "../lib/store.js";
import { LISTED, likedPct, likedRate, randomUnsolved } from "../lib/problems.js";
import { parseFilters, filtersToHash, blankFilters } from "../lib/hash.js";
import { subtopicName } from "../lib/taxonomy.js";

const PER_PAGE = 25;
const WIDE = "(min-width: 721px)";
let F = blankFilters();
let lastHash = "#problems";
export const lastListHash = () => lastHash;

// Folded so "Erdos" finds "Erdős", and cached because it runs on every keystroke.
const fold = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const hay = new Map();
function haystack(p) {
  if (!hay.has(p.id)) hay.set(p.id, fold([p.title, ...p.subtopics, ...p.subtopics.map(subtopicName)].join(" ").replace(/-/g, " ")));
  return hay.get(p.id);
}

const isTried = (p) => !S.solved[p.id] && (S.tries[p.id] > 0 || S.hints[p.id] > 0 || !!S.proofs[p.id]);
const matchesStatus = (p) => F.status === "all" || (F.status === "solved" ? !!S.solved[p.id] : F.status === "tried" ? isTried(p) : !S.solved[p.id]);

function filtered() {
  const words = fold(F.q).split(/\s+/).filter(Boolean);
  const ps = LISTED.filter((p) =>
    (!F.kyu.length || F.kyu.includes(p.kyu)) && (!F.topic.length || F.topic.includes(p.topic)) &&
    (!F.sub || p.subtopics.includes(F.sub)) && (F.type === "all" || p.type === F.type) &&
    matchesStatus(p) && words.every((w) => haystack(p).includes(w)));
  const sorts = {
    easy: (a, b) => b.kyu - a.kyu || b.stats.solves - a.stats.solves,
    hard: (a, b) => a.kyu - b.kyu || a.stats.solves - b.stats.solves,
    popular: (a, b) => b.stats.solves - a.stats.solves,
    loved: (a, b) => likedRate(b) - likedRate(a)
  };
  return ps.sort(sorts[F.sort]);
}

// Only subtopics in the chosen topics, with counts. A bank of hundreds has too many for a row of chips.
function subtopicOptions() {
  const counts = new Map();
  for (const p of LISTED) if (!F.topic.length || F.topic.includes(p.topic)) for (const s of p.subtopics) counts.set(s, (counts.get(s) || 0) + 1);
  if (F.sub && !counts.has(F.sub)) counts.set(F.sub, 0);
  const opts = [...counts].map(([s, n]) => [s, subtopicName(s), n]).sort((a, b) => a[1].localeCompare(b[1]));
  return `<option value="">All subtopics</option>` + opts.map(([s, name, n]) => `<option value="${esc(s)}">${esc(name)} (${n})</option>`).join("");
}

const activeCount = () => F.kyu.length + F.topic.length + (F.type !== "all") + (F.status !== "all") + (F.sub ? 1 : 0);

export function renderProblems() {
  F = parseFilters(location.hash);
  lastHash = filtersToHash(F);
  const v = $("v-problems");
  const open = matchMedia(WIDE).matches || activeCount() > 0;
  v.innerHTML = `
  <div class="list-head">
    <div><div class="eyebrow">The dojo</div><h1 class="h2">Problems</h1></div>
    <button class="btn primary" type="button" id="pRandom">Random unsolved at my rank <span class="btn-note">${myKyu()} kyu</span></button>
  </div>
  <div class="panel filters">
    <div class="frow"><input id="pq" class="search" type="search" placeholder="Search titles and subtopics" aria-label="Search titles and subtopics" value="${esc(F.q)}">
      <select id="psort" class="sel" aria-label="Sort problems">
        <option value="easy">Easiest first</option><option value="hard">Hardest first</option><option value="popular">Most solved</option><option value="loved">Best rated</option>
      </select></div>
    <details id="fmore"${open ? " open" : ""}>
      <summary>Filters<span id="fcount"></span></summary>
      <div class="fbody">
        <div class="frow" role="group" aria-labelledby="lblK"><span class="lbl" id="lblK">Kyu</span>${LADDER.map((k) => `<button type="button" class="chip kchip" data-k="${k}" aria-pressed="${F.kyu.includes(k)}" aria-label="${k} kyu">${badge(k)}</button>`).join("")}</div>
        <div class="frow" role="group" aria-labelledby="lblT"><span class="lbl" id="lblT">Topic</span>${Object.entries(TOPICS).map(([t, n]) => `<button type="button" class="chip" data-t="${t}" aria-pressed="${F.topic.includes(t)}">${n}</button>`).join("")}
          <select id="psub" class="sel sel-sub" aria-label="Subtopic">${subtopicOptions()}</select></div>
        <div class="frow" role="group" aria-labelledby="lblY"><span class="lbl" id="lblY">Type</span>${[["all", "All types"], ["answer", "Answer"], ["proof", "Proof"]].map(([x, n]) => `<button type="button" class="chip" data-type="${x}" aria-pressed="${F.type === x}">${n}</button>`).join("")}</div>
        <div class="frow" role="group" aria-labelledby="lblS"><span class="lbl" id="lblS">Status</span>${[["all", "Any status"], ["open", "Unsolved"], ["tried", "Tried"], ["solved", "Solved"]].map(([x, n]) => `<button type="button" class="chip" data-st="${x}" aria-pressed="${F.status === x}">${n}</button>`).join("")}</div>
      </div>
    </details>
  </div>
  <div class="list-status"><span id="pcount" role="status"></span><button class="btn small ghost" type="button" id="pclear" hidden>Clear filters</button></div>
  <ul class="plist" id="plist"></ul>
  <nav class="pager" id="pager" aria-label="Pages of problems" hidden></nav>
  <p class="faint" id="pRandomNote" role="status"></p>`;
  $("psort").value = F.sort;
  $("psub").value = F.sub;
  const edit = (fn) => { fn(); F.page = 1; syncControls(); commit(); };
  const toggle = (list, x) => (list.includes(x) ? list.filter((y) => y !== x) : [...list, x]);
  v.querySelectorAll("[data-k]").forEach((b) => b.addEventListener("click", () => edit(() => { F.kyu = toggle(F.kyu, +b.dataset.k); })));
  v.querySelectorAll("[data-t]").forEach((b) => b.addEventListener("click", () => edit(() => { F.topic = toggle(F.topic, b.dataset.t); $("psub").innerHTML = subtopicOptions(); $("psub").value = F.sub; })));
  v.querySelectorAll("[data-type]").forEach((b) => b.addEventListener("click", () => edit(() => { F.type = b.dataset.type; })));
  v.querySelectorAll("[data-st]").forEach((b) => b.addEventListener("click", () => edit(() => { F.status = b.dataset.st; })));
  $("psub").addEventListener("change", (e) => edit(() => { F.sub = e.target.value; }));
  $("psort").addEventListener("change", (e) => edit(() => { F.sort = e.target.value; }));
  let typing = null;
  $("pq").addEventListener("input", (e) => { clearTimeout(typing); typing = setTimeout(() => edit(() => { F.q = e.target.value; }), 120); });
  $("pclear").addEventListener("click", () => {
    const { sort, q } = F;
    F = { ...blankFilters(), sort, q };
    renderAfterClear();
  });
  $("pRandom").addEventListener("click", () => {
    const p = randomUnsolved();
    if (p) location.hash = "#p-" + p.id;
    else $("pRandomNote").textContent = "You've solved every problem in the bank. That's a good problem to have.";
  });
  syncControls();
  renderList();
}

function renderAfterClear() {
  $("psub").innerHTML = subtopicOptions();
  $("psub").value = "";
  syncControls();
  commit();
  $("pq").focus();
}

// The list and the URL together. replaceState, so filter edits don't each add a Back step.
function commit() {
  lastHash = filtersToHash(F);
  history.replaceState(null, "", lastHash);
  renderList();
}

function syncControls() {
  const v = $("v-problems");
  v.querySelectorAll("[data-k]").forEach((b) => b.setAttribute("aria-pressed", F.kyu.includes(+b.dataset.k)));
  v.querySelectorAll("[data-t]").forEach((b) => b.setAttribute("aria-pressed", F.topic.includes(b.dataset.t)));
  v.querySelectorAll("[data-type]").forEach((b) => b.setAttribute("aria-pressed", F.type === b.dataset.type));
  v.querySelectorAll("[data-st]").forEach((b) => b.setAttribute("aria-pressed", F.status === b.dataset.st));
  const n = activeCount();
  $("fcount").textContent = n ? ` (${n})` : "";
  $("pclear").hidden = n === 0;
}

const row = (p) => `<li><a class="prow" href="#p-${esc(p.id)}">
    <span>${badge(p.kyu)}</span>
    <span class="prow-main"><span class="t">${esc(p.title)}</span> ${statusTag(p)}
      <span class="meta"><span>${TOPICS[p.topic]}</span><span>${p.type === "proof" ? "Proof" : "Answer"}</span>${p.subtopics.slice(0, 2).map((s) => `<span>${esc(subtopicName(s))}</span>`).join("")}${sourceLine(p) ? `<span>${esc(sourceLine(p))}</span>` : `<span>by ${esc(authorOf(p))}</span>`}</span></span>
    <span class="stats"><span><b>${p.stats.solves.toLocaleString("en-GB")}</b>solves</span><span><b>${likedPct(p)}</b>liked</span></span>
  </a></li>`;

function pageNumbers(cur, last) {
  const want = new Set([1, last, cur - 1, cur, cur + 1].filter((n) => n >= 1 && n <= last));
  const out = []; let prev = 0;
  for (const n of [...want].sort((a, b) => a - b)) { if (n - prev > 1) out.push(null); out.push(n); prev = n; }
  return out;
}

function renderList() {
  const ps = filtered();
  const last = Math.max(1, Math.ceil(ps.length / PER_PAGE));
  if (F.page > last) F.page = last;
  const from = (F.page - 1) * PER_PAGE;
  const shown = ps.slice(from, from + PER_PAGE);
  $("pcount").textContent = !ps.length ? "No problems match" :
    ps.length <= PER_PAGE ? `${ps.length} ${ps.length === 1 ? "problem" : "problems"}` :
    `Showing ${from + 1}–${from + shown.length} of ${ps.length} problems`;
  const list = $("plist");
  list.innerHTML = shown.length ? shown.map(row).join("") : `<li class="empty">${LISTED.length ? `Nothing matches these filters. <button class="linkish" type="button" id="pclear2">Clear them</button> to see all ${LISTED.length} problems.` : "There are no problems in the bank yet."}</li>`;
  if ($("pclear2")) $("pclear2").addEventListener("click", () => { F = blankFilters(); $("pq").value = ""; $("psort").value = F.sort; renderAfterClear(); });
  const pager = $("pager");
  pager.hidden = last < 2;
  if (last < 2) { pager.innerHTML = ""; return; }
  pager.innerHTML = `
    <button class="btn small" type="button" data-pg="${F.page - 1}"${F.page === 1 ? " disabled" : ""}>Previous</button>
    <span class="pg-nums">${pageNumbers(F.page, last).map((n) => n === null ? `<span class="pg-gap" aria-hidden="true">…</span>` :
      `<button class="pg" type="button" data-pg="${n}" aria-label="Page ${n}"${n === F.page ? ` aria-current="page"` : ""}>${n}</button>`).join("")}</span>
    <button class="btn small" type="button" data-pg="${F.page + 1}"${F.page === last ? " disabled" : ""}>Next</button>`;
  pager.querySelectorAll("[data-pg]").forEach((b) => b.addEventListener("click", () => {
    F.page = +b.dataset.pg;
    // pushState, so Back steps through pages. Going back fires hashchange, which restores the list.
    lastHash = filtersToHash(F);
    history.pushState(null, "", lastHash);
    renderList();
    $("pcount").scrollIntoView({ block: "start" });
    const again = pager.querySelector(`[aria-current="page"]`);
    if (again) again.focus({ preventScroll: true });
  }));
}

// When a phone rotates or a window widens, the filters shouldn't stay folded behind a hidden summary.
matchMedia(WIDE).addEventListener("change", (e) => { if (e.matches && $("fmore")) $("fmore").open = true; });
