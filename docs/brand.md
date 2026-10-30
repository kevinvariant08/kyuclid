# Kyuclid brand sheet

**Kyuclid** = *kyu* (the martial-arts rank) + *Euclid*. Say it "KYOO-klid". In running text write **Kyuclid**: not KyuClid, Kyu-clid or KYUCLID (capitals are only for the wordmark). Kevin chose the name on 30 Oct 2026 to replace "MathWars"; [name-report.md](name-report.md) explains why.

The identity carries over from the MathWars draft unchanged: a red seal with ∴, Big Shoulders Display with IBM Plex, a cool grey-blue light theme with a navy dark theme, and martial-arts belts for the kyu ranks.

## Copy

**Tagline:** Contest maths, belt by belt.

**Kevinvariant link card** (replaces the MathWars paragraph in Kevinvariant's `compete.html`; once live duels ship (task 14), change "a timed ghost" to "another solver"):

> Kyuclid ranks contest problems like martial-arts belts, from 8 kyu warm-ups at UKMT Junior and AMC 8 level up to 1 kyu IMO proofs. Answers are checked instantly, proofs are marked against a rubric, and you can duel a timed ghost on the same problem. Every solve earns points and moves you up the belts. A separate site, still a first draft.

**Kevinvariant menu note** (`site.js`): Ranked contest problems, 8 kyu to IMO

**Social bios:**

| Where | Text |
|---|---|
| X / Bluesky / Threads (≤160) | Contest maths, belt by belt. Ranked problems from 8 kyu warm-ups to 1 kyu IMO proofs. Solve, climb, duel. A Kevinvariant project. |
| Instagram / TikTok (≤80) | Contest maths, belt by belt. 8 kyu → IMO. |
| GitHub repo description | Kyuclid: a ranked dojo for contest maths, from 8 kyu warm-ups to 1 kyu IMO proofs. |
| YouTube / Discord (longer) | Kyuclid is a ranked dojo for competition maths. Every problem has a belt, from 8 kyu warm-ups at UKMT Junior and AMC 8 level to 1 kyu olympiad proofs. Solve to earn points, climb the belts and duel a timed ghost on the same problem. Made by Kevin Hu, a Kevinvariant project. |

**Voice:** plain British English (maths, colour, practise as a verb). Short, specific sentences. Name the contests (AMC, AIME, UKMT, BMO, IMO) rather than saying "competitions". The dojo framing is a seasoning: use "belt", "kyu" and "dan" because they're the rank system, and skip "sensei", "grasshopper" and similar.

## Logo

| File | Use |
|---|---|
| `assets/logo/kyuclid-horizontal.svg` | Main logo on light backgrounds |
| `assets/logo/kyuclid-horizontal-dark.svg` | Main logo on dark backgrounds |
| `assets/logo/kyuclid-square.svg`, `-square-dark.svg` | Avatars, link cards and anywhere square: seal above the wordmark on a solid tile |
| `assets/logo/kyuclid-wordmark.svg`, `-wordmark-dark.svg` | Wordmark alone, where the seal is already shown nearby |
| `assets/logo/kyuclid-seal.svg` | The seal alone (transparent) |
| `assets/favicon.svg`, `assets/icons/*` | Browser and app icons (see below) |

**Construction.**
- **Seal:** a rounded square (corner radius 6/34 of its side), tilted **−4°**, in seal red, with **∴** ("therefore") drawn as three dots in white.
- **Wordmark:** KYUCLID set in Big Shoulders Display 900, tracked +0.06 em, then converted to outlines so it renders without the font.
- **Lockup:** the seal is 1.63× the cap height and sits 0.48 × cap height from the wordmark. These are the same proportions as the site header (34 px seal, 26 px wordmark, 10 px gap).
- **Favicon cut:** the favicon and app icons use bigger dots so the ∴ survives at 16–32 px.

**Usage.**
- **Clear space:** leave at least half the seal's width clear on every side of the logo.
- **Minimum size:** the horizontal logo is 96 px wide. Below that, use the seal alone.
- **Backgrounds:** on photos or busy backgrounds, put the logo on a solid tile.
- **Don't:**
  - straighten or re-tilt the seal;
  - set the wordmark in another typeface;
  - recolour the seal outside the two seal reds;
  - add effects.

## Colour

Tokens are the CSS custom properties in `index.html`. The dark theme applies when `prefers-color-scheme: dark` is set, unless `data-theme="light"` overrides it, or when `data-theme="dark"` is set.

| Token | Role | Light | Dark |
|---|---|---|---|
| `--bg` | page background | `#EEF0F4` | `#10121B` |
| `--surface` | cards, top bar | `#FFFFFF` | `#181B28` |
| `--sunk` | hover, wells | `#E4E7EE` | `#0C0E15` |
| `--line` | borders | `#CED3DE` | `#2B3046` |
| `--line-soft` | dividers | `#E0E3EA` | `#22263A` |
| `--ink` | text | `#1B1E33` | `#E7E9F1` |
| `--ink-soft` | secondary text | `#474B63` | `#AEB3C8` |
| `--ink-faint` | captions, meta | `#62667E` | `#8E94AC` |
| `--seal` | seal, primary buttons, accents | `#B42318` | `#E5534B` |
| `--seal-hover` | primary hover | `#951B12` | `#F0716A` |
| `--on-seal` | text and dots on seal | `#FFFFFF` | `#16070A` |
| `--ok` | correct | `#22744C` | `#4CC38A` |
| `--bad` | wrong | `#B8304F` | `#FF7A93` |
| `--focus` | links, focus rings | `#3640A8` | `#9AA3FF` |

Red is the only accent. Keep it for the seal, primary actions and one highlighted word, and let the belts carry the rest of the colour.

## Belts

The kyu badge is a belt: a strip in the belt colour with a short dark tape near the right end. Belt colours mean rank and nothing else, so don't use them for decoration. Points per solve follow the Fibonacci numbers.

| Rank | Belt | Fill | Label ink | Tape | Points |
|---|---|---|---|---|---|
| 8 kyu | White | `#F4F4F1` | `#1B1E33` | `#15161C` | 2 |
| 7 kyu | Yellow | `#E9C440` | `#1B1E33` | `#15161C` | 3 |
| 6 kyu | Orange | `#E5832A` | `#1B1E33` | `#15161C` | 5 |
| 5 kyu | Green | `#2E8B4E` | `#FFFFFF` | `#15161C` | 8 |
| 4 kyu | Blue | `#2A64C8` | `#FFFFFF` | `#15161C` | 13 |
| 3 kyu | Purple | `#6E43B8` | `#FFFFFF` | `#15161C` | 21 |
| 2 kyu | Brown | `#7A4A2B` | `#FFFFFF` | `#15161C` | 34 |
| 1 kyu | Red | `#B8232A` | `#FFFFFF` | `#15161C` | 55 |
| dan | Black | `#15161C` | `#FFFFFF` | `#B8232A` (red tape) | — (book bosses) |

Every badge has a 1 px inner outline at `rgba(0,0,0,.18)` so the white belt shows on light surfaces and the black belt shows on dark ones. The colours are defined once in `KYU` in `index.html`. The OG templates repeat them, so change all three together.

## Type

All four families are from Google Fonts under the SIL Open Font License.

| Family | Weights | Use |
|---|---|---|
| [Big Shoulders Display](https://fonts.google.com/specimen/Big+Shoulders+Display) | 800, 900 | Wordmark, headings, belt labels, big numbers. Always uppercase. Tracking +0.06 em for the wordmark, +0.08 em for belt labels and +0.01–0.03 em for headings. |
| [IBM Plex Sans](https://fonts.google.com/specimen/IBM+Plex+Sans) | 400–700 | Interface text and body copy |
| [IBM Plex Serif](https://fonts.google.com/specimen/IBM+Plex+Serif) | 400, 600, italic | Problem statements, hints and solutions: anything you read carefully. MathJax sits beside it. |
| [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono) | 400, 600 | Answers, points, clocks, ratings and other tabular numbers |

## Icons and link previews

| File | Size | Where it's used |
|---|---|---|
| `assets/favicon.svg` | vector | `<link rel="icon">` (modern browsers) |
| `assets/icons/favicon-32.png`, `favicon-16.png` | 32, 16 | PNG fallback icons |
| `assets/icons/apple-touch-icon.png` | 180 | iOS home screen: seal on navy, opaque |
| `assets/icons/icon-192.png`, `icon-512.png` | 192, 512 | Web app manifest, `purpose: any` (transparent) |
| `assets/icons/icon-maskable-192.png`, `-512.png` | 192, 512 | Manifest, `purpose: maskable`: seal inside the 80 % safe zone on navy |
| `site.webmanifest` | — | Scope and start URL `/mathwars/`, so Kyuclid installs separately from Kevinvariant on the same origin |
| `assets/og/og-home.png` | 1200×630 | Home page `og:image` and `twitter:image` |
| `assets/og/problem-template.html` | 1200×630 | Per-problem card: belt, title, topic and answer or proof (example: `assets/og/problem-example.png`) |

**Link previews** use the dark navy card for the home page and the light card for problems, so the two are easy to tell apart in a feed. A problem card shows only the title, belt, topic and mode, never the statement: contest problem text must stay out of this repo (see rule 1 in `tasks/README.md`).

**Problem pages can't use their cards yet.** Problems live at `#p-<id>`, and link-preview crawlers ignore the part after `#` and don't run JavaScript, so every problem link currently previews as the home page. A problem's card can only be used once the problem has its own static URL with its own `og:image` tags. That is for task 01 or 12 to decide.

**Regenerating.** Install fontTools and Pillow, and have Chrome or Edge available.
- `python tools/brand/build_logos.py <BigShouldersDisplay-900.ttf>` rebuilds every SVG.
- `python tools/brand/render_png.py icons` renders the favicon and app-icon PNGs.
- `python tools/brand/render_png.py og` renders `og-home.png`.
- `python tools/brand/render_png.py problem --id … --title … --kyu … --topic … --mode Answer|Proof` renders one problem card.

After any change, bump `?v=` in `index.html` and `site.webmanifest`. Kevinvariant's service worker caches images forever, so without a new `?v=`, browsers keep the old icon.
