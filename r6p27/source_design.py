"""R6.27: actual Narayani drawing / SAR / geotech / NBC105 design crosswalk.

This is a real source-dimensioned engineering REVIEW product, not a claim that
the current R6.26 trial load path or code actions are accepted for construction.
Every comparison records its source and its unresolved design limit.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path

from r6p25.qa_export import build as draw_graph, CAD_SHA

SCHEMA="jp.structural.r6p27.narayani_actual_source_design_crosswalk.v1"
GEOTECH_SQUARE={1.5:166.,2.0:177.,2.25:184.,2.5:190.,3.0:204.,3.5:219.,4.0:233.}
SCHEDULE={"IF1":(7,1.5,1.5),"IF2":(7,1.8,1.8),
          "IF3":(4,2.1,2.1),"IF4":(1,2.4,2.4),"CF1":(2,4.0,1.5)}
SOURCE_DRAWING="https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
SOURCE_SAR="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
SOURCE_GEO="https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"
CODE_NBC="https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf"
GEO_DEPTH_M=1.5
CONCRETE_UNIT_KN_M3=20.
SOURCE_FOOTING_THICKNESS_M=.5

def require(ok,msg):
    if not ok:raise ValueError("SOURCE-TO-DESIGN REVIEW FAIL: "+msg)

def sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def interp_square(b:float)->float|None:
    xs=sorted(GEOTECH_SQUARE)
    for i,x in enumerate(xs):
        if abs(b-x)<1e-7:return GEOTECH_SQUARE[x]
        if i and xs[i-1]<b<x:
            a=xs[i-1]
            return round(GEOTECH_SQUARE[a]+
                (GEOTECH_SQUARE[x]-GEOTECH_SQUARE[a])*(b-a)/(x-a),4)
    return None

def make_crosswalk(cad_root:Path,site:Path)->dict:
    graph=draw_graph(cad_root)
    require(graph["cad_source_sha"]==CAD_SHA,"pinned Narayani drawing sha")
    data=json.loads((site/"reports/r6p26/narayani-independent-frame-results.json").read_text())
    receipt=json.loads((site/"reports/r6p26/narayani-verified-manifest.json").read_text())
    resultpath=site/"reports/r6p26/narayani-independent-frame-results.json"
    require(sha(resultpath)==receipt["files_sha256"]["reports/r6p26/narayani-independent-frame-results.json"],
            "R6.26 numerical results are no longer hash-matched")
    require(data["professional_engineering_approval"] is False
            and data["construction_release"] is False
            and data["original_F3_unsafe_status_retained"] is True,
            "cannot lose historical F3 engineering adverse status")
    require(data["model_counts"]["source_GF_columns"]==23
            and len(graph["footings"])==21,
            "23 original columns / 21 source footing geometry changed")
    group=Counter(f["family"] for f in graph["footings"])
    require(group=={n:row[0] for n,row in SCHEDULE.items()},
            "actual original-DXF footing counts disagree with printed source sheet")
    sources={c["id"]:c for c in graph["columns"]}
    require(len(sources)==23,"column identity duplicate")
    case_dl={x["node"].split(":",1)[1]:x
             for x in data["cases"]["DL"]["base_support_reactions"]}
    case_ll={x["node"].split(":",1)[1]:x
             for x in data["cases"]["LL"]["base_support_reactions"]}
    require(len(case_dl)==23 and len(case_ll)==23,"R6.26 gravity base reactions absent")
    assigned=[]
    feet=[]
    totals={"source_scheduled_plan_area_m2":0.,"source_scheduled_concrete_m3":0.,
            "original_dxf_drawn_area_m2":0.,"original_dxf_drawn_concrete_m3":0.,
            "sls_trial_dl_reactions_kN":0.,"sls_trial_ll_reactions_kN":0.}
    for f in graph["footings"]:
        name=f["family"]
        refs=[part.strip() for part in f["source_columns"].split(",") if part.strip()]
        require(refs and all(r in sources for r in refs),
                "original DXF footing does not reference actual source column "+f["id"])
        assigned.extend(refs)
        l,w=f["width_m"],f["depth_m"]
        n,sl,sw=SCHEDULE[name]
        area=l*w
        planned=sl*sw
        selfweight=area*SOURCE_FOOTING_THICKNESS_M*CONCRETE_UNIT_KN_M3
        dead=sum(case_dl[r]["Fz_kN"] for r in refs)
        live=sum(case_ll[r]["Fz_kN"] for r in refs)
        require(dead>=0 and live>=-0.0001,"R6.26 wrong-sign base reaction")
        q=(dead+live+selfweight)/area
        # Lower-bound only because the existing trial model omits masonry and
        # other permanent/occupancy sources. Comparison is NOT a capacity pass.
        geo=interp_square(l) if abs(l-w)<1e-7 else None
        family_schedule_difference=round(area-planned,5)
        records={
           "source_footing_id":f["id"],"DXF_handle":f["handle"],
           "source_family":name,"source_support_column_ids":refs,
           "grid_axes":[sources[r]["source_axis"] for r in refs],
           "drawn_L_m":l,"drawn_B_m":w,"drawn_area_m2":round(area,4),
           "scheduled_L_m":sl,"scheduled_B_m":sw,
           "scheduled_area_m2":round(planned,4),
           "area_discrepancy_m2":family_schedule_difference,
           "trial_concrete_volume_m3":round(area*.5,4),
           "plan_only_reinforcement":"2 mats, both directions; 16mm @150mm"
                      if name=="CF1" else "2 mats, both directions; 12mm @150mm",
           "trial_DL_column_reactions_kN":round(dead,4),
           "trial_LL_column_reactions_kN":round(live,4),
           "assumed_footing_selfweight_kN":round(selfweight,4),
           "incomplete_DL_plus_LL_area_proxy_kPa":round(q,4),
           "geotech_Df_1p5m_square_only_kPa":geo,
           "geotech_comparison_status":"SQUARE_INTERPOLATED_INFORMATION_ONLY"
               if geo is not None else "NO_GEOTECH_RECTANGULAR_CF1_VALUE",
           "engineered_capacity_verdict":"NOT_ASSESSED_LOADS_ECCENTRICITY_SHEAR_PUNCHING_SETTLEMENT",
           "actual_construction_permission":False,
        }
        feet.append(records)
        totals["original_dxf_drawn_area_m2"]+=area
        totals["original_dxf_drawn_concrete_m3"]+=area*.5
        totals["sls_trial_dl_reactions_kN"]+=dead
        totals["sls_trial_ll_reactions_kN"]+=live
    require(len(assigned)==23 and set(assigned)==set(sources) and len(set(assigned))==23,
            "each GF column must map to exactly one original footing, including pairs in CF1")
    for name,(n,l,b) in SCHEDULE.items():
        totals["source_scheduled_plan_area_m2"]+=n*l*b
        totals["source_scheduled_concrete_m3"]+=n*l*b*.5
    totals={k:round(v,5) for k,v in totals.items()}
    require(totals["source_scheduled_concrete_m3"]==36.915,
            "sourced footing schedule concrete takeoff changed")
    require(totals["original_dxf_drawn_concrete_m3"]==36.33,
            "G1 exact 1.8 vs scheduled 2.1 source conflict not kept")
    g1=[f for f in feet if "G1" in f["grid_axes"]]
    require(len(g1)==1 and g1[0]["source_family"]=="IF3"
            and g1[0]["drawn_L_m"]==1.8
            and g1[0]["scheduled_L_m"]==2.1,"original G1 dimension conflict changed")
    ccount=Counter(c["family"] for c in graph["columns"])
    require(ccount=={"C1":11,"C2":2,"C3":4,"C4":6},
            "source original column family/quantity changed")
    # Explicitly audit *revised report's* C4 bar schedule, not a verified
    # exact issued-as-built column cage. NBC 105:2025 Annex A cl 4.2.2(b)
    # mandates gross longitudinal area ratio >=1%.
    bararea=8*math.pi*12**2/4
    circlearea=math.pi*350**2/4
    rho=bararea/circlearea
    require(rho<.01,"original SAR C4 source schedule should trigger code-min exception")
    column_table=[
      {"family":"C1","count":11,"section":"400×400 mm",
        "revised_report_GF_bars":"8Ø16",
        "gross_area_mm2":160000,
        "reported_schedule_Ast_mm2":round(8*math.pi*16**2/4,2),
        "reported_schedule_pct":round(8*math.pi*16**2/4/160000*100,3)},
      {"family":"C2","count":2,"section":"400×400 mm",
        "revised_report_GF_bars":"4Ø20 + 4Ø16",
        "gross_area_mm2":160000,
        "reported_schedule_Ast_mm2":round(math.pi*(4*20**2+4*16**2)/4,2),
        "reported_schedule_pct":round(math.pi*(4*20**2+4*16**2)/4/160000*100,3)},
      {"family":"C3","count":4,"section":"400×400 mm",
        "revised_report_GF_bars":"8Ø20",
        "gross_area_mm2":160000,
        "reported_schedule_Ast_mm2":round(8*math.pi*20**2/4,2),
        "reported_schedule_pct":round(8*math.pi*20**2/4/160000*100,3)},
      {"family":"C4","count":6,"section":"Ø350 mm",
        "revised_report_GF_bars":"8Ø12",
        "gross_area_mm2":round(circlearea,2),
        "reported_schedule_Ast_mm2":round(bararea,2),
        "reported_schedule_pct":round(rho*100,3),
        "minimum_NBC105_2025_gross_pct":1.0,
        "code_comparison":"BELOW_1_PERCENT_MINIMUM__DESIGN_REVISION_REQUIRED"}
    ]
    return {
      "schema":SCHEMA,"project_id":"PRJ-000007",
      "source_original_DXF_sha":CAD_SHA,
      "R626_signed_results_sha256":sha(resultpath),
      "source_report_revision":"G+1.5 residential / August 2026 report",
      "source_structural_drawing_revision":"July 2026, Class B Residential+Commercial",
      "earlier_report_version":"G+2.5 Commercial & Semi Residential",
      "occupancy_conflict_requires_reconciled_code_loads":True,
      "footing_schedule":{k:{"count":v[0],"L_m":v[1],"B_m":v[2],
                          "source_rebar":"16Ø @ 150 top and bottom both ways" if k=="CF1"
                                          else "12Ø @ 150 top and bottom both ways"}
                          for k,v in SCHEDULE.items()},
      "footings":feet,"column_schedule":column_table,
      "source_footing_count":21,"source_Gf_column_count":23,
      "source_footing_concrete_thickness_m":SOURCE_FOOTING_THICKNESS_M,
      "owner_approved_concrete_unitweight_kN_m3":CONCRETE_UNIT_KN_M3,
      "footing_quantities":totals,
      "geotech_report_square_footing_allowables_by_size_at_1p5m":
                      {str(k):v for k,v in GEOTECH_SQUARE.items()},
      "geotech_table_note":"Static 25mm settlement and Df=1.5m, square centered footings only; interpolated nominal square values are indicative, no eccentricity/CF1/settlement design acceptance.",
      "seismic_soil_class":"UNRECONCILED_NBC105_2025_GEOTECH_2020_TYPE_B_VS_OLDER_SAR_D",
      "real_building_design_completed":False,
      "construction_release":False,
      "original_F3_unsafe_retained":True,
      "required_engineer_decisions":[
        {"id":"D01","priority":"P0","finding":"C4 8Ø12 gives 0.940% and violates NBC105:2025 Annex A cl 4.2.2 minimum 1% longitudinal ratio as reported.","required_decision":"Reconcile actual signed column cage and complete biaxial strength, ductility, anchorage and joint redesign; reissue code-compliant detail."},
        {"id":"D02","priority":"P0","finding":"Original SAR footing F3/IF3 historical NOT SAFE IN ONE WAY SHEAR.","required_decision":"Check correct support load combinations, depth, critical shear section and reinforcement; redesign and independently recheck F3 before footing casting."},
        {"id":"D03","priority":"P0","finding":"Original G1 DXF 1.8×1.8m vs family IF3 sheet 2.1×2.1m (1.17m², 0.585m³ difference).","required_decision":"Issue corrected dimensioned footing sheet and verified capacity and settlement calculations. Never silently resize source."},
        {"id":"D04","priority":"P0","finding":"The latest drawing says Residential+Commercial, revised report G+1.5 Residential, earlier report G+2.5 Commercial+Semi Residential.","required_decision":"Confirm physically approved building storey count and actual occupancy zones, load/mass and relevant seismic code classes."},
        {"id":"D05","priority":"P0","finding":"Two CF1 combined footings carry two original source column marks each; standard square geotechnical allowable cannot be used as rectangular CF1 approval.","required_decision":"Reconcile resultant load and eccentricity, contact pressures, overturning/uplift, bearing/settlement, beam/slab reinforcement and genuine linked base reactions."},
        {"id":"D06","priority":"P0","finding":"R6.26 elastic solver repeats the 23 GF column axes upward and snaps upper-floor beam-strip candidates; frame connections and actual wall/slab/stair loads are not physically verified.","required_decision":"Crosswalk issued structural drawings and floor wall/opening geometry, apply all code actions, then solve actual source-registered conforming 3D frame+shell and capacity cases."},
        {"id":"D07","priority":"P0","finding":"Geotechnical site Type B is classified under NBC105:2020; current 2025 code uses Vs30 preferentially or NSPT as available; older structural report Type D.","required_decision":"Select documented NBC105:2025 soil category using original 20m borehole N-values or measured Vs30, and compute site-specific spectra and mass/load combinations."},
      ],
      "sources":[{"role":"Structural drawing July 2026","url":SOURCE_DRAWING,"pages":"STR-01–19, footing/column/beam/slab schedules"},
                 {"role":"Revised structural report","url":SOURCE_SAR,"pages":"pp. 42, 49–65, footing F3 and C4 tables"},
                 {"role":"Geotechnical 2025","url":SOURCE_GEO,"pages":"pp.20–22, 25mm static allowable footings"},
                 {"role":"Official NBC105:2025","url":CODE_NBC,"pages":"Annex A, cl 4.2.2(b); section 4.1.3 site soil class"}]
    }

def save_json(out:Path,d:dict):
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")

def fmt(v,n=2):
    return f"{v:,.{n}f}"

def html(d:dict)->str:
    qty=d["footing_quantities"]
    row=[]
    for name,record in d["footing_schedule"].items():
        q=record["count"];a=record["L_m"]*record["B_m"]
        row.append(f"<tr><th>{name}</th><td>{q}</td><td>{record['L_m']:g} × {record['B_m']:g} m</td>"
          f"<td>{fmt(q*a,2)} m²</td><td>{fmt(q*a*.5,3)} m³</td><td>{escape(record['source_rebar'])}</td></tr>")
    detail=[]
    for f in sorted(d["footings"],key=lambda r:(r["source_family"],r["grid_axes"])):
        axes="/".join(f["grid_axes"])
        conflict=" class='conflict'" if f["area_discrepancy_m2"] else ""
        soil=fmt(f["geotech_Df_1p5m_square_only_kPa"])+" *" if f["geotech_Df_1p5m_square_only_kPa"] is not None else "CF1: not covered"
        detail.append(f"<tr{conflict}><th>{escape(axes)}</th><td>{f['source_family']}</td>"
          f"<td>{f['drawn_L_m']:g} × {f['drawn_B_m']:g}</td><td>{fmt(f['trial_concrete_volume_m3'],3)}</td>"
          f"<td>{fmt(f['trial_DL_column_reactions_kN'],1)}</td><td>{fmt(f['trial_LL_column_reactions_kN'],1)}</td>"
          f"<td>{fmt(f['incomplete_DL_plus_LL_area_proxy_kPa'],1)}</td><td>{soil}</td>"
          f"<td>{'DRAWING/SCHEDULE CONFLICT' if f['area_discrepancy_m2'] else 'SOURCE SIZE RECONCILED'}</td></tr>")
    cols=[]
    for c in d["column_schedule"]:
        issue=(c["family"]=="C4")
        cols.append(f"<tr{' class=conflict' if issue else ''}><th>{c['family']}</th><td>{c['count']}</td><td>{escape(c['section'])}</td>"
                    f"<td>{escape(c['revised_report_GF_bars'])}</td><td>{fmt(c['reported_schedule_Ast_mm2'],1)}</td>"
                    f"<td>{fmt(c['reported_schedule_pct'],3)}%</td>"
                    f"<td>{'BELOW 1% CODE MINIMUM' if issue else 'At or above 1% MINIMUM ONLY'}</td></tr>")
    actions=[]
    for item in d["required_engineer_decisions"]:
        actions.append(f"<tr><td>{item['id']}</td><td>{escape(item['finding'])}</td>"
                f"<td>{escape(item['required_decision'])}</td></tr>")
    nav="""<header><a class='mark' href='index.html'>JP Structural Analysis</a>
    <nav><a href='projects.html'>Projects</a><a href='r6p26-report.html'>R6.26 model report</a>
    <a href='research.html'>Research</a><a href='developers.html'>Developers</a></nav></header>"""
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>Narayani — Drawing-derived structural design review · R6.27</title>
    <meta name='description' content='Real original-DXF footing takeoff, source reinforcement schedule, column ratio and original SAR design conflicts'>
    <style>
    :root{{--ink:#232944;--accent:#40348d;--red:#ae2f45;--line:#dadce4;--paper:#faf9f5;--muted:#657084}}*{{box-sizing:border-box}}
    body{{background:var(--paper);color:var(--ink);font:15px/1.57 system-ui,sans-serif;margin:0}}
    header{{padding:17px max(20px,calc((100vw - 1280px)/2));border-bottom:1px solid var(--line);background:white;display:flex;gap:20px;align-items:center;flex-wrap:wrap}}
    header .mark{{font-weight:900;text-decoration:none;color:var(--accent)}}header nav{{display:flex;gap:16px;flex-wrap:wrap}}
    header nav a{{font-size:12px;font-weight:750;color:var(--accent)}}main{{max-width:1280px;margin:0 auto;padding:25px 20px 55px}}
    .eyebrow{{font-size:11px;letter-spacing:.13em;font-weight:900;color:#237c75}}h1{{font-size:clamp(29px,4.7vw,56px);letter-spacing:-.05em;line-height:1.05;margin:14px 0}}h2{{font-size:25px;letter-spacing:-.02em}}
    p{{color:#536075}}.lead{{font-size:17px;max-width:890px}}section{{padding:25px;background:white;border:1px solid var(--line);border-radius:11px;margin-top:18px;scroll-margin-top:12px}}
    .toc{{display:flex;gap:7px;flex-wrap:wrap;margin:25px 0}}.toc a{{background:white;border:1px solid #d6d3df;border-radius:99px;padding:7px 11px;font-size:12px;text-decoration:none;color:var(--accent)}}
    .numbers{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.numbers>div{{background:#f4f1fa;border-radius:8px;padding:16px}}.numbers span{{font-size:11px;color:#626678;display:block}}.numbers b{{font-size:25px;color:var(--accent)}}
    table{{width:100%;border-collapse:collapse;font-size:12px;min-width:770px}}th,td{{border-bottom:1px solid #e8e9ee;padding:10px;text-align:left;vertical-align:top}}thead th{{font-size:10px;letter-spacing:.07em;color:#515b72;background:#f0eff6}}tbody tr.conflict{{background:#fff1f0}}tbody tr.conflict th,tbody tr.conflict td:last-child{{color:var(--red);font-weight:850}}
    .scroll{{width:100%;overflow-x:auto}}.note{{font-size:12px;color:#687084}}.bad{{background:#ffeded;border-left:4px solid #d74a60;border-radius:6px;padding:14px;color:#753d48}}.good{{background:#f0f5f5;border-left:4px solid #36867d;padding:14px}}
    .source-list{{display:flex;gap:9px;flex-wrap:wrap}}a{{color:var(--accent)}}.source-list a{{padding:8px 11px;background:#f6f4fc;border:1px solid #e1ddef;border-radius:6px;font-size:12px}}
    footer{{font-size:12px;color:#677080;margin-top:30px;border-top:1px solid var(--line);padding:20px 0}}
    @media(max-width:700px){{main{{padding:13px}}section{{padding:16px}}.numbers{{grid-template-columns:repeat(2,1fr)}}header{{padding:12px 15px}}}}
    @media print{{header,.toc{{display:none}}main{{padding:0}}section{{break-inside:avoid}}body{{background:white}}}}
    </style></head><body>{nav}
    <main><p class='eyebrow'>PRJ-000007 · POKHARA-15 · R6.27 / 2026-11-16 · SOURCE-DERIVED ENGINEERING REVIEW</p>
    <h1>Actual dimensions.<br>Actual calculations.<br>Construction decisions.</h1>
    <p class='lead'>Built from Narayani's <b>July 2026 structural drawings</b>, the revised structural-analysis report, the project soil report and the independent R6.26 OpenSees output. The quantities and the code/geometry discrepancies below are calculated; trial FE bearing pressures are separately identified as incomplete, not accepted construction loads.</p>
    <div class='numbers'><div><span>Original footing outlines</span><b>21</b></div>
    <div><span>Column axes mapped</span><b>23/23</b></div><div><span>Scheduled 500mm footing concrete</span><b>{fmt(qty['source_scheduled_concrete_m3'],3)} m³</b></div>
    <div><span>Original DXF drawn footprint volume</span><b>{fmt(qty['original_dxf_drawn_concrete_m3'],3)} m³</b></div></div>
    <nav class='toc'><a href='#footings'>Footing takeoff</a><a href='#members'>Column steel/code</a><a href='#loads'>21 footing loads</a>
    <a href='#decisions'>Construction decision register</a><a href='#references'>Original sources</a></nav>
    <div class='bad'><b>DO NOT CAST FROM THIS RESEARCH REPORT.</b> The original structural report itself marks footing F3 <b>NOT SAFE IN ONE WAY SHEAR</b>. C4's report reinforcement is below the NBC105:2025 1% minimum, and the current model omits walls, complete slabs and code seismic actions. A licensed engineer must resolve and issue revised signed construction drawings.</div>
    <section id='footings'><p class='eyebrow'>01 · DRAWING SHEET STR-01</p><h2>Footings — original schedule and concrete calculation</h2>
      <div class='scroll'><table><thead><tr><th>Family</th><th>Units</th><th>Schedule L × B</th><th>Footprint area</th><th>Concrete at 500mm</th><th>Scheduled steel</th></tr></thead>
      <tbody>{''.join(row)}</tbody></table></div>
      <p>Using the drawing's 500 mm footing thickness and family counts: <b>{fmt(qty['source_scheduled_concrete_m3'],3)} m³</b> per schedule. The exact source-DXF outlines yield <b>{fmt(qty['original_dxf_drawn_concrete_m3'],3)} m³</b>; the difference is <b>{fmt(qty['source_scheduled_concrete_m3']-qty['original_dxf_drawn_concrete_m3'],3)} m³</b> because G1 is 1.8×1.8m in the frozen original DXF but called IF3 2.1×2.1m in its schedule. No excavation, PCC/soling, slope, rebar hooks/laps or wastage is included.</p>
      <p class='note'>Source dimensions and 12Ø/16Ø at 150mm top-and-bottom both directions are shown as the <em>existing drawing specification for audit</em>, not a newly approved bar cutting schedule. At 150mm spacing, nominal longitudinal cross-sectional area per metre per direction is 754.0mm²/m (12Ø) or 1,340.4mm²/m (16Ø), before cover, bending and lap detailing.</p>
    </section>
    <section id='members'><p class='eyebrow'>02 · REVISED SAR COLUMN SCHEDULE VS NBC105:2025</p><h2>Column reinforcement — real code arithmetic</h2>
      <div class='scroll'><table><thead><tr><th>Family</th><th>Count</th><th>Section</th><th>Original report GF bars</th><th>Steel area mm²</th><th>Gross ratio</th><th>Minimum area test</th></tr></thead><tbody>{''.join(cols)}</tbody></table></div>
      <p class='bad'>C4 in the <b>revised SAR</b> says 8Ø12 for a Ø350mm column, giving 904.8mm² steel / 96,211mm² gross section = <b>0.9404%</b>; NBC105:2025 Annex A cl.4.2.2(b) requires at least <b>1%</b>. This is a reported-section minimum-area failure; cross-check the actual issued drawing cage because the drawing text extraction itself has multiple story/bar notations. Steel-area compliance alone does not prove axial/biaxial or seismic detailing adequacy.</p>
      <p>Other reported C1, C2 and C3 minimum-percent screens are above 1%; that only clears this single <em>minimum longitudinal ratio</em> condition, not structural member or joint design. The original SAR also shows a 300×400mm B46 beam while the general drawing's main beam family is around 230×405mm: reconcile member-by-member, not by replacing all beams with a single section.</p>
    </section>
    <section id='loads'><p class='eyebrow'>03 · 21 ORIGINAL DXF SUPPORT OUTLINES × 4 CASES GENERATED IN R6.26</p><h2>Footing-to-column crosswalk and trial vertical actions</h2>
    <p>Unlike the previous report, this crosswalk assigns <b>each of the 23 original GF columns to exactly one of the 21 native footing outlines</b>, including two pairs sharing CF1. DL and LL base reactions come from the signed independent OpenSees computation. The last pressure column adds 500mm footing weight at your approved 20 kN/m³ and divides by actual drawn area. <strong>It is an incomplete load diagnostic, not a bearing-capacity or construction verdict</strong>: masonry/walls, full live-load zoning, uplift, moments/eccentricity, geotechnical corrections and seismic/wind combinations are not included.</p>
    <div class='scroll'><table><thead><tr><th>Source grid</th><th>Footing</th><th>DXF L×B m</th><th>Concrete m³</th><th>Trial DL kN</th><th>Trial LL kN</th><th>Trial q kPa</th><th>Geo table kPa</th><th>Source dimension</th></tr></thead><tbody>{''.join(detail)}</tbody></table></div>
    <p class='note'>* For square isolated footings, geotechnical values at founding depth 1.5m and 25mm settlement are size-linear interpolations between the source geotechnical tables (1.5m=166, 2.0m=177, 2.25m=184, 2.5m=190 kPa). The user-approved 160 kPa model scenario is not a universal allowable; the geotechnical report does not directly give the required 4.0×1.5m CF1 rectangular/multi-column bearing and eccentricity capacity. The test values may be low because the model omits important load sources.</p>
    </section>
    <section id='decisions'><p class='eyebrow'>04 · DESIGN REVIEW ACTIONS IN EXECUTION ORDER</p><h2>What must change before issuing construction drawings</h2>
      <div class='scroll'><table><thead><tr><th>Ref</th><th>Actual finding</th><th>Required design output</th></tr></thead><tbody>{''.join(actions)}</tbody></table></div>
      <p>This is the shortest responsible path toward a construction issue: resolve the original contradictory geometry/use, re-create actual wall/slab/beam/column and footing load paths, solve NBC105:2025 governing actions, redesign failing members/foundations, and issue signed, dimensioned construction drawings and bar bending schedules after independent review.</p>
    </section>
    <section id='references'><p class='eyebrow'>05 · EVIDENCE</p><h2>Original sources and machine-readable calculation</h2>
    <div class='source-list'><a href='{SOURCE_DRAWING}'>July 2026 Structural Drawings</a><a href='{SOURCE_SAR}'>Revised Structural Report</a><a href='{SOURCE_GEO}'>Geotechnical Report</a>
    <a href='{CODE_NBC}'>Official NBC105:2025</a><a href='reports/r6p27/source-design-crosswalk.json'>Full 21-footing JSON calculations</a>
    <a href='reports/r6p27/source-design-sha256.json'>Artifact SHA256 receipt</a></div>
    <p class='note'>Original drawing-source revision SHA: {escape(d['source_original_DXF_sha'])}. Baseline independent R6.26 results digest: {d['R626_signed_results_sha256']}. No raw private DXF or PDF is embedded or republished here.</p></section>
    <footer>JP Structural Analysis · R6.27 source-design crosswalk · Derived calculations with primary-source provenance · Engineering review, not signed construction permit.</footer>
    </main></body></html>"""

