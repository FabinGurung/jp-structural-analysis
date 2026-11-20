"""R6.33 independently inspectable closed-form and quadrature cross-checks.

Does not use OpenSees as a capacity solver or claim verified SP16 charts.
"""
from __future__ import annotations
from r6p30.column_pmm import (
 ASSUMED, _uniaxial_response, steel_area, puz_kN, uniaxial_at_pu
)

SCHEMA="jp.sar.column.pmm_benchmarks.v2"
NPTEL_SOURCE="https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l26.pdf"
NPTEL_REFERENCE={
 "source_author":"IIT Kharagpur, NPTEL, Design of Concrete Structures, Lesson 26, Q.5/A.5",
 "source_section":"10.26.8, Fig. 10.26.6 and answer A.5",
 "chart_reference":"SP16:1980 Charts 44–45 as interpolated in the NPTEL worked answer",
 "b_mm":450.,"D_mm":500.,"fck_MPa":25.,"fy_MPa":415.,
 "bar_d_mm":16.,"bar_count":12,"bar_center_cover_mm":56.,
 "unsupported_height_mm":3200.,"effective_height_mm":3200.,
 "Es_MPa":200000.,
 "Pu_kN":1600.,"Mx_kNm":120.,"My_kNm":100.,
 "published_Mx1_kNm":246.376,
 "published_My1_kNm":215.156,
 "published_Puz_kN":3254.85,
 "published_alpha_n":1.4909,
 "published_interaction":.6612,
 "source_inconsistency":"Figure's introductory Given line says M20, but the formal problem and solved A.5 explicitly use M25. M25 is used only for benchmark.",
 "layout_limitation":"The figure identifies 12 perimeter bars and 56mm centre cover; program assumes equal interior spacing on each face; chart-position equality not independently proved.",
}
def compare_nptel_sp16():
    """Independent published chart interpolation vs our *approximate* FE-free section algorithm."""
    from r6p30.column_pmm import uniaxial_at_pu,puz_kN,alpha_n,steel_area,bar_positions,assess
    r=NPTEL_REFERENCE
    section={k:r[k] for k in ("b_mm","D_mm","fck_MPa","fy_MPa",
        "bar_d_mm","bar_count","bar_center_cover_mm",
        "unsupported_height_mm","effective_height_mm","Es_MPa")}
    # Their Mx corresponds to our depth-D local My; minor My to our depth-b local Mz.
    major=uniaxial_at_pu(r["Pu_kN"],section,"My")
    minor=uniaxial_at_pu(r["Pu_kN"],section,"Mz")
    Mmajor=major["M_uniaxial_capacity_approx_kNm"]
    Mminor=minor["M_uniaxial_capacity_approx_kNm"]
    dmajor=(Mmajor-r["published_Mx1_kNm"])/r["published_Mx1_kNm"]
    dminor=(Mminor-r["published_My1_kNm"])/r["published_My1_kNm"]
    alpha=alpha_n(r["Pu_kN"],puz_kN(section))
    source_formula=(r["Mx_kNm"]/r["published_Mx1_kNm"])**r["published_alpha_n"]+(
          r["My_kNm"]/r["published_My1_kNm"])**r["published_alpha_n"]
    ours=(r["Mx_kNm"]/Mmajor)**alpha+(r["My_kNm"]/Mminor)**alpha
    # Tolerance is for comparison/sensitivity only; not code compliance or safety.
    # Predeclared +/-3% chart-vs-numerical moment deviation for both axes.
    deviation_bound=.03
    close=abs(dmajor)<=deviation_bound and abs(dminor)<=deviation_bound
    if not close:
        raise ValueError("external published SP16 reference outside 3% moment benchmark band")
    if len(bar_positions(section))!=12 or abs(steel_area(section)-2412.743157956961)>1e-7:
        raise ValueError("NPTEL bar geometry mismatch")
    return {
      "schema":"jp.sar.column.nptel_sp16_external_benchmark.v1",
      "reference_url":NPTEL_SOURCE,"reference_section":r["source_section"],
      "source_name":r["source_author"],
      "benchmark_independence":"Published NPTEL interpolation of SP16 Charts 44–45 vs fresh uniaxial fiber computation; no OpenSees calibration",
      "external_source_inputs":r,
      "source_conflict_preserved":r["source_inconsistency"],
      "actual_bar_centres_assumed_not_from_drawn_chart":r["layout_limitation"],
      "assumed_equally_spaced_12_bar_coordinates_mm":bar_positions(section),
      "computed_As_mm2":steel_area(section),
      "computed_Puz_kN":puz_kN(section),
      "computed_alpha":alpha,
      "reference_major_M_kNm":r["published_Mx1_kNm"],
      "reference_minor_M_kNm":r["published_My1_kNm"],
      "our_major_approx_M_kNm":Mmajor,
      "our_minor_approx_M_kNm":Mminor,
      "major_relative_difference":dmajor,
      "minor_relative_difference":dminor,
      "predeclared_acceptance_band_fraction":deviation_bound,
      "both_axes_within_benchmark_band":close,
      "reference_interaction_recomputed_from_published_chart":source_formula,
      "published_reference_interaction_rounded":r["published_interaction"],
      "our_approx_biaxial_interaction":ours,
      "reference_alpha_rounded":r["published_alpha_n"],
      "note":"Comparing our approximate constitutive law to one NPTEL chart-derived example is not certification of SP16 or IS456, no original project engineering approval.",
      "full_SP16_chart_verification":False,"construction_approval":False,
      "source_published_nptel_problem_status":"REFERENCE_SAFE_IN_ITS_OWN_EXAMPLE_ONLY",
    }


