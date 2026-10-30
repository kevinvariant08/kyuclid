# MathWars

A ranked dojo for contest maths, in the spirit of Codewars. Problems are graded on a kyu ladder from 8 kyu warm-ups (UKMT Junior, AMC 8) up to 1 kyu (IMO Problems 3 and 6).

A [Kevinvariant](https://kevinvariant08.github.io/) project. First draft.

## What's in the draft

- **21 seed problems** across all eight kyu, in algebra, combinatorics, geometry and number theory. Contest problems name their source.
- **Answer problems (8–3 kyu)** are checked instantly. Answers are stored as salted FNV-1a hashes, not in plain text.
- **Proof problems (3–1 kyu)** have a LaTeX editor with live preview. After submitting, you self-grade out of 7 against a rubric. Peer review is planned.
- **Duels** against a timed ghost opponent, with an Elo rating. A wrong answer locks you out for 15 seconds.
- **Profile** with rank progress, topic and kyu breakdowns, and an activity log.
- **Leaderboard** layout, filled with sample players.

Points per solve follow the Fibonacci numbers: 2, 3, 5, 8, 13, 21, 34, 55 from 8 kyu to 1 kyu.

## How it runs

It's one static `index.html` with no build step. MathJax 3 (SVG output) loads from jsDelivr and fonts load from Google Fonts. Progress is saved in `localStorage`, so it stays in one browser.

To run it locally:

```bash
python -m http.server 8000
```

Then open http://localhost:8000.

## Not built yet

Accounts, friend duels, real leaderboards, peer review of proofs and problem submission all need a backend.

## Adding a problem

Problems live in the `PROBLEMS` array in `index.html`. An answer problem needs `h`, the FNV-1a hash of `id + "|" + canonical answer`. The canonical form is the number rounded to 6 decimal places, written without trailing zeros, so `25/4` and `6.25` both become `6.25`. This Python snippet prints the hash:

```python
def fnv(s):
    h = 0x811c9dc5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xffffffff
    return format(h, "08x")

print(fnv("circle-in-the-square|6.25"))  # a7169a50
```
