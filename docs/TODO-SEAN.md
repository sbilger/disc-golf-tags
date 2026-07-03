# Sean's to-do — Discinsanity app (set up when you wake up)

Built overnight on branch `feat/discinsanity-hub` (PR #2). Everything below is the stuff **only you
can do** (cloud account, real codes, business calls). Each one unblocks the next phase. Reconvene after.

## 🔴 1. Stand up the backend (the big unblock)
Right now every module runs on **localStorage** (per-device). To make it shared + multi-device and let
Jeff's posts/events/accounts be real:
1. Create a free **Supabase** project → supabase.com.
2. SQL Editor → run [`supabase-hub-schema.sql`](../supabase-hub-schema.sql).
3. **Settings → API**, copy the **Project URL** + **anon public** key, paste into the
   `SUPA_URL` / `SUPA_KEY` constants at the top of the `<script>` in **all five**:
   `index.html` (tags), `hub.html`, `doubles.html`, `events.html`, `leaderboards.html`.
   → each flips from `● local` to `☁ cloud` automatically; data syncs across phones.
4. Ping me — I'll then swap the **demo accounts** (account.js) over to **real Supabase Auth**
   (email sign-in, Jeff = admin role) and unify login across every module.

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

## 🟢 4. Business / direction calls (yours)
- Is this a **HogTron-built product** for the shop (scope, pricing, ownership)?
- **Mobile app:** it's already an installable **PWA** (Add to Home Screen). When you want true
  native, easiest path is wrapping this in **Capacitor** → App Store / Play Store with the same code.

---

## What I built overnight (so you can see it)
Live (Pages now serves the hub branch): **https://sbilger.github.io/disc-golf-tags/hub.html**
- **Hub** — home: This Week, module grid, **News & Drops** (Jeff-admin: post/edit/delete), socials.
- **Tags** — the v1 app (bookmarked at tag `v1-tags-app`).
- **Doubles** — random-draw teams → team scores → season points standings + history.
- **Events** — Jeff-editable calendar (add/edit, detail, add-to-calendar .ics).
- **Leaderboards** — season points rolled up across Tags + Doubles (podium, per-division boards,
  tap-a-player night-by-night log). Points = field size − place + 1, ties share the better place.
- **Accounts + Profiles** — login / sign-up / member profile (PDGA, division), admin role.
- **PWA** — manifest + app icon + service worker → installable on phones. Service worker now
  caches the app shell (network-first) → the suite keeps working offline on the course.
- **Plan:** [`HUB-PLAN.md`](HUB-PLAN.md). All branded Discinsanity blue/gold, animated, social links.

### Demo logins (try on the live link)
- Member: create any account.
- Admin (Jeff): `jeff@discinsanity.com` / `discinsanity` → then Hub shows "Admin ✓" + edit controls.
- Modules are **open** (read-only by default) — date lock removed 2026-07-03. `suite.js` shares
  ONE organizer state across the whole suite: enter the 🔑 code once = organizer everywhere;
  Jeff's admin account = organizer **everywhere**. Sign-out drops organizer too.

## Next session (me) — once you've done #1
Supabase wiring + real auth (login is already unified locally via `suite.js` + `account.js` —
Supabase Auth drops in behind the same `DI` shape) → polish + (optional) Capacitor mobile
wrap. (Leaderboards: ✅ built. Unified suite session: ✅ built.)
