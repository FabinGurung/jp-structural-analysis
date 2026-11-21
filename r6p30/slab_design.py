"""R6.36: source-linked elastic shell plate moment -> 1m RC slab-strip screens.

OpenSees ShellMITC4 'stresses' returns FOUR integration point vectors:
[p11,p22,p12,m11,m22,m12,q1,q2] per point, using kN,m units.
For horizontal CCW model panels local 1 = global +X and local 2 = +Y.
Moments are section resultants (kN m /m), shear resultants kN/m,
NOT 24-DOF element nodal forces, NOT material stress at face.

Wood-Armer-style conservative torsion adjustment for mutually orthogonal
face/direction design envelopes: M_bottom = max(0,+Mii+abs(M12));
M_top=max(0,-Mii+abs(M12)). Original sign-to-face relation is assumed;
real sections, local axes, support strips and M12 signs require verification.
IS456:2000 §§26.5.2.1/.2, 26.3.3, 38.1 and Annex G; Table19/40.2.
This screen excludes crackwidth, development, full deflection, openings,
beam shear transfer, corner torsion cages and earthquake design.
"""
from __future__ import annotations
import math
from typing import Mapping
from r6p30.beam_design import tau_c_table19

SCHEMA="jp.sar.r6p36.elastic_shell_slab_screen.v1"
CODE="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
NPTEL_ONEWAY="https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m8l18.pdf"
NPTEL_TWOWAY="https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m8l19.pdf"
SHELL_CODE="https://github.com/OpenSees/OpenSees/blob/master/SRC/element/shell/ShellMITC4.cpp"
DEFAULT={
 "D_mm":120.,"fck_MPa":25.,"fy_MPa":500.,
 "bar_diameter_mm":8.,"bar_spacing_mm":150.,
 "clear_cover_mm":20.,"layer_allowance_mm":8.,
 "steel_source":"HYPOTHETICAL_8MM_150_EACH_FACE_EACH_DIRECTION_NOT_NARAYANI_BAR_SCHEDULE",
 "slab_load_source":"ACTUAL_R6P23_SYNTHETIC_OpenSees_SHELLMITC4",
}
def require(ok,why):
 if not ok:raise ValueError("R6.36 SLAB HOLD: "+why)
def finite(x,label):
 require(isinstance(x,(int,float)) and not isinstance(x,bool)
         and math.isfinite(float(x)),label+" must be finite")
 return float(x)
def section(raw:Mapping=DEFAULT)->dict:
 needed=("D_mm","fck_MPa","fy_MPa","bar_diameter_mm",
         "bar_spacing_mm","clear_cover_mm","layer_allowance_mm")
 a={k:finite(raw[k],k) for k in needed}
 require(all(x>0 for x in a.values()),"positive dimensions and material strengths required")
 require(a["fck_MPa"] in (15.,20.,25.,30.,35.,40.),"IS456 table M15-M40 scope only")
 require(a["fy_MPa"] in (250.,415.,500.),"Fe250/415/500 only")
 d=a["D_mm"]-a["clear_cover_mm"]-a["layer_allowance_mm"]-a["bar_diameter_mm"]/2
 require(d>0 and d<a["D_mm"],"two-layer effective depth invalid")
 require(a["bar_diameter_mm"]<=a["D_mm"]/8,
         "IS456 26.5.2.2 diameter > 1/8 slab thickness")
 require(a["bar_spacing_mm"]>a["bar_diameter_mm"],
         "bar-to-bar spacing less than diameter")
 fy=a["fy_MPa"]
 require(a["bar_spacing_mm"]<=min(3*d,300.),
         "IS456 26.3.3 main reinforcement spacing exceeded")
 As=1000*math.pi*a["bar_diameter_mm"]**2/(4*a["bar_spacing_mm"])
 Amin=(.0015 if fy==250 else .0012)*1000*a["D_mm"]
 xulim={250.:.53,415.:.48,500.:.46}[fy]
 xu=.87*fy*As/(.36*a["fck_MPa"]*1000)
 Mres=(.87*fy*As*(d-.42*xu)/1e6) if xu<=xulim*d else None
 Mlim=.36*a["fck_MPa"]*1000*xulim*d*(d-.42*xulim*d)/1e6
 return {**a,"b_mm":1000.,"d_mm":d,"As_provided_mm2_m":As,
         "As_min_mm2_m":Amin,"xu_mm":xu,"xu_limit_mm":xulim*d,
         "Mres_kNm_m":Mres,"Mlim_kNm_m":Mlim,
         "minimum_steel_ok":As>=Amin,
         "section_tension_zone_ok":xu<=xulim*d,
         "main_bar_spacing_max_mm":min(3*d,300.),
         "secondary_bar_spacing_max_mm":min(5*d,450.),
         "assumed_top_and_bottom_each_direction":True,
         "construction_approval":False}
