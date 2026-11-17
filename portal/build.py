"""Rebuild JP Structural Analysis Pages information architecture, preserving old routes.

Run only after the existing legacy/historical Pages workflow has finished all
source calculations and the independent R6.26 report. This portal is a
presentation layer, not another FE solver or approval authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from content import PAGES
from learning_system import build as build_study_and_system_pages, verify as verify_study_and_system_pages

SCHEMA="jp.structural.portal.six_section.v1"
VERSION="1.0.0"
BUILD_DATE="2026-11-16"
PRIMARY=("home","studio","projects","developers","research","more")
ROUTE={"home":"index.html","studio":"studio.html","projects":"projects.html",
       "developers":"developers.html","research":"research.html","more":"more.html"}
PAGES_URL="https://fabingurung.github.io/jp-structural-analysis/"
R626_SHA="1d6394d1d871b070d17f056b6eec4c74efdfb3af"

def require(ok,msg):
    if not ok:raise ValueError("PORTAL GOVERNANCE HOLD: "+msg)

def sha(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def load_approved_results(site:Path)->dict:
    source=site/"reports/r6p26/narayani-independent-frame-results.json"
    receipt=site/"reports/r6p26/narayani-verified-manifest.json"
    require(source.is_file() and receipt.is_file(),"R6.26 report not generated before portal")
    results=json.loads(source.read_text("utf8"))
    m=json.loads(receipt.read_text("utf8"))
    require(results.get("project_id")=="PRJ-000007","Narayani source project ID")
    require(results.get("professional_engineering_approval") is False
            and results.get("construction_release") is False
            and results.get("original_F3_unsafe_status_retained") is True,
            "do not republish as engineer-approved or safe F3")
    require(results["model_counts"]["source_GF_columns"]==23
            and results["model_counts"]["independent_3D_elastic_frame_scenarios"]==4,
            "model source counts changed; update portal with review")
    require(len(results["source_members"])==132,"known frozen model count drift")
    require(m["engineering_approval"] is False
            and m["F3_one_way_shear_unsafe_preserved"] is True
            and m["independent_engine_recalculated"] is True,
            "R6.26 model receipt fails protected conditions")
    require(sha(source)==m["files_sha256"]["reports/r6p26/narayani-independent-frame-results.json"],
            "original OpenSees results SHA256 mismatch")
    return {"result_sha256":sha(source),
            "original_report_receipt_sha256":sha(receipt),
            "members":len(results["source_members"]),
            "cases":len(results["cases"]),
            "member_end_records":sum(len(case["signed_local_member_forces"])*2
                                     for case in results["cases"].values()),
            "supports":sum(len(case["base_support_reactions"])
                            for case in results["cases"].values())}

def nav(current):
    items=[]
    for k in PRIMARY:
        label=escape(PAGES[k]["label"])
        current_attr=' aria-current="page"' if k==current else ""
        items.append(f'<a href="{ROUTE[k]}"{current_attr}>{label}</a>')
    return "\n".join(items)

def toc(page,css):
    links=[]
    for i,(id,title,_) in enumerate(page["sections"],1):
        label=escape(title)
        links.append(f'<a href="#{id}" data-toc-for="{id}">'
                     f'<span>{i:02d}</span>{label}</a>')
    return f'<nav class="{css}" aria-label="On this page">\n'+"\n".join(links)+"\n</nav>"

def right_pane(page):
    side=page["right"]
    groups=[]
    for title,links in side["groups"]:
        li="\n".join(f'<li><a href="{escape(uri,quote=True)}">{escape(txt)}</a></li>'
                     for txt,uri in links)
        groups.append(f'<section><h3>{escape(title)}</h3><ul>{li}</ul></section>')
    return f'''<aside class="right-pane" aria-label="Context and reference links">
      <details class="context-details" open>
        <summary><span>Context · {escape(side["title"])}</span><span class="chevron">⌄</span></summary>
        <div class="context-body">
          <p class="context-status">{escape(side["status"])}</p>
          {"".join(groups)}
          <p class="context-note">{escape(side["note"])}</p>
        </div>
      </details>
    </aside>'''

def page_card(current,metrics):
    page=PAGES[current]
    order=list(PRIMARY)
    index=order.index(current)
    prev=order[(index-1)%len(order)]
    nex=order[(index+1)%len(order)]
    sections="\n".join(
        f'''<section id="{ident}" class="content-section" aria-labelledby="title-{ident}">
          <div class="section-index"><span>{i:02d} / {len(page["sections"]):02d}</span><span>{escape(page["label"]).upper()}</span></div>
          <h2 id="title-{ident}">{escape(title)}</h2>
          <div class="section-body">{body}</div>
        </section>'''
        for i,(ident,title,body) in enumerate(page["sections"],1))
    # All authored inner content is repository-controlled; no user-provided HTML.
    numbers={"members":str(metrics["members"]),"cases":str(metrics["cases"]),
             "actionrows":f'{metrics["member_end_records"]:,}'}
    for key,value in numbers.items():
        sections=sections.replace(f'data-num="{key}">{ {"members":"132","cases":"4","actionrows":"1,056"}[key] }',
                                  f'data-num="{key}">{value}')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#f6f4ed">
<meta name="description" content="{escape(page["deck"],quote=True)}">
<meta name="jp-portal-version" content="{VERSION}">
<title>{escape(page["label"])} · JP Structural Analysis</title>
<link rel="stylesheet" href="site-system.css">
<script src="site-system.js" defer></script></head>
<body data-page="{current}">
<a class="skip-link" href="#page-main">Skip to content</a>
<header class="global-header">
 <div class="header-inner">
  <a class="brand" href="index.html" aria-label="JP Structural Analysis homepage"><span class="brand-mark">JP</span><span class="brand-copy">STRUCTURAL<span> ANALYSIS</span><small>FIRST-PARTY ENGINE · RESEARCH</small></span></a>
  <div class="header-meta"><span class="meta-dot"></span> ENGINEERING REVIEW PLATFORM <span class="meta-divider">/</span> V1.0</div>
  <button type="button" id="menu-toggle" class="menu-toggle" aria-expanded="false" aria-controls="primary-nav"><span>Menu</span><span aria-hidden="true">☰</span></button>
  <nav id="primary-nav" class="primary-nav" aria-label="Primary site navigation">{nav(current)}</nav>
 </div>
</header>
<div class="site-shell">
 <div class="intro-wrap">
   <div class="micro-header"><span>{escape(page["eyebrow"])}</span><span>R6.26 SOFTWARE PREVIEW · {BUILD_DATE}</span></div>
   <div class="intro-main"><div><p class="intro-signal"><span class="signal-dot"></span>{escape(page["status"])}</p>
     <h1>{escape(page["title"])}</h1><p class="page-deck">{escape(page["deck"])}</p>
   </div><div class="intro-aside" aria-hidden="true"><span class="intro-cross">✳</span><span>STRUCTURE <b>→</b> EVIDENCE</span></div></div>
 </div>
 <div class="top-toc-wrap"><div class="toc-heading">ON THIS PAGE</div>{toc(page,"top-toc")}</div>
 <div class="three-pane">
   <aside class="left-pane" aria-label="Sticky chapter navigation">
    <div class="left-inner"><div class="rail-label">CHAPTERS / {escape(page["label"]).upper()}</div>
     {toc(page,"left-toc")}
     <p class="rail-foot">SOURCE · CALCULATION · REVIEW<br><span>Versioned and reproducible</span></p>
    </div>
   </aside>
   <main id="page-main" tabindex="-1">
      {sections}
      <nav class="page-adjacent" aria-label="Previous and next site sections">
       <a href="{ROUTE[prev]}"><small>← PREVIOUS SECTION</small><strong>{escape(PAGES[prev]["label"])}</strong></a>
       <a href="{ROUTE[nex]}"><small>NEXT SECTION →</small><strong>{escape(PAGES[nex]["label"])}</strong></a>
      </nav>
   </main>
   {right_pane(page)}
 </div>
</div>
<footer class="global-footer"><div class="footer-inner"><div><strong>JP Structural Analysis</strong><p>First-party OpenSees engine · Pokhara source project · Research and design HOLD where unresolved.</p></div>
 <div><a href="studio.html#governance">Source governance</a><a href="developers.html#qa">Verified QA</a><a href="more.html#library">Historical library</a></div>
 <span>© 2026 · R6.26 software preview · {VERSION}</span></div></footer></body></html>'''

def build(site:Path)->dict:
    src=load_approved_results(site)
    require(set(PAGES)==set(PRIMARY),"every nav page has exactly one content record")
    for current,page in PAGES.items():
        ids=[s[0] for s in page["sections"]]
        require(len(ids)==len(set(ids)) and len(ids)>=4,"missing/duplicate TOC anchor "+current)
        require(all(ident.isidentifier() or "-" in ident for ident in ids),
                "invalid anchor in "+current)
        require(all(page.get(x) for x in ("label","title","deck","right")),"page metadata "+current)
    # Preserve the original home/methods in root so their existing relative
    # links continue working. Historic report and viewer URLs never renamed.
    for original,legacy in (("index.html","legacy-home.html"),("more.html","legacy-more.html")):
        live=site/original
        old=site/legacy
        require(live.exists(),"legacy original missing: "+original)
        if not old.exists():
            shutil.copyfile(live,old)
    for src_name,dest_name in (
            ("site-system.css","site-system.css"),
            ("site-system.js","site-system.js"),
            ("STUDIO_STANDARD.md","standards/studio-standard-v1.md"),
            ("project-input-template-v1.json","standards/project-input-template-v1.json")):
        target=site/dest_name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(HERE/src_name,target)
    for current in PRIMARY:
        (site/ROUTE[current]).write_text(page_card(current,src),encoding="utf8")
    # Build the original report educational study + exact repo/Pages/Actions file trees.
    # This is a read-only presentation artifact; the source PDFs remain in Drive.
    educational=build_study_and_system_pages(site)
    manifest={
      "schema":SCHEMA,"version":VERSION,"build_date":BUILD_DATE,
      "active_real_projects":["PRJ-000007"],
      "navigation":[{"id":id,"label":PAGES[id]["label"],"path":ROUTE[id],
          "toc_count":len(PAGES[id]["sections"])}
          for id in PRIMARY],
      "frozen_engine_software_sha":R626_SHA,
      "source_report_results_sha256":src["result_sha256"],
      "source_report_receipt_sha256":src["original_report_receipt_sha256"],
      "numeric_scope":{key:src[key] for key in ("members","cases","member_end_records","supports")},
      "real_building_engineering_approval":False,
      "historical_F3_one_way_shear_safe":False,
      "verified_source_model_ready_for_full_design":False,
      "original_report_explainer":{"page":"original-report-guide.html",
            "reading_order":"6→5→4→3→2→1","primary_source":"revised G+1.5 PDF",
            "educational_only":True},
      "system_file_tree":{"page":"system-map.html","manifest":"site-file-inventory.json",
            "public_files_in_inventory":educational["files"],
            "action_workflow_definitions":educational["workflows"]},
      "legacy_routes_preserved":["legacy-home.html","legacy-more.html","report.html",
          "projects/index.html","r6p23.html","r6p25.html","r6p26-report.html"],
      "files_sha256":{},
    }
    files=[*ROUTE.values(),"original-report-guide.html","system-map.html","site-file-inventory.json",
           "site-system.css","site-system.js",
           "standards/studio-standard-v1.md","standards/project-input-template-v1.json",
           "legacy-home.html","legacy-more.html"]
    manifest["files_sha256"]={f:sha(site/f) for f in sorted(files)}
    (site/"portal-manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf8")
    verify(site)
    return manifest

def verify(site:Path)->dict:
    m=json.loads((site/"portal-manifest.json").read_text("utf8"))
    require(m["schema"]==SCHEMA and m["frozen_engine_software_sha"]==R626_SHA,
            "portal source identity changed")
    require(m["active_real_projects"]==["PRJ-000007"],"project count unreviewed")
    require(m["real_building_engineering_approval"] is False
            and m["historical_F3_one_way_shear_safe"] is False,
            "unsafe building state must not be promoted")
    require(len(m["navigation"])==6 and all(q["toc_count"]>=4 for q in m["navigation"]),
            "six-page top and left nav incomplete")
    study=verify_study_and_system_pages(site)
    require(study["workflows"]==13 and study["guide_sections"]>=12,
            "original report/source code teaching system failed")
    require(m.get("original_report_explainer",{}).get("educational_only") is True,
            "original report guide cannot be a construction design approval")
    require(m.get("system_file_tree",{}).get("action_workflow_definitions")==13,
            "current GitHub Actions inventory absent")
    for f,digest in m["files_sha256"].items():
        require((site/f).is_file() and sha(site/f)==digest,
                "source/output portal asset tampered: "+f)
    for item in m["navigation"]:
        s=(site/item["path"]).read_text("utf8")
        require('id="page-main"' in s and 'class="top-toc"' in s
                and 'class="left-toc"' in s and 'class="right-pane"' in s
                and 'class="page-adjacent"' in s,
                "four pane portal navigation or bottom links missing "+item["path"])
        require(all('href="'+p+'"' in s for p in ROUTE.values()),
                "every page must link all six primary sections: "+item["path"])
        for ident,_,_ in PAGES[item["id"]]["sections"]:
            require(f'id="{ident}"' in s and s.count(f'data-toc-for="{ident}"')==2,
                    "top AND left TOC anchor missing or duplicated "+item["path"]+" #"+ident)
    require("NOT SAFE IN ONE WAY SHEAR" in (site/"research.html").read_text(),
            "historical adverse F3 not disclosed")
    require("r6p26-report.html" in (site/"projects.html").read_text(),
            "active project's independent report must be discoverable")
    require("other" not in m["active_real_projects"],
            "fake project")
    return m

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--site-dir",type=Path,required=True)
    p.add_argument("--verify-only",action="store_true")
    args=p.parse_args()
    manifest=verify(args.site_dir) if args.verify_only else build(args.site_dir)
    print("JP_PORTAL_V1_6_PAGES_INTEGRITY_PASS",
          json.dumps({"version":manifest["version"],"sha":manifest["source_report_results_sha256"],
                      "pages":len(manifest["navigation"]),"active_projects":len(manifest["active_real_projects"]),
                      "engineering_approved":manifest["real_building_engineering_approval"]}))
if __name__=="__main__":
    main()
