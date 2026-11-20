"""Source-constrained *trial*, not issued design: Narayani footing F3.

Original structural report p61 explicitly NOT SAFE IN ONE WAY SHEAR.
This module does not change original observations/drawings and does not
approve seismic/overturning/eccentric foundation behaviour.
The source supports P=571kN, square 2.1m, column .36m, M20 Fe500,
existing 450mm adopted depth, 12mm @150; conservative 160kPa soil.
Revised uniform depth 550mm is a SEPARATE proposed design study.
"""
from __future__ import annotations
import math
SCHEMA="jp.sar.f3.trial_concentric_revision.v1"
ARCHIVE="https://drive.google.com/drive/folders/1qX-FJkPw8p9EF1yINTcPf5kAMxJIMJzU"
SOURCE_REPORT="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
SOURCE_DRAWING="https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
SOURCE_SOIL="https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"
TAU_M20_PT=(.15,.25,.50,.75,1.,1.25,1.5,1.75,2.,2.25,2.5,2.75,3.)
TAU_M20_TC=(.28,.36,.48,.56,.62,.67,.72,.75,.79,.81,.82,.82,.82)
def tau_c_M20(percent):
 if percent<=TAU_M20_PT[0]:return TAU_M20_TC[0]
 if percent>=TAU_M20_PT[-1]:return TAU_M20_TC[-1]
 for i in range(1,len(TAU_M20_PT)):
  if percent<=TAU_M20_PT[i]:
   f=(percent-TAU_M20_PT[i-1])/(TAU_M20_PT[i]-TAU_M20_PT[i-1])
   return TAU_M20_TC[i-1]+f*(TAU_M20_TC[i]-TAU_M20_TC[i-1])
 raise AssertionError("M20 shear lookup missing")
def trial(B_m=2.1,D_m=.55,cover_mm=50.,P_kN=571.,soil_allow_kPa=160.,
          bars_mm=12.,spacing_mm=150.):
 values=(B_m,D_m,cover_mm,P_kN,soil_allow_kPa,bars_mm,spacing_mm)
 if not all(math.isfinite(float(x)) and x>0 for x in values):
  raise ValueError("All input physical parameters must be finite positive")
 if B_m<=.36 or D_m<=0 or cover_mm>=D_m*1000-1.5*bars_mm:
  raise ValueError("Invalid column projection or effective depth")
 area=B_m**2;projection=(B_m-.36)/2.
 effective_mm=D_m*1000-cover_mm-1.5*bars_mm
 effective_m=effective_mm/1000.
 q_u=1.5*P_kN/area
 q_gross=(P_kN+area*D_m*20.)/area
 vs=max(0.,q_u*(projection-effective_m))
 tau_one=vs/(effective_m*1000)
 Ast=math.pi*bars_mm**2/4*1000/spacing_mm
 pt=100*Ast/(1000*effective_mm)
 tauc=tau_c_M20(pt)
 punch_side=.36+effective_m
 v_punch=q_u*max(0.,area-min(area,punch_side**2))
 punch_t=v_punch/(4*punch_side*effective_m*1000)
 punch_max=.25*math.sqrt(20.)
 m_u=q_u*projection**2/2.
 xu=.87*500*Ast/(.36*20*1000.)
 m_res=.87*500*Ast*(effective_mm-.42*xu)/1e6
 min_steel=.0012*1000*D_m*1000
 # Simple straight anchorage length estimate only, IS456 26.2.1.
 # Does not resolve bend/dowel or slab congestion at physical F3.
 Ld=.87*500*bars_mm/(4*(1.2*1.6))
 available=projection*1000-cover_mm
 direct_bearing=1.5*P_kN/(.36*.36*1000.)
 e_axis=(soil_allow_kPa/q_gross-1)*B_m/6
 flags={
  "soil_concentric":q_gross<=soil_allow_kPa,
  "source_report_tau_0p20":tau_one<=.20,
  "IS456_table19_oneway":tau_one<=tauc,
  "two_way_punching":punch_t<=punch_max,
  "bending":m_res>=m_u and xu<=.46*effective_mm,
  "minimum_steel":Ast>=min_steel,
  "straight_bar_anchorage_screen":available>=Ld,
  "direct_column_bearing":direct_bearing<=.45*20.,
 }
 return {
  "footing_B_m":B_m,"uniform_thickness_m":D_m,"assumed_cover_mm":cover_mm,
  "assumed_bar_mm":bars_mm,"assumed_spacing_mm":spacing_mm,
  "source_P_service_kN":P_kN,"column_side_m":.36,
  "effective_depth_upper_layer_mm":effective_mm,
  "original_source_footing_geometry":"SLOPED_FOOTING_AS_DRAWN",
  "this_trial_geometry":"UNIFORM_DEPTH_NEW_ALTERNATIVE",
  "gross_service_concentric_soil_pressure_kPa":q_gross,
  "source_conservative_allowable_soil_kPa":soil_allow_kPa,
  "net_factored_concentric_pressure_kPa":q_u,
  "oneway_tau_v_MPa":tau_one,"oneway_tau_conservative_source_limit_MPa":.20,
  "oneway_tau_c_M20_IS456_table19_MPa":tauc,
  "punching_tau_MPa":punch_t,"punching_tau_allow_MPa":punch_max,
  "bending_Mu_kNm_per_m":m_u,"bending_Mr_kNm_per_m":m_res,
  "provided_steel_mm2_per_m":Ast,"minimum_steel_mm2_per_m":min_steel,
  "eccentricity_limit_single_axis_m_if_other_axis_zero":e_axis,
  "eccentricity_limit_both_equal_axes_m":e_axis/2.,
  "straight_development_length_trial_mm":Ld,
  "concentric_check_flags":flags,"listed_concentric_checks_pass":all(flags.values()),
  "actual_Mx_My_Vx_Vy_seismic_combinations_verified":False,
  "actual_footing_survey_and_source_slope_verified":False,
  "soil_settlement_eccentric_stress_verified":False,
  "construction_approval":False,
 }
