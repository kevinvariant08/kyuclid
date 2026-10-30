// Prints the answer_hash for a problem, with the same canon() and fnv() the site uses.
//   node scripts/hash-answer.mjs circle-in-the-square 25/4    ->  a7169a50
import { canon, fnv } from "../js/lib/answers.js";

const [id, answer] = process.argv.slice(2);
if (!id || answer === undefined) {
  console.error("Usage: node scripts/hash-answer.mjs <id> <answer>");
  process.exit(2);
}
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(id)) {
  console.error(`"${id}" is not a kebab-case id.`);
  process.exit(2);
}
const c = canon(answer);
if (c === null) {
  console.error(`"${answer}" is not a number, a decimal or a fraction, so the site can't check it.`);
  process.exit(1);
}
console.error(`canonical form: ${c}`);
console.log(fnv(id + "|" + c));
