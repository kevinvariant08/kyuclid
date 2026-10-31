// MathJax dry run: compiles each TeX snippet with the version the site loads and reports errors.
// stdin: [{"tex":"x^2","display":false},...]  stdout: [null | "error message", ...]
// Exits 3 if mathjax-full isn't installed (run npm ci), and the gate then falls back to a balance check.
import { readFileSync } from "node:fs";

let mj;
try {
  const [{ mathjax }, { TeX }, { liteAdaptor }, { RegisterHTMLHandler }, { STATE }] = await Promise.all([
    import("mathjax-full/js/mathjax.js"),
    import("mathjax-full/js/input/tex.js"),
    import("mathjax-full/js/adaptors/liteAdaptor.js"),
    import("mathjax-full/js/handlers/html.js"),
    import("mathjax-full/js/core/MathItem.js"),
    import("mathjax-full/js/input/tex/ams/AmsConfiguration.js"),
  ]);
  RegisterHTMLHandler(liteAdaptor());
  const input = new TeX({ packages: ["base", "ams"], formatError: (_, err) => { throw err; } });
  const doc = mathjax.document("", { InputJax: input });
  mj = (tex, display) => doc.convert(tex, { display, end: STATE.COMPILED });
} catch (e) {
  if (e.code === "ERR_MODULE_NOT_FOUND") process.exit(3);
  throw e;
}

const out = JSON.parse(readFileSync(0, "utf8")).map(({ tex, display }) => {
  try { mj(tex, display); return null; }
  catch (e) { return String(e.message || e); }
});
console.log(JSON.stringify(out));
