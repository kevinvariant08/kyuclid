// Lets the Python gate use the site's own canon() and hash, so there is one definition of "same answer".
// stdin: {"canon":["25/4",...],"hash":[["some-id","25/4"],...]}  stdout: {"canon":["6.25",...],"hash":["a7169a50",...]}
import { readFileSync } from "node:fs";
import { canon, hashAnswer } from "../../../js/lib/answers.js";

const req = JSON.parse(readFileSync(0, "utf8"));
console.log(JSON.stringify({
  canon: (req.canon || []).map((s) => canon(s)),
  hash: (req.hash || []).map(([id, a]) => hashAnswer(id, a)),
}));