def study():
 original=trial(D_m=.45)
 proposed=trial(D_m=.55)
 sensitivity=trial(D_m=.55,cover_mm=75)
 alternative=trial(B_m=2.25,D_m=.60)
 if original["concentric_check_flags"]["source_report_tau_0p20"]:
  raise ValueError("Original footing source-adverse screening lost")
 if not all(x["listed_concentric_checks_pass"] for x in (proposed,sensitivity,alternative)):
  raise ValueError("A proposed alternative violates required preliminary checks")
 return {"schema":SCHEMA,
  "original_report_F3_status":"NOT SAFE IN ONE WAY SHEAR",
  "preferred_revision":"2.10 m square, UNIFORM 550 mm, Ø12@150 both directions, preliminary study only",
  "historical_not_safe_preserved":True,
  "approved_for_construction":False,
  "status":"PREFERRED_TRIAL_PASSES_LISTED_CONCENTRIC_SCREENS_ONLY",
  "source_references":{"revised_report_pdf_page61":SOURCE_REPORT,
                       "str02_drawing":SOURCE_DRAWING,
                       "soil_geotech_page21":SOURCE_SOIL},
  "detailed_human_document_archive":ARCHIVE,
  "original_report_adopted_uniform_trial_450mm":original,
  "preferred_uniform_revision_550mm":proposed,
  "cover_75mm_sensitivity_550mm":sensitivity,
  "wider_alternative_2250x600mm":alternative,
  "unresolved_engineering_gates":[
   "actual F3 governing foundation N, Mx, My, Vx, Vy wind+seismic actions",
   "site geometry discrepancy IF3 family 2.1x2.1 versus G1 DXF 1.8x1.8",
   "original sloped foundation versus NEW uniform trial detailing and cover",
   "actual eccentric soil pressure, settlement, sliding and overturning",
   "proper footing one-way d location, punching geometry and column transfer",
   "bar anchorage/dowels, cover, foundation group interactions and structural engineer sign-off"
  ]}
