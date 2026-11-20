"""R6.31 reusable IS456:2000 *isolated rectangular beam* strength screens.

Converts ACTUAL signed R6.23 OpenSees member-end forces to same-case My/Vz
flexure and shear checks. It does not evaluate torsion, biaxial bending,
ductile-earthquake detailing, anchorage, beam-column joints, serviceability,
or a real project. No external library or static substituted FE numbers.

Code (public government-hosted copy):
https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf
- 38.1, Annex G (singly reinforced rectangular beam flexure)
- 26.5.1.1, .5, .6 (beam steel and stirrup limits)
- 40.1-40.4, Tables 19, 20 (beam shear)
kN, kNm, mm, MPa are explicitly converted at every interface.
"""
from __future__ import annotations

import math
from typing import Mapping

SCHEMA = "jp.sar.r6p31.is456_synthetic_beam_strength_screens.v1"
CODE_URL = "https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
CODE_EDITION = "IS 456:2000 (with amendments), illustrative isolated beam checks"
XI_LIMIT = {250.0:0.53, 415.0:0.48, 500.0:0.46}
TABLE19_PT=(0.15,0.25,0.50,0.75,1.0,1.25,1.50,1.75,2.0,2.25,2.5,2.75,3.0)
TABLE19={
 15: (.28,.35,.46,.54,.60,.64,.68,.71,.71,.71,.71,.71,.71),
 20: (.28,.36,.48,.56,.62,.67,.72,.75,.79,.81,.82,.82,.82),
 25: (.29,.36,.49,.57,.64,.70,.74,.78,.82,.85,.88,.90,.92),
 30: (.29,.37,.50,.59,.66,.71,.76,.80,.84,.88,.91,.94,.96),
 35: (.29,.37,.50,.59,.67,.73,.78,.82,.86,.90,.93,.96,.99),
 40: (.30,.38,.51,.60,.68,.74,.79,.84,.88,.92,.95,.98,1.01)
}
TABLE20={15:2.5,20:2.8,25:3.1,30:3.5,35:3.7,40:4.0}
ACTION_NAMES=("N","Vy","Vz","T","My","Mz")
CASES={"U_PLUS":{"DL":1.2,"LL":1.5,"HX":1.0},
       "U_MINUS":{"DL":1.2,"LL":1.5,"HX":-1.0}}
ASSUMED_SECTION={
 "b_mm":300.0, "D_mm":450.0, "d_mm":405.0,
 "fck_MPa":25.0, "fy_long_MPa":500.0,"fy_stirrup_MPa":415.0,
 "longitudinal_bars_each_face":3,"longitudinal_bar_diameter_mm":16.0,
 "stirrup_legs":2,"stirrup_diameter_mm":8.0,"stirrup_spacing_mm":150.0,
 "section_type":"RECTANGULAR",
 "provenance":"SYNTHETIC R6P23; SAME 300x450mm BEAM; ASSUMED EFFECTIVE d AND BOTH FACE BARS",
}

def require(ok,why):
 if not ok:raise ValueError("R6.31 BEAM SCREEN: "+why)

def positive(value,field):
 require(isinstance(value,(int,float)) and not isinstance(value,bool) and
         math.isfinite(float(value)) and float(value)>0,field+" must be finite positive")
 return float(value)

def finite(value,field):
 require(isinstance(value,(int,float)) and not isinstance(value,bool) and
         math.isfinite(float(value)),field+" must be finite")
 return float(value)

