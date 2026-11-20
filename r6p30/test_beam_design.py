"""R6.31 independent equations + same-case OpenSees action-pair regression."""
import copy,math
import pytest
from r6p30.beam_design import (ASSUMED_SECTION,CASES,section_basis,tau_c_table19,
                             flexure,shear,combined_actions,member_checks_from_preview)

def setup():
 return section_basis(ASSUMED_SECTION)

def test_is456_table19_exact_nodes_and_linear_interpolation():
 assert tau_c_table19(25,.15)==pytest.approx(.29)
 assert tau_c_table19(25,.25)==pytest.approx(.36)
 assert tau_c_table19(25,.5)==pytest.approx(.49)
 assert tau_c_table19(25,.375)==pytest.approx(.425)
 assert tau_c_table19(25,2.0)==pytest.approx(.82)
 assert tau_c_table19(25,5)==pytest.approx(.92)
 assert tau_c_table19(20,.25)==pytest.approx(.36)
 assert tau_c_table19(30,.75)==pytest.approx(.59)
 assert tau_c_table19(40,3.0)==pytest.approx(1.01)
 with pytest.raises(ValueError):tau_c_table19(17,.5)
 with pytest.raises(ValueError):tau_c_table19(25,float("nan"))

def test_exact_singly_reinforced_beam_algebra_and_steel_limits():
 b=setup(); a=b["As_long_each_face_mm2"]
 assert a==pytest.approx(3*math.pi*16**2/4)
 assert b["Asv_mm2"]==pytest.approx(2*math.pi*8**2/4)
 x=flexure(50,b)
 assert x["Mu_lim_kNm"]==pytest.approx(164.3555,rel=1e-4)
 assert x["Mu_res_provided_kNm"]==pytest.approx(95.5568292636,rel=1e-8)
 assert x["As_min_mm2"]==pytest.approx(206.55)
 assert x["As_max_mm2"]==pytest.approx(5400)
 assert x["As_req_flexure_mm2"]==pytest.approx(298.71745346,abs=1e-5)
 assert x["provided_isolated_flexure_screen_ok"]
 assert flexure(-50,b)["Mu_abs_kNm"]==50.0
 assert flexure(0,b)["As_required_including_min_mm2"]==pytest.approx(206.55)

def test_flexure_fail_demand_and_overlimit_without_false_pass():
 b=setup()
 p=flexure(120,b)
 assert p["Mu_lim_kNm"]>120
 assert not p["provided_isolated_flexure_screen_ok"]
 assert p["status"]=="PROVIDED_FLEXURE_BELOW_DEMAND"
 high=flexure(200,b)
 assert high["Mu_lim_kNm"]<200
 assert high["As_req_flexure_mm2"] is None
 assert high["status"]=="SINGLY_REINFORCED_LIMIT_EXCEEDED"
 low=copy.deepcopy(ASSUMED_SECTION)
 low["longitudinal_bars_each_face"]=2;low["longitudinal_bar_diameter_mm"]=6
 actual=flexure(0,section_basis(low))
 assert not actual["provided_isolated_flexure_screen_ok"]
 assert actual["status"]=="PROVIDED_STEEL_OR_NEUTRAL_AXIS_OUTSIDE_LIMITS"

def test_shear_uses_M25_table19_and_stirrup_strength_fe415_cap():
 b=setup()
 x=shear(100,b)
 assert x["pt_percent_from_assumed_continuous_tension_bars"]==pytest.approx(.49644920945)
 assert x["tau_c_MPa"]==pytest.approx(.4881535889172,abs=1e-10)
 assert x["Vc_kN"]==pytest.approx(59.31066105344)
 assert x["Vs_required_kN"]==pytest.approx(40.68933894656)
 assert x["Vs_provided_kN"]==pytest.approx(98.00110318279)
 assert x["V_capacity_with_assumed_stirrups_kN"]==pytest.approx(157.311764236)
 assert x["tau_cmax_MPa"]==pytest.approx(3.1)
 assert x["stirrup_s_limit_geometry_mm"]==300
 assert x["stirrup_s_limit_min_steel_mm"]==pytest.approx(302.4725406876)
 assert x["provided_isolated_shear_screen_ok"]
 assert x["fy_stirrup_capped_MPa"]==415
 s=copy.deepcopy(ASSUMED_SECTION);s["fy_stirrup_MPa"]=500.
 assert shear(100,section_basis(s))["fy_stirrup_capped_MPa"]==415.

