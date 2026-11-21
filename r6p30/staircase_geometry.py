"""R6.39 source-verified staircase geometry register and fail-closed FEM gate.

This is a review of original Narayani drawing STR-16 (physical PDF page 16)
and revised engineering report pages 64–65, NOT a stair flight FE solve.
Bay grid dimensions are never reused as flight effective spans. Text/diagram
observations are provenance-bound and sources were visually checked.
"""
from __future__ import annotations

import math
from typing import Mapping

SCHEMA = "jp.sar.r6p39.staircase_geometry_support_readback.v1"
DRAWING = "https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
REVISED_REPORT = "https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
DRAWING_SHA256 = "b4b5ee8a64ceddf267c93a59ca95418d1d9c406c7a954bc43dfb36afca8f1c77"
REPORT_SHA256 = "f122904444a2e2f75230d9d4e41da0093d050da25c6e8140c86d466b7e37cc52"


class StaircaseGeometryHold(ValueError):
    """Physical geometry, connectivity or evidence is not verified."""


def finite(value, name: str, *, positive=True) -> float:
    if (not isinstance(value, (int, float)) or isinstance(value, bool)
            or not math.isfinite(value)):
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: " + name + " nonfinite")
    v = float(value)
    if positive and v <= 0:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: " + name + " nonpositive")
    return v


def source_geometry(*, riser_mm: float, tread_mm: float,
                    waist_mm: float, gamma_kN_m3: float,
                    floor_height_mm: float | None = None) -> dict:
    """Exact step geometry, theoretical concrete section weights; NO design loads.

    Dead load formula presumes solid monolithic triangular steps and inclined
    uniform waist. If stair is hollow/prefabricated or materials differ, invalid.
    gamma is illustrative; floor height is optional context, not flight rise.
    """
    r = finite(riser_mm, "riser mm")
    t = finite(tread_mm, "tread mm")
    D = finite(waist_mm, "waist mm")
    g = finite(gamma_kN_m3, "assumed unit weight kN/m3")
    angle = math.atan2(r, t)
    c = math.cos(angle)
    result = {
        "riser_mm": r, "tread_mm": t, "waist_mm": D,
        "rise_per_step_m": r/1000., "going_per_step_m": t/1000.,
        "inclined_length_per_tread_mm": math.hypot(r, t),
        "inclination_deg": math.degrees(angle),
        "cos_inclination": c,
        "hypothetical_unit_weight_kN_m3": g,
        "waist_selfweight_kPa_on_horizontal_plan": g*(D/1000.)/c,
        "triangular_solid_step_selfweight_kPa_on_horizontal_plan": g*(r/2000.),
        "hypothetical_sum_before_finish_kPa": g*((D/1000.)/c+r/2000.),
        "assumes_monolithic_solid_steps_NOT_verified": True,
        "not_an_applied_factored_staircase_load": True,
        "flight_step_count": None, "actual_flight_span_m": None,
        "actual_support_reactions_kN": None, "actual_fe_elements": None,
        "engineering_approval": False,
    }
    if floor_height_mm is not None:
        H = finite(floor_height_mm, "context storey height mm")
        nearest = int(math.floor(H / r + .5))
        result["optional_context_storey_height_check"] = {
            "source_report_building_level_height_mm_not_confirmed_for_stair": H,
            "noninteger_theoretical_riser_count": H / r,
            "nearest_integer_count_for_sensitivity_only": nearest,
            "signed_height_residual_mm": H - nearest * r,
            "integer_riser_total_not_authorized": True,
        }
    return result


# An observation means the annotation appears on the original drawing,
# NOT that the geometry/load connection has been established in the building.
DRAWING_OBSERVATION = {
    "document": DRAWING,
    "sha256_original_pdf": DRAWING_SHA256,
    "pdf_page_1_based": 16,
    "drawing_sheet_label": "STR-16",
    "revision_date": "July 2026",
    "plan_bay_grid": {"horizontal": ["C", "D"], "vertical": ["1", "2"]},
    "grid_bay_C_to_D_mm": 4965.,
    "grid_bay_1_to_2_mm": 4275.,
    "bay_dimensions_are_not_stair_effective_spans": True,
    "flight_detail_labels": ["STAIR FIRST FLIGHT X-X",
                             "STAIR SECOND FLIGHT Y-Y",
                             "STAIR THIRD FLIGHT X-X"],
    "first_third_and_second_flight_arrangement_needs_3D_connectivity_review": True,
    "riser_mm": 180., "tread_mm": 255., "waist_mm": 150.,
    "main_rebar": "12 mm diameter @ 125 mm c/c",
    "distribution_rebar": "8 mm diameter @ 150 mm c/c",
    "landing_secondary_beam_annotation": '9"x12" Sec Beam',
    "secondary_beam_appears_in_second_flight_section_only": True,
    "end_zone_annotation_mm": 720.,
    "720mm_note_is_not_effective_span_or_landing_clear_length": True,
    "other_note": "60 Ø Ld (development-length notation; not design-approved)",
    "no_verified_section_support_coordinates": True,
    "no_verified_flight_clear_span_or_landing_effective_span": True,
}
REVISED_OBSERVATION = {
    "document": REVISED_REPORT,
    "sha256_original_pdf": REPORT_SHA256,
    "stair_design_physical_pdf_page_1_based": 64,
    "stair_worksheet_continuation_pdf_page_1_based": 65,
    "riser_mm": 170., "tread_mm": 254.,
    "waist_mm_declared": 150., "waist_mm_worked": 127.,
    "width_m_declared": 1.2,
    "max_bending_moment_source_kNm": 20.88,
    "source_moment_width_interpretation": "UNRESOLVED",
    "report_general_storey_height_m": 3.048,
    "storey_height_corresponding_to_three_specific_flights": "UNVERIFIED",
}


