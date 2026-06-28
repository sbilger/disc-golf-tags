from playwright.sync_api import sync_playwright
import pathlib, csv, io, os, glob

APP = "file:///C:/Users/sbilg/Code/disc-golf-tags/index.html"
VID_DIR = "build/video"
pathlib.Path(VID_DIR).mkdir(parents=True, exist_ok=True)

CAP_JS = """(t)=>{let e=document.getElementById('vcap');
if(!e){e=document.createElement('div');e.id='vcap';
e.style.cssText='position:absolute;left:14px;right:14px;bottom:86px;z-index:60;background:rgba(8,30,58,.96);color:#fff;border-left:4px solid #F4CE1A;padding:13px 15px;border-radius:12px;font-family:Assistant,system-ui,sans-serif;font-weight:700;font-size:15px;box-shadow:0 10px 28px rgba(0,0,0,.35);line-height:1.35';
document.querySelector('.phone').appendChild(e);}
e.textContent=t;e.style.opacity='0';e.style.transform='translateY(10px)';e.style.transition='all .35s';
requestAnimationFrame(()=>{e.style.opacity='1';e.style.transform='none';});}"""
HIDE_JS = "()=>{let e=document.getElementById('vcap');if(e)e.style.opacity='0';}"
END_JS = """(url)=>{let e=document.createElement('div');e.id='vend';
e.style.cssText='position:absolute;inset:0;z-index:70;background:linear-gradient(160deg,#0066B3,#003a66);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;color:#fff;text-align:center;padding:30px;animation:viewIn .5s ease';
e.innerHTML='<img src="assets/discinsanity-logo.png" style="width:210px;background:#fff;border-radius:16px;padding:12px">'
+'<div style="font-family:Assistant;font-weight:800;font-size:24px">Discinsanity Tags</div>'
+'<div style="font-family:Assistant;font-weight:700;font-size:13px;opacity:.9">'+url+'</div>';
document.querySelector('.phone').appendChild(e);}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844},
                        record_video_dir=VID_DIR,
                        record_video_size={"width": 390, "height": 844})
    pg = ctx.new_page()

    def cap(t, ms):
        pg.evaluate(CAP_JS, t); pg.wait_for_timeout(int(ms * 1.5))
    def hidecap():
        pg.evaluate(HIDE_JS)

    pg.goto(APP); pg.wait_for_timeout(700)

    # 1) LOCK
    cap("Open the link. Members-only — pick today's date to get in.", 3000)
    tok = pg.evaluate("accessToken()")
    pg.fill("#lockInput", f"{tok[:4]}-{tok[4:6]}-{tok[6:8]}"); pg.wait_for_timeout(1300)
    pg.click("#lock .btn"); pg.wait_for_timeout(700)

    # 2) STANDINGS
    cap("Live standings — each division keeps its own tags. \U0001F451 = current #1.", 5000)

    # 3) SCHEDULE
    pg.click("button[data-tab='schedule']"); pg.wait_for_timeout(600)
    cap("The weekly Valley rotation — this week's course, with a tap-through to the UDisc event.", 5200)

    # 4) PROFILE + PDGA
    pg.evaluate("openProfile('Sarah')"); pg.wait_for_timeout(700)
    cap("Every player's tag graph, full history — and a link straight to their PDGA page.", 5200)

    # 5) ORGANIZER
    pg.on("dialog", lambda d: d.accept("discinsanity"))
    cap("Organizers unlock editing with a code (the key, top-right).", 3400)
    pg.click("#hkey"); pg.wait_for_timeout(900)

    # build a CSV that makes the worst-tag player in each division win -> claims #1
    rows = pg.evaluate("players.map(p=>({name:p.name,division:p.division,tag:p.tag}))")
    buf = io.StringIO(); w = csv.writer(buf); w.writerow(["PlayerName", "Division", "Total"])
    for dv, label in [("PRO", "Mixed Pro"), ("AM", "Mixed Amateur")]:
        grp = sorted([r for r in rows if r["division"] == dv], key=lambda r: -r["tag"])
        for i, r in enumerate(grp):
            w.writerow([r["name"], label, 48 + i * 4])
    csv_path = os.path.abspath("build/demo-night.csv")
    pathlib.Path(csv_path).write_text(buf.getvalue(), encoding="utf-8")

    # 6) IMPORT (hands-off)
    pg.click("button[data-tab='tonight']"); pg.wait_for_timeout(500)
    cap("Import the UDisc scores — it auto-fills who played and auto-adds anyone new.", 4400)
    pg.set_input_files("#v-tonight input[type=file]", csv_path); pg.wait_for_timeout(1300)

    # 7) RESULT
    cap("Tags reshuffle per division — best score takes the lowest tag.", 5000)

    # 8) SAVE -> CELEBRATION
    cap("Save the round… and claim the #1 tag \U0001F3C6", 2600)
    hidecap()
    pg.click("button:has-text('Save Round to History')"); pg.wait_for_timeout(6800)
    if "hide" not in (pg.get_attribute("#celebrate", "class") or ""):
        pg.click("#celebrate"); pg.wait_for_timeout(600)

    # 9) ROUND DETAIL
    cap("Every week's scorecard is saved, grouped by division.", 4400)

    # 10) HISTORY
    pg.click("button[data-tab='history']"); pg.wait_for_timeout(500)
    cap("Browse the whole league history at a glance.", 4000)

    # 11) EXPORT
    pg.click("button[data-tab='players']"); pg.wait_for_timeout(400)
    pg.click("button:has-text('Export / Share')"); pg.wait_for_timeout(500)
    cap("Export the standings to share in the group chat.", 4400)
    hidecap()

    # 12) END CARD
    pg.evaluate(END_JS, "sbilger.github.io/disc-golf-tags"); pg.wait_for_timeout(5500)

    path = pg.video.path()
    ctx.close(); b.close()

print("raw video:", path)
webms = sorted(glob.glob(VID_DIR + "/*.webm"), key=os.path.getmtime)
print("webm files:", webms)