def strip(moment_kNm_m:float,raw:Mapping=DEFAULT)->dict:
 s=section(raw)
 m=max(0,finite(moment_kNm_m,"bending moment"))
 fck=s["fck_MPa"];fy=s["fy_MPa"];d=s["d_mm"];b=1000.
 k={250.:.53,415.:.48,500.:.46}[fy]
 limit=s["Mlim_kNm_m"]
 coef=.42*(.87*fy)**2/(.36*fck*b)
 lin=.87*fy*d
 discr=lin**2-4*coef*m*1e6
 req=(lin-math.sqrt(max(0.,discr)))/(2*coef) if m<=limit+1e-10 and discr>=-1e-4 else None
 with_min=max(req,s["As_min_mm2_m"]) if req is not None else None
 ok=(s["minimum_steel_ok"] and s["section_tension_zone_ok"]
     and s["Mres_kNm_m"] is not None and m<=s["Mres_kNm_m"]+1e-8)
 return {"demand_Mu_kNm_m":m,"As_required_flexure_mm2_m":req,
         "As_required_with_min_mm2_m":with_min,
         "As_provided_mm2_m":s["As_provided_mm2_m"],
         "M_provided_capacity_kNm_m":s["Mres_kNm_m"],
         "M_lim_kNm_m":limit,"isolated_flexure_ok":bool(ok),
         "status":"WITHIN_BOUNDED_FLEXURE_SCREEN" if ok else
           "SINGLY_REINFORCED_LIMIT_EXCEEDED" if m>limit else
           "PROVIDED_STEEL_OR_SPACING_INSUFFICIENT",
         "construction_approval":False}
def shear(q_kN_m:float,raw:Mapping=DEFAULT)->dict:
 s=section(raw)
 q=abs(finite(q_kN_m,"shell shear resultant"))
 tau=q/s["d_mm"]
 pt=100*s["As_provided_mm2_m"]/(1000*s["d_mm"])
 # IS456 40.2.1.1 slab-depth k factor: thickness <=150mm -> 1.3.
 D=s["D_mm"]
 k=1.3 if D<=150 else 1.3-(D-150)*.3/150 if D<300 else 1.
 strength=k*tau_c_table19(int(s["fck_MPa"]),pt)
 return {"Q_signed_input_kN_m":finite(q_kN_m,"q"),
         "tau_v_MPa":tau,"tau_c_slab_MPa":strength,
         "thickness_multiplier_k":k,
         "isolated_transverse_shear_ok":tau<=strength+1e-10,
         "not_a_punching_or_support_zone_check":True}
def wood_armer(m11,m22,m12)->dict:
 a,b,t=map(lambda x:finite(x,"shell moment"),(m11,m22,m12))
 return {"X_bottom":max(0.,a+abs(t)),
         "Y_bottom":max(0.,b+abs(t)),
         "X_top":max(0.,-a+abs(t)),
         "Y_top":max(0.,-b+abs(t))}
def published_oneway_benchmark():
 """NPTEL IIT Kharagpur Lesson18 TQ3 (one-way slab), independent example.

 External SP16 Table41 claim 8mm@120 -> 22.26kNm/m; our singly
 reinforced equation differs: explicitly report, do NOT force an agreement.
 """
 w=1.5*(.175*25+1.+4.)
 Mu=w*3.5**2/8
 Vu=w*3.5/2
 ss={**DEFAULT,"D_mm":175.,"fck_MPa":20.,"fy_MPa":415.,
     "clear_cover_mm":17.,"layer_allowance_mm":4.,
     "bar_spacing_mm":120.}
 design=strip(Mu,ss)
 computed=design["M_provided_capacity_kNm_m"]
 table41=22.26
 return {"source":NPTEL_ONEWAY,"source":"IIT Kharagpur NPTEL Lesson18 TQ3",
         "source_url":NPTEL_ONEWAY,
         "published_D_mm":175.,"published_d_mm":150.,
         "published_span_m":3.5,"published_imposed_kPa":4.,
         "published_finish_kPa":1.,"published_fck_MPa":20.,"published_fy_MPa":415.,
         "factored_pressure_kPa":w,"computed_analytic_Mu_kNm_m":Mu,
         "published_Mu_kNm_m":21.533,"computed_Vu_kN_m":Vu,
         "published_Vu_kN_m":24.61,
         "published_SP16_table41_capacity_kNm_m":table41,
         "our_IS456_AnnexG_capacity_kNm_m":computed,
         "our_relative_chart_capacity_difference":(computed-table41)/table41,
         "published_bar_selection":"8mm @120mm main; 6mm @120mm distribution",
         "our_8mm_120mm_As_mm2_m":design["As_provided_mm2_m"],
         "published_slab_min_As_mm2_m":210.,
         "computed_slab_min_As_mm2_m":section(ss)["As_min_mm2_m"],
         "benchmark_agreement":"ANALYTIC_LOAD_AND_REBAR_AREA_MATCH; MOMENT_CAPACITY_DIFFERS_FROM_SP16_TABLE",
         "benchmark_section_depth_mm":section(ss)["d_mm"],
         "original_source_math_status":"EXTERNAL_WORKED_EXAMPLE_NOT_OUR_MODEL",
         "section_chart_capacity_sp16_certified":False,
         "construction_approval":False}