def observed_geometry_review() -> dict:
    source_draw = source_geometry(
        riser_mm=DRAWING_OBSERVATION["riser_mm"],
        tread_mm=DRAWING_OBSERVATION["tread_mm"], waist_mm=150.,
        gamma_kN_m3=24., floor_height_mm=3048.)
    source_report = source_geometry(
        riser_mm=REVISED_OBSERVATION["riser_mm"],
        tread_mm=REVISED_OBSERVATION["tread_mm"], waist_mm=150.,
        gamma_kN_m3=24., floor_height_mm=3048.)
    return {
        "schema": SCHEMA,
        "classification": "SOURCE-VERIFIED_DIMENSIONS_WITH_DESIGN_HOLDS",
        "original_drawing": DRAWING_OBSERVATION,
        "revised_report": REVISED_OBSERVATION,
        "drawing_180mm_riser_255mm_tread": source_draw,
        "report_170mm_riser_254mm_tread": source_report,
        "flight_count_in_source_sections": 3,
        "physical_flight_count_and_3D_sequencing_verified": False,
        "grid_bay_is_not_FEM_effective_span": True,
        "report_and_drawing_geometry_are_different": True,
        "actual_staircase_model_ready": False,
        "staircase_in_active_2floor_synthetic_OpenSees_model": False,
        "original_source_PDFs_unchanged": True,
        "source_visual_verification": {
            "drawing_pdf_physical_page": 16,
            "drawing_sheet": "STR-16",
            "visually_checked": True,
            "old_STR15_sheet_claim_corrected": True,
            "old_visual_inspection_pending_hold_reclassified_as_resolved": True,
            "landing_support_location_and_spans_visually_confirmed": False,
        },
        "support_and_load_path_holds": [
            "MEASURE_ACTUAL_HORIZ_FLIGHT_GOING_FOR_EACH_LEVEL_AND_LANDING",
            "VERIFY_FLOOR_TO_FLOOR_HEIGHT_PER_FLIGHT_AND_INDIVIDUAL_RISER_COUNTS",
            "RECONCILE_180_255_DRAWING_VS_170_254_REPORT",
            "VERIFY_THREE_FLIGHT_DETAILS_MAP_TO_CONTINUOUS_3D_STAIRS",
            "VERIFY_LANDING_DIMENSIONS_AND_ROTATIONS",
            "VERIFY_9IN_BY_12IN_SEC_BEAM_SUPPORT_AND_WALL_BEAM_CONTINUITY",
            "LOCATE_ALL_SUPPORT_NODE_XYZ_RESTRAINTS_AND_STIFFNESS",
            "VERIFY_SLAB_SHELL_LOCAL_AXES_AND_MESH_COMPATIBILITY_AT_LANDINGS",
            "ESTABLISH_NBC_IMPOSED_AND_SEISMIC_COMBINATIONS_PLUS_LOAD_TRANSFER",
            "VERIFY_ABUTMENTS_LANDING_JOINT_ANCHORAGE_AND_SUPPORT_MOMENTS",
            "RECONCILE_150MM_DRAWING_VS_127MM_WORKED_FLEXURE_DEPTH",
            "CONSTRUCT_ACTUAL_OPENSEES_STAIRCASE_MESH_ONLY_AFTER_GATE",
        ],
        "engineering_approval": False,
    }


# Required independently validated data *before* any proposed stair FEM.
REQUIRED_REAL_FEM_EVIDENCE = (
    "approved_drawing_revision",
    "surveyed_per_flight_xyz_centerline_nodes_m",
    "per_flight_waist_thickness_m",
    "per_flight_width_m",
    "landing_polygon_xyz_m",
    "beam_wall_column_support_node_xyz_m",
    "landing_support_restraints_and_stiffness",
    "verified_stair_to_landing_and_frame_connectivity",
    "source_load_cases_and_combinations_kPa",
    "mesh_and_local_axes_specification",
    "material_properties_with_source",
    "engineering_review_signoff",
)


def require_real_staircase_model_inputs(raw: Mapping) -> None:
    """Gate only. Never runs FEM; passing fields does NOT authorize analysis."""
    if not isinstance(raw, Mapping):
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: source map required")
    missing = [k for k in REQUIRED_REAL_FEM_EVIDENCE if not raw.get(k)]
    if missing:
        raise StaircaseGeometryHold(
            "STAIRCASE SOURCE HOLD: unsupported physical model: "
            + ", ".join(missing))
    # Actual staircase FE solver remains NOT IMPLEMENTED and requires separate
    # rigorous reaction, stiffness, convergence and published benchmark QA.
    raise StaircaseGeometryHold(
        "STAIRCASE SOURCE HOLD: all input fields supplied but no vetted "
        "physical staircase FEM implementation or independent reaction QA")
