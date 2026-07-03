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

    # 6) NEW doubles flow: open check-in -> draw teams + starting holes; org scores +/-par; save
    ctx5 = browser.new_context(viewport={"width": 420, "height": 900})
    page5 = ctx5.new_page()
    page5.on("console", lambda m: console_errs.append(f"{page5.url} :: {m.text}") if m.type == "error" else None)
    page5.on("pageerror", lambda e: console_errs.append(f"{page5.url} :: PAGEERROR {e}"))
    page5.goto(f"{BASE}/doubles.html"); page5.wait_for_timeout(600)
    check("doubles: check-in view is default (no standings tab)",
          page5.evaluate("document.getElementById('v-checkin').classList.contains('on') && !document.getElementById('v-standings')"))
    check("doubles: course picker populated from courses.js",
          page5.evaluate("document.querySelectorAll('#courseSel option').length >= 6"))
    # viewer adds himself + checks in 3 more
    page5.fill("#addName", "Zed Tester"); page5.click("text=Add"); page5.wait_for_timeout(200)
    for i in range(3): page5.locator("#roster .toggle").nth(i).click()
    check("doubles: 4 players checked in (viewer, no code needed)",
          page5.evaluate("document.getElementById('count').textContent.includes('4')"))
    # viewer taps draw -> teams + starting holes
    page5.click(".btn.gold"); page5.wait_for_timeout(300)
    check("doubles: draw made teams (viewer click)", page5.evaluate("document.querySelectorAll('#teams .team').length >= 2"))
    check("doubles: every team got a starting hole",
          page5.evaluate("[...document.querySelectorAll('#teams .hole .hn')].every(e=>+e.textContent>=1)"))
    check("doubles: draw survives reload (persisted)",
          (page5.reload(), page5.wait_for_timeout(600),
           page5.evaluate("document.querySelectorAll('#teams .team').length >= 2"))[-1])
    # organizer enters scores -> UDisc-style to-par chip -> save -> history detail
    page5.evaluate("window.prompt = () => 'discinsanity'")
    page5.click("#hkey"); page5.wait_for_timeout(300)
    n_teams = page5.evaluate("document.querySelectorAll('#teams .team').length")
    for i in range(n_teams):
        page5.locator("#teams .tscore").nth(i).fill(str(50 + i))
    page5.wait_for_timeout(200)
    check("doubles: to-par chip shows UDisc-style (50 on par 54 = -4)",
          page5.evaluate("document.getElementById('tp-0').textContent === '-4'"))
    before = page5.evaluate("JSON.parse(localStorage.getItem('discinsanity_doubles_v1')).rounds.length")
    page5.click("#saveBtn"); page5.wait_for_timeout(400)
    after = page5.evaluate("JSON.parse(localStorage.getItem('discinsanity_doubles_v1')).rounds.length")
    check("doubles: save added a round to history", after == before + 1)
    check("doubles: round detail shows hole + score to par",
          page5.evaluate("document.getElementById('rdBody').innerText.includes('H') && document.getElementById('rdBody').innerText.includes('(')"))
    # course DB: org edits par -> label + math update
    page5.evaluate("DIC.set('South Mountain','White Tee',{par:57,holes:18})")
    page5.evaluate("renderCourseSel()")
    check("courses: par override reflected in picker",
          page5.evaluate("document.querySelector('#courseSel option').textContent.includes('par 57')"))
    check("courses: toPar math (54 on par 57 = -3, 57 = E)",
          page5.evaluate("DIC.toPar(54,57)==='-3' && DIC.toPar(57,57)==='E'"))
    page5.screenshot(path=os.path.join(SHOTS, "v_doubles_new.png"))

    # 7) tags starting holes (organizer propagated from doubles via suite session)
    page5.goto(f"{BASE}/index.html"); page5.wait_for_timeout(700)
    check("tags: organizer inherited for holes test", page5.evaluate("document.body.classList.contains('org')"))
    page5.evaluate("players.slice(0,6).forEach(p=>{tonight[p.name]=tonight[p.name]||{};tonight[p.name].present=true})")
    page5.evaluate("assignHoles()")
    page5.wait_for_timeout(300)
    check("tags: starting-hole groups rendered",
          page5.evaluate("document.querySelectorAll('#holeGroups .hgrp').length >= 2"))
    check("tags: groups spread across holes",
          page5.evaluate("new Set([...document.querySelectorAll('#holeGroups .hole .hn')].map(e=>e.textContent)).size >= 2"))
    page5.screenshot(path=os.path.join(SHOTS, "v_tags_holes.png"))

    # 8) SCORECARD: doubles team -> hole-by-hole card -> totals flow back
    ctx6 = browser.new_context(viewport={"width": 420, "height": 900})
    page6 = ctx6.new_page()
    page6.on("console", lambda m: console_errs.append(f"{page6.url} :: {m.text}") if m.type == "error" else None)
    page6.on("pageerror", lambda e: console_errs.append(f"{page6.url} :: PAGEERROR {e}"))
    page6.goto(f"{BASE}/doubles.html"); page6.wait_for_timeout(600)
    for i in range(4): page6.locator("#roster .toggle").nth(i).click()
    page6.click(".btn.gold"); page6.wait_for_timeout(300)
    team_hole = page6.evaluate("JSON.parse(localStorage.getItem('discinsanity_doubles_v1')).tonight.teams[0].hole")
    page6.locator("#teams .pad").nth(0).click(); page6.wait_for_timeout(800)
    check("scorecard: opens prefilled from doubles team",
          "scorecard.html" in page6.url and page6.evaluate("document.getElementById('v-score').classList.contains('on')"))
    check("scorecard: starts on the team's assigned hole",
          page6.evaluate(f"document.getElementById('holeNum').textContent === 'Hole {team_hole}'"))
    # UDisc-style interactions: tap = par, steppers, color class
    page6.locator(".sc").nth(0).click(); page6.wait_for_timeout(150)
    check("scorecard: tap empty score sets par", page6.evaluate("document.querySelector('.sc').textContent === '3'"))
    page6.locator(".prow .step").nth(1).click(); page6.wait_for_timeout(150)  # + stepper
    check("scorecard: + stepper -> bogey color", page6.evaluate("document.querySelector('.sc').classList.contains('bogey')"))
    page6.click("#nextBtn"); page6.wait_for_timeout(150)
    nxt = team_hole % 18 + 1
    check("scorecard: next hole advances (wraps course)",
          page6.evaluate(f"document.getElementById('holeNum').textContent === 'Hole {nxt}'"))
    page6.click("#prevBtn"); page6.wait_for_timeout(150)
    # per-hole par + distance editing persists through courses.js
    page6.evaluate("DIC.setHole(card.course.course,card.course.layout,curHole(),{par:4,dist:310});renderScore()")
    check("scorecard: hole par/distance editable + shown",
          page6.evaluate("document.getElementById('holePar').textContent.includes('4') && document.getElementById('holePar').textContent.includes('310 ft')"))
    # score every hole at par, finish, send back to doubles
    page6.evaluate("seq().forEach(h=>{card.rows[0].scores[h]=DIC.holePar(card.course.course,card.course.layout,h)});save();renderScore()")
    expected = page6.evaluate("rowTotal(card.rows[0]).t")
    page6.click("text=🏁 Finish round"); page6.wait_for_timeout(300)
    check("scorecard: summary shows E for all-par round",
          page6.evaluate("document.getElementById('sumBody').innerText.includes('(E)')"))
    check("scorecard: send-to-doubles offered",
          page6.evaluate("document.getElementById('sendBtn').style.display==='block' && document.getElementById('sendBtn').textContent.includes('Doubles')"))
    page6.screenshot(path=os.path.join(SHOTS, "v_scorecard_summary.png"))
    page6.click("#sendBtn"); page6.wait_for_timeout(1600)
    check("scorecard: team total flowed back into doubles",
          "doubles.html" in page6.url and page6.evaluate("JSON.parse(localStorage.getItem('discinsanity_doubles_v1')).tonight.teams[0].score") == expected)

    # 9) SCORECARD from tags group + import back into tonight's scores
    page6.goto(f"{BASE}/index.html"); page6.wait_for_timeout(700)
    page6.evaluate("window.prompt = () => 'discinsanity'")
    if not page6.evaluate("document.body.classList.contains('org')"):
        page6.click("#hkey"); page6.wait_for_timeout(300)
    page6.evaluate("players.slice(0,4).forEach(p=>{tonight[p.name]=tonight[p.name]||{};tonight[p.name].present=true});assignHoles()")
    page6.wait_for_timeout(300)
    page6.locator("#holeGroups .hpad").nth(0).click(); page6.wait_for_timeout(800)
    check("scorecard: opens prefilled from tags group",
          "scorecard.html" in page6.url and page6.evaluate("card.from==='tags' && card.rows.length>=2"))
    page6.evaluate("card.rows.forEach(r=>seq().forEach(h=>{r.scores[h]=DIC.holePar(card.course.course,card.course.layout,h)}));save();renderScore()")
    page6.click("text=🏁 Finish round"); page6.wait_for_timeout(300)
    page6.click("#sendBtn"); page6.wait_for_timeout(1600)
    check("tags: back on Tags after send", "index.html" in page6.url)
    page6.click("text=⬇ Import Scorecard result"); page6.wait_for_timeout(300)
    check("tags: scorecard totals imported into tonight's scores",
          page6.evaluate("players.filter(p=>tonight[p.name]&&tonight[p.name].present&&tonight[p.name].score!=null).length >= 2"))
    page6.screenshot(path=os.path.join(SHOTS, "v_tags_imported.png"))

    # 10) live Shopify drops feed on hub (needs internet; CORS is open on the shop)
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
