"""R6.33 independently inspectable closed-form and quadrature cross-checks.

Does not use OpenSees as a capacity solver or claim verified SP16 charts.
"""
from __future__ import annotations
from r6p30.column_pmm import (
 ASSUMED, _uniaxial_response, steel_area, puz_kN, uniaxial_at_pu
)

SCHEMA="jp.sar.column.pmm_benchmarks.v1"

def compute():
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
  "column_actual_member_sign_from_signed_OpenSees":True,
  "source_independent_benchmark":"analytic uniform strain compression force vs 256-strip integration",
  "sp16_verified":False,"construction_approval":False}
