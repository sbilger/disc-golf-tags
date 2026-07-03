# Discinsanity Hub — all-inclusive app plan

Turning the standalone **Tags** app into the full **Discinsanity** app: tags, doubles, events,
news, disc drops — one place for the Lehigh Valley disc golf community Jeff runs.

> The standalone tags app is bookmarked at git tag **`v1-tags-app`** — always returnable.

## Modules
| Module | What | Status |
|---|---|---|
| **Hub / Home** | Landing: this week, news & drops, links to everything | ✅ shell + Jeff-admin built |
| **Tags League** | Weekly bag-tag standings, history, profiles, PDGA | ✅ working (v1) |
| **News & Drops** | Jeff posts announcements + new stock | ✅ admin built (local; cloud next) |
| **Doubles** | Weekly doubles — **random-draw partners**, scoring, standings | ✅ built |
| **Events** | Leagues, one-offs & tournaments calendar | ✅ built (Jeff-editable) |
| **Leaderboards** | Season points across tags + doubles | ✅ built |
| **Shop / Drops** | Links to the Shopify Pro Shop (+ auto drop feed later) | ↗ links live |
| **My Profile** | Member login + profile (PDGA, division), admin role | ✅ built (demo auth) |

## Decisions (locked with Sean)
- **Backend foundation first** — everything else rides on it.
- **Doubles = random-draw partners.**
- **Content managed by Jeff** via an in-app admin (post news/drops, edit "this week").

## Architecture
- Stays a **single static app** (HTML/CSS/JS, no build) hosted free on **GitHub Pages** — fast,
  cheap, easy. `hub.html` = home; `index.html` = tags; future modules = more sections/pages.
- **Dual-mode store** (same pattern as the tags app): runs on **localStorage** today, and flips to
  **Supabase** the moment URL + anon key are pasted in — no rewrite. Admin edits already work this way.
- **Backend = Supabase** (free tier): content tables + **Auth** (member sign-in, `admin` role for Jeff).
- Eventually point a domain at it (e.g. `app.discinsanity.com`) instead of github.io.

## Roadmap
**Phase 0 — DONE**
- Tags app v1 (`v1-tags-app`); Hub shell; Jeff-admin for News & "This Week" (local, cloud-ready).

**Phase 1 — Backend foundation** ← next
- Sean creates a Supabase project + runs the schema; paste keys → hub + tags both go cloud + multi-device.
- Supabase **Auth**: member sign-in; `admin` role unlocks Jeff's posting (replaces the shared code).
- Move tags league state + hub content into Supabase.

**Phase 2 — Doubles** (random draw)
- Check-in players → auto-draw partners → enter team scores → standings + season points.

**Phase 3 — Events + Leaderboards** — DONE
- Unified calendar (tags/doubles/one-offs); season points combining tags + doubles
  (`leaderboards.html`: overall podium + per-division tags board + doubles board + player night log).

**Phase 4 — Shop + Profiles**
- Auto disc-drop feed from the Shopify store; unified member profile (tags, doubles, PDGA).

## What Sean must do for Phase 1 (the one thing me can't do)
Create the Supabase project + run [`supabase-hub-schema.sql`](../supabase-hub-schema.sql) + paste the
URL + anon key into `hub.html` and `index.html`. 3 steps, ~5 min (see BACKEND.md). Everything else is
built to light up automatically.

## Notes / open with Jeff
- Exact **doubles scoring** (best-disc vs combined vs handicap) — confirm.
- **Auth** style for members (email magic-link is simplest on Supabase).
- Whether this becomes a HogTron-built product for the shop (Sean's call).
