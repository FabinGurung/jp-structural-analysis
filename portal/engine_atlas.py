"""SAR product clarity R6.30: actual engine catalog + report-shaped, solved example.

Reads the EXISTING independently OpenSeesPy-solved R6.23 synthetic fixture.
It NEVER calls the Narayani project results an engineer-approved structure.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape as e
import json,math
from pathlib import Path
from r6p30.beam_design import member_checks_from_preview, CASES as BEAM_CASE_FACTORS
from r6p30.report_beam_html import render_beam_chapter

ORIGINAL="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
REPO="https://github.com/FabinGurung/jp-structural-analysis"
OPENSEES="https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html"
SHEAR_FOOTING="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
SCHEMA="jp.sar.example.solved_r6p23_six_chapters.v1"

def need(condition,message):
    if not condition: raise ValueError("R6.30 EXAMPLE SOURCE CONTRACT: "+message)

def money(x,d=3):
    return format(float(x),f",.{d}f")

def flexural_steel(mu_kNm,b_mm,d_mm,fck=25.,fy=500.):
    """Singly reinforced illustrative IS456 rectangular stress-block equation."""
    mlim=0.133*fck*b_mm*d_mm**2/1e6
    p=0.87*fy*d_mm
    q=(0.87*fy)**2*0.42/(0.36*fck*b_mm)
    disc=p*p-4*q*float(mu_kNm)*1e6
    return {"Mu_lim_kNm":mlim,"As_req_mm2":(p-math.sqrt(disc))/(2*q)
             if disc>=0 and mu_kNm<=mlim else None}

def load_source(site):
    p=site/"data/r6p23-preview.json"
    need(p.exists(),"existing R6.23 solved JSON must precede report")
    raw=p.read_bytes();d=json.loads(raw)
    need(d["schema"]=="jp.structural.r6p24.pages_independent_shell_preview.v0.1",
         "existing synthetic independent FE schema")
    need(d["classification"]=="SYNTHETIC_REFERENCE" and d["engineering_approval"] is False,
         "never present project-only observations as source-confirmed physical design")
    from r6p23.runner import reference_fixture
    from r6p23.engine import digest
    fixture=reference_fixture()
    need(d["source_SHA256"]==digest(fixture),"published source does not match actual synthetic input")
    need(d["topology"]["shell_count"]==31 and d["topology"]["beam_segment_count"]==32
        and d["topology"]["column_segment_count"]==8,
        "unexpected FE geometry; edit report and tests before claim")
    l=d["source_ledger"]["gravity_totals_kN"]
    need(math.isclose(l["DL"],339.0,abs_tol=1e-6)
      and math.isclose(l["LL"],62.0,abs_tol=1e-6),"source load ledger drift")
    need(set(d["solutions"])=={"FLEXIBLE_SHELL","RIGID_INPLANE_MPC"},
         "the two FE diaphragm comparison modes must both exist")
    for mode,cases in d["solutions"].items():
        for name in ("DL","LL","HX","SHELL_DL","FRAME_DL"):
            need(name in cases and cases[name]["force_moment_balance_pass"]
                 and cases[name]["max_equilibrium_residual"]<1e-3,
                 "a referenced FE solve has not passed its signed equilibrium")
    return d,sha256(raw).hexdigest(),fixture

def summarize(site):
    data,source_file_sha,fixture=load_source(site)
    # Use precisely the fixture's declared signed combination factors.
    fixture_combos={row["id"]:row["factors"] for row in fixture["combinations"]}
    need(fixture_combos==BEAM_CASE_FACTORS,
         "assumed original source combo does not match beam-design code")
    beam_rc=member_checks_from_preview(data)
    need(beam_rc["source_fixture_sha256"]==data["source_SHA256"],
         "R6.31 actual OpenSees source digest mismatch")
    mode="FLEXIBLE_SHELL"
    raw=data["solutions"][mode]
    beam_ids={q["key"] for q in data["topology"]["beams"]}
    col_ids={q["key"] for q in data["topology"]["columns"]}
    metric=[]
    for member in sorted(beam_ids):
        for end in ("I","J"):
            for component in ("My","Mz"):
                for sign,combo in ((1,"U_PLUS"),(-1,"U_MINUS")):
                    def force(case): return float(raw[case]["signed_frame_end_actions"][member][end][component])
                    value=1.2*force("DL")+1.5*force("LL")+sign*force("HX")
                    metric.append({"member":member,"end":end,"component":component,
                                   "combo":combo,"signed_kNm":value,"absolute_kNm":abs(value)})
    chosen=max(metric,key=lambda x:x["absolute_kNm"])
    need(chosen["member"] in col_ids or chosen["member"] in beam_ids,"selected frame member missing")
    for row in metric: need(math.isfinite(row["signed_kNm"]),"non-finite signed FE action")
    beam_governor=beam_rc["governing_bending_row"]
    beam_design=beam_governor["flexure"]
    steel_min=beam_design["As_min_mm2"]
    column_envelope=[]
    for col in sorted(col_ids):
        for end in ("I","J"):
            for sign in (1,-1):
                def axial(case):return raw[case]["signed_frame_end_actions"][col][end]["N"]
                val=1.2*axial("DL")+1.5*axial("LL")+sign*axial("HX")
                column_envelope.append((abs(val),col,end,val))
    critical_col=max(column_envelope)
    support_DL=raw["DL"]["support_reactions"]
    support_LL=raw["LL"]["support_reactions"]
    support_key=max(support_DL,key=lambda k:abs(support_DL[k]["Fz"]+support_LL[k]["Fz"]))
    reaction_dl=float(support_DL[support_key]["Fz"])
    reaction_ll=float(support_LL[support_key]["Fz"])
    footing_self=1.5*1.5*.45*25
    soil_pressure=(reaction_dl+reaction_ll+footing_self)/2.25
    footing_d=(450-50-12/2)/1000
    footing_q_fact=1.5*(reaction_dl+reaction_ll)/2.25
    footing_v=max(0.,footing_q_fact*1.5*((1.5-.4)/2-footing_d))
    footing_stress=footing_v*1000/(1500*(footing_d*1000))
    slab_w_service=.12*25+1.5+2.
    slab_w_factor=1.2*(.12*25+1.5)+1.5*2.
    strip_m=slab_w_factor*4**2/8
    slab_d=120-20-8/2
    slab_design=flexural_steel(strip_m,1000,slab_d)
    bar_area=math.pi*10**2/4*1000/150
    out={
      "schema":SCHEMA,"case_id":data["case_id"],"classification":"SOLVED_SYNTHETIC_REFERENCE_AND_SEPARATE_HAND_EXAMPLES",
      "source_preview_sha256":source_file_sha,"source_fixture_sha256":data["source_SHA256"],
      "original_report_source":ORIGINAL,"model_engine":"r6p23.engine.build","FE_is_really_computed":True,
      "project_real_or_construction_design":False,
      "assumptions":{
        "grid_x_m":fixture["x_grid_m"],"grid_y_m":fixture["y_grid_m"],"levels_m":fixture["levels_m"],
        "concrete_elastic_E_GPa":fixture["concrete"]["E_kN_m2"]/1e6,
        "concrete_unit_weight_kN_m3":fixture["concrete"]["unit_weight_kN_m3"],
        "illustrative_RC_strength_fck_MPa":25.0,
        "illustrative_RC_steel_fy_MPa":500.0,
        "slab_thickness_mm":120,"beam_mm":[300,450],"column_mm":[400,400],
        "slab_finish_kPa":1.5,"slab_live_kPa":2.,
        "stair_is_in_OpenSees_model":False,"foundation_is_in_OpenSees_model":False,
        "assumed_allowable_soil_kPa":160.0,
        "assumed_beam_effective_depth_mm":405,
        "assumed_footing_dimensions_m":[1.5,1.5,.45],
      },
      "topology":{
        "shell_elements":data["topology"]["shell_count"],"beam_segments":data["topology"]["beam_segment_count"],
        "column_segments":data["topology"]["column_segment_count"],
        "nodes":data["topology"]["physical_node_count"],
        "base_supports":4,
        "floor_areas_m2":data["topology"]["floor_areas_m2"]
      },
      "loads_kN":data["source_ledger"]["gravity_totals_kN"],
      "FE_results":{
        "cases_per_mode":list(raw),
        "mode_list":list(data["solutions"]),
        "max_six_axis_equilibrium_residual":max(c["max_equilibrium_residual"]
                                                for cases in data["solutions"].values()
                                                for c in cases.values()),
        "max_DL_vertical_disp_mm_flexible":max(float(v)*1000 for v in raw["DL"]["floor_max_vertical_displacement_m"].values()),
        "max_DL_vertical_disp_mm_rigid":max(float(v)*1000 for v in data["solutions"]["RIGID_INPLANE_MPC"]["DL"]["floor_max_vertical_displacement_m"].values()),
        "selected_signed_beam_envelope":chosen,
        "selected_signed_column_axial_envelope_kN":critical_col[3],
        "selected_column_member":critical_col[1],
        "selected_support":support_key,
        "selected_support_DL_Fz_kN":reaction_dl,
        "selected_support_LL_Fz_kN":reaction_ll,
        "selected_support_source":"elastic fixed-base reaction, not soil bearing stress"
      },
      "sample_member_arithmetic":{
        "beam":{"Mu_from_signed_synthetic_U_envelope_kNm":beam_governor["flexure"]["Mu_abs_kNm"],
                "beam_member":beam_governor["member"],
                "beam_end":beam_governor["end"],
                "beam_combo":beam_governor["case"],
                "beam_mode":beam_governor["mode"],
                "width_mm":300,"effective_d_mm":405,"fck_MPa":25,"fy_MPa":500,
                "Mu_lim_singly_reinforced_kNm":beam_design["Mu_lim_kNm"],
                "As_required_by_simplified_flexure_mm2":beam_design["As_req_flexure_mm2"],
                "As_provided_assumed_3_16mm_mm2":beam_design["As_provided_tension_mm2"],
                "Mu_res_provided_kNm":beam_design["Mu_res_provided_kNm"],
                "As_min_IS456_demonstration_mm2":steel_min,
                "design_scope":"R6.31 reusable My/Vz same-case beam end screens; no torsion/joint/ductile detailing"},
        "column":{"member":critical_col[1],"axial_envelope_kN":abs(critical_col[3]),
                  "gross_area_mm2":400*400,
                  "nominal_axial_stress_MPa":abs(critical_col[3])*1000/(400*400),
                  "design_scope":"gross axial stress only, not P-M-M or seismic detailing"},
        "slab":{"area_floor1_m2":16.,"area_floor2_net_m2":15.,
                "service_slab_plus_finish_plus_live_kPa":slab_w_service,
                "hypothetical_oneway_strip_factor_load_kPa":slab_w_factor,
                "hypothetical_oneway_4m_strip_Mu_kNm_per_m":strip_m,
                "effective_depth_mm":slab_d,
                "As_required_mm2_per_m":slab_design["As_req_mm2"],
                "assumed_10mm_at_150mm_As_mm2_per_m":bar_area,
                "design_scope":"hypothetical isolated one-way strip; actual solved two-way shell moments differ"},
        "footing":{"chosen_support":support_key,
                   "DL_reaction_kN":reaction_dl,"LL_reaction_kN":reaction_ll,
                   "assumed_footing_weight_kN":footing_self,
                   "gross_service_bearing_kPa":soil_pressure,
                   "assumed_allowable_bearing_kPa":160.,
                   "assumed_slab_d_mm":footing_d*1000,
                   "uniform_concentric_trial_1way_Vu_kN":footing_v,
                   "trial_oneway_tau_v_MPa":footing_stress,
                   "design_scope":"centred, gravity-only, no soil FE, eccentricity, settlement or punching"},
        "staircase":{"assumed_storey_rise_m":3.0,"assumed_risers":18,
                     "assumed_treads":17,"assumed_tread_m":.27,
                     "computed_run_m":17*.27,
                     "design_scope":"geometry-only; absent from original synthetic FE example"}
      },
      "beam_rc_screens_R6p31":beam_rc,
      "professional_approval":False,"construction_release":False,
      "code_compliant_building_design":False,
      "original_f3_not_safe_retained":True,
    }
    need(out["loads_kN"]["DL"]==339 and out["loads_kN"]["LL"]==62,"reference totals")
    need(out["FE_results"]["max_six_axis_equilibrium_residual"]<1e-3,"signed FE equilibrium")
    need(out["sample_member_arithmetic"]["slab"]["As_required_mm2_per_m"] < bar_area,
         "illustrative 10Ø150 strip steel not larger than simplified demand")
    return out

STYLE="""<style>
:root{--ink:#202441;--muted:#647080;--line:#dce0e8;--paper:#f8f7f2;--deep:#383187}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.65 system-ui,Arial,sans-serif}
a{color:var(--deep);text-underline-offset:3px}.mast{padding:16px 3vw;background:#fff;border-bottom:1px solid var(--line);display:flex;gap:18px;justify-content:space-between;flex-wrap:wrap}
.mast strong{letter-spacing:.1em}.mast nav{display:flex;gap:16px;flex-wrap:wrap}
main{max-width:1220px;margin:20px auto;padding:0 22px 48px}.hero{background:#fff;border:1px solid var(--line);padding:clamp(22px,5vw,45px);border-radius:15px;margin-bottom:20px}
.hero h1{font-size:clamp(27px,4vw,49px);line-height:1.13;max-width:930px;margin:14px 0}
.eyebrow{font-size:11px;letter-spacing:.15em;font-weight:850;color:#6550a1}
.lead{font-size:17px;max-width:900px;color:#556074}.frame{display:grid;grid-template-columns:220px minmax(0,1fr);gap:18px}
.toc{background:#fff;border:1px solid var(--line);border-radius:12px;padding:17px;position:sticky;top:20px;height:max-content}
.toc a{display:block;padding:8px 0;font-size:13px;text-decoration:none;border-bottom:1px solid #eee}
section{background:white;border:1px solid var(--line);border-radius:12px;margin-bottom:16px;padding:26px;scroll-margin-top:16px}
h2{font-size:23px;margin:0 0 12px}h3{font-size:16px;margin:21px 0 5px}p{margin:8px 0 12px}
table{border-collapse:collapse;width:100%;min-width:660px;font-size:13px}
th,td{border-bottom:1px solid #e2e5ed;padding:10px 12px;text-align:left;vertical-align:top}
thead{background:#f0f1f7}th{font-weight:750}.scroll{overflow-x:auto}
strong.metric{font-size:25px;color:#3a338e}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px}
.stat{padding:13px;background:#f4f2fa;border-radius:10px}.stat small{display:block;color:#6b7287}.stat b{font-size:24px}
.wire{border-left:4px solid #c87849;padding:13px 15px;background:#fff8ef;margin:16px 0}
.ok{border-left:4px solid #26796b;padding:13px 15px;background:#f2faf8;margin:16px 0}
code{color:#43378e;overflow-wrap:anywhere}pre{overflow-x:auto;background:#f4f5fb;padding:14px}
.footer{padding:20px;color:#647080;text-align:center}@media(max-width:850px){.frame{grid-template-columns:1fr}.toc{position:static}.hero{padding:24px}section{padding:18px}}
@page{size:A4;margin:16mm 14mm}@media print{body{background:white;font-size:11px}.mast,.footer,.noprint{display:none!important}main{max-width:none;margin:0;padding:0}.frame{display:block}.toc{display:block;position:static;border:none;padding:0;break-after:page;page-break-after:always}.toc a{font-size:12px;padding:8px 0}section{border:none;break-before:page;padding:0 0 10px;border-radius:0}.hero{border:0;break-after:page}.scroll{overflow:visible}table{font-size:9px;min-width:0}.wire{page-break-inside:avoid}a{color:black;text-decoration:none}}
</style>"""

def shell(title,subtitle,sections,nav):
    toc="".join(f'<a href="#{e(k)}">{e(label)}</a>' for k,label,_ in sections)
    body="".join(f'<section id="{e(k)}"><h2>{e(label)}</h2>{html}</section>' for k,label,html in sections)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · JP Structural Analysis</title>{STYLE}</head>
<body><header class="mast"><strong>JP / STRUCTURAL ANALYSIS</strong><nav>
<a href="index.html">Home</a><a href="studio.html">Studio Standard</a>
<a href="projects.html">Projects</a><a href="more.html#research">More · Research</a>
<a href="{nav}">Companion report</a></nav></header>
<main><header class="hero"><span class="eyebrow">ENGINE AUDIT · WORKED EXAMPLE · NOVEMBER 2026</span>
<h1>{e(title)}</h1><p class="lead">{e(subtitle)}</p>
<div class="noprint"><button onclick="window.print()" type="button">Print / Save as PDF</button></div></header>
<div class="frame"><aside class="toc" aria-label="On this page"><strong>TABLE OF CONTENTS</strong>{toc}</aside><div>{body}</div></div></main>
<div class="footer">JP Structural Analysis · Source-indexed learning and reproducible numerical demonstrations</div></body></html>"""

def simple_table(headers,rows):
    h="<thead><tr>"+"".join(f"<th>{e(x)}</th>" for x in headers)+"</tr></thead>"
    body="".join("<tr>"+"".join(f"<td>{x}</td>" for x in row)+"</tr>" for row in rows)
    return '<div class="scroll"><table>'+h+"<tbody>"+body+"</tbody></table></div>"

def example_report(d):
    a=d["assumptions"];top=d["topology"];r=d["FE_results"];s=d["sample_member_arithmetic"];loads=d["loads_kN"]
    txt=lambda x:e(money(x,3))
    specimen=s["beam"];slab=s["slab"];foot=s["footing"];col=s["column"]
    beam_detail=render_beam_chapter(d["beam_rc_screens_R6p31"])
    overview=f"""<p>Learning model: a <b>completely hypothetical two-floor reinforced-concrete frame and slab demonstration</b>.
This PDF-style report follows the six numbered chapters of the <a href="{ORIGINAL}">original ETABS report</a> without copying its result values.
All frame and shell reactions in Chapter 5 come from the already executed <code>r6p23.engine.build()</code>
OpenSeesPy solver; selected simple member design arithmetic in Chapter 6 is calculated separately and explicitly labeled.</p>
<div class="stats"><div class="stat"><small>FE shell elements</small><b>{top["shell_elements"]}</b></div>
<div class="stat"><small>Beam segments</small><b>{top["beam_segments"]}</b></div>
<div class="stat"><small>Column segments</small><b>{top["column_segments"]}</b></div>
<div class="stat"><small>Support nodes</small><b>{top["base_supports"]}</b></div></div>
<div class="ok"><b>Actual solver calculations exist.</b> The analytical model runs two diaphragm assumptions with signed
force and moment equilibrium. It is a fully synthetic verification benchmark, not the original Narayani building.</div>"""
    inputs=simple_table(("Input","Hypothetical value","Use"),[
        ("Plan grid","0, 1, 2, 3, 4 m in X and Y","4 × 4 m plan"),
        ("Storey levels","0, 3, 6 m","Two elevated floors"),
        ("Floor openings","One 1 m² opening on level 2","Actual removed FE shell cell"),
        ("Concrete elastic modulus","25 GPa","Assumed OpenSees elastic stiffness"),
        ("Unit weight","25 kN/m³","Original demonstration, not Narayani source's 20"),
        ("Slab thickness","120 mm","ShellMITC4 elastic plate"),
        ("Beam section","300 × 450 mm","elasticBeamColumn"),
        ("Column section","400 × 400 mm","elasticBeamColumn"),
        ("Surface loads","1.5 kPa finishes + 2.0 kPa live","Source-owned demonstration fixture"),
        ("Wall","4 m length, 2.5 m height, 150 mm thickness, 1 m² opening","18 kN/m³, line load"),
        ("Four fixed supports","At base corners","NOT soil flexibility"),
        ("RC example strengths","fck = M25; fy = Fe500","Additional assumed design illustration"),
        ("Seismic / wind","No code-based actions","10 kN HX is diagnostic only")])
    loadtable=simple_table(("Load source","Magnitude","Derivation"),[
        ("Slab + finishes",txt(loads["SHELL_DL"])+" kN","31 m² × (0.12×25 + 1.5) kPa"),
        ("Frame + wall",txt(loads["FRAME_DL"])+" kN","Beam downstand + columns + masonry"),
        ("Total dead (DL)",txt(loads["DL"])+" kN","Actual source load ledger"),
        ("Total live (LL)",txt(loads["LL"])+" kN","31 m² × 2.0 kPa"),
        ("Horizontal HX","10.000 kN","Source-assumed lateral probe"),
        ("U+ / U−","1.2 DL + 1.5 LL ± 1.0 HX","Hypothetical demonstration combination; not verified NBC action")])
    modetable=simple_table(("Computation","Value","Meaning"),[
        ("FE node count",str(top["nodes"]),"Physical FE grid nodes (not a site survey)"),
        ("Slab elements",str(top["shell_elements"]),"ShellMITC4 two-way elastic plates"),
        ("Maximum six-axis equilibrium residual",txt(r["max_six_axis_equilibrium_residual"]),"Computed applied + reaction equilibrium, kN / kN·m units"),
        ("Flexible DL maximum vertical displacement",txt(r["max_DL_vertical_disp_mm_flexible"])+" mm","Actual OpenSees computed elastic result"),
        ("Rigid-in-plane DL maximum vertical displacement",txt(r["max_DL_vertical_disp_mm_rigid"])+" mm","Same source loads, alternative diaphragm assumption"),
        ("Controlling signed frame end moment",txt(r["selected_signed_beam_envelope"]["absolute_kNm"])+" kN·m",e(r["selected_signed_beam_envelope"]["member"]+" · "+r["selected_signed_beam_envelope"]["end"]+" · "+r["selected_signed_beam_envelope"]["component"])),
        ("Control support DL / LL",txt(r["selected_support_DL_Fz_kN"])+" / "+txt(r["selected_support_LL_Fz_kN"])+" kN","Actual fixed-base reactions at "+e(r["selected_support"]))])
    beamtable=simple_table(("Illustrative element","Numerical result","Basis / caution"),[
        ("Beam flexure · selected FE end",txt(specimen["Mu_from_signed_synthetic_U_envelope_kNm"])+" kN·m",
          "Signed 1.2DL + 1.5LL ± HX elastic FE combination"),
        ("Beam limiting moment",txt(specimen["Mu_lim_singly_reinforced_kNm"])+" kN·m","0.133 fck b d²; M25, 300mm width, d405mm"),
        ("Beam flexural steel required",txt(specimen["As_required_by_simplified_flexure_mm2"])+" mm²" if specimen["As_required_by_simplified_flexure_mm2"] is not None else "Exceeds singly reinforced limit",
          "Simplified rectangular stress block, one selected end, no detailing check"),
        ("Column axial action",txt(col["axial_envelope_kN"])+" kN","Signed selected FE column-end envelope"),
        ("Column gross nominal stress",txt(col["nominal_axial_stress_MPa"])+" MPa","Not P–M–M interaction or axial resistance verification"),
        ("Slab hypothetical one-way strip",txt(slab["hypothetical_oneway_4m_strip_Mu_kNm_per_m"])+" kN·m/m","4 m simply supported 1m strip; NOT the two-way FE shell moment"),
        ("Slab required steel (strip)",txt(slab["As_required_mm2_per_m"])+" mm²/m","M25, Fe500, d96mm, simplified flexure"),
        ("Assumed slab 10Ø150 provision",txt(slab["assumed_10mm_at_150mm_As_mm2_per_m"])+" mm²/m","Illustrative flexural area comparison only"),
        ("Footing trial plan", "1.50 × 1.50 × 0.45 m","Separate assumed footing, not part of FE model"),
        ("Footing gross service pressure",txt(foot["gross_service_bearing_kPa"])+" kPa","Gravity base reaction + own weight / 2.25m²"),
        ("Footing uniform 1-way Vu",txt(foot["uniform_concentric_trial_1way_Vu_kN"])+" kN","Assumed centered 400mm column, d394mm, gravity only"),
        ("Staircase",str(s["staircase"]["assumed_risers"])+" risers, "+str(s["staircase"]["assumed_treads"])+" treads","Geometry only; stair was NOT solved by FE")])
    sections=[
       ("intro","1.0 Introduction",overview+"""<p><b>Building purpose:</b> demonstrate the route Input → FE model → solved response → selected member design arithmetic → reproducible HTML report, using wholly assumed dimensions and loads.</p>"""),
       ("data","2.0 General Data for Structural Analysis",inputs+"<h3>2.6 Load Calculations</h3>"+loadtable),
       ("procedure","3.0 Analysis and Design Procedure",f"""<p>Load model: slab dead load, beam downstand, columns, wall net of opening and live load.
OpenSeesPy assembles <a href="{OPENSEES}">ShellMITC4</a> and elasticBeamColumn objects.
Two diaphragm cases are solved separately: <code>FLEXIBLE_SHELL</code> and <code>RIGID_INPLANE_MPC</code>.
For every case, signed support forces and free-body force/moment equilibrium are tested.
The illustrative U± envelope is a linear combination of the <em>same</em> solved model's DL, LL and HX end actions.</p>
<p>Design illustration: a separately specified M25/Fe500 stress block is used for a beam end and
a hypothetical simply-supported slab strip, while a trial assumed footing is checked for gross gravity bearing.
These Chapter 6 computations are <b>not</b> FE shell capacity design nor governing NBC/IS detailed design.</p>"""),
       ("model","4.0 Modeling in OpenSeesPy",f"""<p>Actual source fixture: 4 m × 4 m plan at z=0,3,6 m; 16 m² first floor
and 15 m² second floor after an actual one-cell rectangular opening; {top["shell_elements"]} shells,
{top["beam_segments"]} beam segments, {top["column_segments"]} vertical column segments,
{top["base_supports"]} fixed corner restraints. Nodes are shared exactly across shell/frame interfaces.
There are no invented nearest-neighbour connection snaps in this <em>synthetic</em> model.</p>
<p>Element stiffness and load cases are the same in both diaphragm comparisons. Switching to
a rigid in-plane constraint changes kinematic assumptions, not site-verified diaphragm construction.
This is not a seismic response-spectrum or nonlinear plastic hinge model.</p>"""),
       ("results","5.0 Design Output and Structural Checks",modetable+"""<div class="ok"><b>Numerical verification:</b> signed force/moment equilibrium passes for both diaphragm alternatives and all published cases. This demonstrates a working OpenSees numerical model. It is not a seismic compliance check.</div>
<h3>What the source ETABS report additionally contains</h3>
<p>Model mass participation, seismic base shear, mode shapes, drift, torsional irregularity, soft-storey and load-combination checks. Those quantities are not generated for this synthetic HX reference case, so they are not printed as fake zeroes.</p>"""),
       ("design","6.0 Design of Structural Elements",beam_detail+beamtable+f"""<h3>6.3 Other illustrative member arithmetic</h3>
<p><b>Beam:</b> M<sub>u</sub> comes from a <em>real</em> signed FE end-force envelope at
{e(r["selected_signed_beam_envelope"]["member"])}. Flexure example uses
M<sub>u</sub> = 0.87 f<sub>y</sub> A<sub>st</sub> (d − 0.42x<sub>u</sub>)
with x<sub>u</sub> = 0.87 f<sub>y</sub> A<sub>st</sub>/(0.36 f<sub>ck</sub> b);
f<sub>ck</sub>=25 MPa, f<sub>y</sub>=500 MPa, b=300mm, d=405mm.</p>
<p><b>Slab:</b> 1 m simply supported <em>teaching strip</em> assumes w<sub>u</sub>=
1.2×(0.12×25+1.5)+1.5×2 = {txt(slab["hypothetical_oneway_strip_factor_load_kPa"])} kPa;
M<sub>u</sub>=w<sub>u</sub>L²/8 at L=4m. The actual solved two-way shell distribution is
different. <b>Footing:</b> gross q=[R<sub>DL</sub>+R<sub>LL</sub>+footing weight]/A
and trial V<sub>u</sub>=q<sub>u</sub> B(a−d) for a centred column.
The footing and stair geometry do not exist in the OpenSees benchmark.</p>
<div class="wire"><b>Not an issued structural design:</b> no reliable code-based seismic action
combination, P–M–M interaction, actual torsion/other-axis beam design, ductile joints, two-way slab detailing,
soil springs, footing punching and eccentricity, staircase structural moments, or full schedule
has been passed or certified. These are the exact future calculation modules to connect,
not failures of the present completed shell/frame solver.</div>"""),
       ("annex","Annex — Inputs, Provenance and Reproduction",f"""<p><b>Actual independent source:</b>
<a href="{REPO}/blob/main/r6p23/runner.py">r6p23/runner.py reference_fixture()</a>,
<a href="{REPO}/blob/main/r6p23/engine.py">r6p23/engine.py build()</a>.
Published solved model: <a href="data/r6p23-preview.json">OpenSees source/result JSON</a>.
This educational report: <a href="reports/example-sar/example-sar-numbers.json">machine-readable calculations</a> and <a href="reports/example-sar/beam-end-checks.csv">complete beam-end strength screens (CSV)</a>.
All FE numbers originate from the checksum-matched source fixture and GitHub Actions execution.</p>
<p>Original report whose <i>organization</i> is followed: <a href="{ORIGINAL}">new nbc2025 report REVISED(1).pdf</a>
(pp. 2–3 for TOC; p. 4 general features; pp. 38–65 structural elements; pp. 66–68 annex and conclusion).
Its numeric values were not silently transplanted into this synthetic benchmark.</p>
<p>Full independent model geometry/results, photos/images, schedule and original source are separate evidence.
This demo can be printed from a browser as PDF. No professional approval or site-specific construction release.</p>""")]
    return shell("Worked example — six-chapter structural analysis report",
        "A real OpenSees-solved synthetic frame + two-way shell benchmark, laid out in your original report's chapter order; additional clearly identified hand-design examples.",
        sections,"engine-explained.html")

def inventory_report(d):
    src=f'<a href="{ORIGINAL}">Original revised structural report PDF</a>'
    repo=lambda path: f'<a href="{REPO}/blob/main/{path}"><code>{e(path)}</code></a>'
    table=simple_table(("Software","Actual implementation / inputs","Outputs and reliable accomplishment","Not implemented by that module"),[
      ("Historic governed OpenSees SAR core","Pinned main Pages checkout at f39c89a; core src/ + scripts/ and examples/",
       "Sanitized frame benchmark, model contracts, G15 Gate05–Gate21 calculation experiments, multi-step Pages build and validation",
       "Not one fully source-reconciled Narayani ETABS/SAFE replacement; many Gate scripts are distinct experiments, not independent products"),
      ("R6.23 — shell/frame FE",repo("r6p23/engine.py")+" + "+repo("r6p23/runner.py"),
       "Actual 3D ShellMITC4; exact shared shell/frame nodes, openings, wall/beam/column dead loads; flexible vs rigid diaphragm, signed forces/reactions, source-based combinations",
       "Does not automatically verify seismic code, detailed bar schedules, footings, stair; synthetic contract is not arbitrary Narayani irregular building"),
      ("R6.24 — mesh checks",repo("r6p23/convergence.py"),
       "Tested source-equivalent shell mesh sensitivity and original research viewer",
       "One refinement comparison is not a proof of asymptotic convergence"),
      ("R6.25 — real geometry",repo("r6p25/narayani_intake.py")+" + "+repo("r6p25/qa_export.py"),
       "Reads real DXF-derived GF column/footing entities, positions and candidate beam edges with original file identifiers",
       "Not an FE solver; inferred FF/SF continuity/joint snapping cannot be called built"),
      ("R6.26 — Narayani frame",repo("r6p26/engine.py")+" + "+repo("r6p26/publish.py"),
       "Independent 3D elastic frame with 23 GF columns extended to 69 column segments, 132 total members, 4 cases, signed 6DOF forces, 1,056 member-end CSV rows and 92 reactions, six-chapter report",
       "Does not model real slabs/diaphragms/wall loads, NBC 105 design earthquakes, footing capacity, full RC designs"),
      ("R6.27 — drawing/design crosswalk",repo("r6p27/source_design.py"),
       "21 real-source footing shapes, 23 GF columns, scheduled/drawn concrete quantities, steel areas and original vs independent action comparison",
       "Not a FE solver or concrete-design engine; original code/geometry discrepancies are not automatically repaired"),
      ("R6.28 — F3 shear verifier",repo("r6p27/f3_oneway_verification.py"),
       "Original worksheet pressure reproduced; shear effective-depth and IS456 stress comparisons independently recalculated; machine-verifiable release",
       "Does not physically approve source F3 footing; original NOT SAFE verdict retained"),
      ("Portal/UI",repo("portal/build.py")+" + "+repo("portal/learning_system.py"),
       "Four-section public website; both backwards-reading guides, indexed original-versus-our-product comparison, reports and SHA provenance",
       "Not a structural solver, and a website QA pass does not prove design safety")])
    compare=simple_table(("Original PDF step","Original ETABS / SAFE / worksheet outcome","What our engine genuinely produces today","To match the original format in a complete design product"),[
      ("1.0 Introduction","G+1.5 residential building description; Chapter 1, but conclusion calls it Office","Narayani source study + synthetic demo purpose/assumptions","One accepted occupancy and revision per project; automatic but editable front matter"),
      ("2.0 General Data","M20 / Fe500, cover, layouts, gravity/live, wind/seismic NBC, combinations","R6.25 project source register; R6.23 fully assumed synthetic load ledger; R6.26 partial real project load basis","Complete referenced input contract with source-vs-assumed choices and real slab/wall/site loads"),
      ("3.0 Analysis / design procedure","ETABS frame modelling, response-spectrum method, SAFE and spreadsheet checks","OpenSees linear elastic frame and ShellMITC4, conditional combinations, explicit reproducibility","Validated response-spectrum/seismic design, wind, P–Δ and member/foundation design algorithms"),
      ("4.0 Modeling","3D ETABS frame, floor layouts, assignments and actual connection assumptions","R6.23 regular synthetic shared-node shells; R6.26 actual GF coords + assumed upper storeys / beam joints","Construct verified physical model of irregular building, real walls, diaphragm and boundary restraints"),
      ("5.0 Structural output","Base shear, mass participation, displacement, drift, torsion/soft-storey, member-end forces","Actual signed OpenSees forces and base reactions, 6-axis balance; diaphragm comparisons in synthetic example","Verified site-specific modal/seismic/ULS/SLS outputs and direct source action comparison"),
      ("6.0 Element design","Columns, beam reinforcement, slabs, isolated+combined footings, staircase and schedules","Drawing quantity/steel arithmetic; F3 shear review; a bounded hypothetical beam/slab/footing teaching example","Reusable, tested code-compliant beam/column/slab/foundation/stair checks and signed schedules"),
      ("Annex, references","P–M–M figures, capacity ratios, report conclusions and codes","Source SHA/JSON/CSV, test results, one reproducible report and printable example","Traceable user-reviewed report generation, full detail sheets and engineer's issue/approval workflow")])
    sections=[
      ("answer","01 — Product status in one paragraph",f"""<p><strong>We have working numerical OpenSees engines and a report skeleton, not a finished whole-building structural design generator.</strong>
The current repository contains <b>two maintained independent OpenSees numerical model implementations</b> (R6.23 shell/frame and R6.26 source-conditioned Narayani frame),
plus a frozen earlier core engine with many historical Gate calculations. R6.24, R6.25, R6.27 and R6.28
are comparison, source intake or arithmetic modules, not separate general-purpose FE solvers.</p>
<div class="stats"><div class="stat"><small>Direct independent FE modules</small><b>2</b></div>
<div class="stat"><small>Older governed engine</small><b>1</b></div>
<div class="stat"><small>Active real project</small><b>1</b></div>
<div class="stat"><small>Complete original-equivalent RC report products</small><b>0</b></div></div>
<p>The distinction is supported by actual source code and outputs; see the file-to-capability inventory below.</p>"""),
      ("inventory","02 — Exact engine and module inventory",table),
      ("example","03 — One runnable synthetic report, using our own model",f"""<p>The reference example actually computes <strong>{e(money(d["loads_kN"]["DL"],1))} kN dead</strong> and
<strong>{e(money(d["loads_kN"]["LL"],1))} kN live</strong>, with {d["topology"]["shell_elements"]} shell cells,
{d["topology"]["beam_segments"]} beam segments, {d["topology"]["column_segments"]} columns,
and separate flexible/rigid diaphragm solutions. The report uses your original six main chapter headings,
plus clearly labeled beam/column/slab/footing/stair teaching calculations.</p>
<div class="ok"><a href="example-sar-report.html"><strong>Read the complete worked structural-analysis report →</strong></a></div>
<p>Under the same synthetic model, the actual solver has maximum DL displacement
{e(money(d["FE_results"]["max_DL_vertical_disp_mm_flexible"]))} mm in flexible mode,
and {e(money(d["FE_results"]["max_DL_vertical_disp_mm_rigid"]))} mm in rigid-in-plane mode;
both are measured calculation output, not a guess.</p>"""),
      ("gap","04 — Original engineer's report versus our available product",compare),
      ("backwards","05 — Backwards logic: what is needed to produce a report?",f"""<p><b>Work backwards</b> in exactly this order: <b>element designs</b> (Chapter 6) ← governing <b>signed structural response</b> (Chapter 5) ←
valid <b>physical model</b> (Chapter 4) ← <b>analysis and RC methods</b> (Chapter 3) ←
<b>geometry/material/load/site data</b> (Chapter 2) ← <b>building purpose</b> (Chapter 1).</p>
<p>This order helps answer <i>what do we need to calculate and from where?</i>, while the actual software
executes calculations forward from Chapter 1 to Chapter 6. Learn the source on the
<a href="original-report-guide.html">original backwards page</a> and our current numerical output on the
<a href="independent-report-guide.html">independent report backwards page</a>.</p>
<h3>One useful product decision</h3>
<p>Keep R6.23 as the <b>verified assumed example</b> and R6.26 as a <b>real-project, source-conditioned frame study</b>.
Extend the existing reporting layer with actual Chapter 6 design implementations
against separately validated benchmark examples. Do not force the real Narayani project
through invented connections just to get a printable report.</p>"""),
      ("references","06 — Reproduce, inspect and verify",f"""<p>Original source organization: {src}; official
<a href="{OPENSEES}">OpenSeesPy ShellMITC4 API</a>;
<a href="{SHEAR_FOOTING}">IS456:2000 text with amendments</a>.
R6.23 source: {repo("r6p23/engine.py")} and {repo("r6p23/runner.py")}.
R6.26 source: {repo("r6p26/engine.py")}. Real-source check: {repo("r6p27/source_design.py")}.</p>
<p><a href="data/r6p23-preview.json">Full actually solved synthetic FE JSON</a> ·
<a href="reports/example-sar/example-sar-numbers.json">Report's derived source and hand-check calculations</a> ·
<a href="{REPO}/actions">Actual GitHub Actions runs</a>. Use the companion HTML report's Print button to save a PDF.</p>""")
    ]
    return shell("What our structural engines actually do",
      "A source-file-backed inventory, working OpenSees demonstration, original-report capability comparison and one clear next implementation direction.",
      sections,"example-sar-report.html")

def build(site:Path):
    site.mkdir(exist_ok=True,parents=True)
    d=summarize(site)
    for name,content in (("engine-explained.html",inventory_report(d)),
                         ("example-sar-report.html",example_report(d))):
        (site/name).write_text(content,encoding="utf8")
    folder=site/"reports/example-sar";folder.mkdir(parents=True,exist_ok=True)
    raw=folder/"example-sar-numbers.json"
    raw.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    receipt={"schema":"jp.sar.example_engine_atlas_receipt.v1",
             "example_source_preview_sha256":d["source_preview_sha256"],
             "model_source_SHA256":d["source_fixture_sha256"],
             "engineering_approval":False,"files_sha256":{
                name:sha256((site/name).read_bytes()).hexdigest() for name in
                ("engine-explained.html","example-sar-report.html","reports/example-sar/example-sar-numbers.json")}}
    (folder/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    verify(site)
    return receipt

def verify(site:Path):
    folder=site/"reports/example-sar"
    q=json.loads((folder/"receipt.json").read_text())
    data=json.loads((folder/"example-sar-numbers.json").read_text())
    need(q["schema"]=="jp.sar.example_engine_atlas_receipt.v1","receipt schema")
    need(data["source_preview_sha256"]==sha256((site/"data/r6p23-preview.json").read_bytes()).hexdigest(),
         "published FE source was changed after report generation")
    need(data["FE_results"]["max_six_axis_equilibrium_residual"]<1e-3,
         "solved FE equilibrium cannot be asserted")
    need(data["professional_approval"] is False and data["construction_release"] is False
         and data["original_f3_not_safe_retained"] is True and data["FE_is_really_computed"],
         "source-vs-solver/engineering protection")
    for name,h in q["files_sha256"].items():
        need(sha256((site/name).read_bytes()).hexdigest()==h,
             "generated HTML/JSON SHA drift "+name)
    h=(site/"example-sar-report.html").read_text()
    for term in ("1.0 Introduction","2.0 General Data for Structural Analysis",
                 "3.0 Analysis and Design Procedure","4.0 Modeling in OpenSeesPy",
                 "5.0 Design Output and Structural Checks",
                 "6.0 Design of Structural Elements",
                 "339.000","62.000","ShellMITC4","Print / Save as PDF"):
        need(term in h,"original format or real FE value lost: "+term)
    atlas=(site/"engine-explained.html").read_text()
    for term in ("R6.23","R6.24","R6.25","R6.26","R6.27","R6.28","Historic governed","Chapter 6","What our structural engines actually do"):
        need(term in atlas,"capability/source comparison lost: "+term)
    return q
