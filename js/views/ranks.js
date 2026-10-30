// The kyu explainer. Every number here comes from lib/ranks.js or the problem index.
import { $ } from "../lib/ui.js";
import { KYU, RANKS, LADDER, HINT_COST, MIN_HINT_SHARE, PROOF_MARKS, badge, rankOf } from "../lib/ranks.js";
import { points } from "../lib/store.js";
import { LISTED } from "../lib/problems.js";

const pct = (x) => `${Math.round(x * 100)}%`;

export function renderRanks() {
  const pts = points();
  const me = rankOf(pts).cur;
  const belts = LADDER.map((k) => {
    const ps = LISTED.filter((p) => p.kyu === k);
    const answers = ps.filter((p) => p.type === "answer").length;
    return `<tr>
      <th scope="row">${badge(k)}<span class="sr-only"> ${KYU[k].belt} belt</span></th>
      <td class="anchor">${KYU[k].anchor}</td>
      <td class="num">${KYU[k].pts}</td>
      <td class="num">${answers}</td>
      <td class="num">${ps.length - answers}</td>
    </tr>`;
  }).join("");
  const thresholds = RANKS.map((r, i) => {
    const next = RANKS[i + 1];
    const solves = next && r.k ? Math.ceil((next.min - r.min) / KYU[r.k].pts) : null;
    return `<tr class="${r === me ? "you" : ""}">
      <th scope="row">${badge(r.k, r.label)}${r === me ? ` <span class="faint">you</span>` : ""}</th>
      <td class="num">${r.min.toLocaleString("en-GB")}</td>
      <td class="num">${solves === null ? "–" : solves}</td>
    </tr>`;
  }).join("");
  const worth = KYU[5].pts;
  $("v-ranks").innerHTML = `
  <div><div class="eyebrow">The ladder</div><h1 class="h2">Ranks and belts</h1>
    <p class="muted lede-s">Problems carry a kyu from ${LADDER[0]} (warm-ups) to ${LADDER[LADDER.length - 1]} (the hardest olympiad problems). You carry a rank, which rises with the points you've earned.</p></div>
  <section class="panel flush">
    <h2 class="sub pad" id="beltsH">Problem belts</h2>
    <div class="tablebox bare" tabindex="0" role="region" aria-labelledby="beltsH"><table class="fit">
      <thead><tr><th scope="col">Kyu</th><th scope="col">Contest level</th><th scope="col" class="num">Points</th><th scope="col" class="num">Answer</th><th scope="col" class="num">Proof</th></tr></thead>
      <tbody>${belts}</tbody>
    </table></div>
    <p class="faint pad">Answer and proof columns count the problems in the bank today (${LISTED.length} in all).</p>
  </section>
  <div class="two">
    <section class="panel flush">
      <h2 class="sub pad" id="ranksH">Your rank</h2>
      <div class="tablebox bare" tabindex="0" role="region" aria-labelledby="ranksH"><table class="fit">
        <thead><tr><th scope="col">Rank</th><th scope="col" class="num">Points needed</th><th scope="col" class="num">Solves to next</th></tr></thead>
        <tbody>${thresholds}</tbody>
      </table></div>
      <p class="faint pad">Solves to next counts hint-free solves at the rank's own kyu. Dan ranks are points alone. You have ${pts} ${pts === 1 ? "point" : "points"}.</p>
    </section>
    <section class="panel" aria-labelledby="scoreH">
      <h2 class="sub" id="scoreH">How a solve scores</h2>
      <dl class="rules">
        <dt>Hints</dt><dd>Each hint you open takes off ${pct(HINT_COST)} of the points, down to ${pct(MIN_HINT_SHARE)} at the least. A ${worth}-point problem with one hint is worth ${Math.round(worth * (1 - HINT_COST))}.</dd>
        <dt>Wrong answers</dt><dd>They cost nothing on the problem page. In a duel, each one locks your box for 15 seconds.</dd>
        <dt>Proofs</dt><dd>Points are the problem's value × your mark ÷ ${PROOF_MARKS}, so ${PROOF_MARKS}/${PROOF_MARKS} earns all of it. For now you mark yourself against the rubric, and the points stay provisional.</dd>
      </dl>
      <div class="cta"><a class="btn primary" href="#problems">Browse problems</a><a class="btn" href="#home-quiz">Find your level</a></div>
    </section>
  </div>`;
}
