# Make TagShuffle real (multi-device cloud sync)

Right now the app stores everything in the browser's **localStorage** — works great on one
phone, but data lives only on that device. To sync across the organizer + players' phones, point
it at a free **Supabase** project. The app is already wired for it (REST, no build step, no npm).

There are exactly **3 manual steps** — I can't do these for you because they need YOUR cloud
account + keys.

## 1. Create a free Supabase project
- Go to https://supabase.com → New project (free tier is plenty).
- Wait for it to finish provisioning.

## 2. Create the table
- In the project: **SQL Editor → New query** → paste the contents of
  [`supabase-schema.sql`](supabase-schema.sql) → **Run**.
- That makes a `leagues` table (one JSON row per league) + a prototype access policy.

## 3. Paste your keys into the app
- In Supabase: **Project Settings → API**. Copy:
  - **Project URL**  (e.g. `https://abcd1234.supabase.co`)
  - **anon public** key
- Open `index.html`, find the top of the `<script>`:
  ```js
  const SUPA_URL=''; const SUPA_KEY=''; const LEAGUE_ID='default';
  ```
  Paste:
  ```js
  const SUPA_URL='https://abcd1234.supabase.co';
  const SUPA_KEY='eyJhbGciOi...your anon key...';
  const LEAGUE_ID='default';
  ```
- Reload. The Standings header badge flips from **● local** to **☁ cloud**.

That's it. Every save (round, trade, reassignment, settings) now writes to Supabase, and any
device loading the page reads the same shared state.

## How it works
- `loadState()` reads from Supabase first (falls back to localStorage, then seed).
- `persist()` writes to localStorage **and** fires an upsert to Supabase.
- localStorage stays on as an offline cache, so the app still opens with no signal.

## Notes / next steps
- **Security:** the prototype RLS policy lets the anon key read/write any league row — fine for a
  private group, NOT for a public app. Tighten before launch (per-league secret, or Supabase Auth
  + `owner_id`). See the commented normalized schema at the bottom of `supabase-schema.sql`.
- **Multiple leagues:** change `LEAGUE_ID` per league, or add a league picker.
- **Conflict handling:** last-write-wins on the whole blob. Fine for one organizer entering
  results. If multiple people edit at once, move to the normalized schema (per-round rows).
- **Shareable standings link:** once cloud is on, you can host a read-only standings page that
  always reads live state — vs. the static snapshot the in-app "Download standings page" gives now.
