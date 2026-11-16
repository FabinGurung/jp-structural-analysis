"""Real Chrome UI smoke for six-page portal at phone and desktop viewports."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROUTES=("index.html","studio.html","projects.html","developers.html","research.html","more.html")
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
                    assert page.locator("#primary-nav a").count()==6,route
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
                        assert "Copy prompt" in page.locator(".copy-prompt").inner_text()
                        assert "Do not copy Narayani" in page.locator("#handover-text").inner_text()
                    if route=="projects.html":
                        assert page.locator('a[href="r6p26-report.html"]').count()>=1
                        assert "NOT SAFE" in page.locator("#actual-vs-assumed").inner_text()
                    if route=="research.html":
                        assert "NOT SAFE" in page.locator("#open-debt").inner_text()
                for route in (("index.html","studio.html","projects.html") if name=="phone" else
                              ("index.html","developers.html","research.html")):
                    page.goto(base+route,wait_until="networkidle")
                    target=output/(name+"-"+route.replace(".html","")+".png")
                    page.screenshot(path=str(target),full_page=True)
                    assert target.stat().st_size>25000,(target,target.stat().st_size)
                print("JP_PORTAL_V1_"+name.upper()+"_ALL_6_PAGES_RESPONSIVE_QA_PASS")
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
