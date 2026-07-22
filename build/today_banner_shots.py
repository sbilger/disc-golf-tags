# Sample capture: "what's on today" banner on hub.html, 3 variants.
# Seeds discinsanity_events_v1 in localStorage with an event dated TODAY, then screenshots.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import http.server, socketserver, threading, os, functools, datetime
from playwright.sync_api import sync_playwright

ROOT = r"C:\Users\sbilg\Code\disc-golf-tags"
OUT = os.path.join(ROOT, "build", "casestudy")
os.makedirs(OUT, exist_ok=True)
PORT = 8125
BASE = f"http://localhost:{PORT}"

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
socketserver.ThreadingTCPServer.allow_reuse_address = True
httpd = socketserver.ThreadingTCPServer(("", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

today = datetime.date.today().isoformat()

def seed_js(events):
    import json
    payload = json.dumps({"events": events})
    return f"localStorage.setItem('discinsanity_events_v1', JSON.stringify({payload}));"

TAGS_EVENT = [{"id": "e1", "kind": "tags", "title": "Sunday Tags", "date": today,
               "time": "9:00a", "course": "South Mountain · White Tee", "details": "", "link": ""}]
DOUBLES_EVENT = [{"id": "e2", "kind": "doubles", "title": "Wednesday Doubles", "date": today,
                  "time": "6:00p", "course": "South Mountain", "details": "", "link": ""}]
BOTH_EVENTS = TAGS_EVENT + DOUBLES_EVENT

with sync_playwright() as p:
    b = p.chromium.launch()

    def shot(events, filename):
        pg = b.new_context(viewport={"width": 390, "height": 500}).new_page()
        pg.goto(f"{BASE}/hub.html")
        pg.evaluate(seed_js(events))
        pg.reload()
        pg.wait_for_timeout(1200)
        pg.locator(".phone").screenshot(path=f"{OUT}/{filename}")
        visible = pg.evaluate("document.getElementById('todayBanner').style.display")
        text = pg.evaluate("document.getElementById('todayBanner').innerText")
        print(f"{filename}: display={visible!r} text={text!r}")
        pg.close()

    shot(TAGS_EVENT, "today_banner_tags.png")
    shot(DOUBLES_EVENT, "today_banner_doubles.png")
    shot(BOTH_EVENTS, "today_banner_both.png")
    shot([], "today_banner_none.png")  # confirms it stays hidden with nothing scheduled

    b.close()

httpd.shutdown()
print("done")