def section_basis(section:Mapping)->dict:
 b=positive(section["b_mm"],"b")
 D=positive(section["D_mm"],"D")
 d=positive(section["d_mm"],"d")
 require(d<D,"effective depth must be below overall depth")
 fck=positive(section["fck_MPa"],"fck")
 require(fck in TABLE19,"table 19 concrete grade restricted to M15,M20,M25,M30,M35,M40+")
 fy=positive(section["fy_long_MPa"],"fy_long")
 require(fy in XI_LIMIT,"supported Fe250,Fe415,Fe500 only")
 fys=positive(section["fy_stirrup_MPa"],"fy_stirrup")
 require(fys<=600,"stirrup steel strength outside research bounds")
 n=section["longitudinal_bars_each_face"]
 legs=section["stirrup_legs"]
 require(type(n) is int and n>=2 and type(legs) is int and legs>=2,"bars and stirrup legs integer >=2")
 dia=positive(section["longitudinal_bar_diameter_mm"],"tension_bar_diameter")
 stirrup_dia=positive(section["stirrup_diameter_mm"],"stirrup_diameter")
 spacing=positive(section["stirrup_spacing_mm"],"stirrup_spacing")
 require(section.get("section_type")=="RECTANGULAR","no T/L beam flange handling")
 As=n*math.pi*dia**2/4
 Asv=legs*math.pi*stirrup_dia**2/4
 return dict(b_mm=b,D_mm=D,d_mm=d,fck_MPa=fck,fy_long_MPa=fy,
             fy_stirrup_MPa=fys,longitudinal_bars_each_face=n,
             longitudinal_bar_diameter_mm=dia,As_long_each_face_mm2=As,
             stirrup_legs=legs,stirrup_diameter_mm=stirrup_dia,
             Asv_mm2=Asv,stirrup_spacing_mm=spacing,
             bar_continuity_at_section_verified=False,
             design_scope="SYNTHETIC_RECTANGULAR_BEAM_STRENGTH_ONLY",
             section_type="RECTANGULAR")

def tau_c_table19(fck_MPa:int,pt_percent:float)->float:
 require(fck_MPa in TABLE19,"Table19 concrete grade unsupported")
 pt=positive(pt_percent,"tension reinforcement percentage")
 values=TABLE19[fck_MPa]
 if pt<=TABLE19_PT[0]:return values[0]
 if pt>=TABLE19_PT[-1]:return values[-1]
 for i in range(1,len(TABLE19_PT)):
  x=TABLE19_PT[i];old=TABLE19_PT[i-1]
  if pt<=x:
   return values[i-1]+(pt-old)*(values[i]-values[i-1])/(x-old)
 raise AssertionError("table interpolation incomplete")

def flexure(mu_kNm:float,basis:Mapping)->dict:
 """Singly reinforced *vertical-plane My* flexure using local rectangular b,d."""
 mu=abs(finite(mu_kNm,"Mu"))
 b=basis["b_mm"];d=basis["d_mm"];D=basis["D_mm"]
 fck=basis["fck_MPa"];fy=basis["fy_long_MPa"]
 As=basis["As_long_each_face_mm2"]
 k=XI_LIMIT[fy]
 xu_limit=k*d
 mlim=.36*fck*b*xu_limit*(d-.42*xu_limit)/1e6
 xu=.87*fy*As/(.36*fck*b)
 m_res=.87*fy*As*(d-.42*xu)/1e6 if xu<=xu_limit else None
 min_As=.85*b*d/fy
 max_As=.04*b*D
 coefficient=(.87*fy)**2*.42/(.36*fck*b)
 linear=.87*fy*d
 discr=linear**2-4*coefficient*mu*1e6
 a_req=(linear-math.sqrt(max(0.,discr)))/(2*coefficient) if mu<=mlim+1e-10 and discr>=-1e-6 else None
 a_target=max(min_As,a_req) if a_req is not None else None
 within=(As>=min_As and As<=max_As and xu<=xu_limit)
 ok=(within and m_res is not None and mu<=m_res+1e-8)
 status=("SINGLY_REINFORCED_LIMIT_EXCEEDED" if mu>mlim+1e-8 else
         "PROVIDED_STEEL_OR_NEUTRAL_AXIS_OUTSIDE_LIMITS" if not within else
         "PROVIDED_FLEXURE_BELOW_DEMAND" if not ok else "ISOLATED_FLEXURE_SCREEN_OK")
 return dict(Mu_abs_kNm=mu,Mu_signed_input_kNm=finite(mu_kNm,"signed Mu"),
   Mu_lim_kNm=mlim,Mu_res_provided_kNm=m_res,As_req_flexure_mm2=a_req,
   As_required_including_min_mm2=a_target,As_provided_tension_mm2=As,
   As_min_mm2=min_As,As_max_mm2=max_As,
   xu_provided_mm=xu,xu_max_mm=xu_limit,xu_max_over_d=k,
   provided_isolated_flexure_screen_ok=bool(ok),status=status,
   formula="0.87fy As d (1 - 0.42 xu/d); xu=0.87fy As/(0.36fck b)",
   code=["38.1","Annex G-1.1","26.5.1.1"])

