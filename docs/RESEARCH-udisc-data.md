# TagShuffle — getting scores OUT of UDisc (research, 2026-06-26)

Probed UDisc live (robots.txt, api host, help center). Findings below. Sources = UDisc's own
Intercom help center (help.udisc.com), articles updated through June 2026.

## Verdict
- **No public/open UDisc API.** Help-center search for "api" returns zero results; the only
  "API" on the site is Intercom's support-chatbot. `api.udisc.com` exists but is the **private
  mobile backend** (Cloudflare-fronted, returns 404 to the public, auth-gated). Not usable.
- **Scraping is a dead-end / disallowed.** robots.txt explicitly blocks `ClaudeBot`, `GPTBot`,
  `CCBot`, etc., and `Disallow: /scorecards/` for ALL bots. Site is behind Cloudflare. Fragile
  + against their rules. Do not build on it.
- **Sanctioned export EXISTS — CSV.** This is the path.

## The data-in paths, ranked

### 1. CSV export  ✅ RECOMMENDED (official, legal, stable)
Two flavors depending on how the league runs Tags in UDisc:

**1a. Event/League results export** (best if they run Tags as a UDisc *Event*)
- UDisc help: "How can I export results after an event finishes" (Leagues & Events → Scoring & Results).
- Gives the exact field for that event: every player, finishing order, scores. Cleanest possible feed.

**1b. Personal rounds CSV** (if they just keep one shared scorecard)
- In the UDisc **app**: tap **"You"** tab → Rounds → **hamburger ☰ (top-right)** → **"Export to CSV"**.
- Downloads a CSV of **all** that account's rounds. Includes every player on the organizer's cards.
- Our parser filters to the most-recent round (by date/course) and ignores the rest.
- Source: help article 10705081 (updated 2026-03-06).

App side: **"Import CSV"** button → parse → match player names to our roster (one-time mapping,
remembered) → pull each player's total → run reshuffle. ~20 sec on the organizer's phone each week.
⚠ Must confirm exact CSV columns against a REAL export before building the parser.

### 2. Manual entry  ✅ already built (fallback + v1)
Type N scores. Zero dependency on UDisc internals. ~30 sec. Always works.

### 3. Screenshot OCR  — possible, not worth it
CSV beats OCR on reliability. Skip unless export ever breaks.

### 4. API / scraping  ❌ RULED OUT
No public API; private backend auth-gated; robots + Cloudflare + AI-bot blocks. Don't.

## Strategic note — UDisc already has a "Bag Tag" column (but NOT the math)
- UDisc **Event tools** have a **Bag Tag optional extra**. Enable it on the event, then:
  Event tools → Leaderboard → **Actions** (top-left) → **Edit player values** → fill the
  **Payout + Bag Tag** columns → Save. Shows on the public leaderboard.
  Source: help article 10860614 (updated 2026-06-12).
- BUT it's **manual** — organizer hand-types each tag number. UDisc does **NOT** auto-reshuffle.
- => UDisc = a place to *record/display* tags. Our app = the *brain* (auto-assign + trading +
  history). The bridge between them is the CSV. **This gap is exactly our product.**

## Bonus: CardCast (live share link)
- From a scorecard, tap share icon → **CardCast** link → scores populate live as entered
  (help article 11899171). It's a public webpage, so NOT a scrape target, but confirms each
  round has a shareable public URL if we ever want a "follow live" feature.

## SINGLE most valuable next step
Get **one real CSV export** from the organizer (either flavor above) so we build the parser
against the actual column layout, not an assumption. Everything else is ready.
