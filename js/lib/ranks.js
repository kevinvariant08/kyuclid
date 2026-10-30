// Ranks: kyu belts, points grow like Fibonacci.
export const KYU = {
  8: { belt: "White",  bg: "#F4F4F1", ink: "#1B1E33", tape: "#15161C", pts: 2,  anchor: "<b>Warm-ups.</b> UKMT Junior, AMC 8 openers" },
  7: { belt: "Yellow", bg: "#E9C440", ink: "#1B1E33", tape: "#15161C", pts: 3,  anchor: "<b>UKMT Intermediate</b>, AMC 8 finishers" },
  6: { belt: "Orange", bg: "#E5832A", ink: "#1B1E33", tape: "#15161C", pts: 5,  anchor: "<b>AMC 10/12 middle</b>, UKMT Senior, TMUA" },
  5: { belt: "Green",  bg: "#2B864B", ink: "#FFFFFF", tape: "#15161C", pts: 8,  anchor: "<b>AMC 12 late</b>, AIME 1–5, MAT" },
  4: { belt: "Blue",   bg: "#2A64C8", ink: "#FFFFFF", tape: "#15161C", pts: 13, anchor: "<b>AIME 6–10</b>, BMO1 Q1–3" },
  3: { belt: "Purple", bg: "#6E43B8", ink: "#FFFFFF", tape: "#15161C", pts: 21, anchor: "<b>AIME 11–15</b>, BMO1 late, BMO2 openers" },
  2: { belt: "Brown",  bg: "#7A4A2B", ink: "#FFFFFF", tape: "#15161C", pts: 34, anchor: "<b>IMO P1/P4</b>, BMO2, USAMO" },
  1: { belt: "Red",    bg: "#B8232A", ink: "#FFFFFF", tape: "#15161C", pts: 55, anchor: "<b>IMO P3/P6.</b> Weeks, sometimes months" },
  0: { belt: "Black",  bg: "#15161C", ink: "#FFFFFF", tape: "#B8232A", pts: 0,  anchor: "" }
};
export const RANKS = [
  { label: "8 kyu", k: 8, min: 0 }, { label: "7 kyu", k: 7, min: 6 }, { label: "6 kyu", k: 6, min: 15 },
  { label: "5 kyu", k: 5, min: 30 }, { label: "4 kyu", k: 4, min: 60 }, { label: "3 kyu", k: 3, min: 110 },
  { label: "2 kyu", k: 2, min: 190 }, { label: "1 kyu", k: 1, min: 320 }, { label: "1 dan", k: 0, min: 520 },
  { label: "2 dan", k: 0, min: 850 }, { label: "3 dan", k: 0, min: 1300 }, { label: "4 dan", k: 0, min: 1900 }
];
// How a solve turns into points. store.js scores with these and the #ranks page quotes them.
export const HINT_COST = 0.25;       // share of the points each opened hint removes
export const MIN_HINT_SHARE = 0.25;  // the least a solve can be worth after hints
export const PROOF_MARKS = 7;        // proofs score points x grade / 7
export const LADDER = [8, 7, 6, 5, 4, 3, 2, 1];
export const badge = (k, label, cls = "") => {
  const b = KYU[k];
  return `<span class="kyu ${cls}" style="--belt:${b.bg};--belt-ink:${b.ink};--tape:${b.tape}">${label || k + " kyu"}</span>`;
};
export const rankOf = (pts) => {
  let i = 0; while (i + 1 < RANKS.length && pts >= RANKS[i + 1].min) i++;
  const cur = RANKS[i], next = RANKS[i + 1] || null;
  const frac = next ? (pts - cur.min) / (next.min - cur.min) : 1;
  return { cur, next, frac };
};
export const TOPICS = { A: "Algebra", C: "Combinatorics", G: "Geometry", N: "Number theory" };
