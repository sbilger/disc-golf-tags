# 🥏 TagShuffle (disc-golf-tags)

A tiny web app for running a **disc golf Tags league** — the weekly game where players
compete for the lowest-numbered bag tag, swapping tags based on how they finish.

Modeled on the real **Discinsanity Tags League** at South Mountain (Bethlehem, PA), which runs
two divisions — **Mixed Pro** and **Mixed Amateur** — each with its **own tag set**.

UDisc keeps score great, but it **won't auto-reshuffle the tags** — the organizer does that math
by hand every week. This does it instantly: pull in the scores, compute the new tag numbers per
division, keep the history, and show each player's progression.

> Status: **working single-file prototype**. Open `index.html` in any browser — no build, no install.

## What it does

- **Per-division reshuffle** — each division (Mixed Pro / Mixed Amateur) has its own tag pool and
  reshuffles independently. Present-only swap: only the tags held by players who showed up get
  re-sorted among themselves (by score, golf rules — low wins). Absent players keep their tag.
  Ties = hold position.
- **UDisc CSV import** — drop in a UDisc event-results export; auto-detects name, score AND
  division columns, skips the "Par" row, picks the latest round, maps names to the roster.
  (No UDisc API exists — see [docs/RESEARCH-udisc-data.md](docs/RESEARCH-udisc-data.md).)
- **History** — every Tags night saved: date, course/layout, full scorecard grouped by division.
- **Player profiles** — tag-progression graph (lower = better), the chips of tags they moved
  through, round-by-round score history, stats (current/best tag, rounds, wins), and division.
- **Trading** — swap two players' tags or reassign one (within a division); logged to history,
  keeps tags unique per division.
- **New-player rule** — setting: rookie joins their division's swap immediately, or holds out the
  first night.
- **Standings export / share** — copy text for group chat, download CSV, or download a
  self-contained read-only standings page (both divisions).
- **View live event on UDisc** — deep-links to the real Discinsanity event leaderboard.
- **Backend-ready** — runs on `localStorage` by default; paste Supabase keys to sync across
  devices. See [BACKEND.md](BACKEND.md).

## Run it

Open `index.html` in a browser. The app seeds 8 weeks of demo data (3 Pro + 5 Am players) so
History and the graphs have content immediately. `↺ reset demo data` (Standings tab) re-seeds.

Test CSV import: **⬆ Import UDisc CSV** → pick a file from [`samples/`](samples/).

## Getting scores out of UDisc

UDisc has **no public API** and scraping is disallowed; the public event page is a client-rendered
shell (the leaderboard streams from a private API and isn't in the page source). The sanctioned
path is its **CSV export** — for this league, the **event results export**. Full findings:
[docs/RESEARCH-udisc-data.md](docs/RESEARCH-udisc-data.md).

So the loop is: **UDisc scores the round → organizer exports event results to CSV → import here →
TagShuffle does the per-division tag math.**

## Going multi-device (cloud)

Default storage is the browser. To sync the organizer + players across phones, wire a free
Supabase project — 3 steps in [BACKEND.md](BACKEND.md), schema in
[supabase-schema.sql](supabase-schema.sql).

## Files

```
index.html              the whole app (HTML + CSS + JS, no dependencies)
supabase-schema.sql     one-row-per-league cloud store + RLS
BACKEND.md              how to switch on cloud sync
docs/RESEARCH-udisc-data.md   how UDisc data export works (research notes)
samples/                example UDisc CSV exports for testing import
```

## License

MIT — see [LICENSE](LICENSE).
