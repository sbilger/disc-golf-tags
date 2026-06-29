from playwright.sync_api import sync_playwright
import pathlib, datetime, os

APP = "file:///C:/Users/sbilg/Code/disc-golf-tags/index.html"
SHOTS = pathlib.Path("build/shots"); SHOTS.mkdir(parents=True, exist_ok=True)
today = datetime.date.today().strftime("%B %d, %Y")
REAL_CSV = os.environ.get("REAL_CSV", "")
REAL = bool(REAL_CSV)

def capture():
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.on("dialog", lambda d: d.accept("discinsanity" if d.type == "prompt" else None))
        pg.goto(APP); pg.wait_for_timeout(500)
        tok = pg.evaluate("accessToken()")
        pg.wait_for_timeout(150); pg.screenshot(path=str(SHOTS / "01_lock.png")); shots.append(("01_lock.png", "Members-only date lock"))
        pg.fill("#lockInput", f"{tok[:4]}-{tok[4:6]}-{tok[6:8]}"); pg.click("#lock .btn"); pg.wait_for_timeout(450)
        if REAL:
            pg.click("#hkey"); pg.wait_for_timeout(250)
            pg.evaluate("players=[];rounds=[];trades=[];persist();resetTonight();renderAll();")
            pg.click("button[data-tab='tonight']"); pg.wait_for_timeout(350)
            pg.set_input_files("#v-tonight input[type=file]", os.path.abspath(REAL_CSV)); pg.wait_for_timeout(1300)
            pg.screenshot(path=str(SHOTS / "05_result.png")); shots.append(("05_result.png", "Per-division reshuffle (real results)"))
            pg.click("button:has-text('Save Round to History')"); pg.wait_for_timeout(800)
            if "hide" not in (pg.get_attribute("#celebrate", "class") or ""): pg.click("#celebrate"); pg.wait_for_timeout(400)
            pg.click("button[data-tab='players']"); pg.wait_for_timeout(450); pg.screenshot(path=str(SHOTS / "02_standings.png")); shots.append(("02_standings.png", "Standings across MPO / MA1 / MA2 / MA3"))
            pg.click("button[data-tab='schedule']"); pg.wait_for_timeout(400); pg.screenshot(path=str(SHOTS / "03_schedule.png")); shots.append(("03_schedule.png", "Weekly course rotation"))
            pg.evaluate("openProfile('Sean Bilger')"); pg.wait_for_timeout(650); pg.screenshot(path=str(SHOTS / "04_profile.png")); shots.append(("04_profile.png", "Profile: tag graph + PDGA link"))
            pg.click("button[data-tab='history']"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "09_history.png")); shots.append(("09_history.png", "League history"))
        else:
            pg.screenshot(path=str(SHOTS / "02_standings.png")); shots.append(("02_standings.png", "Standings — crown on each #1"))
            pg.click("button[data-tab='schedule']"); pg.wait_for_timeout(450); pg.screenshot(path=str(SHOTS / "03_schedule.png")); shots.append(("03_schedule.png", "Weekly course rotation"))
            pg.evaluate("openProfile('Sarah')"); pg.wait_for_timeout(650); pg.screenshot(path=str(SHOTS / "04_profile.png")); shots.append(("04_profile.png", "Profile: tag graph + PDGA link"))
            pg.click("#hkey"); pg.wait_for_timeout(250)
            pg.click("button[data-tab='tonight']"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "05_tonight.png")); shots.append(("05_tonight.png", "Organizer: import / enter scores"))
            for idx in [0, 1, 2]:
                pg.query_selector_all("#roster .toggle")[idx].click(); pg.wait_for_timeout(110)
            ins = pg.query_selector_all("#roster .score"); ins[0].fill("55"); ins[1].fill("60"); ins[2].fill("50")
            pg.click("#mainBtn"); pg.wait_for_timeout(400); pg.screenshot(path=str(SHOTS / "06_result.png")); shots.append(("06_result.png", "Per-division reshuffle"))
            pg.click("button:has-text('Save Round to History')"); pg.wait_for_timeout(700); pg.screenshot(path=str(SHOTS / "07_celebrate.png")); shots.append(("07_celebrate.png", "Claiming the #1 tag"))
            pg.click("#celebrate"); pg.wait_for_timeout(400); pg.screenshot(path=str(SHOTS / "08_round.png")); shots.append(("08_round.png", "Saved scorecard"))
            pg.click("button[data-tab='history']"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "09_history.png")); shots.append(("09_history.png", "League history"))
        b.close()
    return shots

