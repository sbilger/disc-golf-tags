from playwright.sync_api import sync_playwright
import pathlib, datetime, os

APP = "file:///C:/Users/sbilg/Code/disc-golf-tags/index.html"
SHOTS = pathlib.Path("build/shots"); SHOTS.mkdir(parents=True, exist_ok=True)
today = datetime.date.today().strftime("%B %d, %Y")

# ---------- Phase 1: capture fresh screenshots ----------
def capture():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg.goto(APP); pg.wait_for_timeout(500)
        tok = pg.evaluate("accessToken()")
        pg.wait_for_timeout(200); pg.screenshot(path=str(SHOTS / "01_lock.png"))
        pg.fill("#lockInput", f"{tok[:4]}-{tok[4:6]}-{tok[6:8]}"); pg.click("#lock .btn"); pg.wait_for_timeout(450)
        pg.screenshot(path=str(SHOTS / "02_standings.png"))
        pg.click("button[data-tab='schedule']"); pg.wait_for_timeout(450); pg.screenshot(path=str(SHOTS / "03_schedule.png"))
        pg.evaluate("openProfile('Sarah')"); pg.wait_for_timeout(650); pg.screenshot(path=str(SHOTS / "04_profile.png"))
        pg.on("dialog", lambda d: d.accept("discinsanity")); pg.click("#hkey"); pg.wait_for_timeout(250)
        pg.click("button[data-tab='tonight']"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "05_tonight.png"))
        for idx in [0, 1, 2]:
            pg.query_selector_all("#roster .toggle")[idx].click(); pg.wait_for_timeout(110)
        ins = pg.query_selector_all("#roster .score"); ins[0].fill("55"); ins[1].fill("60"); ins[2].fill("50")
        pg.click("#mainBtn"); pg.wait_for_timeout(400); pg.screenshot(path=str(SHOTS / "06_result.png"))
        pg.click("button:has-text('Save Round to History')"); pg.wait_for_timeout(700); pg.screenshot(path=str(SHOTS / "07_celebrate.png"))
        pg.click("#celebrate"); pg.wait_for_timeout(400); pg.screenshot(path=str(SHOTS / "08_round.png"))
        pg.click("button[data-tab='history']"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "09_history.png"))
        pg.click("button[data-tab='players']"); pg.wait_for_timeout(200); pg.click("button:has-text('Trade tags')"); pg.wait_for_timeout(350); pg.screenshot(path=str(SHOTS / "10_trade.png"))
        b.close()

capture()

# ---------- Phase 2: build doc + render PDF ----------
def shot(src, cap):
    return f'<figure><img src="shots/{src}"><figcaption>{cap}</figcaption></figure>'
hero = "".join(f'<img src="shots/{s}">' for s in ["02_standings.png", "07_celebrate.png", "04_profile.png"])

feats = [
    ("&#128256;", "Per-division reshuffle", "Present-only swap, golf scoring (low wins), hold-position ties. Mixed Pro and Mixed Amateur each have their own tag set and reshuffle independently."),
    ("&#11014;", "Hands-off UDisc import", "Auto-detects name / score / division / PDGA columns, skips \"Par\", picks the latest round. Anyone not already on the roster is <b>auto-added</b> as a new player &mdash; zero clicks for the coordinator."),
    ("&#127942;", "Big celebrations", "Claiming the #1 tag triggers a full-screen gold moment (crown + confetti). Beating your best-ever tag gets a callout. The #1 is what everyone chases."),
    ("&#128197;", "Weekly schedule", "The Sunday rotation across the Valley, this week highlighted. Organizers set the course + tee per week; players see where tags is each week."),
    ("&#8599;", "Jump to UDisc", "Open the day's UDisc event in the UDisc app and bounce back &mdash; each scheduled week links to its own event. Keep score in UDisc, tags here."),
    ("&#128202;", "Player profiles + PDGA", "Tag-progression graph (lower = better), the tags they moved through, round-by-round history, a #1 streak, and a link to their <b>PDGA</b> page."),
    ("&#128451;", "League history", "Every Tags night saved with date, course, and the full scorecard grouped by division. Trades are logged too."),
    ("&#8644;", "Tag trading", "Swap two players' tags or reassign one &mdash; within a division, keeping tags unique. Logged to history."),
    ("&#128081;", "Standings + export", "Live standings per division with a crown on each #1. Copy text for the group chat, download CSV, or a shareable standings page."),
    ("&#128274;", "Access &amp; roles", "Date-password lock to view; an organizer code unlocks editing. Viewers can't change scores; saved rounds are immutable."),
    ("&#127912;", "Real branding", "Logo and colors pulled from discinsanity.com &mdash; blue, gold, the Assistant typeface &mdash; with animations to make it feel alive."),
    ("&#9729;", "Backend-ready", "Runs offline in the browser (localStorage); paste Supabase keys to sync across phones. One self-contained file, hosted free on GitHub Pages."),
]
feat_html = "".join(f'<div class="feat"><h3><span class="ic">{ic}</span> {t}</h3><p>{d}</p></div>' for ic, t, d in feats)