def shear(vu_kN:float,basis:Mapping)->dict:
 """My/Vz conjugate vertical plane only, using signed Vz member-end forces."""
 v=abs(finite(vu_kN,"Vu"))
 b=basis["b_mm"];d=basis["d_mm"];fck=int(basis["fck_MPa"])
 As=basis["As_long_each_face_mm2"]
 pt=100*As/(b*d)
 tau_c=tau_c_table19(fck,pt)
 tau_max=TABLE20[fck]
 tau_v=v*1000/(b*d)
 vc=tau_c*b*d/1000
 vs_required=max(0.,v-vc)
 fys=min(basis["fy_stirrup_MPa"],415.)
 Asv=basis["Asv_mm2"]
 s_min_reinf=.87*fys*Asv/(.4*b)
 s_geom=min(.75*d,300.)
 if vs_required>0:
  s_strength=.87*fys*Asv*d/(vs_required*1000)
 else:s_strength=None
 s_ceiling=min(s_min_reinf,s_geom,s_strength if s_strength is not None else float("inf"))
 spacing=basis["stirrup_spacing_mm"]
 sv_provided=.87*fys*Asv*d/spacing/1000
 resistance=vc+sv_provided
 shear_ok=(tau_v<=tau_max+1e-10 and
           spacing<=s_min_reinf+1e-9 and spacing<=s_geom+1e-9 and
           resistance+1e-9>=v)
 status=("CONCRETE_MAX_SHEAR_STRESS_EXCEEDED" if tau_v>tau_max+1e-10 else
         "SHEAR_STIRRUPS_OR_SPACING_INSUFFICIENT" if not shear_ok else
         "ISOLATED_SHEAR_SCREEN_OK")
 return dict(Vu_signed_input_kN=finite(vu_kN,"signed Vu"),Vu_abs_kN=v,
   tau_v_MPa=tau_v,pt_percent_from_assumed_continuous_tension_bars=pt,
   tau_c_MPa=tau_c,tau_cmax_MPa=tau_max,
   Vc_kN=vc,Vs_required_kN=vs_required,Vs_provided_kN=sv_provided,
   V_capacity_with_assumed_stirrups_kN=resistance,
   fy_stirrup_capped_MPa=fys,Asv_mm2=Asv,
   stirrup_spacing_provided_mm=spacing,
   stirrup_s_limit_min_steel_mm=s_min_reinf,
   stirrup_s_limit_geometry_mm=s_geom,
   stirrup_s_limit_strength_mm=s_strength,
   stirrup_s_upper_bound_mm=s_ceiling,
   provided_isolated_shear_screen_ok=bool(shear_ok),status=status,
   formula="tau_v=Vu/(bd); Vus=Vu-tau_c bd; sv<=0.87fy Asv d/Vus",
   code=["40.1","40.2.1","Table 19","40.2.3","Table 20","40.4","26.5.1.5","26.5.1.6"])

def combined_actions(raw:Mapping,member:str,end:str,factors:Mapping)->dict:
 """Same member+end+case for all six axes; avoid combining unrelated maxima."""
 action={}
 for axis in ACTION_NAMES:
  q=0.
  for case,f in factors.items():
   src=raw[case]["signed_frame_end_actions"][member][end]
   q+=finite(f,"factor")*finite(src[axis],f"{case}.{member}.{end}.{axis}")
  action[axis]=q
 return action