def from_opensees(solved:Mapping,section_data:Mapping=DEFAULT)->dict:
 require(solved.get("classification")=="SYNTHETIC_REFERENCE","not a source-verified project")
 need=dict(solved["signed_combinations"])
 solutions=solved["solutions"]
 top=solved["topology"]
 shellcells=top["shell_cells"]
 keys={f"L{x['floor']}:CELL:{x['i']}:{x['j']}":x for x in shellcells}
 require(len(keys)==len(shellcells)>0,"unique shell panel geometry")
 s=section(section_data)
 out=[]
 for mode,combos in need.items():
  raw=solutions[mode]
  for name,combo in combos.items():
   factors=combo["factors"]
   require(factors and all(k in raw for k in factors),"combination source cases missing")
   for cell,geo in keys.items():
    pressure=[]
    for gauss in range(4):
     z=[0.]*8
     for cid,factor in factors.items():
      record=raw[cid]["shell_gauss_section_resultants"][cell]
      require(len(record)==4,"four actual shell Gauss section results required")
      point=record[gauss]
      for j,k in enumerate(("p11","p22","p12","m11","m22","m12","q1","q2")):
       z[j]+=float(factor)*finite(point[k],k)
     pressure.append(z)
    for label in ("X_bottom","Y_bottom","X_top","Y_top"):
     direction=label[0];face=label.split("_")[1]
     records=[]
     for gp,x in enumerate(pressure,1):
      env=wood_armer(x[3],x[4],x[5])
      records.append((env[label],gp,x))
     mom,gp,orig=max(records,key=lambda a:a[0])
     q=orig[6] if direction=="X" else orig[7]
     flex=strip(mom,section_data)
     sq=shear(q,section_data)
     out.append({"mode":mode,"combination":name,"cell":cell,
       "floor":geo["floor"],"i":geo["i"],"j":geo["j"],
       "gauss":gp,"direction":direction,"face":face,
       "shell_original_signed_m11_m22_m12_kNm_m":orig[3:6],
       "shell_original_signed_q1_q2_kN_m":orig[6:8],
       "design_moment_WoodArmer_assumed_kNm_m":mom,
       "bending":flex,"transverse_shear":sq,
       "original_project_slab_reinforcement_8mm_150_IS_NOT_this_model":True,
       "actual_top_bottom_sign_validated_in_real_structure":False})
 expected=len(solutions)*sum(len(c) for c in need.values())//len(need)*len(shellcells)*4
 require(len(out)==expected,"slab panel/face/combination coverage mismatch")
 gov=max(out,key=lambda q:q["design_moment_WoodArmer_assumed_kNm_m"])
 count=sum(r["bending"]["isolated_flexure_ok"] for r in out)
 shearcount=sum(r["transverse_shear"]["isolated_transverse_shear_ok"] for r in out)
 bench=published_oneway_benchmark()
 return {"schema":SCHEMA,"source_SHA256":solved["source_SHA256"],
  "original_source":"HYPOTHETICAL_R6P23_SHELLMITC4_NOT_NARAYANI",
  "FE_section_response":"ShellMITC4 stresses: 4 Gauss x [p11,p22,p12,m11,m22,m12,q1,q2]",
  "FE_section_force_units":"kN.m/m plate moments and kN/m shear resultants",
  "local_axes":"CCW horizontal cells local 1 +global X, local 2 +global Y",
  "torsion_adjustment":"WoodArmer-style Mii +/- |M12| at each Gauss, design face convention assumed",
  "combination_kind":"SYNTHETIC_ULS_1.2DL_1.5LL_plusminus_DIAGNOSTIC_HX_NOT_CODE_COMPLETE",
  "section":s,"rows_count":len(out),"shell_cells":len(shellcells),
  "gauss_per_cell":4,"rows":out,"governing_example":gov,
  "flexure_screen_ok":count,"transverse_shear_screen_ok":shearcount,
  "published_oneway_nptel_benchmark":bench,
  "opening_cells_excluded":True,"complete_crackwidth_deflection_checked":False,
  "support_strip_rebar_curtailment_development_verified":False,
  "actual_project_slab_geometry_and_rebar_verified":False,
  "engineering_approval":False}
