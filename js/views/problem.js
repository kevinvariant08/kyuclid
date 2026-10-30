// One problem: statement, answer box or proof editor, hints, solution, rating.
import { $, esc, renderMe, sourceLine, authorOf } from "../lib/ui.js";
import { KYU, badge, TOPICS } from "../lib/ranks.js";
import { S, save, award, logEvent } from "../lib/store.js";
import { LISTED, byId, cachedProblem, getProblem, likedPct } from "../lib/problems.js";
import { check } from "../lib/answers.js";
import { tex, paras } from "../lib/tex.js";
import { D } from "./duel.js";

const rubricLine = (r) => `${r.marks} mark${r.marks > 1 ? "s" : ""}: ${r.criterion}`;

let proofTimer = null;
export async function renderProblem(id) {
  const v = $("v-problem");
  if (!byId[id]) { v.innerHTML = `<div class="panel">That problem doesn't exist. <a href="#problems">Back to the problem list</a>.</div>`; return; }
  let p = cachedProblem(id);
  if (!p) {
    const at = location.hash;
    v.innerHTML = "";
    p = await getProblem(id);
    if (location.hash !== at) return;
  }
  const solved = S.solved[p.id];
  const used = S.hints[p.id] || 0;
  const base = KYU[p.kyu].pts;
  const sameKyu = LISTED.filter((x) => x.kyu === p.kyu && x.id !== p.id && !S.solved[x.id]);
  const next = sameKyu[0] || LISTED.find((x) => !S.solved[x.id] && x.id !== p.id);
  const pf = S.proofs[p.id] || { text: "", submitted: false };
  const source = sourceLine(p);

  let work;
  if (p.type === "answer") {
    work = `
    <div class="sec"><h3>Your answer</h3>
      ${solved ? `<div class="feedback ok">Solved, +${solved.pts} pts.</div>` : `
      <form class="answer" id="ansForm" autocomplete="off">
        <input id="ans" inputmode="decimal" placeholder="e.g. 42, 25/4 or 6.25" aria-label="Your answer">
        <button class="btn primary" type="submit">Submit</button>
      </form>
      <div class="feedback" id="fb" role="status">${S.tries[p.id] ? `${S.tries[p.id]} wrong attempt${S.tries[p.id] > 1 ? "s" : ""} so far. Wrong answers cost nothing here; in a duel they cost 15 seconds.` : `Worth ${base} pts, minus a quarter for each hint you open.`}</div>`}
    </div>`;
  } else {
    work = `
    <div class="sec"><h3>Your proof</h3>
      <p class="faint" style="margin:0 0 10px">Write in plain text with LaTeX between dollar signs. The preview updates as you type.</p>
      <div class="proof-area">
        <textarea id="proofText" aria-label="Your proof" placeholder="Write your proof here. Maths goes between dollar signs, e.g. $\\frac{a}{b+c} \\ge 0$.">${esc(pf.text)}</textarea>
        <div class="preview" id="proofPrev" aria-label="Preview"></div>
      </div>
      <div class="cta" style="margin-top:12px">
        ${pf.submitted ? `<span class="status review">Submitted. In the full site this waits for two reviewers.</span>` : `<button class="btn primary" type="button" id="submitProof">Submit for review</button>`}
      </div>
      ${pf.submitted ? `
      <div class="sec"><h3>Self-grade against the rubric</h3>
        <ol class="rubric">${p.rubric.map((r) => `<li>${esc(rubricLine(r))}</li>`).join("")}</ol>
        <div class="grades" id="grades">${[0, 1, 2, 3, 4, 5, 6, 7].map((g) => `<button type="button" data-g="${g}" aria-pressed="${solved && solved.grade === g}" aria-label="Grade ${g} out of 7">${g}</button>`).join("")}</div>
        <p class="faint">${solved ? `Recorded ${solved.grade}/7: +${solved.pts} provisional pts until review.` : `Points are provisional: ${base} × grade ÷ 7.`}</p>
      </div>` : ""}
    </div>`;
  }

  const showSolution = p.type === "answer" ? !!solved : !!pf.submitted;
  v.innerHTML = `
  <div><a href="#problems" class="faint">← All problems</a></div>
  <div class="pgrid">
    <article class="panel">
      ${badge(p.kyu, null, "lg")}
      <h1 class="ptitle">${esc(p.title)}</h1>
      <div class="pmeta"><span>${TOPICS[p.topic]}</span><span>${p.type === "proof" ? "Proof, peer-reviewed" : "Single answer, auto-checked"}</span><span>${source ? "Source: " + esc(source) : "Original, by " + esc(authorOf(p))}</span></div>
      <div class="statement">${paras(p.statement)}</div>
      ${work}
      <div class="sec"><h3>Hints</h3>
        ${p.hints.slice(0, used).map((h, i) => `<div class="hint"><b class="faint">Hint ${i + 1}.</b> ${h}</div>`).join("")}
        ${used < p.hints.length && !solved ? `<button class="btn small" type="button" id="hintBtn">Open hint ${used + 1} of ${p.hints.length}${p.type === "answer" ? " (−25% pts)" : ""}</button>` : used === 0 ? `<span class="locked">Solved without hints.</span>` : ""}
      </div>
      <div class="sec"><h3>${p.type === "proof" ? "Reference proof" : "Solution"}</h3>
        ${showSolution ? `<div class="solution">${paras(p.solution)}</div>` : `<div class="locked">${p.type === "proof" ? "Unlocks when you submit a proof." : "Unlocks when you solve it, so nobody can peek their way up the ranks."}</div>`}
      </div>
      ${solved ? `
      <div class="sec"><h3>Rate this problem</h3>
        <div class="vote" id="votes">
          ${[["easier", "Felt easier"], ["right", "Rank feels right"], ["harder", "Felt harder"]].map(([x, n]) => `<button type="button" class="chip" data-vote="${x}" aria-pressed="${S.votes[p.id] === x}">${n}</button>`).join("")}
        </div>
        <p class="faint" id="voteNote">${S.votes[p.id] ? "Vote saved. Rank votes are how beta problems get their kyu." : "Rank votes are how beta problems get their kyu."}</p>
      </div>` : ""}
    </article>
    <aside class="side">
      <div class="panel">
        <dl class="kvlist">
          <dt>Rank</dt><dd>${p.kyu} kyu · ${KYU[p.kyu].belt}</dd>
          <dt>Worth</dt><dd>${base} pts</dd>
          <dt>Solves</dt><dd>${p.stats.solves.toLocaleString("en-GB")}</dd>
          <dt>Liked by</dt><dd>${likedPct(p)}</dd>
          <dt>Your status</dt><dd>${solved ? (solved.how === "proof" ? "self-graded" : "solved") : "open"}</dd>
        </dl>
      </div>
      ${p.type === "answer" ? `<div class="panel"><b>Race someone on this kyu</b><p class="faint" style="margin:4px 0 12px">A random ${p.kyu} kyu problem against the clock.</p><a class="btn" href="#duel" id="duelHere">Duel at ${p.kyu} kyu</a></div>` : ""}
      ${next ? `<div class="panel"><span class="eyebrow">Next up</span><p style="margin:6px 0 10px"><b>${esc(next.title)}</b> ${badge(next.kyu)}</p><a class="btn small" href="#p-${next.id}">Open</a></div>` : ""}
    </aside>
  </div>`;

  if ($("ansForm")) $("ansForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const val = $("ans").value; const r = check(p, val); const fb = $("fb");
    if (r === null) { fb.className = "feedback bad"; fb.textContent = "Enter a number, a fraction like 25/4, or a decimal."; return; }
    if (r) { award(p, "answer"); renderMe(); renderProblem(p.id); return; }
    S.tries[p.id] = (S.tries[p.id] || 0) + 1; save();
    fb.className = "feedback bad"; fb.textContent = `${val.trim()} is not it. Attempt ${S.tries[p.id]}.`;
  });
  if ($("hintBtn")) $("hintBtn").addEventListener("click", () => { S.hints[p.id] = used + 1; save(); renderProblem(p.id); });
  if ($("duelHere")) $("duelHere").addEventListener("click", () => { D.kyu = p.kyu; });
  if ($("proofText")) {
    const ta = $("proofText"), pv = $("proofPrev");
    const draw = () => { pv.innerHTML = ta.value.trim() ? paras(esc(ta.value)) : `<span class="faint">Your rendered proof appears here.</span>`; tex(pv); };
    draw();
    ta.addEventListener("input", () => { S.proofs[p.id] = Object.assign(S.proofs[p.id] || {}, { text: ta.value }); save(); clearTimeout(proofTimer); proofTimer = setTimeout(draw, 350); });
  }
  if ($("submitProof")) $("submitProof").addEventListener("click", () => {
    const t = $("proofText").value.trim();
    if (t.length < 40) { $("proofText").focus(); $("proofText").setAttribute("placeholder", "Write at least a few lines before submitting."); return; }
    S.proofs[p.id] = { text: t, submitted: true }; logEvent(`Submitted a proof for ${p.title}`); save(); renderProblem(p.id);
  });
  if ($("grades")) $("grades").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    const g = +b.dataset.g; delete S.solved[p.id];
    if (g > 0) award(p, "proof", g); else save();
    renderMe(); renderProblem(p.id);
  }));
  if ($("votes")) $("votes").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    S.votes[p.id] = b.dataset.vote; save();
    $("votes").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
    $("voteNote").textContent = "Vote saved. Rank votes are how beta problems get their kyu.";
  }));
  tex(v);
}
