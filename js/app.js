// Boot and router. Routes are bare hash tokens: #home, #problems, #p-<id>, #duel, #profile, #leaderboard.
import { $, renderMe } from "./lib/ui.js";
import { loadIndex } from "./lib/problems.js";
import { renderHome } from "./views/home.js";
import { renderProblems } from "./views/problems.js";
import { renderProblem } from "./views/problem.js";
import { D, stopDuel, renderDuelSetup } from "./views/duel.js";
import { renderProfile } from "./views/profile.js";
import { renderBoard } from "./views/leaderboard.js";

const failed = (view) => () => {
  $("v-" + view).innerHTML = `<div class="panel">This page couldn't load its problems. Check your connection and <a href="">reload</a>.</div>`;
};

function route() {
  const h = (location.hash || "#home").slice(1);
  let view = h, arg = null;
  if (h.startsWith("p-")) { view = "problem"; arg = h.slice(2); }
  if (!["home", "problems", "problem", "duel", "profile", "leaderboard"].includes(view)) view = "home";
  if (view !== "duel") stopDuel();
  document.querySelectorAll("main > .view").forEach((s) => { s.hidden = s.id !== "v-" + view; });
  document.querySelectorAll("#nav a").forEach((a) => a.toggleAttribute("aria-current", a.dataset.v === view || (view === "problem" && a.dataset.v === "problems")));
  document.querySelectorAll("#nav a[aria-current]").forEach((a) => a.setAttribute("aria-current", "page"));
  let done;
  if (view === "home") done = renderHome();
  if (view === "problems") renderProblems();
  if (view === "problem") done = renderProblem(arg);
  if (view === "duel" && !D.live) renderDuelSetup();
  if (view === "profile") renderProfile();
  if (view === "leaderboard") renderBoard();
  if (done) done.catch(failed(view));
  window.scrollTo(0, 0);
}

renderMe();
loadIndex().then(() => {
  window.addEventListener("hashchange", route);
  route();
}, () => { $("v-home").hidden = false; failed("home")(); });
