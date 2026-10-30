// Small shared pieces of the page.
import { S, points } from "./store.js";
import { badge, rankOf } from "./ranks.js";

export const $ = (id) => document.getElementById(id);
export const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function renderMe() {
  const pts = points(); const r = rankOf(pts);
  const chip = $("meChip");
  chip.setAttribute("aria-label", `Your rank: ${r.cur.label}, ${pts} points. Open your profile.`);
  chip.innerHTML = `${badge(r.cur.k, r.cur.label)}<span class="pts">${pts} pts</span>`;
}

export const statusTag = (p) => {
  const s = S.solved[p.id];
  if (s && s.how === "proof") return `<span class="status review">Self-graded ${s.grade}/7</span>`;
  if (s) return `<span class="status solved">Solved</span>`;
  if (S.proofs[p.id] && S.proofs[p.id].submitted) return `<span class="status review">In review</span>`;
  return "";
};

export const dayIndex = () => Math.floor(Date.now() / 86400000);
export const fmtDate = (t) => new Date(t).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

// What the list and the problem page say about where a problem comes from.
export const sourceLine = (p) => (p.provenance ? p.provenance.source : p.source);
export const authorOf = (p) => (p.provenance ? p.provenance.author : p.author);

// Shown when a view can't fetch what it needs.
export const errorPanel = (what) => `<div class="panel state" role="alert"><h1 class="h2">Couldn't load ${what}</h1><p class="muted">Check your connection and <a href="">reload the page</a>. Your progress is safe in this browser.</p></div>`;
export const loadingPanel = (what) => `<div class="panel state" role="status"><span class="spinner" aria-hidden="true"></span>Loading ${what}…</div>`;
