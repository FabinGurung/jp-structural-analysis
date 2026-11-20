"""R6.32 P-M-M independently reproducible numerical benchmarks."""
import math
import pytest
from r6p30.column_pmm import (ASSUMED,validate,steel_area,bar_positions,puz_kN,
    alpha_n,_concrete_stress,_steel_stress,uniaxial_at_pu,assess,
    column_checks_from_preview,FACTORS)
def test_section_and_code_reference_axial_puz():
 a=ASSUMED
 assert len(bar_positions(a))==8
 assert len(set(bar_positions(a)))==8
 assert steel_area(a)==pytest.approx(8*math.pi*16**2/4)
 ag=400*400;Ast=steel_area(a)
 assert puz_kN(a)==pytest.approx((.45*25*(ag-Ast)+.75*500*Ast)/1000)
 assert .8 < Ast/ag*100 < 6.0 # IS456 column steel general range only
 for wrong in ({"bar_count":4},{"bar_d_mm":-4},{"D_mm":90},{"fy_MPa":550}):
  s={**a,**wrong}
  with pytest.raises(ValueError):validate(s)
def test_alpha_from_code_axial_fraction_and_min_eccentricity():
 puz=puz_kN(ASSUMED)
 for r,v in ((0,1),(.2,1),(.5,1.5),(.8,2),(1,2)):
  assert alpha_n(r*puz,puz)==pytest.approx(v)
 q=assess(.5*puz,0,0)
 assert q["minimum_eccentricity_y_mm"]==20
 assert q["minimum_eccentricity_z_mm"]==20
 assert q["My_effective_demand_kNm"]==pytest.approx(.5*puz*.02)
 assert q["Mz_effective_demand_kNm"]==pytest.approx(.5*puz*.02)
 assert q["biaxial_exponent_alpha"]==pytest.approx(1.5)
 assert not q["engineering_approval"] and not q["global_code_compliance"]
def test_material_stress_law_and_biaxial_symmetry():
 assert _concrete_stress(-.001,ASSUMED)==0
 assert _concrete_stress(0,ASSUMED)==0
 assert _concrete_stress(.001,ASSUMED)==pytest.approx(.446*25*.75)
 assert _concrete_stress(.004,ASSUMED)==pytest.approx(.446*25)
 assert _steel_stress(1,ASSUMED)==pytest.approx(.87*500)
 assert _steel_stress(-1,ASSUMED)==pytest.approx(-.87*500)
 for p in (0.,300.,900.):
  ay=uniaxial_at_pu(p,ASSUMED,"My")
  az=uniaxial_at_pu(p,ASSUMED,"Mz")
  assert ay["P_reconstructed_kN"]==pytest.approx(p,abs=.002)
  assert az["P_reconstructed_kN"]==pytest.approx(p,abs=.002)
  assert ay["M_uniaxial_capacity_approx_kNm"]>0
  assert ay["M_uniaxial_capacity_approx_kNm"]==pytest.approx(
      az["M_uniaxial_capacity_approx_kNm"],rel=1e-8)
def test_biaxial_interaction_monotonic_demand_and_explicit_failure():
 p=500.
 zero=assess(p,0.,0.)
 low=assess(p,20.,15.)
 high=assess(p,1000.,900.)
 assert zero["biaxial_load_contour_utilization"]<=low["biaxial_load_contour_utilization"]
 assert low["biaxial_load_contour_utilization"]<high["biaxial_load_contour_utilization"]
 assert not high["isolated_PMM_approx_screen_ok"]
 assert high["status"]=="APPROX_SECTION_SCREEN_DEMAND_EXCEEDS_CAPACITY"
 assert zero["isolated_PMM_approx_screen_ok"]
 assert zero["uniaxial_solutions"]["My"]["P_reconstructed_kN"]==pytest.approx(p,abs=.002)
 with pytest.raises(ValueError):assess(-1,0,0)
 with pytest.raises(ValueError):uniaxial_at_pu(1.05*puz_kN(ASSUMED),ASSUMED,"My")
def test_source_synthetic_64_paired_actions_and_original_flags():
 cols=[{"key":"C:TEST:"+str(i)} for i in range(8)]
 def case(P,My,Mz):
  a={"N":P,"Vy":0.,"Vz":0.,"T":0.,"My":My,"Mz":Mz}
  return {"force_moment_balance_pass":True,"max_equilibrium_residual":0.,
    "signed_frame_end_actions":{
      col["key"]:{"I":a,"J":{**a,"N":-P,"My":-My,"Mz":-Mz}} for col in cols}}
 raw={"DL":case(80,4,5),"LL":case(20,1,2),"HX":case(0,2,-3)}
 preview={"source_SHA256":"fake-test-only","classification":"SYNTHETIC_REFERENCE",
          "engineering_approval":False,"topology":{"columns":cols},
          "solutions":{"FLEXIBLE_SHELL":raw,"RIGID_INPLANE_MPC":raw}}
 result=column_checks_from_preview(preview)
 assert result["col_count"]==8 and result["row_count"]==64
 assert result["original_narayani_F3_not_safe_preserved"]
 assert not result["construction_release"]
 assert result["approx_screen_ok_count"]<=64
 row=next(x for x in result["rows"] if x["member"]=="C:TEST:0"
     and x["end"]=="I" and x["combination"]=="U_PLUS")
 assert row["signed_local_actions"]["N"]==pytest.approx(126)
 assert row["signed_local_actions"]["My"]==pytest.approx(8.3)
 assert row["signed_local_actions"]["Mz"]==pytest.approx(6)
 assert row["PMM"]["Pu_assumed_compression_kN"]==pytest.approx(126)
 assert row["axial_sign_interpretation"].startswith("ABS_SIGNED")
