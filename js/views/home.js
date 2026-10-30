// The landing page: pitch, belt rack, today's problem and the placement quiz.
import { $, dayIndex, esc, errorPanel } from "../lib/ui.js";
import { KYU, LADDER, badge, rankOf } from "../lib/ranks.js";
import { S, points, myKyu } from "../lib/store.js";
import { LISTED, getProblem, randomUnsolved } from "../lib/problems.js";
import { texWhenVisible } from "../lib/tex.js";
import { renderQuiz } from "./quiz.js";

function welcomeBack() {
  const pts = points();
  if (!pts && !S.placement) return "";
  const k = myKyu();
  return `<div class="panel back-strip">
    <div>${badge(rankOf(pts).cur.k, rankOf(pts).cur.label)} <b>Welcome back, ${esc(S.handle)}.</b> <span class="muted">${pts} pts, practising at ${k} kyu.</span></div>
    <button class="btn small primary" type="button" id="homeRandom">Random unsolved at my rank</button>
  </div>`;
}

async function fillPotd(entry) {
  const box = $("potdBox");
  try {
    const p = await getProblem(entry.id);
    if (!$("potdBox") || box !== $("potdBox")) return;
    box.innerHTML = p.statement;
    box.removeAttribute("role");
    texWhenVisible(box);
  } catch { box.innerHTML = errorPanel("today's problem"); }
}

export function renderHome() {
  const answers = LISTED.filter((p) => p.type === "answer");
  const potd = answers.length ? answers[dayIndex() % answers.length] : null;
  const level = myKyu();
  const placed = points() > 0 || S.placement;
  const rows = LADDER.map((k) => {
    const ps = LISTED.filter((p) => p.kyu === k);
    const proof = ps.some((p) => p.type === "proof"), ans = ps.some((p) => p.type === "answer");
    const mode = (ans ? `<span class="mode-tag">answer</span>` : "") + (proof ? `<span class="mode-tag proof">proof</span>` : "");
    return `<a class="rack-row" href="#problems-k${k}"${placed && k === level ? ` aria-current="true"` : ""}>${badge(k)}<span class="anchor">${KYU[k].anchor}${mode}</span><span class="r">+${KYU[k].pts} pts · ${ps.length}</span></a>`;
  }).join("");
  $("v-home").innerHTML = `
  ${welcomeBack()}
  <div class="hero">
    <div>
      <div class="eyebrow">Contest maths, belt by belt</div>
      <h1>From your first AMC to <em>IMO Problem 6</em></h1>
      <p class="lede">Kyuclid ranks competition problems like martial-arts belts. Start with 8 kyu warm-ups, climb to 1 kyu olympiad proofs, and race a ghost on the same problem with the clock running.</p>
      <div class="cta"><a class="btn primary" href="#home-quiz" id="ctaQuiz">Find your level</a><a class="btn" href="#problems">Browse all ${LISTED.length} problems</a></div>
      <ul class="facts">
        <li><b>Answers</b> checked the moment you submit</li>
        <li><b>Proofs</b> marked out of 7 against a rubric</li>
        <li><b>Progress</b> saved in this browser, no sign-up</li>
      </ul>
    </div>
    <nav class="rack" aria-labelledby="rackH">
      <div class="rack-h"><h2 class="eyebrow" id="rackH">The belt rack</h2><span class="faint">pts per solve · problems · <a href="#ranks">how ranks work</a></span></div>
      ${rows}
    </nav>
  </div>

  <div class="home-two">
    <section class="panel potd" aria-labelledby="potdH">
      <div class="quiz-head"><h2 class="sub" id="potdH">Today's problem</h2>${potd ? badge(potd.kyu) : ""}</div>
      ${potd ? `<p class="potd-title"><b>${esc(potd.title)}</b></p>
      <div class="stmt" id="potdBox" role="status"><span class="spinner" aria-hidden="true"></span>Loading…</div>
      <div class="cta"><a class="btn primary" href="#p-${potd.id}">Answer it</a></div>` : `<p class="muted">There's no problem to show yet. New ones are on the way.</p>`}
    </section>
    <section class="panel quiz" id="quiz" aria-labelledby="quizH"></section>
  </div>

  <div class="three">
    <div class="panel"><h2 class="sub">Solve</h2><p>From 8 kyu to 4 kyu every problem has a single numerical answer, checked the moment you submit, the way AIME and UKMT are marked. 3 kyu mixes answers and proofs. Solutions unlock once you have it right.</p></div>
    <div class="panel"><h2 class="sub">Prove</h2><p>At 2 and 1 kyu, and for some 3 kyu problems, you write proofs. Your write-up will go to two reviewers ranked above the problem, who mark it out of 7 like an olympiad script. For now you self-grade against the official rubric.</p></div>
    <div class="panel"><h2 class="sub">Duel</h2><p>One problem, one clock. First correct answer wins, and a wrong answer locks you out for 15 seconds, so guessing costs time. Today you race a timed ghost, and duels carry their own Elo rating.</p></div>
  </div>

  <div class="draft">
    <h2 class="sub">What this first draft does and doesn't do</h2>
    <ul>
      <li>There are ${LISTED.length} problems so far, across all eight kyu.</li>
      <li>Answers are checked against hashes in the page, and your progress lives in this browser only.</li>
      <li>Friend duels, accounts, peer review and problem submission need a backend, which comes later.</li>
      <li>The leaderboard shows sample players so you can see the layout.</li>
    </ul>
  </div>`;
  renderQuiz();
  if (potd) fillPotd(potd);
  if ($("homeRandom")) $("homeRandom").addEventListener("click", () => { const p = randomUnsolved(); location.hash = p ? "#p-" + p.id : "#problems"; });
  $("ctaQuiz").addEventListener("click", (e) => { e.preventDefault(); showQuiz(); });
}

// Scrolls to the quiz without leaving the home route. #home-quiz is a route so other views can link here.
export function showQuiz() {
  const q = $("quiz");
  if (!q) return;
  q.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
  const go = $("quizGo") || q.querySelector("input, button, a");
  if (go) go.focus({ preventScroll: true });
}
