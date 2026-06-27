from playwright.sync_api import sync_playwright
import pathlib, datetime, os

today = datetime.date.today().strftime("%B %d, %Y")

def shot(src, cap):
    return f'<figure><img src="shots/{src}"><figcaption>{cap}</figcaption></figure>'

hero = "".join(f'<img src="shots/{s}">' for s in ["02_standings.png", "06_celebrate.png", "03_profile.png"])

doc = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
@page{{size:A4;margin:14mm 14mm 16mm}}
*{{box-sizing:border-box}}
body{{font-family:'Assistant',-apple-system,Segoe UI,Roboto,sans-serif;color:#16202b;margin:0;font-size:12px;line-height:1.5}}
h1{{font-size:30px;color:#0066B3;margin:0 0 4px}}
h2{{font-size:18px;color:#0066B3;border-bottom:3px solid #F4CE1A;padding-bottom:4px;margin:26px 0 12px}}
h3{{font-size:13px;margin:0 0 4px;color:#16202b}}
.cover{{text-align:center;padding:40px 0 20px;page-break-after:always}}
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
a{{color:#0066B3;text-decoration:none}}
.tag{{display:inline-block;background:#F4CE1A;color:#5a4500;font-weight:800;border-radius:20px;padding:1px 9px;font-size:11px}}
</style></head><body>

<div class="cover">
  <img class="logo" src="../assets/discinsanity-logo.png">
  <h1>Discinsanity Tags</h1>
  <div class="sub">A weekly bag-tag league app for South Mountain &middot; Bethlehem, PA</div>
  <div class="hero">{hero}</div>
  <div class="meta">Project overview &middot; generated {today}</div>
</div>

<h2>What it is</h2>
<p class="lead">Discinsanity Tags is a phone web-app that runs the league's weekly <b>bag-tag</b> game: players
compete for the lowest-numbered tag and swap tags based on how they finish. UDisc keeps score great, but it
<b>won't reshuffle the tags</b> &mdash; the organizer was doing that math by hand every week. This app does it
instantly, keeps the full history, and shows each player's progression &mdash; with a celebration when someone climbs.</p>

<h2>The problem it solves</h2>
<p>After every round the tags get re-handed-out: best finisher takes the lowest tag in play, and so on &mdash;
<b>separately for each division</b> (Mixed Pro / Mixed Amateur), with absent players keeping their tag. By hand
that is slow and error-prone. The app turns it into: pull in the scores &rarr; tap once &rarr; done.</p>

<h2>Everything included</h2>
<div class="grid">
  <div class="feat"><h3><span class="ic">&#128256;</span> Per-division reshuffle</h3><p>Present-only swap, golf scoring (low wins), hold-position ties. Each division has its own tag set and reshuffles independently.</p></div>
  <div class="feat"><h3><span class="ic">&#11014;</span> UDisc CSV import</h3><p>Auto-detects name/score/division columns, skips the "Par" row, picks the latest round, and auto-fills who played plus their scores.</p></div>
  <div class="feat"><h3><span class="ic">&#127942;</span> #1-tag &amp; personal-best moments</h3><p>Claiming the top tag triggers a full-screen gold celebration; beating your best-ever tag gets a callout. Confetti throughout.</p></div>
  <div class="feat"><h3><span class="ic">&#128200;</span> Player profiles</h3><p>Tag-progression graph (lower = better), the tags they moved through, round-by-round score history, and stats including a #1 streak.</p></div>
  <div class="feat"><h3><span class="ic">&#128451;</span> League history</h3><p>Every Tags night saved with date, course, and the full scorecard grouped by division. Trades are logged too.</p></div>
  <div class="feat"><h3><span class="ic">&#8644;</span> Tag trading</h3><p>Swap two players' tags or reassign one &mdash; within a division, keeping tags unique. Logged to history.</p></div>
  <div class="feat"><h3><span class="ic">&#128081;</span> Standings + export</h3><p>Live standings per division with a crown on each #1. Copy text for the group chat, download CSV, or a shareable standings page.</p></div>
  <div class="feat"><h3><span class="ic">&#128274;</span> Access &amp; roles</h3><p>Date-password lock to view; a separate organizer code unlocks editing. Viewers cannot change scores; saved rounds are immutable.</p></div>
  <div class="feat"><h3><span class="ic">&#127912;</span> Real branding</h3><p>Logo and colors pulled from discinsanity.com &mdash; blue, gold, the Assistant typeface &mdash; with animations to make it feel alive.</p></div>
  <div class="feat"><h3><span class="ic">&#9729;</span> Backend-ready</h3><p>Runs offline in the browser (localStorage); paste Supabase keys to sync across phones. One self-contained file, hosted free on GitHub Pages.</p></div>
</div>

<h2>How the workflow goes</h2>
<ol class="flow">
  <li><b>Unlock</b> &mdash; open the link, pick today's date. Only people there that day get in.</li>
  <li><b>View</b> &mdash; anyone can browse standings, player graphs and past scorecards (read-only).</li>
  <li><b>Go organizer</b> &mdash; tap the key, enter the code, to run the night.</li>
  <li><b>Import scores</b> &mdash; drop in the UDisc CSV; the roster auto-fills (present + score + division).</li>
  <li><b>Reshuffle</b> &mdash; tags recompute per division; best score takes the lowest tag in play.</li>
  <li><b>Save</b> &mdash; the new tags lock in, the week is filed, and milestones celebrate (#1, personal best).</li>
  <li><b>Share</b> &mdash; copy or export the standings for the group chat.</li>
</ol>

<div class="gallery">
{shot('01_lock.png','Members-only date lock')}
{shot('02_standings.png','Standings &mdash; crown on each #1')}
{shot('03_profile.png','Player profile + tag graph')}
{shot('04_tonight.png','Organizer: import or enter scores')}
{shot('05_result.png','Per-division reshuffle result')}
{shot('06_celebrate.png','Claiming the #1 tag')}
{shot('07_round.png','Saved scorecard')}
{shot('08_history.png','League history')}
{shot('09_trade.png','Trade / reassign tags')}
</div>

<h2>Notes</h2>
<div class="note">
<b>Honest caveats:</b> the date/organizer lock is a <i>client-side</i> gate &mdash; fine for a private league, but
real access control would need the cloud backend. The CSV parser is best-guess until we import a real Sunday
export to lock the exact column names. Both are quick follow-ups.
</div>

<div class="foot">
  <span>Discinsanity Tags &middot; built for the weekly league</span>
  <span><span class="tag">LIVE</span> sbilger.github.io/disc-golf-tags</span>
</div>

</body></html>"""

pathlib.Path("build/doc.html").write_text(doc, encoding="utf-8")
out = "docs/Discinsanity-Tags-App-Overview.pdf"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto("file:///C:/Users/sbilg/Code/disc-golf-tags/build/doc.html", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.pdf(path=out, format="A4", print_background=True,
           margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("PDF:", out, os.path.getsize(out), "bytes")
