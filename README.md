# 🥏 TagShuffle (disc-golf-tags)

A tiny web app for running a **disc golf Tags league** — the weekly game where players
compete for the lowest-numbered bag tag, swapping tags based on how they finish.

UDisc keeps score great, but it **won't auto-reshuffle the tags** — the organizer does that math
by hand every week. This does it instantly: pull in the scores, compute the new tag numbers, keep
the history, and show each player's progression.

> Status: **working single-file prototype**. Open `index.html` in any browser — no build, no install.

## What it does

- **Reshuffle** — present-only swap: only the tags held by players who showed up get re-sorted
  among themselves (by score, golf rules — low wins). Absent players keep their tag.
  Ties = hold position (lower current tag stays lower).
- **UDisc CSV import** — drop in a UDisc export; auto-detects the name + score columns, skips the
  "Par" row, picks the latest round, maps names to the roster. (No UDisc API exists — see
  [docs/RESEARCH-udisc-data.md](docs/RESEARCH-udisc-data.md).)
- **History** — every Tags night saved: date, course/layout, full scorecard.
- **Player profiles** — tag-progression graph (lower = better), the chips of tags they moved
  through, round-by-round score history, and stats (current/best tag, rounds, wins).
- **Trading** — swap two players' tags or reassign one; logged to history, keeps tags unique.
- **New-player rule** — setting: rookie joins the swap immediately, or holds out the first night.
- **Standings export / share** — copy text for group chat, download CSV, or download a
  self-contained read-only standings page.
- **Backend-ready** — runs on `localStorage` by default; paste Supabase keys to sync across
  devices. See [BACKEND.md](BACKEND.md).

## Run it

Open `index.html` in a browser. The app seeds 8 weeks of demo data so History and the graphs have
content immediately. `↺ reset demo data` (Standings tab) re-seeds.

Test CSV import: **⬆ Import UDisc CSV** → pick a file from [`samples/`](samples/).

## Getting scores out of UDisc

UDisc has **no public API** and scraping is disallowed. The sanctioned path is its **CSV export**
(personal: You → Rounds → ☰ → Export to CSV; or event/league results export). Full findings:
[docs/RESEARCH-udisc-data.md](docs/RESEARCH-udisc-data.md).

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
