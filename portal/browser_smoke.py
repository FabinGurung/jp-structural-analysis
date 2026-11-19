"""Real Chrome UI smoke for four-page portal at phone and desktop viewports."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROUTES=("index.html","studio.html","projects.html","more.html")
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def run(site:Path,output:Path):
    output.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(("127.0.0.1",0),
        partial(Quiet,directory=str(site.resolve())))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f"http://127.0.0.1:{server.server_port}/"
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True)
            for name,width,height in (("phone",390,844),("tablet",768,950),("desktop",1440,920)):
                page=b.new_page(viewport={"width":width,"height":height})
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                for route in ROUTES:
                    response=page.goto(base+route,wait_until="networkidle")
                    assert response is not None and response.status==200,(route,response)
                    assert page.locator("#page-main").count()==1,route
                    assert page.locator("#primary-nav a").count()==4,route
                    assert page.locator(".top-toc a").count()>=4,route
                    assert page.locator(".left-toc a").count()>=4,route
                    assert page.locator(".right-pane").count()==1,route
                    assert page.locator(".page-adjacent a").count()==2,route
                    for a in page.locator(".top-toc a").all():
                        ident=a.get_attribute("href")
                        assert ident and ident.startswith("#")
                        assert page.locator(ident).count()==1,(route,ident)
                    assert not errors,(route,errors)
                    sizes=page.evaluate("""({
                       viewport:window.innerWidth,
                       document:document.documentElement.scrollWidth,
                       body:document.body.scrollWidth
                    })""")
                    assert sizes["document"]<=sizes["viewport"]+2,(route,name,sizes)
                    assert sizes["body"]<=sizes["viewport"]+2,(route,name,sizes)
                    if width<=780:
                        assert page.locator("#menu-toggle").is_visible(),route
                        assert not page.locator("#primary-nav").is_visible(),route
                        page.locator("#menu-toggle").click()
                        assert page.locator("#primary-nav").is_visible(),route
                        assert page.locator("#menu-toggle").get_attribute("aria-expanded")=="true"
                        page.locator("#menu-toggle").click()
                        assert not page.locator("#primary-nav").is_visible()
                    else:
                        assert page.locator("#primary-nav").is_visible(),(route,name)
                    if route=="studio.html":
                        assert "Studio Standard" in page.locator("h1").inner_text() or "reusable standard" in page.locator("h1").inner_text()
                    if route=="projects.html":
                        assert "Narayani" in page.locator("h1").inner_text()
                        assert page.locator('#purpose').count()==1
                        assert page.locator('#design').count()==1
                        assert page.locator('a[href="r6p26-report.html"]').count()==0
                        stage=page.locator("#purpose").inner_text()
                        assert "Office Building" in stage and "Residential" in stage
                        assert "3.048 m" in stage and "9.144 m" in stage
                        assert "application" in stage
                        assert page.locator('#purpose a[href^="https://drive.google.com/file/d/"]').count()==1
                    if route=="more.html":
                        assert page.locator('a[href="engine-explained.html"]').count()>=1
                        assert page.locator('a[href="example-sar-report.html"]').count()>=1
                        assert page.locator("#research").count()==1
                        assert "Original" in page.locator("#research").inner_text()
                        assert "OpenSeesPy" in page.locator("#research").inner_text()
                # Explicit learning pages: same real browser, source-bound facts,
                # complete tree readability, sticky/upper TOC and mobile menu.
                for route in ("original-report-guide.html","independent-report-guide.html","system-map.html"):
                    resp=page.goto(base+route,wait_until="networkidle")
                    assert resp is not None and resp.status==200,(route,resp)
                    expected=13 if route=="original-report-guide.html" else 7
                    assert page.locator(".guide-section").count()==expected,(route,name)
                    assert page.locator(".guide-topnav a").count()==expected,(route,name)
                    assert page.locator(".guide-right").count()==1,(route,name)
                    assert page.locator("#primary-nav a").count()==4,(route,name)
                    for link in page.locator(".guide-topnav a").all():
                        href=link.get_attribute("href")
                        assert href and page.locator(href).count()==1,(route,href)
                    if route=="original-report-guide.html":
                        for token in ("36.915","0.9404%","894.9803",
                                      "Chapter 6","Chapter 5","Chapter 1",
                                      "NOT SAFE IN ONE WAY SHEAR"):
                            assert token in page.locator("#guide-main").inner_text(),token
                        assert page.locator('a[href="#worked-foundation"]').count()>=1
                        assert page.locator('a[href="r6p27-construction-review.html"]').count()>=1
                    elif route=="independent-report-guide.html":
                        assert "1,056" in page.locator("#guide-main").inner_text()
                        assert "OpenSeesPy" in page.locator("#guide-main").inner_text()
                    else:
                        assert page.locator('a[href="site-file-inventory.json"]').count()>=1
                        for wf in ("pages.yml","portal-v1-qa.yml",
                                   "r6p26-report-qa.yml","r6p27-source-design-qa.yml"):
                            assert wf in page.content(),wf
                        assert "complete actual file inventory" in page.content().lower()
                    sizes=page.evaluate("""({
                       viewport:window.innerWidth,
                       document:document.documentElement.scrollWidth,
                       body:document.body.scrollWidth
                    })""")
                    assert sizes["document"]<=sizes["viewport"]+2,(route,name,sizes)
                    assert sizes["body"]<=sizes["viewport"]+2,(route,name,sizes)
                    if width<=780:
                        assert page.locator("#menu-toggle").is_visible(),route
                        assert not page.locator("#primary-nav").is_visible(),route
                        page.locator("#menu-toggle").click()
                        assert page.locator("#primary-nav").is_visible(),route
                        page.locator("#menu-toggle").click()
                        assert not page.locator("#primary-nav").is_visible(),route
                    if name in ("phone","desktop"):
                        target=output/(name+"-"+route.replace(".html","")+".png")
                        page.screenshot(path=str(target),full_page=False)
                        assert target.stat().st_size>10000,(target,target.stat().st_size)
                for route in (("index.html","studio.html","projects.html") if name=="phone" else
                              ("index.html","more.html")):
                    page.goto(base+route,wait_until="networkidle")
                    target=output/(name+"-"+route.replace(".html","")+".png")
                    page.screenshot(path=str(target),full_page=True)
                    assert target.stat().st_size>25000,(target,target.stat().st_size)
                print("JP_PORTAL_V1_"+name.upper()+"_ALL_4_PAGES_RESPONSIVE_QA_PASS")
                page.close()
            b.close()
    finally:
        server.shutdown();server.server_close()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site-dir",type=Path,required=True)
    p.add_argument("--screenshots",type=Path,required=True)
    a=p.parse_args()
    run(a.site_dir,a.screenshots)
