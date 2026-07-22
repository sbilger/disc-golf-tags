# Sean's to-do — Discinsanity app

Each one unblocks the next phase. Reconvene after.

## ✅ 1. Backend — DONE (2026-07-21)
Supabase project (`discinsanity`, ref `ohvhhcpmohztmlossbjv`) created, `supabase-hub-schema.sql`
run, keys wired into all 5 files (index/hub/doubles/events/leaderboards.html) — verified live
end-to-end (real read + write + delete round-trip against the project).

## ✅ 1b. GitHub Pages fixed — LANDMINE, was serving a dead branch for 2.5+ weeks (2026-07-22)
Pages was configured to build from the old `feat/discinsanity-hub` branch (last commit July 4),
not `main` — every merge since PR #3 (the recovery itself, scheduling, PDGA work, Supabase,
Stripe, code changes) was invisible on the live site the whole time despite being on `main`.
Repointed Pages source to `main` via the GitHub API, forced a fresh build, verified the live
site now serves current code. **If the live site ever looks stale again, check Pages source
first** (`gh api repos/sbilger/disc-golf-tags/pages`) before assuming a code bug.

## 🔴 2. Real Supabase Auth — run the new schema (the current big unblock)
Sean's call 2026-07-22: full migration off local/demo auth, including Google/Apple/Facebook
sign-in. Code is written across all 7 files (`account.js` rewritten, `account.html` has OAuth
buttons + email confirm handling, all 6 other pages get `supabase-js` + `await DI.init()` in
their boot). **Blocked on you running the new schema — table doesn't exist yet (checked live,
404).**

1. **SQL Editor** (Supabase) → run [`supabase-auth-schema.sql`](../supabase-auth-schema.sql).
   Creates `members` (one row per real Supabase Auth user, auto-created by a trigger on
   `auth.users` insert — works for email/password AND every OAuth provider the same way),
   `app_secrets`, and the `claim_admin()` function.
2. **Set your real admin code** — the schema file inserts a placeholder
   (`'CHANGE_ME_IN_SQL_EDITOR'`). In the SQL Editor, run:
   ```sql
   insert into public.app_secrets (key, value) values ('admin_code', 'pick-your-own-value')
     on conflict (key) do update set value = excluded.value;
   ```
   Pick something not posted anywhere in chat/git history — **this one is a real secret**,
   unlike every ORGANIZER_CODE/ADMIN_CODE before it (those were always visible in page source;
   this one lives only in Postgres, checked server-side inside `claim_admin()`).
