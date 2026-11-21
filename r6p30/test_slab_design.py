"""R6.36: one-metre slab strip, genuine shell section-response and external NPTEL tests."""
import math
import pytest
from r6p30.slab_design import (DEFAULT,SCHEMA,section,strip,shear,wood_armer,
                               published_oneway_benchmark,from_opensees)

def test_slab_is456_26_5_2_minimum_spacing_diameter_and_flexure_limits():
 s=section()
 assert s["D_mm"]==120 and s["d_mm"]==pytest.approx(88)
 assert s["As_min_mm2_m"]==pytest.approx(144)
 assert s["As_provided_mm2_m"]==pytest.approx(math.pi*8**2/4*1000/150)
 assert s["main_bar_spacing_max_mm"]==pytest.approx(264)
 assert s["minimum_steel_ok"] and s["section_tension_zone_ok"]
 assert strip(0)["isolated_flexure_ok"]
 assert strip(1000)["isolated_flexure_ok"] is False
 assert strip(1000)["status"]=="SINGLY_REINFORCED_LIMIT_EXCEEDED"
 assert strip(s["Mres_kNm_m"]-.0001)["isolated_flexure_ok"]
 assert not strip(s["Mres_kNm_m"]+.01)["isolated_flexure_ok"]
 assert strip(0)["As_required_with_min_mm2_m"]==pytest.approx(144)
 assert not s["construction_approval"]
 assert section({**DEFAULT,"fy_MPa":250.})["As_min_mm2_m"]==pytest.approx(180)
 for change in ({"bar_diameter_mm":20.},{"bar_spacing_mm":400.},
                {"clear_cover_mm":140.},{"fy_MPa":700.},
                {"D_mm":-120.}):
  with pytest.raises(ValueError):section({**DEFAULT,**change})

def test_wood_armer_signed_moments_and_torsion_are_distinct_on_all_faces():
 assert wood_armer(10.,8.,2.)=={"X_bottom":12.,"Y_bottom":10.,
                              "X_top":0.,"Y_top":0.}
 assert wood_armer(-10.,-8.,2.)=={"X_bottom":0.,"Y_bottom":0.,
                                 "X_top":12.,"Y_top":10.}
 assert all(v==3. for v in wood_armer(0.,0.,-3.).values())
 assert wood_armer(1.,2.,0.)["Y_bottom"]==2.
 with pytest.raises(ValueError):wood_armer(float("nan"),0,1)

def test_slab_shear_resultant_is_kN_per_m_not_nodal_force():
 v=shear(20.)
 assert v["tau_v_MPa"]==pytest.approx(20/88)
 assert v["thickness_multiplier_k"]==pytest.approx(1.3)
 assert v["tau_c_slab_MPa"]>0
 assert v["not_a_punching_or_support_zone_check"]

def test_nptel_oneway_published_load_reactions_and_capacity_disagreement_exposed():
 q=published_oneway_benchmark()
 assert q["factored_pressure_kPa"]==pytest.approx(14.0625)
 assert q["computed_analytic_Mu_kNm_m"]==pytest.approx(21.533203125)
 assert q["computed_analytic_Mu_kNm_m"]==pytest.approx(q["published_Mu_kNm_m"],abs=.001)
 assert q["computed_Vu_kN_m"]==pytest.approx(24.609375)
 assert q["computed_Vu_kN_m"]==pytest.approx(q["published_Vu_kN_m"],abs=.01)
 assert q["benchmark_section_depth_mm"]==pytest.approx(150.)
 assert q["published_slab_min_As_mm2_m"]==q["computed_slab_min_As_mm2_m"]==210
 assert q["our_8mm_120mm_As_mm2_m"]==pytest.approx(math.pi*8**2/4*1000/120)
 assert q["published_SP16_table41_capacity_kNm_m"]==22.26
 # The precise Annex G approximation (at d=150) is ~21.35, not
 # the source SP16 table's 22.26. Do not fake a +/-3% certification.
 assert q["our_IS456_AnnexG_capacity_kNm_m"]==pytest.approx(21.35,abs=.04)
 assert q["our_relative_chart_capacity_difference"]<-.03
 assert not q["construction_approval"]

def test_real_opensees_shell_moments_are_four_gauss_points_per_cell():
 from r6p23.runner import reference_fixture
 from r6p23.engine import build as solve
 spec=reference_fixture()
 raw=solve(spec)
 sample=raw["solutions"]["FLEXIBLE_SHELL"]["DL"]
 moments=sample["shell_gauss_section_resultants"]
 assert len(moments)==31
 assert "L2:CELL:1:1" not in moments  # actual opening is excluded
 assert "L1:CELL:0:0" in moments
 assert set(moments["L1:CELL:0:0"][0])=={"p11","p22","p12","m11","m22","m12","q1","q2"}
 assert all(len(rows)==4 for rows in moments.values())
 assert any(abs(p["m11"])+abs(p["m22"])+abs(p["m12"])>1e-6
            for four in moments.values() for p in four)
 result=from_opensees(raw)
 assert result["schema"]==SCHEMA
 assert result["source_SHA256"]==raw["source_SHA256"]
 assert result["shell_cells"]==31
 assert result["rows_count"]==31*2*2*2*2==496
 assert len(result["rows"])==496
 assert 0<=result["flexure_screen_ok"]<=496
 assert 0<=result["transverse_shear_screen_ok"]<=496
 assert result["governing_example"]["design_moment_WoodArmer_assumed_kNm_m"]>0
 assert all(not r["bending"]["construction_approval"] for r in result["rows"])
 assert all(not r["actual_top_bottom_sign_validated_in_real_structure"] for r in result["rows"])
 assert result["opening_cells_excluded"]
 assert result["engineering_approval"] is False
 assert result["complete_crackwidth_deflection_checked"] is False
 assert result["actual_project_slab_geometry_and_rebar_verified"] is False
 # Each sampled combined Gauss point MUST be the actual 1.2DL+1.5LL±HX
 row=next(r for r in result["rows"]
          if r["cell"]=="L1:CELL:0:0" and r["mode"]=="FLEXIBLE_SHELL"
          and r["combination"]=="U_PLUS" and r["direction"]=="X"
          and r["face"]=="bottom")
 gp=row["gauss"]-1
 for k,val in zip(("m11","m22","m12"),row["shell_original_signed_m11_m22_m12_kNm_m"]):
  expected=(1.2*raw["solutions"]["FLEXIBLE_SHELL"]["DL"]["shell_gauss_section_resultants"][row["cell"]][gp][k]
      +1.5*raw["solutions"]["FLEXIBLE_SHELL"]["LL"]["shell_gauss_section_resultants"][row["cell"]][gp][k]
      +raw["solutions"]["FLEXIBLE_SHELL"]["HX"]["shell_gauss_section_resultants"][row["cell"]][gp][k])
  assert val==pytest.approx(expected,rel=1e-7,abs=1e-8)