def compute():
    nptel=compare_nptel_sp16()
 v=ASSUMED
 key=(v["b_mm"],v["D_mm"],v["fck_MPa"],v["fy_MPa"],
      v["bar_d_mm"],v["bar_center_cover_mm"],v["Es_MPa"])
 ast=steel_area(v)
 ac=v["b_mm"]*v["D_mm"]-ast
 # In uniform axial compression IS456 39.1(a) limits concrete
 # extreme strain to .002. Fe500 at Es=200000 => 400 MPa < .87fy.
 steel_stress=min(v["Es_MPa"]*.002,.87*v["fy_MPa"])
 closed=(.446*v["fck_MPa"]*ac+steel_stress*ast)/1000
 numeric,M=_uniaxial_response(*key,1.e10,"My",n_slices=256)
 error=abs(numeric-closed)/closed
 if not error<.001 or abs(M)>.02:
  raise ValueError("independent 39.1(a) pure axial benchmark failed")
 rows=[]
 for c in (180.,800.,6000.):
  record={"neutral_axis_mm":c,"fully_compressed":c>v["D_mm"],"quadrature":{}}
  for n in (32,64,128):
   p,m=_uniaxial_response(*key,c,"My",n_slices=n)
   record["quadrature"][str(n)]={"P_kN":p,"My_kNm":m}
  p32=record["quadrature"]["32"]["P_kN"]
  p64=record["quadrature"]["64"]["P_kN"]
  p128=record["quadrature"]["128"]["P_kN"]
  record["relative_64_vs_128_P_error"]=abs(p64-p128)/max(1,abs(p128))
  if record["relative_64_vs_128_P_error"]>.003:
   raise ValueError("32/64/128 column compression quadrature not converged")
  rows.append(record)
 high=uniaxial_at_pu(.95*puz_kN(v),v,"My")
 return {
  "schema":SCHEMA,"assumed_model":v,
  "code":"IS456:2000 §§25.4,39.1(a,b),39.5,39.6",
  "closed_form_P_at_uniform_epsilon_0002_kN":closed,
  "numerical_256_strip_P_at_uniform_epsilon_0002_kN":numeric,
  "numerical_pure_compression_moment_residual_kNm":M,
  "steel_stress_at_uniform_epsilon_0002_MPa":steel_stress,
  "relative_pure_axial_error":error,
  "full_compression_95pct_Puz":high,
  "quadrature":rows,
  "external_sp16_nptel_reference":nptel,
  "column_actual_member_sign_from_signed_OpenSees":True,
  "source_independent_benchmark":"analytic uniform strain compression force vs 256-strip integration",
  "sp16_verified":False,"construction_approval":False}
