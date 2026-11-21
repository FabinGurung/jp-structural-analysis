"""R6.37: fail-closed source reconciliation, no site-approved stair FEM."""
import math
import pytest

from r6p30.staircase_review import flexural_strip, review, DRAWING, REVISED_REPORT


def test_source_provenance_and_conflicting_waist_geometry_remain_separate():
    x=review()
    assert x["drawing"]["source"]==DRAWING
    assert x["revised_report"]["source"]==REVISED_REPORT
    assert x["drawing"]["riser_mm"]==180
    assert x["revised_report"]["riser_mm"]==170
    assert x["drawing"]["tread_mm"]==255
    assert x["revised_report"]["tread_mm"]==254
    assert x["drawing"]["waist_D_mm"]==150
    assert x["revised_report"]["waist_D_used_in_flexure_mm"]==127
    assert x["revised_report"]["waist_D_declared_mm"]==150
    assert x["report_moment_normalization_unresolved"] is True
    assert x["staircase_present_in_active_opensees_reference_model"] is False
    assert x["source_originals_preserved"] is True
    assert not x["engineering_approval"]
    assert not x["staircase_design_approved"]
    assert len(x["open_holds"])>=10


def test_independently_recomputed_is456_flexural_strip_and_unit_variants():
    x=review()
    v=x["report_moment_interpretations"]
    full=v["if_20p88_is_already_per_one_metre_strip"]
    normalized=v["if_20p88_is_a_full_1p2m_flight_moment"]
    assert full["source_moment_kNm_per_m_if_interpretation_valid"]==pytest.approx(20.88)
    assert normalized["source_moment_kNm_per_m_if_interpretation_valid"]==pytest.approx(17.4)
    assert full["As_required_mm2_per_m"]==pytest.approx(516.7550206755)
    assert normalized["As_required_mm2_per_m"]==pytest.approx(419.4822790505)
    assert full["back_substitution_Mu_kNm_per_m"]==pytest.approx(20.88,abs=1e-9)
    assert normalized["back_substitution_Mu_kNm_per_m"]==pytest.approx(17.4,abs=1e-9)
    assert full["As_provided_mm2_per_m"]==pytest.approx(math.pi*12**2/4*1000/127)
    assert not full["singly_reinforced_ductile_limit_ok"]
    assert full["provided_Mu_kNm_per_m_if_ductile"] is None
    assert not full["bounded_section_flexure_ok"]
    assert not normalized["bounded_section_flexure_ok"]
    assert x["source_report_As_value_without_verified_strip_units_mm2"]==383.62


def test_drawing_source_conditional_thickness_not_silent_actual_approval():
    v=review()
    d=v["drawing_150mm_waist_conditional_overlay_NOT_actual_demand"]
    assert d["D_mm"]==150
    assert d["d_mm"]==129
    assert d["As_provided_mm2_per_m"]==pytest.approx(math.pi*12**2/4*1000/125)
    assert d["M_lim_kNm_per_m"]==pytest.approx(44.4667755456)
    assert d["bounded_section_flexure_ok"] is True
    assert d["engineering_approval"] is False


def test_independent_stair_geometry_dead_load_math_and_report_conflict():
    x=review()
    a=x["independent_geometric_load_checks"]
    angle=math.atan(.170/.254)
    assert a["waist_weight_per_horizontal_area_kPa"]==pytest.approx(24*.15/math.cos(angle))
    assert a["triangular_step_weight_per_horizontal_area_kPa"]==pytest.approx(2.04)
    assert a["reported_flight_total_dead_kPa"]==8.41
    assert a["finishes_and_report_DL_reconciliation"]=="HOLD"
    assert a["not_a_verified_project_load_combination"]


@pytest.mark.parametrize("change",[
    {"mu_kNm_m":-1}, {"mu_kNm_m":float("nan")},
    {"D_mm":0}, {"d_mm":150}, {"bar_diameter_mm":22},
    {"bar_spacing_mm":12}, {"fy_MPa":600},
    {"fck_MPa":float("inf")}, {"mu_kNm_m":True},
])
def test_invalid_inputs_are_rejected(change):
    kwargs=dict(mu_kNm_m=5,D_mm=150,d_mm=129,
                bar_diameter_mm=12,bar_spacing_mm=125,
                fck_MPa=20,fy_MPa=500)
    kwargs.update(change)
    with pytest.raises(ValueError,match="STAIRCASE HOLD"):
        flexural_strip(**kwargs)


def test_published_iit_kharagpur_staircase_waist_benchmark_independent():
    from r6p30.staircase_review import published_nptel_staircase_benchmark
    x=published_nptel_staircase_benchmark()
    assert x["source"].endswith("/m9l20.pdf")
    assert x["source_total_factored_moment_kNm_for_1p5m_width"]==pytest.approx(102.08)
    assert x["moment_normalized_kNm_per_m"]==pytest.approx(102.08/1.5)
    assert x["source_required_steel_mm2_m"]==pytest.approx(920.64)
    assert x["independent_required_steel_mm2_m"]==pytest.approx(921.2607899924,abs=.001)
    assert x["within_predeclared_1pct_research_band"] is True
    assert abs(x["relative_stress_block_vs_SP16_difference"])<.01
    assert x["independent_bar_section_screen_ok"] is True
    assert x["not_complete_staircase_loading_or_reactions_benchmark"] is True
    assert x["not_a_Narayani_building_design"] is True
    assert x["engineering_approval"] is False
    assert review()["published_nptel_stair_waist_section_benchmark"]==x
