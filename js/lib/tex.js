// MathJax. The config and the script tag stay in index.html's <head> so MathJax starts
// downloading at once; its startup.ready hook sets window.__mjReady.
let mjChain = Promise.resolve();
export function tex(el) {
  const MJ = window.MathJax;
  if (!window.__mjReady || !MJ || !MJ.typesetPromise) return;
  mjChain = mjChain.then(() => { if (MJ.typesetClear) MJ.typesetClear([el]); return MJ.typesetPromise([el]); }).catch(() => {});
}

// Blank lines separate paragraphs.
export const paras = (s) => s.split(/\n\s*\n/).map((x) => `<p>${x}</p>`).join("");
