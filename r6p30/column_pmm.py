"""R6.32 — reproducible short-column axial+bending interaction study.

IS 456:2000 §39.6 biaxial interaction exponent, with Mux1/Muy1
estimated from a clearly identified *approximate* strain-compatible
uniaxial rectangular section integration, NOT from SP16 verified charts.

This is a bounded numerical prototype for a wholly synthetic
OpenSeesPy reference fixture, never a signed construction-design check.
"""
from __future__ import annotations
import math
from functools import lru_cache
from typing import Mapping

SCHEMA="jp.sar.r6p33.column_pmm_sign_strain_benchmark.v1"
REFERENCE="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
ASSUMED={"b_mm":400.0,"D_mm":400.0,"fck_MPa":25.0,"fy_MPa":500.0,
         "bar_d_mm":16.0,"bar_count":8,"bar_center_cover_mm":50.0,
         "effective_height_mm":3000.0,"unsupported_height_mm":3000.0,"Es_MPa":200000.0}
FACTORS={"U_PLUS":{"DL":1.2,"LL":1.5,"HX":1.0},
         "U_MINUS":{"DL":1.2,"LL":1.5,"HX":-1.0}}

def require(condition,message):
 if not condition:raise ValueError("R6.32 PMM: "+message)

def _finite(v,name):
 require(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v),name+" is not finite")
 return float(v)

def validate(s:Mapping)->dict:
 required=("b_mm","D_mm","fck_MPa","fy_MPa","bar_d_mm","bar_center_cover_mm",
           "effective_height_mm","unsupported_height_mm","Es_MPa")
 x={k:_finite(s[k],k) for k in required}
 for k,v in x.items():require(v>0,k+" must be positive")
 n=s["bar_count"];require(type(n) is int and n==8,"fixed 8-bar perimeter model only")
 require(x["b_mm"]>2*x["bar_center_cover_mm"] and
         x["D_mm"]>2*x["bar_center_cover_mm"],"bar centres outside section")
 require(x["bar_d_mm"]<2*x["bar_center_cover_mm"],"bar geometry inconsistent")
 require(x["fy_MPa"] in (415,500),"only Fe415/Fe500 prototype tested")
 require(x["effective_height_mm"]/x["b_mm"]<12 and x["effective_height_mm"]/x["D_mm"]<12,
         "slender column requires second-order effects, not this short-column screen")
 require(.008<=n*math.pi*x["bar_d_mm"]**2/(4*x["b_mm"]*x["D_mm"])<=.06,
         "longitudinal steel ratio outside 0.8% to 6%")
 return {**x,"bar_count":n}

def bar_positions(s:Mapping)->list[tuple[float,float]]:
 v=validate(s)
 x=v["b_mm"]/2-v["bar_center_cover_mm"]
 y=v["D_mm"]/2-v["bar_center_cover_mm"]
 return [(-x,-y),(0.,-y),(x,-y),(x,0.),(x,y),(0.,y),(-x,y),(-x,0.)]

def steel_area(s:Mapping)->float:
 v=validate(s)
 return v["bar_count"]*math.pi*v["bar_d_mm"]**2/4

def puz_kN(s:Mapping)->float:
 """IS456 §39.6 nominal reference Puz for biaxial exponent."""
 v=validate(s)
 ast=steel_area(v)
 ag=v["b_mm"]*v["D_mm"]
 return (.45*v["fck_MPa"]*(ag-ast)+.75*v["fy_MPa"]*ast)/1000.

def alpha_n(p_kN:float,puz:float)->float:
 ratio=max(0.,_finite(p_kN,"P"))/_finite(puz,"Puz")
 require(puz>0,"invalid Puz")
 if ratio<=.2:return 1.0
 if ratio>=.8:return 2.0
 return 1+(ratio-.2)/.6

def _steel_stress(epsilon:float,s:Mapping)->float:
 return max(-.87*s["fy_MPa"],min(.87*s["fy_MPa"],s["Es_MPa"]*epsilon))

def _concrete_stress(epsilon:float,s:Mapping)->float:
 """Simplified IS456 design parabola-rectangle, compression positive."""
 if epsilon<=0:return 0.
 if epsilon>=.002:return .446*s["fck_MPa"]
 u=epsilon/.002
 return .446*s["fck_MPa"]*(2*u-u*u)

