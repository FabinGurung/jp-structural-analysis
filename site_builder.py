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
from r6p30.column_pmm import column_checks_from_preview
from r6p30.column_validation import compute as column_benchmark
from r6p30.footing_f3 import study as f3_study, ARCHIVE as F3_ARCHIVE
from r6p30.slab_design import from_opensees as slab_from_opensees
from r6p30.staircase_review import review as staircase_review
F3_PDF="https://drive.google.com/file/d/1s9u6nqceP4iygo9E1ijMeDlNsS0npvqc/view"
SLAB_ARCHIVE="https://drive.google.com/drive/folders/1u-vkOxS7VuOQMKe908HeeP-VlGmRxTfn"
SLAB_QA_PDF="https://drive.google.com/file/d/1Jppw9fFZ9p28IQbmBN3ezpVMTvJXJOyG/view"
STAIR_QA_DOC="https://docs.google.com/document/d/1MVWeuQEEqKlcngzOFyU3JShvJE-7_yByvWJYiQJRd90/edit"

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

def report(spec,solved,beam,col,verification,f3,slab,stair):
    loading=solved["source_ledger"]["gravity_totals_kN"]
    tf=solved["topology"]
    mode=solved["solutions"]["FLEXIBLE_SHELL"]
    rigid=solved["solutions"]["RIGID_INPLANE_MPC"]
    disp=lambda m:max(float(x) for x in m["DL"]["floor_max_vertical_displacement_m"].values())*1000.
    bend=beam["governing_bending_row"]
    sh=beam["governing_vertical_shear_row"]
    gov=col["governing_example"]
    cv=gov["PMM"]
    external=verification["external_sp16_nptel_reference"]
    twenty=verification["external_sp16_nptel_twenty_bar_reference"]
    revised=f3["preferred_uniform_revision_550mm"]
    original_f3=f3["original_report_adopted_uniform_trial_450mm"]
    slab_gov=slab["governing_example"]
    slab_ref=slab["published_oneway_nptel_benchmark"]
    stair_drawing=stair["drawing"]
    stair_source=stair["revised_report"]
    stair_full=stair["report_moment_interpretations"]["if_20p88_is_already_per_one_metre_strip"]
    stair_width=stair["report_moment_interpretations"]["if_20p88_is_a_full_1p2m_flight_moment"]
    stair_case=stair["drawing_150mm_waist_conditional_overlay_NOT_actual_demand"]
    stair_bm=stair["published_nptel_stair_waist_section_benchmark"]
    stair_table=table(("Staircase source comparison","Readback or independently calculated value"),[
      ("Riser / tread — drawing",n(stair_drawing["riser_mm"])+" / "+n(stair_drawing["tread_mm"])+" mm"),
      ("Riser / tread — report",n(stair_source["riser_mm"])+" / "+n(stair_source["tread_mm"])+" mm"),
      ("Drawing waist and main bars","150 mm; Ø12 @125mm"),
      ("Report waist","150 mm declared; 127 mm worked; effective d=106 mm"),
      ("Source maximum bending moment",n(stair_source["reported_maximum_BM_kNm"])+" kN·m; 1.2m flight vs 1m strip unresolved"),
      ("Required steel if per-metre",n(stair_full["As_required_mm2_per_m"])+" mm²/m at d=106mm"),
      ("Required steel if full 1.2m flight",n(stair_width["As_required_mm2_per_m"])+" mm²/m at d=106mm"),
      ("Source report required steel number",n(stair_source["reported_required_As_number_mm2"])+" mm²; section/units not reconciled"),
      ("Worked 127mm section provided Ø12@127","Exceeds singly reinforced neutral-axis limit at d=106mm"),
      ("Drawing 150mm section — assumption only",n(stair_case["As_provided_mm2_per_m"])+" mm²/m; d=129mm ASSUMED"),
      ("Physical staircase OpenSees model","NOT PRESENT; all real design approvals on hold")])
    slab_table=table(("Slab calculation","Current worked example result"),[
      ("Actual finite-element basis","31 ShellMITC4 panels, 4 Gauss points each"),
      ("Screen count",str(slab["rows_count"])+" face/direction combinations"),
      ("Assumed depth and rebar","120 mm; Ø8 @150 both faces and directions"),
      ("Conservative effective depth",n(slab["section"]["d_mm"])+" mm"),
      ("Rebar area provided",n(slab["section"]["As_provided_mm2_m"])+" mm²/m"),
      ("Minimum steel",n(slab["section"]["As_min_mm2_m"])+" mm²/m"),
      ("Governing panel",slab_gov["cell"]+" / "+slab_gov["mode"]),
      ("Governing X/Y and face",slab_gov["direction"]+"/"+slab_gov["face"]),
      ("Governing Gauss point",str(slab_gov["gauss"])),
      ("Design moment with assumed torsion adjustment",
         n(slab_gov["design_moment_WoodArmer_assumed_kNm_m"])+" kN·m/m"),
      ("Isolated bending screens",str(slab["flexure_screen_ok"])+"/"+str(slab["rows_count"])),
      ("Transverse shear screens",str(slab["transverse_shear_screen_ok"])+"/"+str(slab["rows_count"])),
      ("Actual building or site approval","NOT VERIFIED")])
    f3_table=table(("Condition","Original adopted depth","Proposed uniform-thickness trial"),[
      ("Plan geometry","2.10 × 2.10 m","2.10 × 2.10 m; confirm site"),
      ("Structural depth","450 mm adopted, sloped drawing","550 mm uniform, NEW proposal"),
      ("Concentric one-way shear stress",
         n(original_f3["oneway_tau_v_MPa"])+" MPa",
         n(revised["oneway_tau_v_MPa"])+" MPa"),
      ("Conservative source screening limit","0.200 MPa","0.200 MPa"),
      ("Concentric punching shear",
         n(original_f3["punching_tau_MPa"])+" MPa",
         n(revised["punching_tau_MPa"])+" MPa"),
      ("Soil gross static pressure","Original design still needs reconciling",
         n(revised["gross_service_concentric_soil_pressure_kPa"])+" kPa ≤ 160 kPa"),
      ("Original verdict","NOT SAFE IN ONE WAY SHEAR","Historical failure preserved"),
      ("Revised status","Not a valid approved redesign",
         "Conditional concentric screens pass; not approved for construction")])
    external_table=table(("Capacity or check","NPTEL SP16 chart-derived value","Our independently calculated value","Difference"),[
      ("Long-axis uniaxial moment",
        n(external["reference_major_M_kNm"])+" kN·m",
        n(external["our_major_approx_M_kNm"])+" kN·m",
        n(100*external["major_relative_difference"])+"%"),
      ("Short-axis uniaxial moment",
        n(external["reference_minor_M_kNm"])+" kN·m",
        n(external["our_minor_approx_M_kNm"])+" kN·m",
        n(100*external["minor_relative_difference"])+"%"),
      ("Puz, axial code reference",
        n(external["external_source_inputs"]["published_Puz_kN"])+" kN",
        n(external["computed_Puz_kN"])+" kN","published rounded values"),
      ("Biaxial exponent αn",
        n(external["reference_alpha_rounded"]),
        n(external["computed_alpha"]),
        "code interpolation vs rounded lesson"),
      ("Biaxial interaction",
        n(external["published_reference_interaction_rounded"]),
        n(external["our_approx_biaxial_interaction"]),
        "NOT a whole-building design check"),
    ])
    summary=table(("Report scope","Computed information","What it means"),[
      ("3-D elastic FE","31 shells · 32 beams · 8 columns","Actually solved by OpenSeesPy"),
      ("Dead load",n(loading["DL"])+" kN","Source-derived synthetic model ledger"),
      ("Live load",n(loading["LL"])+" kN","Source-derived synthetic model ledger"),
      ("Flexible diaphragm vertical displacement",n(disp(mode))+" mm","Actually solved DL"),
      ("Rigid diaphragm vertical displacement",n(disp(rigid))+" mm","Actually solved DL"),
      ("Beam design screens",str(beam["rows_count"]),"Matched same-end My/Vz for two modes and two synthetic U± cases"),
      ("Column P–M–M screens",str(col["row_count"]),"Simultaneous N/My/Mz with approximate strain-compatible uniaxial capacities"),
      ("Slab reinforcement screens",str(slab["rows_count"]),"Genuine four-Gauss ShellMITC4 moments; top/bottom X/Y strip design") ,
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
        '§39.6 biaxial load-contour exponent. The slab screen takes four-point '
        'signed ShellMITC4 plate moments and shear, applies Wood–Armer-style '
        'twisting adjustment to the top/bottom X/Y strip envelope, then uses '
        'IS456 §26.5.2/26.3.3 and Annex G slab flexure formulas.</p>'
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
        '<h3>6.2.1 Independent numerical verification</h3>'
        '<p>IS456:2000 Clause 39.1(a) uniform compression imposes ε=0.002. '
        'For Fe500 the revised SP16 Table A stress at ε=0.002 is '
        +n(verification["steel_stress_at_uniform_epsilon_0002_MPa"])+' MPa, '
        'not the former bilinear 400 MPa estimate. '
        'Our <strong>closed-form uniform axial force</strong> is '
        +n(verification["closed_form_P_at_uniform_epsilon_0002_kN"])+' kN; '
        'independent numerical integration gives '
        +n(verification["numerical_256_strip_P_at_uniform_epsilon_0002_kN"])+' kN. '
        'The relative discrepancy is '
        +n(100*verification["relative_pure_axial_error"])+'%. '
        'Additional 32/64/128 strip comparisons cover tension-zone and wholly '
        'compressed neutral-axis positions, with §39.1(b) full compression strain '
        'properly limited below 0.0035.</p>'
        +A('data/column-verification.json','Inspect benchmark numbers and assumptions')+'.'
        '<div class="note">These checks verify numerical consistency and signed '
        'input mapping; they do NOT validate the approximate steel model against '
        'SP16 charts, any final actual-column design, or construction approval.</div>'
        '<h3>6.2.2 Independent published SP16-chart example comparison</h3>'
        '<p>External worked case: a 450 × 500 mm short rectangular column, '
        '12Ø16 longitudinal bars with 56 mm bar-centre cover, M25 concrete '
        'and Fe415 steel, with Pu=1,600 kN. IIT Kharagpur (NPTEL), '
        'Lesson 26, Q.5/A.5 interpolates SP16 Charts 44–45. '
        +A(external["reference_url"],'Read the original NPTEL reference')+'. '
        'We independently recompute the approximate uniaxial capacities for '
        'the same stated material and section parameters. The 12 bar-centres '
        'are assumed equally distributed on the perimeter.</p>'
        +external_table+
        '<p>Both directional approximate moment predictions fall within '
        '<strong>±3% of the published chart-derived capacities</strong>, '
        'a predefined research comparison band, not a certified code tolerance. '
        'The figure caption says M20 while the formal question and answer '
        'use M25; the numerical comparison follows the answered M25 case, '
        'without silently removing this inconsistency. '
        'The lesson uses rounded alpha and moment values, so its reported '
        'interaction is not an exact floating-point source for verification. '
        'The live hypothetical building above still uses its original 400 × 400 mm '
        '8-bar assumptions; the NPTEL benchmark is separate.</p>'
        '<div class="note">External NPTEL chart-derived comparison is independent; '
        'it is NOT a certified chart-suite or whole-building approval. '
        'The fuller 13-published-value audit and 720-point *internal numerical* '
        'mesh refinement research are in Drive; the latter are NOT 720 independent '
        'SP16 chart comparisons. Formal SP16 chart verification remains open.</div>'
        '<p><strong>Additional independent Fe415 benchmark:</strong> '
        'NPTEL Lesson 25, 400 × 400 mm and 20Ø16, Pu 2,240 kN: '
        'chart-derived Mu='+n(twenty["published_Mu_kNm"])+' kN·m; '
        'our Table A based result='+n(twenty["our_table_A_Mu_kNm"])+' kN·m '
        '(difference '+n(100*twenty["relative_difference"])+'%). '
        +A(twenty["source_url"],'Read NPTEL 20-bar reference')+'. '
        +A(F3_ARCHIVE,'Open the full external reference matrix in Drive')+'.</p>'
        +A('data/column-verification.json','Inspect both reference and independent numerical evidence')+'.'

        '<h3>6.3 Narayani F3 — proposed foundation redesign study</h3>'
        '<p>The original structural report page 61 explicitly records F3 '
        '<strong>NOT SAFE IN ONE WAY SHEAR</strong>. The engineering study '
        'does not alter those original drawings or the safety history. '
        'Under the worksheet 571 kN concentric axial assumption only, '
        'the NEW 2.10m square uniform-thickness 550mm footing passes '
        'the listed shear, punching, bending and concentric bearing screens. '
        'It is NOT a field-approved design, and it does not justify '
        'constructing without full governing moments and seismic loads.</p>'
        +f3_table+
        '<div class="note"><strong>HOLD FOR ENGINEERING APPROVAL.</strong> '
        'The site-specific foundation actions N/Mx/My/Vx/Vy, '
        'source 2.1m versus G1 1.8m geometry, original sloped cross-section, '
        'eccentric soil bearing and settlement, bar anchorage, dowels '
        'and independent structural review remain unresolved. '
        'The earlier failed footing is NOT retroactively marked safe.</div>'
        +A('data/f3-trial.json','Open source-traceable trial calculation (JSON)')+' · '
        +A(F3_PDF,'Full eight-page F3 and SP16 research report in Drive')+'.'
        '<h3>6.4 Slab reinforcement from actual OpenSees shell moments</h3>'
        '<p>ShellMITC4 <em>stresses</em> returns four eight-component '
        'Gauss section resultants per panel; we use M11, M22, M12 '
        'and transverse shears Q1/Q2, not element nodal resisting forces. '
        'The same load-case Gauss results are superposed for each '
        'synthetic U combination. Wood–Armer-style M11/M22 ± |M12| '
        'adjustments are evaluated independently at top/bottom faces '
        'and both axes; the actual local-to-face sign convention '
        'remains an explicit source-review assumption.</p>'
        +slab_table+
        '<p>'+A('data/slab-checks.csv','Download all slab design screens (CSV)')+
        ' · '+A('data/slab-benchmark.json','Read independent benchmark values (JSON)')+
        ' · '+A(SLAB_QA_PDF,'Full slab QA engineering review in Drive')+'.</p>'
        '<h3>6.4.1 Published NPTEL one-way slab benchmark</h3>'
        '<p>IIT Kharagpur Lesson 18 TQ3: 175mm slab, 150mm effective depth, '
        '3.5m simply supported one-way span, M20 Fe415, 1kPa finish '
        'and 4kPa live load. The independent formula gives '
        +n(slab_ref["factored_pressure_kPa"])+' kPa factored pressure '
        'and '+n(slab_ref["computed_analytic_Mu_kNm_m"])+
        ' kN·m/m bending, agreeing with the published 21.533 value. '
        'With 8mm @120mm main steel, our simplified Annex G section '
        'strength is '+n(slab_ref["our_IS456_AnnexG_capacity_kNm_m"])+
        ' kN·m/m versus the source SP16 Table41 '
        +n(slab_ref["published_SP16_table41_capacity_kNm_m"])+
        ' kN·m/m, a '+n(100*slab_ref["our_relative_chart_capacity_difference"])+
        '% disagreement. This is openly retained, NOT certified capacity agreement. '
        +A(slab_ref["source_url"],'Read original IIT Kharagpur lesson')+'.</p>'
        '<div class="note"><strong>NOT A NARAYANI SLAB DESIGN.</strong> '
        'The Narayani source drawing specifies Ø8 @150 in both directions '
        'and shows a typical 125mm depth, unlike this 120mm synthetic fixture. '
        'Governing project span, supports, live loads, bar continuity/anchorage, '
        'torsion steel at corners, service deflection, cracks and actual '
        'seismic combinations remain unresolved. F3 foundation safety '
        'review remains separately held.</div>'
        '<h3>6.5 Narayani staircase — original-source reconciliation</h3>'
        '<p>The July 2026 stair drawing and revised structural analysis disagree on riser, '
        'tread and worked waist depth. The report moment may apply to the full '
        '1.2m flight rather than a one-metre strip. Both interpretations remain held.</p>'
        +stair_table+
        '<h3>6.5.1 External NPTEL staircase reinforcement benchmark</h3>'
        '<p>The IIT Kharagpur Lesson 20 Example 9.1 waist-slab has a published '
        '102.08 kN·m for a 1.5m full-width staircase and an effective depth '
        'of 224mm, M20/Fe415. For a one-metre strip, independent IS456 bending '
        'calculation requires '+n(stair_bm["independent_required_steel_mm2_m"])
        +' mm²/m, versus the published SP16-based '
        +n(stair_bm["source_required_steel_mm2_m"])+' mm²/m ('
        +n(100*stair_bm["relative_stress_block_vs_SP16_difference"])
        +'% difference). '
        +A(stair_bm["source"],'Read published IIT Kharagpur staircase example')
        +'. This checks isolated section reinforcement only, not the physical '
        'staircase loading, landing support, full-span solution or Narayani.</p>'
        '<p>'+A('data/staircase-source-review.json','Read full staircase arithmetic and unresolved holds')
        +' · '+A(STAIR_QA_DOC,'Full R6.37 staircase research QA (Drive)')
        +' · '+A(stair_drawing['source'],'Original July 2026 drawing')
        +' · '+A(stair_source['source'],'Revised structural report')+'.</p>'
        '<div class="note"><strong>ENGINEERING HOLD.</strong> This is only a source '
        'reconciliation and IS456 strip arithmetic, not a staircase OpenSees '
        'simulation, approved load path or construction design. The assumed '
        'cover, effective span, landings, supports, seismic actions, shear, '
        'deflection and anchorage require physical-project verification. '
        'IS456 §33.1–33.3 apply to actual support and load models. '
        'The original F3 footing remains NOT SAFE.</div>'),
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
    verification=column_benchmark()
    f3=f3_study()
    slab=slab_from_opensees(solved)
    stair=staircase_review()
    (data/"staircase-source-review.json").write_text(json.dumps(stair,indent=2,
         sort_keys=True,allow_nan=False)+"\n")
    (data/"slab-benchmark.json").write_text(json.dumps(
        slab["published_oneway_nptel_benchmark"],indent=2,
        sort_keys=True,allow_nan=False)+"\n")
    (data/"f3-trial.json").write_text(json.dumps(f3,indent=2,
        sort_keys=True,allow_nan=False)+"\n")
    (data/"column-verification.json").write_text(json.dumps(verification,indent=2,
        sort_keys=True,allow_nan=False)+"\n")
    # Preserve the signed independent numerical evidence, but not every
    # historical experiment or intermediate image in the public site.
    result={"schema":"jp.structural.clean.report.v1",
      "model_source_SHA256":model_digest(spec),
      "synthetic":True,"original_project_engineering_approval":False,
      "original_narayani_F3_NOT_SAFE":True,
      "source_loads_kN":solved["source_ledger"]["gravity_totals_kN"],
      "topology":{"shells":31,"beams":32,"columns":8},
      "beam_checks":beam,"column_pmm_checks":col,
      "column_capacity_verification":verification,
      "f3_proposed_concentric_redesign_study":f3,
      "slab_reinforcement_screen":slab,
      "staircase_source_reconciliation":stair,
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
    write_csv(data/"slab-checks.csv",
        ("mode","combination","cell","floor","gauss","axis","face",
         "signed_M11","signed_M22","signed_M12","signed_Q1","signed_Q2",
         "WoodArmer_Mu_kNm_m","As_required_with_min_mm2_m","As_provided_mm2_m",
         "M_provided_kNm_m","bending_status","shear_tau_v_MPa","shear_tau_c_MPa",
         "shear_ok","real_building_sign_validated"),
        [(x["mode"],x["combination"],x["cell"],x["floor"],x["gauss"],
          x["direction"],x["face"],
          *x["shell_original_signed_m11_m22_m12_kNm_m"],
          *x["shell_original_signed_q1_q2_kN_m"],
          x["design_moment_WoodArmer_assumed_kNm_m"],
          x["bending"]["As_required_with_min_mm2_m"],
          x["bending"]["As_provided_mm2_m"],
          x["bending"]["M_provided_capacity_kNm_m"],
          x["bending"]["status"],
          x["transverse_shear"]["tau_v_MPa"],
          x["transverse_shear"]["tau_c_slab_MPa"],
          x["transverse_shear"]["isolated_transverse_shear_ok"],
          x["actual_top_bottom_sign_validated_in_real_structure"])
         for x in slab["rows"]])
    home=page("Structural Analysis",
       "A simple working studio: review your building and generate a reproducible structural report.",
       box("Start here",'<div class="grid">'+
          f'<div class="tile"><b>{A("projects.html","Narayani project")}</b><p>Read the original scope and sources before changing model assumptions.</p></div>'+
          f'<div class="tile"><b>{A("report.html","Working example report")}</b><p>Original six-chapter format, actual OpenSees output and beam/column strength calculations.</p></div>'+
          f'<div class="tile"><b>{A("studio.html","Studio Standard")}</b><p>The repeatable intake → model → response → design → report stages.</p></div>'+
          f'<div class="tile"><b>{A("more.html","Resources")}</b><p>Retrievable full historical archive in Google Drive and original reference files.</p></div></div>')+
       box("Current engine capabilities",
         '<p><strong>Working:</strong> elastic slab/frame FE, member forces and reactions, '
         'beam flexure/shear, approximate column P–M–M and new ShellMITC4 slab reinforcement screens.'
         ' <strong>Not yet complete:</strong> seismic design verification, detailed slabs,'
         ' final slab detailing/deflection, footings, stairs, ductile detailing and signed drawings.</p>'
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
          'it is not Narayani design approval. Original F3 is still NOT SAFE; '
          'a new uniform 550mm trial passes its limited concentric checks '
          'but awaits actual load, site geometry and engineering approval. '
          +A(F3_PDF,"Read the proposed F3 revision and SP16 audit in Drive")+'.</div>')+
       box("Working demonstration",f'<p>{A("report.html","Open full six-chapter structural example")}. '
           'Beam and column design calculations are linked to signed OpenSees results.</p>'))
    more=page("Resources and archived research","Everything historical is stored in Google Drive; the active site stays uncluttered.",
       box("Historical archive in Google Drive",
          f'<div class="tile"><b>{A(DRIVE_ARCHIVE,"Open the complete structural-analysis archive")}</b>'
          '<p>Original source repository, full Git history bundle, source checksum manifest, '
          'previous published website, responsive screenshots and source-design QA. '
          'These experimental files are not in the active website.</p></div>')+
       box("Current engineering verification studies",
          f'<p>{A(F3_PDF,"R6.35 engineer-review PDF — F3 footing and expanded SP16 verification")} '
          f' · {A(F3_ARCHIVE,"Original calculations and full 720-case study in Drive")}</p>'
          '<p>The 550mm uniform F3 option is only a conditional proposal; '
          'the original F3 failure remains in the historic record. '
          'The expanded SP16 work compares 13 published reference values and '
          '720 internal mesh checks, but is not formal full-chart certification.</p>'
          f'<p>{A(SLAB_QA_PDF,"Slab Gauss and reinforcement numerical QA (PDF)")}'
          f' · {A(SLAB_ARCHIVE,"Retrieve full slab research and source snapshot in Drive")}</p>'
          f'<p>{A(STAIR_QA_DOC,"R6.37 staircase source/reinforcement QA (Drive)")} — '
          'independent arithmetic and open engineering holds; not construction approved.</p>'
          '<p>The slab study tests a synthetic 120mm model. It does not '
          'replace the original Narayani slab reinforcement drawing or its '
          'professional review and construction approval.</p>')+
       box("Original sources",
         f'<p>{A(ORIGINAL_REPORT,"Revised original structural PDF")}'
         f' · {A(ORIGINAL_DRAWING,"Structural drawings")} '
         f' · {A(ORIGINAL_SOIL,"Soil study")} '
         f' · {A(CODE_IS456,"IS 456:2000 with amendments")}'
         f' · {A("https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l26.pdf","NPTEL SP16 column example")}'
         f' · {A("https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l23.pdf","SP16 Table A stress-strain reference")}</p>')+
       box("Active calculations",
         f'<p>{A("report.html","Working six-chapter report")} · '
         f'{A("data/report-results.json","Reproducible current calculations")}'
         f' · {A("data/beam-checks.csv","Beam design evidence")}'
         f' · {A("data/column-pmm-checks.csv","Column P–M–M evidence")}'
         f' · {A("data/slab-checks.csv","Slab bending and transverse-shear evidence")}</p>'
         '<p>Historical experiments can be retrieved by archive link without '
         'running their old workflows or putting their developer UI back on the public site.</p>'))
    files={"index.html":home,"studio.html":studio,"projects.html":projects,"more.html":more,
           "report.html":report(spec,solved,beam,col,verification,f3,slab,stair)}
    for name,text in files.items():(out/name).write_text(text,encoding="utf8")
    receipt={"schema":"jp.sar.clean.site.receipt.v1",
      "pages":sorted(files),"archive_url":DRIVE_ARCHIVE,
      "original_engineering_approval":False,
      "beam_rows":beam["rows_count"],"column_rows":col["row_count"],
      "slab_rows":slab["rows_count"],
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
    assert receipt["slab_rows"]==496
    assert len(receipt["pages"])==5 and len(NAV)==4
    assert (out/"more.html").read_text().count(DRIVE_ARCHIVE)>=1
    assert "6.0 Design of Structural Elements" in (out/"report.html").read_text()
    assert "P–M–M" in (out/"report.html").read_text()
    assert "NOT SAFE" in (out/"projects.html").read_text()
    result=json.loads((out/"data/report-results.json").read_text())
    assert result["original_narayani_F3_NOT_SAFE"]
    assert result["slab_reinforcement_screen"]["rows_count"]==496
    assert result["slab_reinforcement_screen"]["shell_cells"]==31
    assert not result["staircase_source_reconciliation"]["engineering_approval"]
    assert result["staircase_source_reconciliation"]["report_moment_normalization_unresolved"]
    assert result["staircase_source_reconciliation"]["published_nptel_stair_waist_section_benchmark"]["within_predeclared_1pct_research_band"]
    assert not result["staircase_source_reconciliation"]["published_nptel_stair_waist_section_benchmark"]["engineering_approval"]
    assert "6.5 Narayani staircase" in (out/"report.html").read_text()
    assert (out/"data/staircase-source-review.json").exists()
    assert STAIR_QA_DOC in (out/"report.html").read_text()
    assert STAIR_QA_DOC in (out/"more.html").read_text()
    assert not result["slab_reinforcement_screen"]["engineering_approval"]
    assert not result["slab_reinforcement_screen"]["actual_project_slab_geometry_and_rebar_verified"]
    assert result["f3_proposed_concentric_redesign_study"]["historical_not_safe_preserved"]
    assert result["f3_proposed_concentric_redesign_study"]["preferred_uniform_revision_550mm"]["listed_concentric_checks_pass"]
    assert not result["f3_proposed_concentric_redesign_study"]["approved_for_construction"]
    assert result["column_capacity_verification"]["external_sp16_nptel_twenty_bar_reference"]["relative_difference"]<.03
    assert not result["column_capacity_verification"]["full_SP16_chart_verification"]
    assert result["column_capacity_verification"]["relative_pure_axial_error"]<.001
    assert result["column_capacity_verification"]["sp16_verified"] is False
    assert result["column_pmm_checks"]["axial_tension_rows_excluded"]>=0
    assert not result["original_project_engineering_approval"]
    for file,sha in receipt["files_sha256"].items():
        assert hashlib.sha256((out/file).read_bytes()).hexdigest()==sha,file
    with (out/"data/beam-checks.csv").open(newline="") as fp:
        assert sum(1 for _ in csv.reader(fp))==257
    with (out/"data/slab-checks.csv").open(newline="") as fp:
        assert sum(1 for _ in csv.reader(fp))==497
    with (out/"data/column-pmm-checks.csv").open(newline="") as fp:
        assert sum(1 for _ in csv.reader(fp))==65
    return receipt
if __name__=="__main__":
    build()
