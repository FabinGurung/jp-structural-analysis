"""R6.39 source geometry/readback and fail-closed physical stair FEM QA."""
import math

import pytest

from r6p30.staircase_geometry import (
    DRAWING, DRAWING_SHA256, REVISED_REPORT, REPORT_SHA256,
    REQUIRED_REAL_FEM_EVIDENCE, StaircaseGeometryHold,
    observed_geometry_review, require_real_staircase_model_inputs,
    source_geometry,
)


def test_actual_drawing_page_and_source_provenance_corrected():
    a=observed_geometry_review()
    d=a["original_drawing"]
    assert d["document"]==DRAWING
    assert d["sha256_original_pdf"]==DRAWING_SHA256
    assert len(DRAWING_SHA256)==64
    assert a["revised_report"]["document"]==REVISED_REPORT
    assert a["revised_report"]["sha256_original_pdf"]==REPORT_SHA256
    assert d["pdf_page_1_based"]==16
    assert d["drawing_sheet_label"]=="STR-16"
    assert a["source_visual_verification"]["old_STR15_sheet_claim_corrected"]
    assert a["source_visual_verification"]["visually_checked"]
    assert a["source_visual_verification"]["landing_support_location_and_spans_visually_confirmed"] is False
    assert a["original_source_PDFs_unchanged"] is True


def test_grid_bay_and_local_annotation_are_not_flight_clear_spans():
    a=observed_geometry_review()
    d=a["original_drawing"]
    assert d["plan_bay_grid"]=={"horizontal":["C","D"],"vertical":["1","2"]}
    assert d["grid_bay_C_to_D_mm"]==4965.
    assert d["grid_bay_1_to_2_mm"]==4275.
    assert d["bay_dimensions_are_not_stair_effective_spans"] is True
    assert d["end_zone_annotation_mm"]==720.
    assert d["720mm_note_is_not_effective_span_or_landing_clear_length"] is True
    assert d["secondary_beam_appears_in_second_flight_section_only"] is True
    assert d["landing_secondary_beam_annotation"]=='9"x12" Sec Beam'
    assert len(d["flight_detail_labels"])==3
    assert a["physical_flight_count_and_3D_sequencing_verified"] is False
    assert a["actual_staircase_model_ready"] is False
    assert a["staircase_in_active_2floor_synthetic_OpenSees_model"] is False
    for k in ("drawing_180mm_riser_255mm_tread","report_170mm_riser_254mm_tread"):
        assert a[k]["actual_flight_span_m"] is None
        assert a[k]["actual_support_reactions_kN"] is None
        assert a[k]["flight_step_count"] is None
        assert a[k]["actual_fe_elements"] is None
        assert not a[k]["engineering_approval"]


def test_trigonometry_source_vs_report_not_blended():
    a=observed_geometry_review()
    d=a["drawing_180mm_riser_255mm_tread"]
    r=a["report_170mm_riser_254mm_tread"]
    assert d["inclination_deg"]==pytest.approx(math.degrees(math.atan2(180,255)))
    assert r["inclination_deg"]==pytest.approx(math.degrees(math.atan2(170,254)))
    assert d["inclined_length_per_tread_mm"]==pytest.approx(math.hypot(180,255))
    assert r["inclined_length_per_tread_mm"]==pytest.approx(math.hypot(170,254))
    assert d["waist_selfweight_kPa_on_horizontal_plan"]==pytest.approx(24*.15/d["cos_inclination"])
    assert d["triangular_solid_step_selfweight_kPa_on_horizontal_plan"]==pytest.approx(24*.18/2)
    assert r["triangular_solid_step_selfweight_kPa_on_horizontal_plan"]==pytest.approx(24*.17/2)
    assert d["inclination_deg"]>r["inclination_deg"]
    assert d["not_an_applied_factored_staircase_load"] and r["not_an_applied_factored_staircase_load"]
    assert d["assumes_monolithic_solid_steps_NOT_verified"]


def test_floor_height_3048_is_only_contextual_not_physical_riser_count():
    a=observed_geometry_review()
    d=a["drawing_180mm_riser_255mm_tread"]["optional_context_storey_height_check"]
    r=a["report_170mm_riser_254mm_tread"]["optional_context_storey_height_check"]
    assert d["noninteger_theoretical_riser_count"]==pytest.approx(3048/180)
    assert r["noninteger_theoretical_riser_count"]==pytest.approx(3048/170)
    assert d["nearest_integer_count_for_sensitivity_only"]==17
    assert r["nearest_integer_count_for_sensitivity_only"]==18
    assert d["signed_height_residual_mm"]==pytest.approx(-12)
    assert r["signed_height_residual_mm"]==pytest.approx(-12)
    assert d["integer_riser_total_not_authorized"] is True
    assert r["integer_riser_total_not_authorized"] is True


def test_staircase_fe_gate_fails_on_incomplete_or_fictional_inputs():
    with pytest.raises(StaircaseGeometryHold,match="source map required"):
        require_real_staircase_model_inputs(None)
    with pytest.raises(StaircaseGeometryHold,match="surveyed_per_flight_xyz_centerline_nodes_m"):
        require_real_staircase_model_inputs({"approved_drawing_revision":"STR-16"})
    assert len(REQUIRED_REAL_FEM_EVIDENCE)>=10
    with pytest.raises(StaircaseGeometryHold,match="no vetted physical staircase FEM implementation"):
        require_real_staircase_model_inputs({k:"SOURCE_PEND_CONFIRMATION" for k in REQUIRED_REAL_FEM_EVIDENCE})


@pytest.mark.parametrize("data",[
  {"riser_mm":0.}, {"riser_mm":-180.}, {"tread_mm":0.},
  {"riser_mm":math.nan}, {"waist_mm":math.inf},
  {"gamma_kN_m3":-1.}, {"riser_mm":True},
  {"floor_height_mm":0.}, {"floor_height_mm":math.inf}
])
def test_invalid_geometry_fails_closed(data):
    kw={"riser_mm":180,"tread_mm":255,"waist_mm":150,
        "gamma_kN_m3":24,"floor_height_mm":3048}
    kw.update(data)
    with pytest.raises(StaircaseGeometryHold):
        source_geometry(**kw)


def test_geometry_review_retains_f3_and_source_conflicts_as_holds():
    from r6p30.staircase_review import review
    x=review()
    a=x["source_geometry_and_support_gate"]
    assert x["drawing"]["source_sheet"]=="STR-16, July 2026"
    assert "STR15_SHEET_MISIDENTIFICATION_CORRECTED" in x["resolved_evidence_items"]
    assert "F3_ORIGINAL_NOT_SAFE_REMAINS_OPEN" in x["open_holds"]
    assert "DRAWING_VS_REPORT_RISER_TREAD_CONFLICT" in x["open_holds"]
    assert not x["engineering_approval"]
    assert not a["actual_staircase_model_ready"]
    assert len(a["support_and_load_path_holds"])>=12