shots = capture()
def fig(src, cap): return f'<figure><img src="shots/{src}"><figcaption>{cap}</figcaption></figure>'
hero = "".join(f'<img src="shots/{s}">' for s in ["02_standings.png", "04_profile.png", ("05_result.png" if REAL else "07_celebrate.png")])
gallery = "".join(fig(s, c) for s, c in sorted(shots))

subtitle = "Live results demo &mdash; this week's Sunday card" if REAL else "A weekly bag-tag league app for the Lehigh Valley"
datanote = (f"<b>Live data:</b> built from the real Sunday scorecard &mdash; 31 players across MPO / MA1 / MA2 / MA3. "
            if REAL else "")

feats = [
    ("&#128256;", "Per-division reshuffle", "Present-only swap, golf scoring, hold-position ties. Every UDisc division (MPO, MA1, MA2, MA3, &hellip;) gets its own tag set and reshuffles independently."),
    ("&#11014;", "Hands-off UDisc import", "Auto-detects name / score / division / PDGA columns. Anyone not on the roster is <b>auto-added</b> as a new player &mdash; zero clicks for the coordinator."),
    ("&#127942;", "Big celebrations", "Claiming the #1 tag triggers a full-screen gold moment (crown + confetti). Beating your best-ever tag gets a callout."),
    ("&#128197;", "Weekly schedule", "The Sunday rotation across the Valley, this week highlighted, each week linking to its own UDisc event."),
    ("&#8599;", "Jump to UDisc", "Open the day's UDisc event in the UDisc app and bounce back. Keep score in UDisc, tags here."),
    ("&#128202;", "Profiles + PDGA", "Tag-progression graph (lower = better), round-by-round history, a #1 streak, and a link to each player's <b>PDGA</b> page."),
    ("&#128451;", "League history", "Every Tags night saved with date, course, and the full scorecard grouped by division. Trades logged too."),
    ("&#8644;", "Tag trading", "Swap two players' tags or reassign one &mdash; within a division, keeping tags unique."),
    ("&#128081;", "Standings + export", "Live standings per division with a crown on each #1. Copy text, download CSV, or a shareable page."),
    ("&#128274;", "Access &amp; roles", "Date-password lock to view; an organizer code unlocks editing. Viewers can't change scores."),
    ("&#127912;", "Real branding", "Logo and colors pulled from discinsanity.com &mdash; blue, gold, the Assistant typeface &mdash; with animations."),
    ("&#9729;", "Backend-ready", "Runs offline in the browser; paste Supabase keys to sync across phones. One file, hosted free on GitHub Pages."),
]
feat_html = "".join(f'<div class="feat"><h3><span class="ic">{ic}</span> {t}</h3><p>{d}</p></div>' for ic, t, d in feats)

