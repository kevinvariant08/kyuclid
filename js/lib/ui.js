// Small shared pieces of the page.
import { S, points } from "./store.js";
import { badge, rankOf } from "./ranks.js";

export const $ = (id) => document.getElementById(id);
export const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function renderMe() {
  const pts = points(); const r = rankOf(pts);
  $("meChip").innerHTML = `${badge(r.cur.k, r.cur.label)}<span class="pts">${pts} pts</span>`;
}

export const statusTag = (p) => {
  const s = S.solved[p.id];
  if (s && s.how === "proof") return `<span class="status review">Self-graded ${s.grade}/7</span>`;
  if (s) return `<span class="status solved">Solved</span>`;
  if (S.proofs[p.id] && S.proofs[p.id].submitted) return `<span class="status review">In review</span>`;
  return "";
};

export const dayIndex = () => Math.floor(Date.now() / 86400000);

// What the list and the problem page say about where a problem comes from.
export const sourceLine = (p) => (p.provenance ? p.provenance.source : p.source);
export const authorOf = (p) => (p.provenance ? p.provenance.author : p.author);
