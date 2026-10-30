import { $, esc, renderMe } from "../lib/ui.js";
import { KYU, badge, rankOf, TOPICS } from "../lib/ranks.js";
import { S, save, points, resetState } from "../lib/store.js";
import { LISTED, byId } from "../lib/problems.js";

let confirmReset = false;
export function renderProfile() {
  const pts = points(); const r = rankOf(pts);
  const solvedList = Object.keys(S.solved).map((id) => byId[id]).filter(Boolean);
  const topicCount = (t) => solvedList.filter((p) => p.topic === t).length;
  const topicTotal = (t) => LISTED.filter((p) => p.topic === t).length;
  $("v-profile").innerHTML = `
  <div class="panel">
    <div class="prof-head">
      ${badge(r.cur.k, r.cur.label, "lg")}
      <div style="flex:1;min-width:0">
        <label class="eyebrow" for="handle">Your handle</label><br>
        <input id="handle" value="${esc(S.handle)}" maxlength="24" spellcheck="false">
      </div>
    </div>
    <div style="margin-top:18px">
      <div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(r.frac * 100)}" aria-label="Progress to next rank"><i style="width:${Math.max(2, r.frac * 100)}%"></i></div>
      <div class="faint">${r.next ? `${pts} pts. ${r.next.min - pts} more to ${r.next.label}.` : `${pts} pts. Top rank.`}</div>
    </div>
  </div>
  <div class="tiles">
    <div class="tile"><span class="eyebrow">Points</span><b>${pts}</b></div>
    <div class="tile"><span class="eyebrow">Solved</span><b>${solvedList.length}<span class="faint" style="font-family:var(--f-body)"> / ${LISTED.length}</span></b></div>
    <div class="tile"><span class="eyebrow">Duel rating</span><b>${Math.round(S.duel.rating)}</b></div>
    <div class="tile"><span class="eyebrow">Duels</span><b>${S.duel.w}–${S.duel.l}–${S.duel.d}</b></div>
  </div>
  <div class="two">
    <div class="panel"><b>By topic</b>
      <div class="bars" style="margin-top:12px">${Object.entries(TOPICS).map(([t, n]) => `<div class="bar"><span>${n}</span><span class="track"><i style="width:${(topicCount(t) / topicTotal(t)) * 100}%"></i></span><span class="n">${topicCount(t)}/${topicTotal(t)}</span></div>`).join("")}</div>
      <b style="display:block;margin-top:20px">By kyu</b>
      <div class="bars" style="margin-top:12px">${[8, 7, 6, 5, 4, 3, 2, 1].map((k) => { const tot = LISTED.filter((p) => p.kyu === k).length, c = solvedList.filter((p) => p.kyu === k).length; return `<div class="bar"><span>${badge(k)}</span><span class="track"><i style="width:${(c / tot) * 100}%;background:${KYU[k].bg}"></i></span><span class="n">${c}/${tot}</span></div>`; }).join("")}</div>
    </div>
    <div class="panel"><b>Recent activity</b>
      ${S.log.length ? `<ul class="log" style="margin-top:12px">${S.log.slice(0, 12).map((e) => `<li><span>${esc(e.text)}</span><span class="faint">${new Date(e.at).toLocaleDateString("en-GB", { day: "numeric", month: "short" })}</span></li>`).join("")}</ul>` : `<p class="faint">Nothing yet. Solve a problem or start a duel and it shows up here.</p>`}
      <div class="confirm" style="margin-top:18px" id="resetBox">
        ${confirmReset ? `<span>Erase all progress in this browser?</span><button class="btn small primary" type="button" id="resetYes">Erase</button><button class="btn small" type="button" id="resetNo">Keep it</button>` : `<button class="btn small ghost" type="button" id="resetBtn">Reset progress</button>`}
      </div>
    </div>
  </div>`;
  $("handle").addEventListener("change", (e) => { S.handle = e.target.value.trim().slice(0, 24) || "you"; save(); });
  if ($("resetBtn")) $("resetBtn").addEventListener("click", () => { confirmReset = true; renderProfile(); });
  if ($("resetNo")) $("resetNo").addEventListener("click", () => { confirmReset = false; renderProfile(); });
  if ($("resetYes")) $("resetYes").addEventListener("click", () => { resetState(); confirmReset = false; renderMe(); renderProfile(); });
}