def publish(cad_root:Path,site:Path)->dict:
    d=make_crosswalk(cad_root,site)
    p=site/"reports/r6p27"
    p.mkdir(parents=True,exist_ok=True)
    data=p/"source-design-crosswalk.json"
    save_json(data,d)
    page=site/"r6p27-construction-review.html"
    page.write_text(html(d),encoding="utf8")
    receipt={
      "schema":"jp.structural.r6p27.source_design_manifest.v1",
      "source_original_DXF_sha":CAD_SHA,
      "R626_source_results_sha256":d["R626_signed_results_sha256"],
      "source_geometry_count_footings":21,
      "source_geometry_count_GF_columns":23,
      "scheduled_concrete_m3":d["footing_quantities"]["source_scheduled_concrete_m3"],
      "actual_DXF_dim_concrete_m3":d["footing_quantities"]["original_dxf_drawn_concrete_m3"],
      "C4_code_minimum_ratio_failure":True,
      "historical_F3_unsafe":True,
      "construction_approved":False,
      "files_sha256":{
        "r6p27-construction-review.html":sha(page),
        "reports/r6p27/source-design-crosswalk.json":sha(data)
      }
    }
    save_json(p/"source-design-sha256.json",receipt)
    return verify(site)

def verify(site:Path)->dict:
    receipt=json.loads((site/"reports/r6p27/source-design-sha256.json").read_text())
    require(receipt["schema"]=="jp.structural.r6p27.source_design_manifest.v1"
            and receipt["construction_approved"] is False
            and receipt["historical_F3_unsafe"] is True
            and receipt["C4_code_minimum_ratio_failure"] is True,
            "wrong construction/safety status in published receipt")
    for file,digest in receipt["files_sha256"].items():
        require(sha(site/file)==digest,"published crosswalk SHA256 failed "+file)
    d=json.loads((site/"reports/r6p27/source-design-crosswalk.json").read_text())
    require(len(d["footings"])==21 and sum(len(f["source_support_column_ids"]) for f in d["footings"])==23,
            "source footing-to-column mapping missing")
    require(d["footing_quantities"]["original_dxf_drawn_concrete_m3"]==36.33,
            "original drawing G1 takeoff lost")
    require(d["column_schedule"][3]["reported_schedule_pct"]<1.0,
            "original C4 steel-ratio design defect missing")
    return receipt
