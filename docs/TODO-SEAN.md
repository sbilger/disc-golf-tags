# Sean's to-do — Discinsanity app

Each one unblocks the next phase. Reconvene after.

## 🔴 1. Stand up the backend (the big unblock — blocks Section 3 payments too)
Right now every module runs on **localStorage** (per-device). To make it shared + multi-device and let
Jeff's posts/events/accounts be real — and before Stripe payments (Section 3) can be built as anything
more than UI scaffolding, since Stripe secret-key operations must run server-side:
1. Create a free **Supabase** project → supabase.com.
2. SQL Editor → run [`supabase-hub-schema.sql`](../supabase-hub-schema.sql). (The old
   `supabase-schema.sql` was removed 2026-07-21 — superseded, was a landmine waiting to happen.)
3. **Settings → API**, copy the **Project URL** + **anon public** key, paste into the
   `SUPA_URL` / `SUPA_KEY` constants at the top of the `<script>` in **all five**:
   `index.html` (tags), `hub.html`, `doubles.html`, `events.html`, `leaderboards.html`.
   → each flips from `● local` to `☁ cloud` automatically; data syncs across phones.
   (Confirmed 2026-07-21: still exactly these 5 files, even after the scheduling/PDGA-export
   additions — new state lives in the same JSON blob columns, no schema change needed.)
4. Ping me — I'll then swap the **demo accounts** (account.js) over to **real Supabase Auth**
   (email sign-in, Jeff = admin role) and unify login across every module. `account.html` /
   `account.js` still has NO cloud wiring at all (member accounts + ratings are local-only,
   per-device) — that's the Phase-1+ normalized-tables work, commented out at the bottom of
   `supabase-hub-schema.sql`.

## 🟠 2. Change the codes (before anyone else uses it)
All currently `discinsanity` — change them:
- Organizer/admin code in `index.html`, `doubles.html`, `events.html` (`ORGANIZER_CODE`).
- Admin code in `account.js` (`ADMIN_CODE`) — this is what makes someone an admin.
- Note: the date unlock was **removed** (Sean's call, 2026-07-03) — modules are open read-only;
  the organizer code gates all editing. For real "members only," proper Supabase login later.

## 🟡 3. Info to get from Jeff (shapes the next builds)
- **Doubles format details:** scoring = best-disc, combined, or handicap? Buy-in / payouts? Points scheme?
- **Tags course rotation:** which course each Sunday (the Schedule TBD weeks).
- **Course pars:** app has a shared LV course DB (`courses.js`: South Mountain White/Blue, Jordan
  Creek Short/Long, Little Gap, Trexler) defaulted to par 54 / 18 holes — have Jeff correct any
  via ✎ next to the Doubles course picker (UDisc has no public API; see RESEARCH-udisc-data.md).
- **Real event lineup** for the Events calendar (or Jeff adds them in-app via admin).
- **Jeff's real email** (replace the demo `jeff@discinsanity.com`).
- **Social links** — confirm IG `@discinsanitydgproshop`, FB `/Discinsanity` (already wired).
- **Domain?** Eventually point e.g. `app.discinsanity.com` at it instead of github.io.

## 🟡 3b. PDGA sanctioning — real-world steps, not code (added 2026-07-21)
If you want Discinsanity's Tags league to actually count toward official PDGA ratings:
- Jeff needs to become a **PDGA Certified Official** (real exam) to be League Director.
- Submit PDGA's **Event Sanctioning Agreement** (pdga.com) + pay the **$25** one-time fee per
  league session (6-10 weeks).
- Collect the mandatory **$1/player/round fee** ($0.50 PDGA / $0.50 TD) — this is what Section 3
  payments needs to support, not just a generic entry fee.
- **Singles play only** — Tags qualifies, Doubles cannot be PDGA-sanctioned, ever (PDGA rule).
- Reporting stays 100% manual either way (email to `tdreport@pdga.com` or PDGA's own Tournament
  Manager) — the app's PDGA League Report export (Tags → Export/Share) gets the data
  copy/paste-ready, but nothing submits automatically; no API exists on PDGA's end (verified).

## 🟢 4. Business / direction calls (yours)
- Is this a **HogTron-built product** for the shop (scope, pricing, ownership)?
- **Mobile app:** it's already an installable **PWA** (Add to Home Screen). When you want true
  native, easiest path is wrapping this in **Capacitor** → App Store / Play Store with the same code.

---

## Current state (2026-07-21)
Live: **https://sbilger.github.io/disc-golf-tags/hub.html** (now served correctly from `main` —
see landmine note below, this used to be branch-only).
- **Hub** — home: This Week, module grid, News & Drops (Jeff-admin), socials.
- **Tags** — the bag-tag ladder league + PDGA League Report export (new).
- **Doubles** — random-draw teams → team scores → season points standings + history.
- **Events** — calendar + recurring league defs, RSVP roster, organizer group/tee-time
  assignment (new).
- **Leaderboards** — season points rolled up across Tags + Doubles + self-reported PDGA rating
  badges (new).
- **Accounts + Profiles** — login / sign-up / member profile (PDGA #, rating, division), admin role.
- **Scorecard** — UDisc-style hole-by-hole scoring, feeds Tags + Doubles.
- **PWA** — installable, offline service worker.

### Demo logins (try on the live link)
- Member: create any account.
- Admin (Jeff): `jeff@discinsanity.com` / `discinsanity` → then Hub shows "Admin ✓" + edit controls.
- Modules are **open** (read-only by default). `suite.js` shares ONE organizer state across the
  whole suite: enter the 🔑 code once = organizer everywhere; Jeff's admin account = organizer
  **everywhere**. Sign-out drops organizer too.

### LANDMINE fixed 2026-07-21
The whole module suite (Hub/Doubles/Events/Accounts/Leaderboards/Scorecard) was stranded on a
branch for ~2.5 weeks — PR #2 targeted the wrong base branch instead of `main`, so `main` only
ever had the standalone Tags app even though Pages (which serves branches directly) made it look
live and done. Fixed via PR #3. Rule going forward: every new PR bases off current `main`.

## Next session (me)
- Once you've done #1 (Supabase live): wire Supabase Auth into account.js, unify login.
- Once #1 is confirmed live: start Section 3 (Stripe + Stripe Connect... actually just plain
  Stripe, single-account, per your 2026-07-21 call — Discinsanity-only, no multi-tenant Connect
  needed unless this becomes a multi-league platform).