3. **Email confirmation** — Supabase's default requires clicking a confirmation email before
   first sign-in. Decide: leave it on (safer, more friction) or turn it off for frictionless
   league signup (**Authentication → Providers → Email → toggle "Confirm email"**). The app
   handles either case (shows "check your email" if confirmation's required), so this is your
   call, not a blocker either way.
4. **Existing local demo accounts (including the one you made earlier) do NOT carry over.**
   Local/demo auth and real Supabase Auth are two different systems — you'll need to sign up
   fresh with your real email once this is live. Sorry — that's the real cost of doing this
   properly instead of faking a migration path for throwaway demo data.
5. **Social sign-in (Google/Apple/Facebook)** — the buttons exist in `account.html` now, but
   each provider needs its own one-time setup before it actually works (clicking before that
   just shows Supabase's own error page):
   - **Google**: Google Cloud Console → create OAuth 2.0 Client ID (Web application) → add
     `https://ohvhhcpmohztmlossbjv.supabase.co/auth/v1/callback` as an authorized redirect URI →
     copy Client ID + Secret → Supabase Dashboard → Authentication → Providers → Google → paste
     both, enable.
   - **Facebook**: Meta for Developers → create an app → add Facebook Login product → same
     redirect URI as above → copy App ID + Secret → Supabase → Authentication → Providers →
     Facebook → paste, enable.
   - **Apple**: Apple Developer account (needs the $99/yr Apple Developer Program) → create a
     Services ID + Sign in with Apple config → same redirect URI → Supabase → Authentication →
     Providers → Apple → paste the Services ID/Team ID/Key ID/private key, enable. Apple's setup
     is the most involved of the three and the only one with a real cost — do it last, or skip
     it if the $99/yr isn't worth it for a hobby league app.
   Do these in whatever order/pace makes sense — email/password works the moment step 1-2 are
   done, independent of any of this.
6. Ping me once step 1 is done (schema run) — I'll do a real signup test via curl to confirm
   the trigger/RPC actually work before either of us trusts it, then we do a live browser
   click-through together.

**NOT VERIFIED yet, cannot be until step 1 above:** the members table, the auto-create trigger,
claim_admin() — none of it has been exercised against a live database yet (checked: table
returns 404 right now). Every file syntax-checks clean (`node --check`) and smoke-tests 200,
but that's necessary, not sufficient, for something this size. **This is the single largest,
most cross-cutting change in the project** (touches auth boot sequence in every file) — treat
the first real signup + first real admin claim as the actual test, not the code review.

## 🔴 3. Section 3 — Stripe setup
Card-on-file, off-session charge-when-round-is-saved. All the code is written and scaffolded
(Supabase tables, 3 Edge Functions, client wiring) — **but none of it can go live until you've
done the Stripe-side setup below**:

1. Create a **Stripe account** → stripe.com (test mode needs no business verification).
2. **SQL Editor** (Supabase) → run [`supabase-stripe-schema.sql`](../supabase-stripe-schema.sql).
   Creates `stripe_customers` + `payments` tables — **locked down, zero anon access** (only the
   Edge Functions, via service_role, can touch them).
3. Install the **Supabase CLI** if you don't have it (`npm install -g supabase` or
   `scoop install supabase` on Windows), then:
   ```
   supabase login
   supabase link --project-ref ohvhhcpmohztmlossbjv
   supabase functions deploy save-card
   supabase functions deploy charge-players
   supabase functions deploy stripe-webhook
   ```
4. **Stripe Dashboard → Developers → API keys**: copy the **test publishable key** (`pk_test_...`)
   and **test secret key** (`sk_test_...`).
   - Publishable key → paste into `STRIPE_PK` constant in `account.html` (safe for client code).
   - Secret key → **never paste in chat or any file.** Set it as an Edge Function secret:
     `supabase secrets set STRIPE_SECRET_KEY=sk_test_...`
5. **Stripe Dashboard → Developers → Webhooks → Add endpoint**:
   URL = `https://ohvhhcpmohztmlossbjv.supabase.co/functions/v1/stripe-webhook`
   Events to send: `setup_intent.succeeded`, `payment_intent.succeeded`, `payment_intent.payment_failed`.
   Stripe gives you a signing secret (`whsec_...`) — set it the same way, never in chat:
   `supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...`
6. Ping me with confirmation steps 1-5 are done — I'll wire `STRIPE_PK` and we test the full
   loop: save a card (Stripe test card `4242 4242 4242 4242`) → organizer saves a Tags round →
   confirm charges land in Stripe's test dashboard + the `payments` table.

## 🟢 4. Info to get from Jeff (shapes the next builds)
- **Doubles format details:** scoring = best-disc, combined, or handicap? Buy-in / payouts? Points scheme?
- **Tags course rotation:** which course each Sunday (the Schedule TBD weeks).
- **Course pars:** app has a shared LV course DB (`courses.js`) defaulted to par 54 / 18 holes —
  have Jeff correct any via ✎ next to the Doubles course picker.
- **Real event lineup** for the Events calendar (or Jeff adds them in-app via admin).
- **Jeff's real email**, once real accounts are live (see #2 above).
- **League fee amount** — defaults to $1.00 (100¢) to match the PDGA minimum, editable in
  Tags → Standings → Settings.

## 🟢 5. PDGA sanctioning — real-world steps, not code
If you want Discinsanity's Tags league to actually count toward official PDGA ratings: Jeff
needs to become a **PDGA Certified Official**, submit PDGA's Event Sanctioning Agreement + pay
**$25**/session, collect the mandatory **$1/player/round fee**. **Singles play only** — Tags
qualifies, Doubles cannot be PDGA-sanctioned. Reporting stays manual (email or PDGA's Tournament
Manager) — the app's PDGA League Report export gets the data copy/paste-ready, nothing submits
automatically.

## 🟢 6. Business / direction calls (yours)
- Is this a **HogTron-built product** for the shop (scope, pricing, ownership)?
- **Mobile app:** already an installable **PWA**. True native later = wrap in **Capacitor**.

---

## Current state (2026-07-22)
Live: **https://sbilger.github.io/disc-golf-tags/hub.html** (Pages source fixed, now actually
serves `main` — see #1b above).
- **Hub / Tags / Doubles / Events / Leaderboards / Scorecard** — all as before, plus Tags'
  League fee / charge-on-save and Leaderboards' PDGA rating badges.
- **Accounts** — being migrated to real Supabase Auth (email/password + Google/Apple/Facebook
  OAuth) — **code written, blocked on you running `supabase-auth-schema.sql` (§2 above)**.
  Until then, sign-in will error (members table doesn't exist yet).
- **Backend** — Supabase live for game/hub data + (once §2 runs) real accounts. Stripe
  scaffolded, not yet live (needs §3).

## Next session (me)
- Once §2's schema is run: real curl-based signup test (auto-create trigger, claim_admin RPC)
  before trusting any of it, then a live browser click-through together.
- Once §3's Stripe setup is confirmed: wire `STRIPE_PK`, full test-card click-through.