@lru_cache(maxsize=80000)
def _uniaxial_response(b:float,D:float,fck:float,fy:float,bar_d:float,
                      cover:float,Es:float,c_mm:float,axis:str,n_slices:int=64)->tuple[float,float]:
 """Return axial kN, uniaxial moment kNm for a plane-section curvature.

 Uniform concrete fibers across the orthogonal width. Steel forces replace
 displaced concrete stress at the bar centroid. Biaxiality is evaluated by
 separately determined uniaxial moment strengths at the same axial load,
 as in the IS456 39.6 load-contour method.
 """
 s={"b_mm":b,"D_mm":D,"fck_MPa":fck,"fy_MPa":fy,
    "bar_d_mm":bar_d,"bar_count":8,"bar_center_cover_mm":cover,
    "effective_height_mm":3000.,"unsupported_height_mm":3000.,"Es_MPa":Es}
 require(axis in ("My","Mz"),"unsupported axis")
 depth=D if axis=="My" else b
 width=b if axis=="My" else D
 edge=depth/2
 area=width*depth/n_slices
 P=M=0.
 for i in range(n_slices):
  u=-edge+(i+.5)*depth/n_slices
  compression_edge_strain=.0035 if c_mm<=depth else .0035/(1+.75*(1-depth/c_mm))
  strain=compression_edge_strain*(1-(edge-u)/c_mm)
  stress=_concrete_stress(strain,s)
  F=stress*area
  P+=F;M+=F*u
 a=math.pi*bar_d**2/4
 for x,y in bar_positions(s):
  u=y if axis=="My" else x
  strain=compression_edge_strain*(1-(edge-u)/c_mm)
  delta=a*(_steel_stress(strain,s)-_concrete_stress(strain,s))
  P+=delta;M+=delta*u
 return P/1000.,abs(M)/1e6

def uniaxial_at_pu(p_kN:float,section:Mapping,axis:str)->dict:
 """Bisection of source axial load with physically transparent strain plane."""
 s=validate(section)
 p=_finite(p_kN,"axial")
 require(p>=0,"this compression-only screen excludes tensile axial load")
 pmax=puz_kN(s)
 require(p<=pmax,"axial compression beyond Puz reference; reject rather than invent M capacity")
 key=(s["b_mm"],s["D_mm"],s["fck_MPa"],s["fy_MPa"],s["bar_d_mm"],
      s["bar_center_cover_mm"],s["Es_MPa"])
 def response(c):return _uniaxial_response(*key,c,axis)
 lo=.1;hi=1e8
 Plo,_=response(lo);Phi,_=response(hi)
 require(Plo<=p<=Phi+1e-6,"moment capacity not bracketed by section strains")
 for _ in range(65):
  mid=(lo+hi)/2
  Pmid,_=response(mid)
  if Pmid<p:lo=mid
  else:hi=mid
 c=(lo+hi)/2
 force,moment=response(c)
 require(abs(force-p)<max(.002,p*.000002),"section force did not equilibrate")
 return {"P_reconstructed_kN":force,"neutral_axis_depth_mm":c,
         "M_uniaxial_capacity_approx_kNm":moment,
         "section_method":"1D_64_STRIPS_IS456_39_1A_B_CONDITIONAL_STRAIN_NOT_SP16",
         "compression_regime":"ALL_COMPRESSED" if c>(s["D_mm"] if axis=="My" else s["b_mm"]) else "TENSION_ZONE",
         "epsilon_max":.0035 if c <= (s["D_mm"] if axis=="My" else s["b_mm"]) else
              .0035/(1+.75*(1-(s["D_mm"] if axis=="My" else s["b_mm"])/c))}

def assess(Pu_kN:float,My_kNm:float,Mz_kNm:float,
           section:Mapping=ASSUMED)->dict:
 s=validate(section)
 p=_finite(Pu_kN,"P");my=_finite(My_kNm,"My");mz=_finite(Mz_kNm,"Mz")
 require(p>=0,"compression-only")
 puz=puz_kN(s)
 alpha=alpha_n(p,puz)
 limits={"Mx":uniaxial_at_pu(p,s,"Mz"),
         "My":uniaxial_at_pu(p,s,"My")} if p<=puz else None
 # OpenSees local frame My & Mz are recorded unchanged. Axis labels here
 # follow local bending components, not global structural coordinates.
 # IS456 25.4 uses UNSUPPORTED length, and permits min eccentricity
 # about one axis at a time. Two alternatives: evaluate and govern by worse.
 ey=max(s["unsupported_height_mm"]/500+s["D_mm"]/30,20.)
 ez=max(s["unsupported_height_mm"]/500+s["b_mm"]/30,20.)
 demand_options=[
     (max(abs(my),p*ey/1000),abs(mz)),
     (abs(my),max(abs(mz),p*ez/1000))
 ]
 mcap_y=limits["My"]["M_uniaxial_capacity_approx_kNm"] if limits else None
 mcap_z=limits["Mx"]["M_uniaxial_capacity_approx_kNm"] if limits else None
 def utilization_of(my_design,mz_design):
  return ((my_design/mcap_y)**alpha if mcap_y and mcap_y>0 else float("inf"))+(
          (mz_design/mcap_z)**alpha if mcap_z and mcap_z>0 else float("inf"))
 candidate_utilizations=[utilization_of(*x) for x in demand_options]
 controlling_idx=max(range(2),key=lambda ix:candidate_utilizations[ix])
 demand_my,demand_mz=demand_options[controlling_idx]
 utilization=candidate_utilizations[controlling_idx]
 ok=p<=puz and utilization<=1.0
 return {"Pu_assumed_compression_kN":p,"signed_local_My_kNm":my,
         "signed_local_Mz_kNm":mz,"Puz_IS456_kN":puz,
         "Pu_over_Puz":p/puz,"biaxial_exponent_alpha":alpha,
         "minimum_eccentricity_y_mm":ey,"minimum_eccentricity_z_mm":ez,
         "minimum_eccentricity_rule":"ONE_AXIS_AT_A_TIME_WORST_ALTERNATIVE_IS456_25_4",
         "minimum_eccentricity_candidate_utilizations":candidate_utilizations,
         "minimum_eccentricity_governing":"MIN_MY" if controlling_idx==0 else "MIN_MZ",
         "My_effective_demand_kNm":demand_my,"Mz_effective_demand_kNm":demand_mz,
         "My1_approx_capacity_kNm":mcap_y,"Mz1_approx_capacity_kNm":mcap_z,
         "uniaxial_solutions":limits,"biaxial_load_contour_utilization":utilization,
         "isolated_PMM_approx_screen_ok":bool(ok),
         "status":"APPROX_SECTION_SCREEN_OK_NOT_APPROVED" if ok else
                  "APPROX_SECTION_SCREEN_DEMAND_EXCEEDS_CAPACITY",
         "global_code_compliance":False,"engineering_approval":False}

