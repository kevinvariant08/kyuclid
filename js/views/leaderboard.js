// Leaderboard, with sample players until there are accounts.
import { $, esc } from "../lib/ui.js";
import { badge, rankOf } from "../lib/ranks.js";
import { S, points } from "../lib/store.js";

const SAMPLE = [
  ["vieta_jumper", 2140, 1912], ["cauchy_crusher", 1610, 1840], ["incircle_ivy", 1205, 1755], ["lemma_lad", 890, 1690],
  ["pigeonhole_pat", 744, 1622], ["modular_mo", 512, 1580], ["telescoper", 430, 1497], ["orthocentre_ollie", 318, 1441],
  ["am_gm_amy", 260, 1388], ["sieve_sam", 199, 1302], ["bashful_bash", 120, 1251], ["fermat_fan", 75, 1170]
];
let boardMode = "pts";
export function renderBoard() {
  const rows = SAMPLE.map(([h, p, r]) => ({ h, p, r, you: false }));
  rows.push({ h: S.handle, p: points(), r: Math.round(S.duel.rating), you: true });
  rows.sort((a, b) => boardMode === "pts" ? b.p - a.p : b.r - a.r);
  $("v-leaderboard").innerHTML = `
  <div class="list-head">
    <h1 class="h2">Leaderboard</h1>
    <div class="seg" role="group" aria-label="Rank by"><button type="button" data-m="pts" aria-pressed="${boardMode === "pts"}">Kyu points</button><button type="button" data-m="duel" aria-pressed="${boardMode === "duel"}">Duel rating</button></div>
  </div>
  <p class="sample" style="margin:0"><b>Sample players.</b> Everyone here except you is made up to show the layout. Real rankings need accounts.</p>
  <div class="tablebox" tabindex="0" role="region" aria-label="Leaderboard table"><table>
    <thead><tr><th scope="col" class="num">#</th><th scope="col">Player</th><th scope="col">Rank</th><th scope="col" class="num">Points</th><th scope="col" class="num">Duel rating</th></tr></thead>
    <tbody>${rows.map((x, i) => { const rk = rankOf(x.p).cur; return `<tr class="${x.you ? "you" : ""}"><td class="num">${i + 1}</td><td>${esc(x.h)}${x.you ? `<span class="here">You</span>` : ""}</td><td>${badge(rk.k, rk.label)}</td><td class="num">${x.p.toLocaleString("en-GB")}</td><td class="num">${x.r}</td></tr>`; }).join("")}</tbody>
  </table></div>`;
  $("v-leaderboard").querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", () => { boardMode = b.dataset.m; renderBoard(); }));
}
