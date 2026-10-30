// This browser's progress, under the localStorage key mathwars:v1.
import { KYU } from "./ranks.js";

const KEY = "mathwars:v1";
const fresh = () => ({ handle: "you", solved: {}, tries: {}, hints: {}, proofs: {}, votes: {}, duel: { rating: 1200, w: 0, l: 0, d: 0 }, log: [] });

// S is one object for the whole session; resetState() empties it in place so every importer sees the change.
export const S = fresh();
try { const raw = localStorage.getItem(KEY); if (raw) Object.assign(S, JSON.parse(raw)); } catch {}

export const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch {} };
export const resetState = () => { for (const k of Object.keys(S)) delete S[k]; Object.assign(S, fresh()); save(); };
export const points = () => Object.values(S.solved).reduce((a, s) => a + s.pts, 0);
export const logEvent = (text) => { S.log.unshift({ at: Date.now(), text }); S.log = S.log.slice(0, 30); };

// p needs id, kyu and title, so an index entry or a full problem both work.
export function award(p, how, grade) {
  if (S.solved[p.id]) return 0;
  const base = KYU[p.kyu].pts;
  const usedHints = S.hints[p.id] || 0;
  let pts = Math.max(1, Math.round(base * Math.max(0.25, 1 - 0.25 * usedHints)));
  if (grade !== undefined) pts = Math.round(base * grade / 7);
  S.solved[p.id] = { at: Date.now(), pts, how, grade };
  logEvent(`${how === "duel" ? "Won a duel on" : how === "proof" ? "Self-graded " + grade + "/7 on" : "Solved"} ${p.title} (+${pts})`);
  save();
  return pts;
}
