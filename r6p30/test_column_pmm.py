"""R6.32 P-M-M independently reproducible numerical benchmarks."""
import math
import pytest
from r6p30.column_pmm import (ASSUMED,validate,steel_area,bar_positions,puz_kN,
    alpha_n,_concrete_stress,_steel_stress,_uniaxial_response,uniaxial_at_pu,assess,
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
 assert q["Mz_effective_demand_kNm"]==pytest.approx(0.)
 assert q["minimum_eccentricity_rule"]=="ONE_AXIS_AT_A_TIME_WORST_ALTERNATIVE_IS456_25_4"
 assert len(q["minimum_eccentricity_candidate_utilizations"])==2
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
 assert row["axial_sign_interpretation"].startswith("LOCAL_I_PLUS_J_MINUS")
 joint=next(x for x in result["rows"] if x["member"]=="C:TEST:0"
     and x["end"]=="J" and x["combination"]=="U_PLUS")
 assert joint["signed_local_actions"]["N"]==pytest.approx(-126)
 assert joint["compression_signed_kN"]==pytest.approx(126)
 assert joint["PMM"]["Pu_assumed_compression_kN"]==pytest.approx(126)
 assert result["axial_tension_rows_excluded"]==0


def test_is456_39_1_full_compression_strain_pivot_and_axial_limit():
  s=ASSUMED
  kw=(s["b_mm"],s["D_mm"],s["fck_MPa"],s["fy_MPa"],s["bar_d_mm"],
      s["bar_center_cover_mm"],s["Es_MPa"])
  # At neutral axis >> section depth: all compressed and extreme epsilon
  # tends to .002 as IS456 39.1(a), not .0035 (old defective assumption).
  top=.0035/(1+.75*(1-s["D_mm"]/1.e10))
  assert top==pytest.approx(.002,rel=.000001)
  p,m=_uniaxial_response(*kw,1.e10,"My",n_slices=256)
  Ac=s["b_mm"]*s["D_mm"]-steel_area(s)
  estimated=(.446*s["fck_MPa"]*Ac+min(.87*s["fy_MPa"],s["Es_MPa"]*.002)*steel_area(s))/1000.
  # At epsilon=.002 Fe500 steel is at 400 MPa (Es*epsilon), below .87fy=435 MPa.
  # Do NOT assume a fully plastic compression bar where strain cannot develop it.
  assert p==pytest.approx(estimated,rel=.001)
  assert m==pytest.approx(0.,abs=.01)
  # 39.1(b) wholly compressed must have strain_top below .0035
  full=uniaxial_at_pu(.95*puz_kN(s),s,"My")
  assert full["compression_regime"] in ("ALL_COMPRESSED","TENSION_ZONE")
  if full["compression_regime"]=="ALL_COMPRESSED":
    assert .002<=full["epsilon_max"]<.0035
  assert full["section_method"].endswith("NOT_SP16")

def test_section_numerical_quadrature_converges_and_symmetry_preserved():
  s=ASSUMED
  args=(s["b_mm"],s["D_mm"],s["fck_MPa"],s["fy_MPa"],s["bar_d_mm"],
        s["bar_center_cover_mm"],s["Es_MPa"])
  for neutral_axis in (180.,800.,6000.):
    p32,m32=_uniaxial_response(*args,neutral_axis,"My",n_slices=32)
    p64,m64=_uniaxial_response(*args,neutral_axis,"My",n_slices=64)
    p128,m128=_uniaxial_response(*args,neutral_axis,"My",n_slices=128)
    assert abs(p64-p128)<=abs(p32-p128)+.0002
    assert abs(m64-m128)<=abs(m32-m128)+.0002
    assert abs(p64-p128)/max(1,abs(p128))<.001
    assert abs(m64-m128)/max(1,abs(m128))<.003
    py,my=_uniaxial_response(*args,neutral_axis,"Mz",n_slices=128)
    assert py==pytest.approx(p128,abs=.001)
    assert my==pytest.approx(m128,abs=.001)

def test_open_sees_signed_tensile_axial_force_is_never_misclassified_compression():
  cols=[{"key":"C:T:"+str(i)} for i in range(8)]
  # In a tensile member N_i is negative and N_j positive.
  ends={"I":{"N":-20.,"My":3.,"Mz":4.,"Vy":0.,"Vz":0.,"T":0.},
        "J":{"N":20.,"My":-3.,"Mz":-4.,"Vy":0.,"Vz":0.,"T":0.}}
  def cases(n):
    return {"force_moment_balance_pass":True,"max_equilibrium_residual":0.,
      "signed_frame_end_actions":{
        c["key"]:ends if i==0 else {
          "I":{**ends["I"],"N":80.},"J":{**ends["J"],"N":-80.}
        } for i,c in enumerate(cols)}}
  raw={"DL":cases(0),"LL":cases(1),"HX":cases(2)}
  source={"source_SHA256":"test","classification":"SYNTHETIC_REFERENCE",
          "engineering_approval":False,"topology":{"columns":cols},
          "solutions":{"FLEXIBLE_SHELL":raw,"RIGID_INPLANE_MPC":raw}}
  z=column_checks_from_preview(source)
  tensile=[x for x in z["rows"] if x["member"]=="C:T:0"]
  assert len(tensile)==8
  assert z["axial_tension_rows_excluded"]==8
  assert all(t["PMM"]["status"]=="AXIAL_TENSION_NOT_SCREENED" for t in tensile)
  assert all(t["PMM"]["biaxial_load_contour_utilization"] is None for t in tensile)

def test_slender_or_underreinforced_columns_do_not_receive_short_pmm_approval():
  for update in ({"effective_height_mm":5000},{"bar_d_mm":10},
                 {"unsupported_height_mm":-10}):
    with pytest.raises(ValueError):
      validate({**ASSUMED,**update})
