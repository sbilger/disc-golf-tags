# Sean's to-do — Discinsanity app

Each one unblocks the next phase. Reconvene after.

## ✅ 1. Backend — DONE (2026-07-21)
Supabase project (`discinsanity`, ref `ohvhhcpmohztmlossbjv`) created, `supabase-hub-schema.sql`
run, keys wired into all 5 files (index/hub/doubles/events/leaderboards.html) — verified live
end-to-end (real read + write + delete round-trip against the project). `● local` → `☁ cloud`
badge should show next time you load the app.

## 🔴 2. Section 3 — Stripe setup (the new big unblock)
Card-on-file, off-session charge-when-round-is-saved. All the code is written and scaffolded
(Supabase tables, 3 Edge Functions, client wiring) — **but none of it can go live until you've
done the Stripe-side setup below**, same shape as the Supabase handoff:

1. Create a **Stripe account** → stripe.com (test mode needs no business verification).
2. **SQL Editor** (Supabase) → run [`supabase-stripe-schema.sql`](../supabase-stripe-schema.sql).
   Creates `stripe_customers` + `payments` tables — **locked down, zero anon access** (only the
   Edge Functions, via service_role, can touch them; unlike hubs/leagues these aren't
   open-policy prototype tables, since they hold payment data).
3. Install the **Supabase CLI** if you don't have it (`npm install -g supabase` or
   `scoop install supabase` on Windows), then:
   ```
   supabase login
   supabase link --project-ref ohvhhcpmohztmlossbjv
   supabase functions deploy save-card
   supabase functions deploy charge-players
   supabase functions deploy stripe-webhook
   ```
   (`supabase/config.toml` already sets `verify_jwt = false` on all three — needed because
   there's no real Supabase Auth session yet to verify against.)
4. **Stripe Dashboard → Developers → API keys**: copy the **test publishable key** (`pk_test_...`)
   and **test secret key** (`sk_test_...`).
   - Publishable key → paste into `STRIPE_PK` constant in `account.html` (safe for client code,
     same handling as `SUPA_KEY`).
   - Secret key → **never paste in chat or any file.** Set it as an Edge Function secret:
     `supabase secrets set STRIPE_SECRET_KEY=sk_test_...`
5. **Stripe Dashboard → Developers → Webhooks → Add endpoint**:
   URL = `https://ohvhhcpmohztmlossbjv.supabase.co/functions/v1/stripe-webhook`
   Events to send: `setup_intent.succeeded`, `payment_intent.succeeded`, `payment_intent.payment_failed`.
   Stripe gives you a signing secret (`whsec_...`) — set it the same way, never in chat:
   `supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...`
6. Ping me with confirmation steps 1-5 are done (no need to share any key value except the
   publishable one, which is safe) — I'll wire `STRIPE_PK` into `account.html` and we test the
   full loop: save a card (Stripe test card `4242 4242 4242 4242`, any future date/CVC) →
   organizer saves a Tags round with present players who have cards → confirm charges show up
   in the Stripe test dashboard + `payments` table.

**What this builds, in plain terms:** a player saves a card once (Account → Payment method).
Every week, when the organizer taps "Save Round to History" in Tags, everyone marked present
that night gets charged the league fee (Settings → League fee, in cents, default $1.00) off
that saved card automatically — no re-entering a card, no manual Venmo chasing. No card on file
= silently skipped, round still saves. Single Stripe account, no Stripe Connect (Discinsanity-
only scope, per your 2026-07-21 call).

**NOT VERIFIED yet (needs steps above + a real click-through, no browser tool available to me
this session):** the actual Stripe.js card-save flow, an actual charge succeeding, the webhook
actually firing. The Edge Function code type-checks clean (real `tsc` run, zero errors once
Deno globals are stubbed) and the SQL is written to the same pattern as the working
`supabase-hub-schema.sql` — but none of it has touched a real Stripe API call yet.

## 🟠 3. Change the codes (before anyone else uses it)
All currently `discinsanity` — change them:
- Organizer/admin code in `index.html`, `doubles.html`, `events.html` (`ORGANIZER_CODE`).
- Admin code in `account.js` (`ADMIN_CODE`) — this is what makes someone an admin.
- Note: the date unlock was **removed** (Sean's call, 2026-07-03) — modules are open read-only;
  the organizer code gates all editing. For real "members only," proper Supabase login later.

## 🟡 4. Info to get from Jeff (shapes the next builds)
- **Doubles format details:** scoring = best-disc, combined, or handicap? Buy-in / payouts? Points scheme?
- **Tags course rotation:** which course each Sunday (the Schedule TBD weeks).
- **Course pars:** app has a shared LV course DB (`courses.js`: South Mountain White/Blue, Jordan
  Creek Short/Long, Little Gap, Trexler) defaulted to par 54 / 18 holes — have Jeff correct any
  via ✎ next to the Doubles course picker (UDisc has no public API; see RESEARCH-udisc-data.md).
- **Real event lineup** for the Events calendar (or Jeff adds them in-app via admin).
- **Jeff's real email** (replace the demo `jeff@discinsanity.com`).
- **Social links** — confirm IG `@discinsanitydgproshop`, FB `/Discinsanity` (already wired).
- **Domain?** Eventually point e.g. `app.discinsanity.com` at it instead of github.io.
- **League fee amount** — defaults to $1.00 (100¢) to match the PDGA minimum, editable in
  Tags → Standings → Settings. Confirm with Jeff whether Discinsanity wants to charge more
  (PDGA rule allows the TD's cut to be $0.50-plus, at Jeff's discretion).

## 🟡 5. PDGA sanctioning — real-world steps, not code
If you want Discinsanity's Tags league to actually count toward official PDGA ratings:
- Jeff needs to become a **PDGA Certified Official** (real exam) to be League Director.
- Submit PDGA's **Event Sanctioning Agreement** (pdga.com) + pay the **$25** one-time fee per
  league session (6-10 weeks).
- Collect the mandatory **$1/player/round fee** ($0.50 PDGA / $0.50 TD) — this is exactly what
  Section 3's League fee setting is for.
- **Singles play only** — Tags qualifies, Doubles cannot be PDGA-sanctioned, ever (PDGA rule).
- Reporting stays 100% manual either way (email to `tdreport@pdga.com` or PDGA's own Tournament
  Manager) — the app's PDGA League Report export (Tags → Export/Share) gets the data
  copy/paste-ready, but nothing submits automatically; no API exists on PDGA's end (verified).

## 🟢 6. Business / direction calls (yours)
- Is this a **HogTron-built product** for the shop (scope, pricing, ownership)?
- **Mobile app:** it's already an installable **PWA** (Add to Home Screen). When you want true
  native, easiest path is wrapping this in **Capacitor** → App Store / Play Store with the same code.

---

## Current state (2026-07-21)
Live: **https://sbilger.github.io/disc-golf-tags/hub.html**.
- **Hub** — home: This Week, module grid, News & Drops (Jeff-admin), socials.
- **Tags** — bag-tag ladder league + PDGA League Report export + **League fee / charge-on-save
  (new, needs Stripe setup above to actually charge anything)**.
- **Doubles** — random-draw teams → team scores → season points standings + history.
- **Events** — calendar + recurring league defs, RSVP roster, organizer group/tee-time assignment.
- **Leaderboards** — season points rolled up across Tags + Doubles + self-reported PDGA ratings.
- **Accounts + Profiles** — login / sign-up / member profile (PDGA #, rating, division), admin
  role, **+ Payment method card (new — "Save a card," needs `STRIPE_PK` to actually work)**.
- **Scorecard** — UDisc-style hole-by-hole scoring, feeds Tags + Doubles.
- **PWA** — installable, offline service worker.
- **Backend** — Supabase live (all game/hub state); Stripe scaffolded, not yet live (needs #2 above).

### Demo logins (try on the live link)
- Member: create any account.
- Admin (Jeff): `jeff@discinsanity.com` / `discinsanity` → then Hub shows "Admin ✓" + edit controls.

## Next session (me)
- Once you've confirmed Stripe setup (#2): wire `STRIPE_PK`, do the full test-card click-through,
  confirm a charge lands in Stripe's test dashboard + the `payments` table.
- Later: real Supabase Auth swap for account.js (currently still local/demo auth — a player's
  saved card is keyed by email in Supabase, independent of that, so this can happen either order).
