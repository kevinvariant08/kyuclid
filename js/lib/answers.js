// Answer checking. Answers are stored as salted hashes, never in plain text:
// answer_hash = fnv(id + "|" + canon(answer)). scripts/hash-answer.mjs imports these
// same functions, so keep this module free of browser globals.

// The canonical form of a numerical answer: the value rounded to 6 decimal places,
// without trailing zeros, so "25/4", "6.25" and "6.250" all become "6.25".
// Returns null for anything that isn't a number, a decimal or a fraction.
export function canon(s) {
  s = String(s).trim().replace(/\s+/g, "").replace(/,/g, "").replace(/^\+/, "");
  let v;
  const m = s.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
  if (m) v = Number(m[1]) / Number(m[2]);
  else if (/^-?(\d+\.?\d*|\.\d+)$/.test(s)) v = Number(s);
  else return null;
  if (!isFinite(v)) return null;
  return String(Math.round(v * 1e6) / 1e6);
}

// 32-bit FNV-1a, as 8 lowercase hex digits.
export function fnv(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(16).padStart(8, "0");
}

export const hashAnswer = (id, answer) => { const c = canon(answer); return c === null ? null : fnv(id + "|" + c); };

// true if right, false if wrong, null if the input isn't a number at all.
export const check = (p, input) => { const c = canon(input); return c === null ? null : fnv(p.id + "|" + c) === p.answer_hash; };