def test_shear_fail_high_V_and_stirrups_missing_even_at_zero_demand():
 b=setup()
 p=shear(170,b)
 assert p["status"]=="SHEAR_STIRRUPS_OR_SPACING_INSUFFICIENT"
 assert not p["provided_isolated_shear_screen_ok"]
 over=shear(400,b)
 assert over["status"]=="CONCRETE_MAX_SHEAR_STRESS_EXCEEDED"
 assert not over["provided_isolated_shear_screen_ok"]
 s=copy.deepcopy(ASSUMED_SECTION);s["stirrup_spacing_mm"]=400
 assert not shear(0,section_basis(s))["provided_isolated_shear_screen_ok"]

def test_section_rejects_invalid_physical_inputs():
 for key,value in [("b_mm",0),("d_mm",460),("fck_MPa",23),
                   ("fy_long_MPa",550),("stirrup_diameter_mm",-8),
                   ("stirrup_spacing_mm",float("nan"))]:
  s=copy.deepcopy(ASSUMED_SECTION);s[key]=value
  with pytest.raises(ValueError): section_basis(s)
 s=copy.deepcopy(ASSUMED_SECTION);s["section_type"]="T_BEAM"
 with pytest.raises(ValueError): section_basis(s)

def _fake_case(My,Vz):
 a=dict.fromkeys(("N","Vy","Vz","T","My","Mz"),0.)
 a["My"]=My; a["Vz"]=Vz
 return {"force_moment_balance_pass":True,"max_equilibrium_residual":0.,
         "signed_frame_end_actions":{"B:TEST":{"I":a,"J":a}}}

def test_all_cases_keep_corresponding_signed_My_and_Vz_from_same_beam_end():
 raw={"DL":_fake_case(10,2),"LL":_fake_case(20,3),"HX":_fake_case(5,-1)}
 assert combined_actions(raw,"B:TEST","I",CASES["U_PLUS"])["My"]==pytest.approx(47)
 assert combined_actions(raw,"B:TEST","I",CASES["U_PLUS"])["Vz"]==pytest.approx(5.9)
 assert combined_actions(raw,"B:TEST","I",CASES["U_MINUS"])["My"]==pytest.approx(37)
 assert combined_actions(raw,"B:TEST","I",CASES["U_MINUS"])["Vz"]==pytest.approx(7.9)
 fake={"source_SHA256":"real-fixture-digest-required-in-production",
       "classification":"SYNTHETIC_REFERENCE","engineering_approval":False,
       "topology":{"beams":[{"key":"B:TEST"}]},
       "solutions":{"FLEXIBLE_SHELL":raw,"RIGID_INPLANE_MPC":raw}}
 q=member_checks_from_preview(fake)
 assert q["rows_count"]==8
 assert q["beam_count"]==1
 assert not q["member_design_complete"] and not q["professional_engineering_approval"]
 assert q["original_narayani_F3_NOT_SAFE_retained"]
 rows=q["all_qualifying_beam_end_case_rows"]
 plus=next(x for x in rows if x["mode"]=="FLEXIBLE_SHELL" and x["end"]=="I" and x["case"]=="U_PLUS")
 assert plus["signed_local_actions"]["My"]==pytest.approx(47)
 assert plus["signed_local_actions"]["Vz"]==pytest.approx(5.9)
 assert plus["flexure"]["Mu_abs_kNm"]==pytest.approx(47)
 assert plus["shear"]["Vu_abs_kN"]==pytest.approx(5.9)
 assert plus["source_component_pair"]==["My","Vz"]
 assert q["governing_bending_row"]["flexure"]["Mu_abs_kNm"]==47
 assert q["governing_vertical_shear_row"]["shear"]["Vu_abs_kN"]==7.9
