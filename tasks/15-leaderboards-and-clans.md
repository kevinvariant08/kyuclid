# 15. Leaderboards, public profiles and clans

## Goal
Replace the sample leaderboard with real rankings, give players a profile page they can share, and add clans, such as a school or a maths circle, in the way Codewars does.

## Depends on
13.

## Spec
1. **Leaderboards:**
   - Overall rank points and duel rating.
   - Filters for this week, this month and all time, plus per topic.
   - Each one is a paginated database view, refreshed at most every 5 minutes.
   - Show the user's own position even when it is off the page.
2. **Public profile** at `#u-<handle>`: rank badge, points, solves by kyu and topic, duel record, recent solves (problem titles only, never answers) and clan. Handles are unique, between 3 and 20 characters, and filtered for offensive words.
3. **Clans.** A `mw_clans` table holds the name, an optional verified school, members and an owner. A user joins one clan at a time with a join code. Clan leaderboards rank by the sum of members' points this month. The owner can remove members.
4. **Privacy.** Profiles are public by default, with a setting to hide one from leaderboards. Kevinvariant users are often school students, so show no real names or emails anywhere, and keep all identity data out of public views.
5. **Abuse.** Rate-limit handle changes to once a month. Admins (Kevin) can rename or hide a profile.

## Acceptance criteria
- Seeded test accounts produce correct rankings, checked with SQL. Pagination and the "your position" row both work.
- An anonymous visitor can view profiles and leaderboards but can't read any non-public field. Prove this with direct REST calls.

## Out of scope
Badges and achievements: Kevinvariant has a rewards system, and whether to share it is task 20.