doc = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
@page{{size:A4;margin:14mm 14mm 16mm}}*{{box-sizing:border-box}}
body{{font-family:'Assistant',-apple-system,Segoe UI,Roboto,sans-serif;color:#16202b;margin:0;font-size:12px;line-height:1.5}}
h1{{font-size:30px;color:#0066B3;margin:0 0 4px}}h2{{font-size:18px;color:#0066B3;border-bottom:3px solid #F4CE1A;padding-bottom:4px;margin:24px 0 12px}}
h3{{font-size:13px;margin:0 0 4px;color:#16202b}}
.cover{{text-align:center;padding:38px 0 18px;page-break-after:always}}
.cover img.logo{{width:240px;margin:10px auto 22px}}.cover .sub{{font-size:16px;color:#67737f;font-weight:600}}
.cover .meta{{margin-top:18px;font-size:12px;color:#9aa6b2}}
.cover .hero{{display:flex;gap:10px;justify-content:center;margin-top:26px}}
.cover .hero img{{height:300px;border:1px solid #dce3ea;border-radius:14px;box-shadow:0 6px 18px rgba(20,40,70,.12)}}
.lead{{font-size:13px;background:#eaf2fb;border-left:4px solid #0066B3;padding:12px 14px;border-radius:8px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px}}
.feat{{background:#fff;border:1px solid #dce3ea;border-radius:10px;padding:10px 12px;break-inside:avoid}}
.feat .ic{{font-size:15px}}.feat p{{margin:3px 0 0;color:#55626e;font-size:11px}}
ol.flow{{counter-reset:s;list-style:none;padding:0;margin:0}}
ol.flow li{{position:relative;padding:8px 0 8px 38px;border-bottom:1px dashed #e2e8ef;break-inside:avoid}}
ol.flow li:before{{counter-increment:s;content:counter(s);position:absolute;left:0;top:7px;width:26px;height:26px;background:#0066B3;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px}}
ol.flow b{{color:#0066B3}}
.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;page-break-before:always}}
figure{{margin:0;break-inside:avoid;text-align:center}}figure img{{width:100%;border:1px solid #dce3ea;border-radius:10px}}
figcaption{{font-size:10px;color:#67737f;margin-top:5px;font-weight:600}}
.note{{background:#fffaf0;border:1px solid #f0e2bd;border-radius:8px;padding:10px 12px;font-size:11px;color:#6b5a25}}
.foot{{margin-top:22px;border-top:1px solid #dce3ea;padding-top:10px;font-size:11px;color:#67737f;display:flex;justify-content:space-between}}
.tag{{display:inline-block;background:#F4CE1A;color:#5a4500;font-weight:800;border-radius:20px;padding:1px 9px;font-size:11px}}
</style></head><body>
<div class="cover">
  <img class="logo" src="../assets/discinsanity-logo.png">
  <h1>Discinsanity Tags</h1>
  <div class="sub">{subtitle}</div>
  <div class="hero">{hero}</div>
  <div class="meta">Project overview &middot; {('REAL DATA &middot; ' if REAL else '')}updated {today}</div>
</div>
<h2>What it is</h2>
<p class="lead">{datanote}Discinsanity Tags is a phone web-app that runs the league's weekly <b>bag-tag</b> game: players
compete for the lowest-numbered tag and swap tags based on how they finish. UDisc keeps score, but it
<b>won't reshuffle the tags</b>. This app does it instantly across every division, tracks the rotating
schedule, keeps the full history, links back to UDisc + PDGA, and celebrates when someone climbs.</p>
<h2>Everything included</h2>
<div class="grid">{feat_html}</div>
<h2>How the workflow goes</h2>
<ol class="flow">
  <li><b>Unlock</b> &mdash; open the link, pick today's date.</li>
  <li><b>View</b> &mdash; standings, schedule, and player profiles (graph, history, PDGA) &mdash; read-only.</li>
  <li><b>Go organizer</b> &mdash; tap the key, enter the code.</li>
  <li><b>Import scores</b> &mdash; drop in the UDisc CSV; the roster auto-fills and new players are added automatically.</li>
  <li><b>Reshuffle</b> &mdash; tags recompute per division; best score takes the lowest tag.</li>
  <li><b>Save</b> &mdash; new tags lock in, the week is filed, milestones celebrate.</li>
  <li><b>Share</b> &mdash; export the standings, or jump to that day's UDisc event.</li>
</ol>
<div class="gallery">{gallery}</div>
<h2>Notes</h2>
<div class="note"><b>Honest caveats:</b> the date/organizer lock is a <i>client-side</i> gate (fine for a private
league; real access needs the cloud backend). Week-one tags are seeded by finishing order; from week two the
come-in / leave-with swap takes over. The Valley course rotation is filled in-app.</div>
<div class="foot"><span>Discinsanity Tags &middot; built for the weekly league</span>
<span><span class="tag">LIVE</span> sbilger.github.io/disc-golf-tags</span></div>
</body></html>"""

pathlib.Path("build/doc.html").write_text(doc, encoding="utf-8")
out = (os.path.expanduser("~/OneDrive/Desktop") + "/Discinsanity-Tags-App-Overview-RealData.pdf") if REAL else "docs/Discinsanity-Tags-App-Overview.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto("file:///C:/Users/sbilg/Code/disc-golf-tags/build/doc.html", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.pdf(path=out, format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("MODE:", "REAL" if REAL else "SEED", "-> PDF:", out, os.path.getsize(out), "bytes")
