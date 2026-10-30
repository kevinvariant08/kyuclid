# 12. Frontend polish for a bank of hundreds

## Goal
Make the site feel finished and work well with 500 or more problems: faster to browse, clearer to read, and comfortable on a phone.

## Depends on
01, the modular codebase.

## Read first
- `css/site.css` tokens (keep the identity: belt badges, the ∴ seal, the Big Shoulders / IBM Plex type pairing) and every view in `js/views/`.

## Spec
1. **Problem list at scale:**
   - Paginate or virtualise the list.
   - Search over title and subtopics, with filters for kyu, topic, subtopic, type and status, all kept in the URL hash (for example `#problems-k5-N`) so a filtered view can be shared.
   - A "random unsolved at my rank" button.
2. **Problem page:**
   - A comfortable reading measure.
   - Sticky answer box on mobile.
   - Keyboard flow: Enter submits, `h` opens the next hint, `n` goes to the next problem.
   - "Previous / next at this kyu".
   - A clear solved state.
   - Copy-link and report-a-problem buttons. The report button opens a short form that, for now, writes a GitHub issue link with the problem ID pre-filled.
3. **The kyu explainer page** (`#ranks`) shows the ladder, contest anchors, points and rank thresholds. It reads its numbers from data rather than prose.
4. **Home:** a real landing page for a first-time visitor, with a short pitch, today's problem, a "find your level" placement quiz (one problem each from 8 to 4 kyu, adaptive) and the belt rack.
5. **Profile:**
   - A 12-week activity heatmap.
   - A per-subtopic strength table that uses the taxonomy.
   - The current streak.
6. **Accessibility.** Run an axe-core audit with no serious issues. Check focus order, contrast in both themes and labels on every control, and test with a screen reader on the problem page. MathJax's assistive MathML must be enabled.
7. **Performance.** Lighthouse scores 90 or more for Performance, Accessibility and Best Practices on the home and problem pages, measured on mobile emulation. Load MathJax only on views that need maths.
8. **Empty, loading and error states** for every view.

## Acceptance criteria
- All of the above are checked at 375 px and 1280 px, in light and dark mode, with screenshots in the PR.
- No horizontal scroll at any width, and no console errors.

## Out of scope
Backend features (13 onward).