doc = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
@page{{size:A4;margin:14mm 14mm 16mm}}
*{{box-sizing:border-box}}
body{{font-family:'Assistant',-apple-system,Segoe UI,Roboto,sans-serif;color:#16202b;margin:0;font-size:12px;line-height:1.5}}
h1{{font-size:30px;color:#0066B3;margin:0 0 4px}}
h2{{font-size:18px;color:#0066B3;border-bottom:3px solid #F4CE1A;padding-bottom:4px;margin:24px 0 12px}}
h3{{font-size:13px;margin:0 0 4px;color:#16202b}}
.cover{{text-align:center;padding:38px 0 18px;page-break-after:always}}
.cover img.logo{{width:240px;margin:10px auto 22px}}
.cover .sub{{font-size:16px;color:#67737f;font-weight:600}}
.cover .meta{{margin-top:18px;font-size:12px;color:#9aa6b2}}
.cover .hero{{display:flex;gap:10px;justify-content:center;margin-top:26px}}
.cover .hero img{{height:300px;border:1px solid #dce3ea;border-radius:14px;box-shadow:0 6px 18px rgba(20,40,70,.12)}}
.lead{{font-size:13px;background:#eaf2fb;border-left:4px solid #0066B3;padding:12px 14px;border-radius:8px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px}}
.feat{{background:#fff;border:1px solid #dce3ea;border-radius:10px;padding:10px 12px;break-inside:avoid}}
.feat .ic{{font-size:15px}}
.feat p{{margin:3px 0 0;color:#55626e;font-size:11px}}
ol.flow{{counter-reset:s;list-style:none;padding:0;margin:0}}
ol.flow li{{position:relative;padding:8px 0 8px 38px;border-bottom:1px dashed #e2e8ef;break-inside:avoid}}
ol.flow li:before{{counter-increment:s;content:counter(s);position:absolute;left:0;top:7px;width:26px;height:26px;background:#0066B3;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px}}
ol.flow b{{color:#0066B3}}
.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;page-break-before:always}}
figure{{margin:0;break-inside:avoid;text-align:center}}
figure img{{width:100%;border:1px solid #dce3ea;border-radius:10px}}
figcaption{{font-size:10px;color:#67737f;margin-top:5px;font-weight:600}}
.note{{background:#fffaf0;border:1px solid #f0e2bd;border-radius:8px;padding:10px 12px;font-size:11px;color:#6b5a25}}
.foot{{margin-top:22px;border-top:1px solid #dce3ea;padding-top:10px;font-size:11px;color:#67737f;display:flex;justify-content:space-between}}
.tag{{display:inline-block;background:#F4CE1A;color:#5a4500;font-weight:800;border-radius:20px;padding:1px 9px;font-size:11px}}
</style></head><body>

<div class="cover">
  <img class="logo" src="../assets/discinsanity-logo.png">
  <h1>Discinsanity Tags</h1>
  <div class="sub">A weekly bag-tag league app for the Lehigh Valley</div>
  <div class="hero">{hero}</div>
  <div class="meta">Project overview &middot; updated {today}</div>
</div>

<h2>What it is</h2>
<p class="lead">Discinsanity Tags is a phone web-app that runs the league's weekly <b>bag-tag</b> game: players
compete for the lowest-numbered tag and swap tags based on how they finish. UDisc keeps score, but it
<b>won't reshuffle the tags</b> &mdash; the organizer was doing that math by hand every week. This app does it
instantly, tracks the rotating schedule, keeps the full history, links back to UDisc + PDGA, and celebrates
when someone climbs &mdash; built to be as hands-off for the coordinator as possible.</p>

<h2>The problem it solves</h2>
<p>After every round the tags get re-handed-out: best finisher takes the lowest tag in play, and so on &mdash;
<b>separately for each division</b>, with absent players keeping their tag, as the league rotates courses
across the Valley each Sunday. By hand that is slow and error-prone. The app turns it into: import the scores
&rarr; tap once &rarr; done.</p>

<h2>Everything included</h2>
<div class="grid">{feat_html}</div>

<h2>How the workflow goes</h2>
<ol class="flow">
  <li><b>Unlock</b> &mdash; open the link, pick today's date. Only people there that day get in.</li>
  <li><b>View</b> &mdash; standings, the weekly schedule, and player profiles (graph, history, PDGA) &mdash; read-only for everyone.</li>
  <li><b>Go organizer</b> &mdash; tap the key, enter the code, to run the night.</li>
  <li><b>Import scores</b> &mdash; drop in the UDisc CSV; the roster auto-fills and any new player is added automatically.</li>
  <li><b>Reshuffle</b> &mdash; tags recompute per division; best score takes the lowest tag in play.</li>
  <li><b>Save</b> &mdash; new tags lock in, the week is filed, milestones celebrate (#1, personal best).</li>
  <li><b>Share</b> &mdash; export the standings, or jump to that day's UDisc event.</li>
</ol>

<div class="gallery">
{shot('01_lock.png','Members-only date lock')}
{shot('02_standings.png','Standings &mdash; crown on each #1')}
{shot('03_schedule.png','Weekly course rotation')}
{shot('04_profile.png','Profile: tag graph + PDGA link')}
{shot('05_tonight.png','Organizer: import / enter scores')}
{shot('06_result.png','Per-division reshuffle')}
{shot('07_celebrate.png','Claiming the #1 tag')}
{shot('08_round.png','Saved scorecard')}
{shot('09_history.png','League history')}
</div>

<h2>Notes</h2>
<div class="note">
<b>Honest caveats:</b> the date/organizer lock is a <i>client-side</i> gate &mdash; fine for a private league, but
real access control would need the cloud backend. The CSV parser is best-guess until a real Sunday export
locks the exact column names (incl. whether UDisc includes a PDGA column). The Valley course rotation is
filled in-app (UDisc doesn't expose it to scrape). All quick follow-ups.
</div>

<div class="foot">
  <span>Discinsanity Tags &middot; built for the weekly league</span>
  <span><span class="tag">LIVE</span> sbilger.github.io/disc-golf-tags</span>
</div>

</body></html>"""

pathlib.Path("build/doc.html").write_text(doc, encoding="utf-8")
out = "docs/Discinsanity-Tags-App-Overview.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto("file:///C:/Users/sbilg/Code/disc-golf-tags/build/doc.html", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.pdf(path=out, format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("PDF:", out, os.path.getsize(out), "bytes")
