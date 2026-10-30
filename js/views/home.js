import { $, dayIndex } from "../lib/ui.js";
import { KYU, badge } from "../lib/ranks.js";
import { LISTED, getProblem } from "../lib/problems.js";
import { tex } from "../lib/tex.js";
import { F } from "./problems.js";

export async function renderHome() {
  const answerProblems = LISTED.filter((p) => p.type === "answer");
  const at = location.hash;
  const potd = await getProblem(answerProblems[dayIndex() % answerProblems.length].id);
  if (location.hash !== at) return;
  const rows = [8, 7, 6, 5, 4, 3, 2, 1].map((k) => {
    const ps = LISTED.filter((p) => p.kyu === k);
    const proof = ps.some((p) => p.type === "proof"), ans = ps.some((p) => p.type === "answer");
    const mode = proof && ans ? `<span class="mode-tag">answer</span><span class="mode-tag proof">proof</span>` : proof ? `<span class="mode-tag proof">proof</span>` : `<span class="mode-tag">answer</span>`;
    return `<a class="rack-row" href="#problems" data-kyu="${k}">${badge(k)}<span class="anchor">${KYU[k].anchor}${mode}</span><span class="r">+${KYU[k].pts} pts · ${ps.length}</span></a>`;
  }).join("");
  $("v-home").innerHTML = `
  <div class="hero">
    <div>
      <div class="eyebrow">Contest maths, ranked</div>
      <h1>From your first AMC to <em>IMO Problem 6</em></h1>
      <p class="lede">MathWars is a dojo for competition problems. Start at 8 kyu with warm-ups, climb to 1 kyu olympiad proofs, and duel other solvers on the same problem with the clock running.</p>
      <div class="cta"><a class="btn primary" href="#p-${potd.id}">Solve today's problem</a><a class="btn" href="#duel">Start a duel</a><a class="btn ghost" href="#problems">Browse all ${LISTED.length}</a></div>
    </div>
    <div class="rack" aria-label="Kyu ladder">
      <div class="rack-h"><span class="eyebrow">The belt rack</span><span class="faint">pts per solve · problems in this draft</span></div>
      ${rows}
    </div>
  </div>

  <div class="panel potd">
    <div>
      <div class="eyebrow">Problem of the day · ${badge(potd.kyu)}</div>
      <div class="stmt">${potd.statement}</div>
    </div>
    <a class="btn primary" href="#p-${potd.id}">Answer it</a>
  </div>

  <div class="three">
    <div class="panel"><h3>Solve</h3><p>From 8 kyu to 4 kyu every problem has a single numerical answer, checked the moment you submit, the way AIME and UKMT are marked. 3 kyu mixes answers and proofs. Solutions unlock once you have it right.</p></div>
    <div class="panel"><h3>Prove</h3><p>At 2 and 1 kyu, and for some 3 kyu problems, you write proofs. Your write-up goes to two reviewers ranked above the problem, who mark it out of 7 like an olympiad script. This draft lets you self-grade against the official rubric.</p></div>
    <div class="panel"><h3>Duel</h3><p>Two solvers, one problem, one clock. First correct answer wins. A wrong answer locks you out for 15 seconds, so guessing costs time. Duels carry their own Elo rating.</p></div>
  </div>

  <div>
    <div class="eyebrow" style="margin-bottom:10px">How problems get here</div>
    <div class="steps">
      <div><div class="n">1</div><h3>Propose</h3><p>Anyone at 4 kyu or above submits a problem with an answer or a model proof, plus its source if it comes from a contest.</p></div>
      <div><div class="n">2</div><h3>Beta</h3><p>Solvers attempt it and vote on its kyu and quality. Duplicates of existing problems get flagged.</p></div>
      <div><div class="n">3</div><h3>Ranked</h3><p>After enough votes it gets an official kyu and starts awarding points. Authors earn points for every solve.</p></div>
    </div>
  </div>

  <div class="draft">
    <b>What this first draft does and doesn't do</b>
    <ul>
      <li>${LISTED.length} seed problems across all eight kyu. Contest problems name their source.</li>
      <li>Answers are checked against hashes in the page, and your progress lives in this browser only.</li>
      <li>Duels are against a timed ghost. Friend duels, accounts, peer review and problem submission need a backend.</li>
      <li>The leaderboard shows sample players so you can see the layout.</li>
    </ul>
  </div>`;
  $("v-home").querySelectorAll(".rack-row").forEach((a) => a.addEventListener("click", () => { F.kyu = new Set([+a.dataset.kyu]); }));
  tex($("v-home"));
}