def signed_actions(raw:Mapping,member:str,end:str,factors:Mapping)->dict:
 components=("N","Vy","Vz","T","My","Mz")
 return {k:sum(_finite(raw[c]["signed_frame_end_actions"][member][end][k],k)
               *float(f) for c,f in factors.items()) for k in components}

def column_checks_from_preview(preview:Mapping,section:Mapping=ASSUMED)->dict:
 require(preview["classification"]=="SYNTHETIC_REFERENCE" and
         preview["engineering_approval"] is False,"only source-hashed synthetic FE records")
 col_ids=sorted(x["key"] for x in preview["topology"]["columns"])
 require(len(col_ids)==8,"benchmark column connectivity unexpectedly changed")
 modes=sorted(preview["solutions"])
 require(set(modes)=={"FLEXIBLE_SHELL","RIGID_INPLANE_MPC"},"all modes required")
 rows=[]
 for mode in modes:
  raw=preview["solutions"][mode]
  for case in ("DL","LL","HX"):
   require(raw[case]["force_moment_balance_pass"] and
           raw[case]["max_equilibrium_residual"]<.001,
           "non-equilibrated OpenSees input")
  for key in col_ids:
   for end in ("I","J"):
    for name,factors in FACTORS.items():
     a=signed_actions(raw,key,end,factors)
     # OpenSees localForce is the internal nodal end-force vector.
     # For vertical +local-x member from bottom I to top J,
     # compression is +N_i and -N_j; never abs() a tension action.
     compression=a["N"] if end=="I" else -a["N"]
     if compression>0:
      q=assess(compression,a["My"],a["Mz"],section)
     else:
      q={"status":"AXIAL_TENSION_NOT_SCREENED",
         "Pu_assumed_compression_kN":None,
         "biaxial_load_contour_utilization":None,
         "isolated_PMM_approx_screen_ok":False,
         "engineering_approval":False}
     rows.append({"diaphragm":mode,"member":key,"end":end,
                  "combination":name,"signed_local_actions":a,
                  "compression_signed_kN":compression,
                  "axial_sign_interpretation":"LOCAL_I_PLUS_J_MINUS_COMPRESSIVE_TENSION_EXCLUDED",
                  "PMM":q})
 require(len(rows)==64,"expected 8×2×2×2 synthetic column checks")
 evaluated=[x for x in rows if x["PMM"]["biaxial_load_contour_utilization"] is not None]
 require(evaluated,"no compression member-end records to screen")
 critical=max(evaluated,key=lambda x:x["PMM"]["biaxial_load_contour_utilization"])
 return {"schema":SCHEMA,"assumed_section":validate(section),
         "source_SHA256":preview["source_SHA256"],
         "compression_axis_assumption":"localForce I N positive, J N negative => compression for local+x vertical column; tension never screened as compression",
         "axial_tension_rows_excluded":len(rows)-len(evaluated),
         "signed_n_convention_source":"OpenSees elasticBeamColumn localForce resisting element end nodal forces",
         "source_scope":"hypothetical 4x4m R6P23 OpenSees model; 1.2DL+1.5LL±HX is a DIAGNOSTIC, not NBC seismic design",
         "model_use":"IS456 §39.6 approximate contour; 39.1(a,b) conditional strain; 25.4 min eccentricity one-axis-at-a-time; NOT SP16-verified",
         "bars":bar_positions(section),"As_total_mm2":steel_area(section),
         "col_count":8,"row_count":len(rows),
         "rows":rows,"governing_example":critical,
         "approx_screen_ok_count":sum(x["PMM"]["isolated_PMM_approx_screen_ok"] for x in rows),
         "code_compliant_project_design":False,
         "ductile_confinement_and_tie_design_complete":False,
         "slenderness_and_second_order_effects_checked":False,
         "bi_axial_PMM_interaction_exact_sp16_verified":False,
         "short_column_slenderness_input_screened":True,
         "longitudinal_steel_ratio_screened":True,
         "local_column_I_J_force_sign_reviewed_on_fixture":True,
         "engineering_approval":False,"construction_release":False,
         "original_narayani_F3_not_safe_preserved":True}
