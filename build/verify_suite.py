# Headless verify: Discinsanity suite — open modules (date-gate removed 2026-07-03),
# shared organizer session, admin sign-in, cross-module integration, live drops.
# Serves repo on :8123, drives Chromium, asserts every flow, saves screenshots to build/shots/.
import http.server, socketserver, threading, os, sys, functools
from playwright.sync_api import sync_playwright

ROOT = r"C:\Users\sbilg\Code\disc-golf-tags"
SHOTS = os.path.join(ROOT, "build", "shots")
os.makedirs(SHOTS, exist_ok=True)
PORT = 8123
BASE = f"http://localhost:{PORT}"

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
socketserver.ThreadingTCPServer.allow_reuse_address = True
httpd = socketserver.ThreadingTCPServer(("", PORT), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

errors = []
passed = []

def check(name, cond):
    (passed if cond else errors).append(name)
    print(("PASS " if cond else "FAIL ") + name)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 420, "height": 900})
    page = ctx.new_page()
    console_errs = []
    page.on("console", lambda m: console_errs.append(f"{page.url} :: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errs.append(f"{page.url} :: PAGEERROR {e}"))

    ALL = ["hub.html", "index.html", "doubles.html", "events.html", "leaderboards.html", "account.html"]
    MODULES = ["index.html", "doubles.html", "events.html", "leaderboards.html"]

    # 1) every page renders OPEN — no lock element anywhere, content visible immediately
    for f in ALL:
        page.goto(f"{BASE}/{f}")
        page.wait_for_timeout(600)
        check(f"{f}: no lock element", page.evaluate("!document.getElementById('lock')"))
        if f in MODULES:
            check(f"{f}: starts as viewer (not organizer)",
                  page.evaluate("!document.body.classList.contains('org')"))
        page.screenshot(path=os.path.join(SHOTS, f"v_{f.replace('.html','')}_open.png"))

    # content actually renders without any unlock step
    page.goto(f"{BASE}/index.html"); page.wait_for_timeout(600)
    check("tags: standings content visible with no unlock",
          page.evaluate("document.body.innerText.length > 200"))
    page.goto(f"{BASE}/leaderboards.html"); page.wait_for_timeout(800)
    check("leaderboards: board renders with no unlock",
          page.evaluate("document.body.innerText.toLowerCase().includes('season')"))

    # 2) organizer code entered ONCE (doubles) -> organizer everywhere, survives reload
    page.goto(f"{BASE}/doubles.html"); page.wait_for_timeout(400)
    page.evaluate("window.prompt = () => 'discinsanity'")
    page.click("#hkey"); page.wait_for_timeout(300)
    check("doubles organizer ON via key", page.evaluate("document.body.classList.contains('org')"))
    page.goto(f"{BASE}/index.html"); page.wait_for_timeout(600)
    check("tags inherits organizer mode", page.evaluate("document.body.classList.contains('org')"))
    page.goto(f"{BASE}/events.html"); page.wait_for_timeout(600)
    check("events inherits admin mode", page.evaluate("document.body.classList.contains('org')"))
    page.screenshot(path=os.path.join(SHOTS, "v_events_admin.png"))

    # organizer OFF from tags -> off everywhere
    page.goto(f"{BASE}/index.html"); page.wait_for_timeout(600)
    page.click("#hkey"); page.wait_for_timeout(300)
    check("tags organizer toggled OFF", page.evaluate("!document.body.classList.contains('org')"))
    page.goto(f"{BASE}/doubles.html"); page.wait_for_timeout(600)
    check("doubles organizer dropped too", page.evaluate("!document.body.classList.contains('org')"))

    # 3) fresh device + Jeff signs in -> admin/organizer everywhere; sign-out drops it
    ctx2 = browser.new_context(viewport={"width": 420, "height": 900})
    page2 = ctx2.new_page()
    page2.on("console", lambda m: console_errs.append(f"{page2.url} :: {m.text}") if m.type == "error" else None)
    page2.on("pageerror", lambda e: console_errs.append(f"{page2.url} :: PAGEERROR {e}"))
    page2.goto(f"{BASE}/account.html"); page2.wait_for_timeout(400)
    page2.fill("#email", "jeff@discinsanity.com")
    page2.fill("#pw", "discinsanity")
    page2.click("#form .btn"); page2.wait_for_timeout(400)
    check("Jeff signed in (admin badge)",
          page2.evaluate("document.body.innerText.toLowerCase().includes('admin')"))
    for f in ["index.html", "doubles.html", "events.html"]:
        page2.goto(f"{BASE}/{f}"); page2.wait_for_timeout(600)
        check(f"{f}: Jeff is organizer/admin", page2.evaluate("document.body.classList.contains('org')"))
    page2.goto(f"{BASE}/hub.html"); page2.wait_for_timeout(600)
    check("hub shows Admin badge for Jeff",
          page2.evaluate("document.getElementById('signbtn').textContent.includes('Admin')"))
    page2.screenshot(path=os.path.join(SHOTS, "v_hub_admin.png"))
    page2.goto(f"{BASE}/account.html"); page2.wait_for_timeout(400)
    page2.click("button.red"); page2.wait_for_timeout(300)
    page2.goto(f"{BASE}/doubles.html"); page2.wait_for_timeout(600)
    check("after sign-out organizer dropped", page2.evaluate("!document.body.classList.contains('org')"))

    # 4) housekeeping: suite.js wipes retired date-gate tokens
    ctx3 = browser.new_context(viewport={"width": 420, "height": 900})
    page3 = ctx3.new_page()
    page3.goto(f"{BASE}/hub.html")
    page3.evaluate("localStorage.setItem('di_access','x');localStorage.setItem('discinsanity_access_v1','x')")
    page3.goto(f"{BASE}/events.html"); page3.wait_for_timeout(500)
    check("retired date-gate tokens wiped by suite.js",
          page3.evaluate("!localStorage.getItem('di_access') && !localStorage.getItem('discinsanity_access_v1')"))

    # 5) integration: hub This-Week mirrors Events; profile shows real league stats
    ctx4 = browser.new_context(viewport={"width": 420, "height": 900})
    page4 = ctx4.new_page()
    page4.on("console", lambda m: console_errs.append(f"{page4.url} :: {m.text}") if m.type == "error" else None)
    page4.on("pageerror", lambda e: console_errs.append(f"{page4.url} :: PAGEERROR {e}"))
    page4.goto(f"{BASE}/events.html"); page4.wait_for_timeout(600)   # seeds events store
    page4.goto(f"{BASE}/doubles.html"); page4.wait_for_timeout(600)  # seeds doubles store (Mike R history)
    page4.goto(f"{BASE}/hub.html"); page4.wait_for_timeout(600)
    check("hub This-Week mirrors Events calendar (marker present)",
          page4.evaluate("!!document.querySelector('#week .wkev')"))
    check("hub This-Week shows event course",
          page4.evaluate("document.getElementById('week').innerText.includes('South Mountain')"))
    page4.goto(f"{BASE}/account.html"); page4.wait_for_timeout(400)
    page4.evaluate("setMode('up')")
    page4.fill("#name", "Mike R"); page4.fill("#email", "mike@test.com"); page4.fill("#pw", "test1234")
    page4.click("#form .btn"); page4.wait_for_timeout(400)
    check("profile shows My league stats card",
          page4.evaluate("document.body.innerText.includes('My league stats')"))
    check("profile picked up real doubles points",
          page4.evaluate("leagueStats(DI.current()).dblPts > 0"))
    page4.screenshot(path=os.path.join(SHOTS, "v_account_stats.png"))

    # 6) live Shopify drops feed on hub (needs internet; CORS is open on the shop)
    page4.goto(f"{BASE}/hub.html"); page4.wait_for_timeout(3500)
    check("hub Fresh Drops feed rendered from Shopify",
          page4.evaluate("document.querySelectorAll('#drops .drop').length > 0"))
    page4.screenshot(path=os.path.join(SHOTS, "v_hub_drops.png"))

    browser.close()

httpd.shutdown()

print("\n--- console errors ---")
fatal = [e for e in console_errs if "favicon" not in e]
for e in fatal: print(e)
print(f"\n{len(passed)} passed, {len(errors)} failed, {len(fatal)} console errors")
sys.exit(1 if (errors or fatal) else 0)
