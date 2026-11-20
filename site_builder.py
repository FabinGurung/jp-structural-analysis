"""JP Structural Analysis: minimal 4-page publication + one computed 6-chapter report.

No experimental routes, old workflow UI or database identifiers. Archives in Drive.
All published numerical values are recomputed from REAL OpenSeesPy reference solves.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from html import escape as e
from pathlib import Path

from r6p23.engine import build as solve, digest as model_digest
from r6p23.runner import reference_fixture
from r6p30.beam_design import member_checks_from_preview
from r6p30.column_pmm import column_checks_from_preview, ASSUMED, puz_kN, steel_area, _uniaxial_response, uniaxial_at_pu

DRIVE_ARCHIVE="https://drive.google.com/drive/folders/1ViudVSKVdDr7OPl-xFjJTankIDAEQJoO"
ORIGINAL_REPORT="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
ORIGINAL_DRAWING="https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
ORIGINAL_SOIL="https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"
CODE_IS456="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
REPO="https://github.com/FabinGurung/jp-structural-analysis"
NAV=(("Home","index.html"),("Studio Standard","studio.html"),("Projects","projects.html"),("More","more.html"))
CSS=r"""<style>
:root{--ink:#252841;--muted:#677083;--paper:#f8f8f6;--line:#e1e2e8;--indigo:#51448b}
*{box-sizing:border-box}body{background:var(--paper);color:var(--ink);margin:0;font:15px/1.65 system-ui,Arial,sans-serif}
a{color:#473791;text-underline-offset:3px}.top{background:white;border-bottom:1px solid var(--line);padding:15px max(3vw,18px);display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.brand{font-weight:900;letter-spacing:.08em}.top nav{display:flex;gap:16px;flex-wrap:wrap}.top nav a{text-decoration:none;color:#333650;font-size:14px}
main{max-width:1160px;margin:22px auto;padding:0 20px 60px}
.hero,.panel{background:white;border:1px solid var(--line);border-radius:14px;padding:clamp(20px,3vw,36px);margin-bottom:16px}
.eyebrow{color:var(--indigo);text-transform:uppercase;letter-spacing:.15em;font-weight:800;font-size:11px}
h1{font-size:clamp(27px,3.6vw,46px);line-height:1.1;margin:12px 0 15px}h2{font-size:23px;line-height:1.22;margin-top:0}
h3{margin:18px 0 8px;font-size:16px}p{margin:9px 0 16px;color:#4e5369}.sub{max-width:780px;font-size:17px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.tile{border:1px solid var(--line);border-radius:12px;padding:18px;background:#fff}.tile b{font-size:18px}.tile p{font-size:13px}
.meta{display:flex;flex-wrap:wrap;gap:10px}.meta span{background:#f0eff8;border-radius:8px;padding:6px 10px;font-size:13px;color:#3d336d}
.report-layout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:16px}
.toc{background:white;padding:17px;position:sticky;top:15px;align-self:start;border:1px solid var(--line);border-radius:12px}
.toc a{font-size:13px;display:block;padding:9px 0;border-bottom:1px solid var(--line);text-decoration:none}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:700px}td,th{padding:9px 10px;border-bottom:1px solid #e5e5ec;text-align:left;vertical-align:top}
th{background:#f4f3f7}section[id]{scroll-margin-top:15px}.scroll{overflow-x:auto}
.note{border-left:4px solid #c39a66;padding:12px 16px;background:#fdf8ed;margin:14px 0}
.detail{border:1px solid var(--line);border-radius:9px;padding:12px}summary{font-weight:700;cursor:pointer}
.footer{max-width:1160px;margin:0 auto;padding:20px;font-size:12px;color:var(--muted)}
button{border:1px solid var(--line);padding:8px 13px;border-radius:8px;background:#fff;font-weight:700;cursor:pointer}
@media(max-width:780px){.report-layout{grid-template-columns:1fr}.toc{position:static}.top{gap:9px}}
@page{size:A4;margin:16mm 15mm}
@media print{body{background:white;font-family:Georgia,'Times New Roman',serif;font-size:11px}.top,.footer,.no-print{display:none!important}main{max-width:none;margin:0;padding:0}.hero,.panel{border:0;padding:0;margin:0 0 10mm;break-inside:avoid}
.report-layout{display:block}.toc{display:block;border:0;position:static;break-after:page;padding:0}.toc a{font-size:12px}
section[id]{break-before:page}.tile{break-inside:avoid}.scroll{overflow:visible}table{font-size:9px;min-width:0}a{color:black;text-decoration:none}}
</style>"""
def page(title,subtitle,body,report=False):
    nav=''.join(f'<a href="{u}">{e(k)}</a>' for k,u in NAV)
    head=f'<header class="top"><div class="brand">JP / STRUCTURAL ANALYSIS</div><nav>{nav}</nav></header>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — JP Structural Analysis</title>{CSS}</head>
<body>{head}<main><div class="hero"><div class="eyebrow">JP Structural Analysis / {("report" if report else "workspace")}</div>
<h1>{e(title)}</h1><p class="sub">{e(subtitle)}</p></div>{body}</main>
<div class="footer">Project sources in Google Drive · Numerical examples are not professional design approval</div></body></html>'''
def box(title,content,anchor=""):
    return f'<section class="panel"'+(f' id="{anchor}"' if anchor else '')+f'><h2>{e(title)}</h2>{content}</section>'
def table(headers,rows):
    h=''.join("<th>"+e(x)+"</th>" for x in headers)
    b=''.join('<tr>'+''.join('<td>'+e(str(v))+'</td>' for v in row)+'</tr>' for row in rows)
    return '<div class="scroll"><table><thead><tr>'+h+'</tr></thead><tbody>'+b+'</tbody></table></div>'
def n(x):
    return f"{float(x):,.3f}"
def A(href,label):
    return f'<a href="{href}">{e(label)}</a>'
def read_actual_solver():
    spec=reference_fixture()
    out=solve(spec)
    assert out["engineering_approval"] is False
    assert out["source_ledger"]["gravity_totals_kN"]["DL"]==339.0
    assert out["source_ledger"]["gravity_totals_kN"]["LL"]==62.0
    assert out["topology"]["shell_count"]==31
    assert out["topology"]["beam_segment_count"]==32
    assert out["topology"]["column_segment_count"]==8
    assert len(out["solutions"])==2
    preview={"schema":"synthetic-open-sees-preview",
      "source_SHA256":model_digest(spec),"classification":"SYNTHETIC_REFERENCE",
      "engineering_approval":False,"topology":out["topology"],
      "solutions":out["solutions"]}
    beam=member_checks_from_preview(preview)
    column=column_checks_from_preview(preview)
    assert beam["rows_count"]==256 and column["row_count"]==64
    assert beam["original_narayani_F3_NOT_SAFE_retained"]
    assert column["original_narayani_F3_not_safe_preserved"]
    return spec,out,beam,column

def report(spec,solved,beam,col):
    loading=solved["source_ledger"]["gravity_totals_kN"]
    tf=solved["topology"]
    mode=solved["solutions"]["FLEXIBLE_SHELL"]
    rigid=solved["solutions"]["RIGID_INPLANE_MPC"]
    disp=lambda m:max(float(x) for x in m["DL"]["floor_max_vertical_displacement_m"].values())*1000.
    bend=beam["governing_bending_row"]
    sh=beam["governing_vertical_shear_row"]
    gov=col["governing_example"]
    cv=gov["PMM"]
    summary=table(("Report scope","Computed information","What it means"),[
      ("3-D elastic FE","31 shells · 32 beams · 8 columns","Actually solved by OpenSeesPy"),
      ("Dead load",n(loading["DL"])+" kN","Source-derived synthetic model ledger"),
      ("Live load",n(loading["LL"])+" kN","Source-derived synthetic model ledger"),
      ("Flexible diaphragm vertical displacement",n(disp(mode))+" mm","Actually solved DL"),
      ("Rigid diaphragm vertical displacement",n(disp(rigid))+" mm","Actually solved DL"),
      ("Beam design screens",str(beam["rows_count"]),"Matched same-end My/Vz for two modes and two synthetic U± cases"),
      ("Column P–M–M screens",str(col["row_count"]),"Simultaneous N/My/Mz with approximate strain-compatible uniaxial capacities"),
    ])
    btable=table(("Item","Selected genuine numerical result"),[
       ("Source member",bend["member"]+" / "+bend["end"]+" / "+bend["mode"]),
       ("Governing bending My",n(bend["flexure"]["Mu_abs_kNm"])+" kNm"),
       ("Required longitudinal steel (including min.)",n(bend["flexure"]["As_required_including_min_mm2"])+" mm²"),
       ("Assumed top/bottom steel",n(bend["flexure"]["As_provided_tension_mm2"])+" mm²"),
       ("Governing vertical shear Vz",n(sh["shear"]["Vu_abs_kN"])+" kN"),
       ("Concrete shear strength τc",n(sh["shear"]["tau_c_MPa"])+" MPa"),
       ("Max stirrup spacing for governing Vz",n(sh["shear"]["stirrup_s_upper_bound_mm"])+" mm"),
       ("Strength-screen results",str(beam["isolated_screen_flexure_ok_count"])+
        "/256 flexure, "+str(beam["isolated_screen_shear_ok_count"])+"/256 shear"),
    ])
    ctable=table(("Item","Governing approximate P–M–M value"),[
       ("Source column",gov["member"]+" / "+gov["end"]+" / "+gov["diaphragm"]),
       ("Synthetic U case",gov["combination"]),
       ("Signed original local N",n(gov["signed_local_actions"]["N"])+" kN"),
       ("Mapped compression (I:+N; J:−N)",n(gov["compression_signed_kN"])+" kN"),
       ("Compression action screened Pu",n(cv["Pu_assumed_compression_kN"])+" kN"),
       ("Signed local My / Mz",n(cv["signed_local_My_kNm"])+" / "+n(cv["signed_local_Mz_kNm"])+" kNm"),
       ("Puz reference",n(cv["Puz_IS456_kN"])+" kN"),
       ("Approx. uniaxial My1 / Mz1",n(cv["My1_approx_capacity_kNm"])+" / "+n(cv["Mz1_approx_capacity_kNm"])+" kNm"),
       ("IS456 39.6 αn",n(cv["biaxial_exponent_alpha"])),
       ("Minimum eccentricity scenario (one axis at a time)",
        cv["minimum_eccentricity_governing"]),
       ("Biaxial interaction measure",n(cv["biaxial_load_contour_utilization"])),
       ("Excluded axial tension cases",str(col["axial_tension_rows_excluded"])),
       ("Approximate screen results",str(col["approx_screen_ok_count"])+"/64 within bounded model"),
    ])
    chapters=[
       ("chapter1","1.0 Introduction",f'''<p><strong>Purpose:</strong> a fully assumed 4m × 4m plan and two elevated
       reinforced-concrete floors demonstrate the working project-independent OpenSees report engine.
       The model is NOT the Narayani building. No site-specific occupancy or permit approval is inferred.</p>
       <div class="note">Design examples are for method verification only, with construction release false.</div>'''),
       ("chapter2","2.0 General Data for Structural Analysis",
        table(("Category","Assumed source fixture"),[
         ("Plan grid","0, 1, 2, 3, 4 m in both axes"),
         ("Floor levels","0, 3, 6 m"),
         ("Slabs","120 mm thick; one upper-floor opening of 1 m²"),
         ("Beam section","300 × 450 mm, M25 assumed for later RC checks"),
         ("Column section","400 × 400 mm, 8Ø16 reinforcement assumed in PMM method"),
         ("Source elastic modulus","25 GPa"),
         ("Dead load",n(loading["DL"])+" kN from actual model ledger"),
         ("Live load",n(loading["LL"])+" kN from actual model ledger"),
         ("Diagnostic lateral action","10 kN HX; not a design earthquake"),
         ("Loads for design screens","1.2 DL + 1.5 LL ± diagnostic HX; NOT source NBC ULS envelope")])
         +f'<p>{A(CODE_IS456,"Original IS456:2000 code reference")}. These are synthetic inputs, not copied Narayani values.</p>'),
       ("chapter3","3.0 Analysis and Design Procedure",
        '<p>OpenSeesPy uses elasticBeamColumn members and ShellMITC4 two-way slab elements. '
        'It solves flexible-shell and rigid-in-plane diaphragm alternatives separately. '
        'The tested beam procedure evaluates IS456 rectangular flexure and vertical shear for every '
        'signed same-beam-end load combination. The column procedure evaluates an approximate '
        'uniaxial fiber strain-compatibility section strength at a given Pu, then the IS456 '
        '§39.6 biaxial load-contour exponent.</p>'
        '<div class="note">The column uniaxial capacities are numerical approximations, NOT verified SP16 '
        'chart capacities. Axial member-end forces now follow the signed I/J compression convention in '
        'this demonstration. Tension cases are excluded, not disguised as compression. The uniaxial capacities remain outside SP16 verification.</div>'),
       ("chapter4","4.0 Structural Model",
        f'<p>Exact conforming shared nodes; {tf["shell_count"]} ShellMITC4 plates, '
        f'{tf["beam_segment_count"]} beam segments, {tf["column_segment_count"]} column segments, '
        'four fixed corner bases; one slab opening physically removed. Neither soil springs nor '
        'the staircase are included.</p>'),
       ("chapter5","5.0 Structural Analysis Results",summary+
        '<p>Loads, support reactions, signed member end forces and displacements come from a fresh '
        'OpenSeesPy solve. This is a static elastic benchmark; mass participation, response spectrum '
        'and seismic code drift have not been generated.</p>'),
       ("chapter6","6.0 Design of Structural Elements",
        '<h3>6.1 Beam flexure and vertical shear</h3>'+btable+
        '<p>All 256 same-member/end/mode/combination signed My/Vz results are checked using '
        'the stated M25/Fe500, 300×450 mm beam and assumed reinforcement/stirrups. '
        +A('data/beam-checks.csv','Inspect full beam checks (CSV)')+'.</p>'
        '<h3>6.2 Column axial load and biaxial bending</h3>'+ctable+
        '<p>64 end-case interactions use signed simultaneous local N, My and Mz from actual '
        'OpenSees results. The isolated biaxial contour is (|My|/My1)^α+(|Mz|/Mz1)^α, '
        'including the one-axis-at-a-time minimum eccentricity rule; the uniaxial capacities derive from '
        'an approximate 64-strip compression block with distinct full-compression and tension-zone strain assumptions. '
        +A('data/column-pmm-checks.csv','Inspect all 64 column checks (CSV)')+'.</p>'
        '<div class="note"><strong>Not a completed structural design:</strong> no signed '
        'real-world member orientation and design load sign verification, original-project seismic actions, '
        'slenderness/P-Δ, ductile confinement, joint forces, development length, '
        'verified SP16 column capacity diagrams, or independent columns/slabs/footing/staircase '
        'design for Narayani. The original F3 one-way shear result remains NOT SAFE.</div>'
        '<h3>6.3 Additional original-report elements</h3><p>Slab reinforcement, isolated '
        'and combined footings, and stair reinforcement are outside the current production '
        'design modules. Their past exploratory outputs are stored in the Drive archive '
        'and are deliberately not republished as live project designs.</p>'),
    ]
    toc='<nav class="toc"><b>TABLE OF CONTENTS</b>'+''.join(
      f'<a href="#{key}">{e(label)}</a>' for key,label,_ in chapters)+'</nav>'
    sections=''.join(box(label,text,key) for key,label,text in chapters)
    return page("Structural analysis and design — worked reference report",
        "Original six-chapter organization. Genuine OpenSees frame and slab results; bounded beam and column design checks.",
        '<div class="no-print"><button onclick="window.print()">Print / Save A4 PDF</button></div>'
        '<div class="report-layout">'+toc+'<article>'+sections+'</article></div>',True)

def write_csv(path:Path,cols,rows):
    with path.open("w",encoding="utf8",newline="") as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(rows)

def build(out:Path=Path("site")):
    out.mkdir(parents=True,exist_ok=True)
    data=out/"data";data.mkdir(exist_ok=True)
    spec,solved,beam,col=read_actual_solver()
    # Preserve the signed independent numerical evidence, but not every
    # historical experiment or intermediate image in the public site.
    result={"schema":"jp.structural.clean.report.v1",
      "model_source_SHA256":model_digest(spec),
      "synthetic":True,"original_project_engineering_approval":False,
      "original_narayani_F3_NOT_SAFE":True,
      "source_loads_kN":solved["source_ledger"]["gravity_totals_kN"],
      "topology":{"shells":31,"beams":32,"columns":8},
      "beam_checks":beam,"column_pmm_checks":col,
      "provenance_code":REPO,"original_report":ORIGINAL_REPORT,
      "archive":DRIVE_ARCHIVE}
    (data/"report-results.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    write_csv(data/"beam-checks.csv",
        ("mode","member","end","combo","N","Vy","Vz","T","My","Mz","As_required_mm2","As_provided_mm2",
         "tau_c_MPa","tau_v_MPa","flexure","shear"),
        [(r["mode"],r["member"],r["end"],r["case"],
          *(r["signed_local_actions"][k] for k in ("N","Vy","Vz","T","My","Mz")),
          r["flexure"]["As_required_including_min_mm2"],
          r["flexure"]["As_provided_tension_mm2"],
          r["shear"]["tau_c_MPa"],r["shear"]["tau_v_MPa"],
          r["flexure"]["status"],r["shear"]["status"])
          for r in beam["all_qualifying_beam_end_case_rows"]])
    write_csv(data/"column-pmm-checks.csv",
        ("mode","member","end","combo","signed_N","signed_My","signed_Mz",
         "N_mapped_compression_kN","Pu_screen_kN","My1_approx_kNm","Mz1_approx_kNm",
         "alpha","min_eccentricity_alternative","interaction","screen"),
        [(r["diaphragm"],r["member"],r["end"],r["combination"],
          r["signed_local_actions"]["N"],r["signed_local_actions"]["My"],
          r["signed_local_actions"]["Mz"],r["compression_signed_kN"],r["PMM"]["Pu_assumed_compression_kN"],
          r["PMM"]["My1_approx_capacity_kNm"],r["PMM"]["Mz1_approx_capacity_kNm"],
          r["PMM"].get("biaxial_exponent_alpha"),r["PMM"].get("minimum_eccentricity_governing"),r["PMM"]["biaxial_load_contour_utilization"],
          r["PMM"]["status"]) for r in col["rows"]])
    home=page("Structural Analysis",
       "A simple working studio: review your building and generate a reproducible structural report.",
       box("Start here",'<div class="grid">'+
          f'<div class="tile"><b>{A("projects.html","Narayani project")}</b><p>Read the original scope and sources before changing model assumptions.</p></div>'+
          f'<div class="tile"><b>{A("report.html","Working example report")}</b><p>Original six-chapter format, actual OpenSees output and beam/column strength calculations.</p></div>'+
          f'<div class="tile"><b>{A("studio.html","Studio Standard")}</b><p>The repeatable intake → model → response → design → report stages.</p></div>'+
          f'<div class="tile"><b>{A("more.html","Resources")}</b><p>Retrievable full historical archive in Google Drive and original reference files.</p></div></div>')+
       box("Current engine capabilities",
         '<p><strong>Working:</strong> elastic slab/frame FE, member forces and reactions, '
         'reusable isolated beam flexure/shear, and bounded approximate column P–M–M.'
         ' <strong>Not yet complete:</strong> seismic design verification, detailed slabs,'
         ' footings, stairs, ductile detailing and signed construction drawings.</p>'
         '<div class="meta"><span>4 clean site sections</span><span>1 report</span>'
         '<span>2 active numerical design checks</span></div>'))
    studio=page("Studio Standard","One project sequence; use the original sources as authority.",
       box("Required stages",table(("Stage","Purpose"),[
         ("01 Purpose","Occupancy, storeys, building intent and governing document revision"),
         ("02 Inputs","Dimensions, materials, soils, loads and original code editions"),
         ("03 Methods","FE analysis method and independent design formulas"),
         ("04 Model","Real beam, column, slab and foundation connectivity"),
         ("05 Response","Actual reactions, member forces, displacement and seismic effects"),
         ("06 Design","Columns, beams, slabs, footings, stairs, reinforcement and details"),
         ("07 Report","Chaptered original-equivalent report with evidence and checked equations")
       ]))+
       box("Example",f'<p>{A("report.html","Open the solved hypothetical six-chapter example")}. '
           'This is not a replacement for project-specific engineering verification.</p>'))
    projects=page("Projects","Source-first overview; no legacy experiments cluttering the project workspace.",
       box("Narayani Parajuli Residence",
          '<p><strong>Original revised report:</strong> G+1.5 residential RC frame, '
          'Pokhara/Leknath, reported typical storey 3.048m and height 9.144m. '
          'The same report conclusion uses “Office Building”; the governing use '
          'and physical floor levels require source and client confirmation.</p>'
          '<div class="meta"><span>Purpose</span><span>Inputs</span><span>Methods</span>'
          '<span>Model</span><span>Response</span><span>Design</span></div>'
          f'<p>{A(ORIGINAL_REPORT,"Original revised structural report")}'
          f' · {A(ORIGINAL_DRAWING,"Original structural drawing")}'
          f' · {A(ORIGINAL_SOIL,"Geotechnical source")}</p>'
          '<div class="note">A solved hypothetical reference report is available separately; '
          'it is not Narayani design approval. Original F3 one-way shear remains NOT SAFE.</div>')+
       box("Working demonstration",f'<p>{A("report.html","Open full six-chapter structural example")}. '
           'Beam and column design calculations are linked to signed OpenSees results.</p>'))
    more=page("Resources and archived research","Everything historical is stored in Google Drive; the active site stays uncluttered.",
       box("Historical archive in Google Drive",
          f'<div class="tile"><b>{A(DRIVE_ARCHIVE,"Open the complete structural-analysis archive")}</b>'
          '<p>Original source repository, full Git history bundle, source checksum manifest, '
          'previous published website, responsive screenshots and source-design QA. '
          'These experimental files are not in the active website.</p></div>')+
       box("Original sources",
         f'<p>{A(ORIGINAL_REPORT,"Revised original structural PDF")}'
         f' · {A(ORIGINAL_DRAWING,"Structural drawings")} '
         f' · {A(ORIGINAL_SOIL,"Soil study")} '
         f' · {A(CODE_IS456,"IS 456:2000 with amendments")}</p>')+
       box("Active calculations",
         f'<p>{A("report.html","Working six-chapter report")} · '
         f'{A("data/report-results.json","Reproducible current calculations")}'
         f' · {A("data/beam-checks.csv","Beam design evidence")}'
         f' · {A("data/column-pmm-checks.csv","Column P–M–M evidence")}</p>'
         '<p>Historical experiments can be retrieved by archive link without '
         'running their old workflows or putting their developer UI back on the public site.</p>'))
    files={"index.html":home,"studio.html":studio,"projects.html":projects,"more.html":more,
           "report.html":report(spec,solved,beam,col)}
    for name,text in files.items():(out/name).write_text(text,encoding="utf8")
    receipt={"schema":"jp.sar.clean.site.receipt.v1",
      "pages":sorted(files),"archive_url":DRIVE_ARCHIVE,
      "original_engineering_approval":False,
      "beam_rows":beam["rows_count"],"column_rows":col["row_count"],
      "source_sha256":model_digest(spec),
      "files_sha256":{
       p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
       for p in sorted(out.rglob("*")) if p.is_file() and p.name!="receipt.json"}}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    verify(out)
    print("CLEAN_STRUCTURAL_PRODUCT_COMPUTED_6_CHAPTER_REPORT_SUCCESS",receipt["beam_rows"],receipt["column_rows"])
    return receipt

def verify(out:Path):
    receipt=json.loads((out/"receipt.json").read_text())
    assert receipt["beam_rows"]==256 and receipt["column_rows"]==64
    assert len(receipt["pages"])==5 and len(NAV)==4
    assert (out/"more.html").read_text().count(DRIVE_ARCHIVE)>=1
    assert "6.0 Design of Structural Elements" in (out/"report.html").read_text()
    assert "P–M–M" in (out/"report.html").read_text()
    assert "NOT SAFE" in (out/"projects.html").read_text()
    result=json.loads((out/"data/report-results.json").read_text())
    assert result["original_narayani_F3_NOT_SAFE"]
    assert not result["original_project_engineering_approval"]
    for file,sha in receipt["files_sha256"].items():
        assert hashlib.sha256((out/file).read_bytes()).hexdigest()==sha,file
    with (out/"data/beam-checks.csv").open(newline="") as fp:
        assert sum(1 for _ in csv.reader(fp))==257
    with (out/"data/column-pmm-checks.csv").open(newline="") as fp:
        assert sum(1 for _ in csv.reader(fp))==65
    return receipt
if __name__=="__main__":
    build()