def member_checks_from_preview(preview:Mapping,section:Mapping=ASSUMED_SECTION)->dict:
 """Evaluate every beam end in every actual R6.23 mode and signed U+/U- combination."""
 basis=section_basis(section)
 require(preview["classification"]=="SYNTHETIC_REFERENCE" and preview["engineering_approval"] is False,
         "only synthetic source solves; no physical project adoption")
 require(preview["source_SHA256"] and isinstance(preview["source_SHA256"],str),
         "FE fixture provenance required")
 beam_ids=sorted(x["key"] for x in preview["topology"]["beams"])
 require(len(beam_ids)>0 and len(beam_ids)==len(set(beam_ids)),"beam id count/duplicates")
 modes=sorted(preview["solutions"])
 require(set(modes)=={"FLEXIBLE_SHELL","RIGID_INPLANE_MPC"},"all diaphragm comparison modes required")
 rows=[]
 for mode in modes:
  raw=preview["solutions"][mode]
  for case in ("DL","LL","HX"):
   require(raw[case]["force_moment_balance_pass"] and
           raw[case]["max_equilibrium_residual"]<1e-3,
           "real FE equilibrium for "+mode+" "+case)
   require(set(beam_ids)==set(x for x in raw[case]["signed_frame_end_actions"] if x in beam_ids),
           "beam/FE action membership mismatch")
  for m in beam_ids:
   for end in ("I","J"):
    for combo,fac in CASES.items():
     action=combined_actions(raw,m,end,fac)
     flex=flexure(action["My"],basis)
     sh=shear(action["Vz"],basis)
     rows.append(dict(mode=mode,case=combo,member=m,end=end,
       source_component_pair=["My","Vz"],
       signed_local_actions={k:action[k] for k in ACTION_NAMES},
       flexure=flex,shear=sh,
       unverified_effects={"other_axis_Mz_kNm":action["Mz"],
          "other_axis_Vy_kN":action["Vy"],
          "torsion_T_kNm":action["T"],
          "axial_N_kN":action["N"]},
       professional_approval=False))
 require(len(rows)==len(beam_ids)*2*len(CASES)*len(modes),"every real beam/end/mode/combo must have result")
 control_m=max(rows,key=lambda x:x["flexure"]["Mu_abs_kNm"])
 control_v=max(rows,key=lambda x:x["shear"]["Vu_abs_kN"])
 return {"schema":SCHEMA,
  "source_fixture_sha256":preview["source_SHA256"],
  "source_classification":"SOURCE-HASHED_OPEN_SEES_R6P23_SYNTHETIC_REFERENCE",
  "source_CAD_or_as_built":False,
  "code_reference":CODE_URL,"code_edition":CODE_EDITION,
  "reference":"R6.23 actual signed beam local-end FE outputs, no fake reactions",
  "assumed_section":basis,
  "combination_factors":CASES,
  "limits":{"checked_planes":"local My (vertical bending) + conjugate Vz shear only",
            "local_Mz_Vy_T_N":"recorded, NOT designed",
            "same_case_and_same_end":True,
            "load_combinations":"hypothetical 1.2DL + 1.5LL +/- diagnostic HX; NOT NBC seismic/Uls adopted",
            "end_forces":"member end forces only, not shifted to code d section from face",
            "shear_steel_percent":"assumes longitudinal bars continue beyond section, not verified",
            "seismic_ductile_detailing":"NOT CHECKED",
            "development_and_anchorage":"NOT CHECKED",
            "negative_positive_section_d":"same symmetric 3-16 assumed top and bottom",
            "shear_torsion_interaction":"NOT CHECKED (IS456 Clause41)",
            "serviceability_and_cracking":"NOT CHECKED"},
  "rows_count":len(rows),"beam_count":len(beam_ids),"modes":modes,
  "all_qualifying_beam_end_case_rows":rows,
  "governing_bending_row":control_m,
  "governing_vertical_shear_row":control_v,
  "isolated_screen_flexure_ok_count":sum(x["flexure"]["provided_isolated_flexure_screen_ok"] for x in rows),
  "isolated_screen_shear_ok_count":sum(x["shear"]["provided_isolated_shear_screen_ok"] for x in rows),
  "member_design_complete":False,"code_complete":False,
  "professional_engineering_approval":False,"construction_release":False,
  "original_narayani_F3_NOT_SAFE_retained":True,
  }
