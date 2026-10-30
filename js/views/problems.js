// The problem list. It needs only data/index.json.
import { $, esc, statusTag, sourceLine, authorOf } from "../lib/ui.js";
import { badge, TOPICS } from "../lib/ranks.js";
import { S } from "../lib/store.js";
import { LISTED, likedPct, likedRate } from "../lib/problems.js";

// Filters survive leaving the view; the home page's belt rack sets F.kyu.
export const F = { kyu: new Set(), topic: new Set(), type: "all", status: "all", q: "", sort: "easy" };

export function renderProblems() {
  const v = $("v-problems");
  v.innerHTML = `
  <div><div class="eyebrow">The dojo</div><h2 class="h2">Problems</h2></div>
  <div class="panel filters">
    <div class="frow"><input id="pq" class="search" type="search" placeholder="Search titles and sources" aria-label="Search problems" value="${esc(F.q)}">
      <select id="psort" class="sel" aria-label="Sort">
        <option value="easy">Easiest first</option><option value="hard">Hardest first</option><option value="popular">Most solved</option><option value="loved">Best rated</option>
      </select></div>
    <div class="frow"><span class="lbl">Kyu</span>${[8, 7, 6, 5, 4, 3, 2, 1].map((k) => `<button type="button" class="chip kchip" data-k="${k}" aria-pressed="${F.kyu.has(k)}">${badge(k)}</button>`).join("")}</div>
    <div class="frow"><span class="lbl">Topic</span>${Object.entries(TOPICS).map(([t, n]) => `<button type="button" class="chip" data-t="${t}" aria-pressed="${F.topic.has(t)}">${n}</button>`).join("")}</div>
    <div class="frow"><span class="lbl">Show</span>
      ${[["all", "All types"], ["answer", "Answer"], ["proof", "Proof"]].map(([x, n]) => `<button type="button" class="chip" data-type="${x}" aria-pressed="${F.type === x}">${n}</button>`).join("")}
      <span style="width:8px"></span>
      ${[["all", "Any status"], ["open", "Unsolved"], ["done", "Solved"]].map(([x, n]) => `<button type="button" class="chip" data-st="${x}" aria-pressed="${F.status === x}">${n}</button>`).join("")}
    </div>
  </div>
  <div class="plist" id="plist"></div>`;
  $("psort").value = F.sort;
  v.querySelectorAll("[data-k]").forEach((b) => b.addEventListener("click", () => { const k = +b.dataset.k; F.kyu.has(k) ? F.kyu.delete(k) : F.kyu.add(k); b.setAttribute("aria-pressed", F.kyu.has(k)); renderList(); }));
  v.querySelectorAll("[data-t]").forEach((b) => b.addEventListener("click", () => { const t = b.dataset.t; F.topic.has(t) ? F.topic.delete(t) : F.topic.add(t); b.setAttribute("aria-pressed", F.topic.has(t)); renderList(); }));
  v.querySelectorAll("[data-type]").forEach((b) => b.addEventListener("click", () => { F.type = b.dataset.type; v.querySelectorAll("[data-type]").forEach((x) => x.setAttribute("aria-pressed", x === b)); renderList(); }));
  v.querySelectorAll("[data-st]").forEach((b) => b.addEventListener("click", () => { F.status = b.dataset.st; v.querySelectorAll("[data-st]").forEach((x) => x.setAttribute("aria-pressed", x === b)); renderList(); }));
  $("pq").addEventListener("input", (e) => { F.q = e.target.value; renderList(); });
  $("psort").addEventListener("change", (e) => { F.sort = e.target.value; renderList(); });
  renderList();
}

function renderList() {
  const q = F.q.trim().toLowerCase();
  const ps = LISTED.filter((p) =>
    (!F.kyu.size || F.kyu.has(p.kyu)) && (!F.topic.size || F.topic.has(p.topic)) &&
    (F.type === "all" || p.type === F.type) &&
    (F.status === "all" || (F.status === "done") === !!S.solved[p.id]) &&
    (!q || (p.title + " " + (p.source || "")).toLowerCase().includes(q)));
  const sorts = {
    easy: (a, b) => b.kyu - a.kyu || b.stats.solves - a.stats.solves,
    hard: (a, b) => a.kyu - b.kyu || a.stats.solves - b.stats.solves,
    popular: (a, b) => b.stats.solves - a.stats.solves,
    loved: (a, b) => likedRate(b) - likedRate(a)
  };
  ps.sort(sorts[F.sort]);
  $("plist").innerHTML = ps.length ? ps.map((p) => `
    <a class="prow" href="#p-${p.id}">
      <span>${badge(p.kyu)}</span>
      <span style="min-width:0"><span class="t">${esc(p.title)}</span> ${statusTag(p)}
        <span class="meta"><span>${TOPICS[p.topic]}</span><span>${p.type === "proof" ? "Proof" : "Answer"}</span>${sourceLine(p) ? `<span>${esc(sourceLine(p))}</span>` : `<span>by ${esc(authorOf(p))}</span>`}</span></span>
      <span class="stats"><span><b>${p.stats.solves.toLocaleString("en-GB")}</b>solves</span><span><b>${likedPct(p)}</b>liked</span></span>
    </a>`).join("") : `<div class="empty">No problems match these filters. Clear a kyu or topic to see more.</div>`;
}
