"""R6.40 reproducible Narayani staircase source worksheet, NOT project approval."""
import math
import pytest

from r6p30.staircase_loads import audit, worksheet_geometry_and_loads, SCHEMA
from r6p30.staircase_geometry import StaircaseGeometryHold


def source_fixture():
    return dict(
        riser_mm=170,tread_mm=254,waist_mm=150,
        finish_thickness_mm=50.8,flight_gamma_kN_m3=24,
        flight_width_m=1.2,imposed_stair_kPa=3,
        landing_waist_mm=150,landing_gamma_kN_m3=25,
        landing_finish_kPa=1.22,imposed_landing_kPa=3)


def test_source_section_areas_and_FF_face_reconstruction():
    x=worksheet_geometry_and_loads(**source_fixture())
    a=x["source_cell_area_reconstruction_m2_per_m_width"]
    assert a["triangular_step"]==pytest.approx(.17*.254/2)
    assert a["inclined_waist"]==pytest.approx(.15*math.hypot(.170,.254))
    assert a["finish_horizontal_and_vertical_assumed"]==pytest.approx(.0508*(.170+.254))
    assert a["total"]==pytest.approx(.08897524672160947)
    assert x["finish_area_method_is_inferred_not_documented"] is True


def test_dead_live_and_report_specific_worksheet_values_reconciled():
    x=audit()
    assert x["schema"]==SCHEMA
    assert x["source_numbers_reproduced_with_printed_precision"] is True
    a=x["report_170_254_worksheet_reconstruction"]
    assert a["flight_deadload_from_reconstructed_section_kPa"]==pytest.approx(8.407109926451287)
    assert a["flight_deadload_per_unit_width_per_tread_kN_per_m"]==pytest.approx(2.135405921318627)
    assert a["flight_service_kPa"]==pytest.approx(11.407109926451287)
    assert a["flight_worksheet_factor_1p5_DL_plus_LL_kPa"]==pytest.approx(17.110664889676933)
    assert a["flight_worksheet_full_width_line_load_kN_per_m"]==pytest.approx(20.53279786761232)
    assert a["landing_dead_kPa"]==pytest.approx(4.97)
    assert a["landing_worksheet_factor_1p5_DL_plus_LL_kPa"]==pytest.approx(11.955)
    assert a["landing_worksheet_full_width_line_load_kN_per_m"]==pytest.approx(14.346)


def test_load_combinations_are_distinct_and_not_approved():
    x=audit()
    a=x["report_170_254_worksheet_reconstruction"]
    assert a["flight_report_declared_1p2_DL_plus_1p5_LL_kPa"]==pytest.approx(14.588531911741544)
    assert x["flight_combo_difference_kPa"]==pytest.approx(2.522132977935389)
    assert x["flight_combo_difference_fraction_of_worksheet"]==pytest.approx(.14740122573828335)
    assert x["landing_combo_difference_kPa"]==pytest.approx(1.491)
    assert a["not_a_verified_NBC_action_envelope"]
    assert not a["engineering_approval"]
    assert not x["construction_design_approved"]


def test_drawing_and_report_occupancy_geometry_kept_separate():
    x=audit()
    assert x["source_drawing_physical_pdf_page"]==16
    assert x["source_report_physical_pdf_pages"]==[64,65]
    assert x["occupancy_description_conflict"]["drawing_STR16"]=="CLASS B (Residential+Commercial)"
    assert x["occupancy_description_conflict"]["revised_analysis_cover"]=="Residential building"
    assert x["occupancy_description_conflict"]["applicable_imposed_load_and_permit_occupancy_unresolved"]
    g=x["drawing_180_255_counterfactual_NOT_project_load"]
    w=x["report_170_254_worksheet_reconstruction"]
    assert g["input_geometry"]["riser_mm"]==pytest.approx(180)
    assert w["input_geometry"]["riser_mm"]==pytest.approx(170)
    assert g["flight_deadload_from_reconstructed_section_kPa"]!=pytest.approx(w["flight_deadload_from_reconstructed_section_kPa"])
    assert g["source_geometry_not_a_verified_flight_span"] is True
    assert x["flight_or_landing_effective_span_m"] is None


def test_open_holds_keep_source_moments_and_F3_unsafe():
    x=audit()
    assert "SOURCE_REPORT_1P5_DL_PLUS_LL_VS_1P2_DL_PLUS_1P5_LL_DESIGN_BASIS" in x["engineering_holds"]
    assert "ORIGINAL_F3_ONE_WAY_SHEAR_NOT_SAFE" in x["engineering_holds"]
    assert "R6P36_SLAB_SP16_BENCHMARK_DISCREPANCY" in x["engineering_holds"]
    eff=x["manual_design_effects_unverified"]
    assert eff["AB_maximum_moment_kNm"]==20.88
    assert eff["BC_maximum_moment_kNm"]==14.96
    assert eff["reported_BC_line_load_kN_per_m"]==17.83
    assert eff["not_recalculated_or_approved"]
    assert not eff["effective_spans_and_support_condition_from_sources_verified"]
    assert x["actual_staircase_FEM_completed"] is False
    assert x["engineering_approval"] is False


@pytest.mark.parametrize("key,value",[
    ("riser_mm",0),("riser_mm",True),("tread_mm",float("nan")),
    ("waist_mm",-50),("flight_gamma_kN_m3",float("inf")),
    ("finish_thickness_mm",.0),("flight_width_m",0),
    ("flight_width_m",120),("imposed_stair_kPa",-3),
    ("landing_gamma_kN_m3",-25),("landing_finish_kPa",-1),
    ("imposed_landing_kPa",-3)
])
def test_bad_inputs_fail_closed(key,value):
    a=source_fixture();a[key]=value
    with pytest.raises(StaircaseGeometryHold,match="STAIRCASE SOURCE HOLD"):
        worksheet_geometry_and_loads(**a)


def test_source_density_scenarios_are_not_silently_normalized():
    x=audit()
    g=x["different_material_densities_in_same_source"]
    assert (g["summary"],g["source_materials_plain_concrete"],
            g["source_materials_reinforced_concrete"])==(20,24,25)
    assert g["worksheet_flight"]==24
    assert g["worksheet_landing"]==25
    assert not g["reconciled_for_actual_project"]
