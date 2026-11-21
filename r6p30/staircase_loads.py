"""R6.40 — Narayani staircase worksheet arithmetic and load-basis reconciliation.

Source: revised report PDF physical pp. 64–65, original structural drawing
STR-16 PDF p. 16. This is a source check, NOT a verified building load envelope
or actual staircase FEM. Staircase landing support topology remains unknown.

The finish cross-section equation inferred from source workbook numbers is
t_finish * (riser + tread). Its existence reproduces the listed area but does
not independently prove that both horizontal and vertical finishes were
constructed or loaded in the structural analysis.

No comparison herein claims which design combination is governing or valid.
"""
from __future__ import annotations
import math
from r6p30.staircase_geometry import (
    DRAWING, DRAWING_SHA256, REVISED_REPORT, REPORT_SHA256,
    finite, StaircaseGeometryHold,
)

SCHEMA = "jp.sar.r6p40.staircase_load_worksheet_audit.v1"
OFFICIAL_NBC105_PAGE = "https://dudbc.gov.np/pages/building-code/"
OFFICIAL_NBC103_PAGE = "https://dudbc.gov.np/content/2397/2397-nbc-103-occupancy-load-impo/"
IS456_33_REFERENCE = "https://www.cracindia.in/admin/uploads/IS-456.pdf"


def worksheet_geometry_and_loads(
        *, riser_mm: float, tread_mm: float, waist_mm: float,
        finish_thickness_mm: float, flight_gamma_kN_m3: float,
        flight_width_m: float, imposed_stair_kPa: float,
        landing_waist_mm: float, landing_gamma_kN_m3: float,
        landing_finish_kPa: float, imposed_landing_kPa: float) -> dict:
    """Explicit source-arithmetic reconstruction; outputs hypothetical until
    finishes, flight spans, loading and occupancy are independently verified.
    All areas are cross-sections PER METRE OF FLIGHT WIDTH in a riser/tread cell.
    """
    r=finite(riser_mm, "flight riser mm")/1000.
    t=finite(tread_mm, "flight tread mm")/1000.
    D=finite(waist_mm, "flight waist thickness mm")/1000.
    f=finite(finish_thickness_mm, "finish thickness mm")/1000.
    g=finite(flight_gamma_kN_m3, "flight gamma kN/m3")
    width=finite(flight_width_m, "flight full width m")
    live=finite(imposed_stair_kPa, "flight imposed kPa",positive=False)
    lw=finite(landing_waist_mm, "landing waist mm")/1000.
    lg=finite(landing_gamma_kN_m3, "landing gamma kN/m3")
    lf=finite(landing_finish_kPa, "landing finish kPa",positive=False)
    ll=finite(imposed_landing_kPa, "landing live kPa",positive=False)
    if live<0 or lf<0 or ll<0:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: negative floor load")
    if t>2. or r>1. or D>1. or f>.5 or width>10.:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: out-of-scope geometry")

    # Geometric source-reconstruction hypotheses, separate from code approval.
    A_step=r*t/2.                         # m2 per m width
    A_waist=D*math.hypot(r,t)             # m2 per m width
    A_finish=f*(r+t)                     # m2 per m width; inferred from source area
    A_total=A_step+A_waist+A_finish
    flight_DL=A_total*g/t                # kN/m2 of horizontal flight plan
    landing_dead=lw*lg+lf
    return {
        "input_geometry": {
            "riser_mm":1000*r,"tread_mm":1000*t,
            "flight_waist_mm":1000*D,"finish_thickness_mm":1000*f,
            "width_m":width,
        },
        "source_cell_area_reconstruction_m2_per_m_width": {
            "triangular_step":A_step,
            "inclined_waist":A_waist,
            "finish_horizontal_and_vertical_assumed":A_finish,
            "total":A_total,
        },
        "finish_area_method_is_inferred_not_documented":True,
        "flight_deadload_from_reconstructed_section_kPa":flight_DL,
        "flight_deadload_per_unit_width_per_tread_kN_per_m":A_total*g,
        "flight_live_kPa":live,
        "flight_service_kPa":flight_DL+live,
        "flight_worksheet_factor_1p5_DL_plus_LL_kPa":1.5*(flight_DL+live),
        "flight_report_declared_1p2_DL_plus_1p5_LL_kPa":1.2*flight_DL+1.5*live,
        "flight_worksheet_full_width_line_load_kN_per_m":
            1.5*(flight_DL+live)*width,
        "flight_report_declared_full_width_line_load_kN_per_m":
            (1.2*flight_DL+1.5*live)*width,
        "landing_dead_kPa":landing_dead,
        "landing_live_kPa":ll,
        "landing_service_kPa":landing_dead+ll,
        "landing_worksheet_factor_1p5_DL_plus_LL_kPa":1.5*(landing_dead+ll),
        "landing_report_declared_1p2_DL_plus_1p5_LL_kPa":
            1.2*landing_dead+1.5*ll,
        "landing_worksheet_full_width_line_load_kN_per_m":
            1.5*(landing_dead+ll)*width,
        "landing_report_declared_full_width_line_load_kN_per_m":
            (1.2*landing_dead+1.5*ll)*width,
        "flight_gamma_kN_m3":g,
        "landing_gamma_kN_m3":lg,
        "landing_finish_kPa":lf,
        "not_a_verified_NBC_action_envelope":True,
        "source_geometry_not_a_verified_flight_span":True,
        "engineering_approval":False,
    }


def audit() -> dict:
    # Source physical PDF p64/65. All values are exactly those printed or
    # explicitly reconstructed from the text table, not inferred floor spans.
    case=worksheet_geometry_and_loads(
        riser_mm=170.,tread_mm=254.,waist_mm=150.,
        finish_thickness_mm=50.8,flight_gamma_kN_m3=24.,
        flight_width_m=1.2,imposed_stair_kPa=3.,
        landing_waist_mm=150.,landing_gamma_kN_m3=25.,
        landing_finish_kPa=1.22,imposed_landing_kPa=3.)
    published={
        "flight_step_section_m2":.0216,
        "flight_inclined_slab_section_m2":.0458,
        "flight_finish_section_m2":.0215,
        "flight_total_section_m2":.0890,
        "flight_deadload_kPa":8.41,
        "flight_step_cell_deadload_kN_per_m":2.14,
        "flight_service_kPa":11.41,
        "flight_worksheet_factored_kPa":17.11,
        "flight_worksheet_full_width_line_kN_per_m":20.53,
        "landing_dead_waist_kPa":3.75,
        "landing_finish_kPa":1.22,
        "landing_service_kPa":7.97,
        "landing_worksheet_factored_kPa":11.95,
        "landing_worksheet_full_width_line_kN_per_m":14.34,
        "unreconciled_BC_combined_line_load_kN_per_m":17.83,
        "AB_source_maximum_moment_kNm":20.88,
        "AB_source_maximum_shear_kN":21.98,
        "BC_source_maximum_moment_kNm":14.96,
        "BC_source_maximum_shear_kN":18.48,
        "AB_source_required_steel_area_number_mm2":383.62,
        "BC_source_required_steel_area_number_mm2":234.68,
    }
    checks={
        "step_area":case["source_cell_area_reconstruction_m2_per_m_width"]["triangular_step"],
        "inclined_waist_area":case["source_cell_area_reconstruction_m2_per_m_width"]["inclined_waist"],
        "finish_area":case["source_cell_area_reconstruction_m2_per_m_width"]["finish_horizontal_and_vertical_assumed"],
        "total_area":case["source_cell_area_reconstruction_m2_per_m_width"]["total"],
        "dead_kPa":case["flight_deadload_from_reconstructed_section_kPa"],
        "step_cell_DL_kN_per_m":case["flight_deadload_per_unit_width_per_tread_kN_per_m"],
        "service_kPa":case["flight_service_kPa"],
        "worksheet_factored_kPa":case["flight_worksheet_factor_1p5_DL_plus_LL_kPa"],
        "worksheet_factored_line_kN_per_m":
            case["flight_worksheet_full_width_line_load_kN_per_m"],
        "landing_service_kPa":case["landing_service_kPa"],
        "landing_worksheet_kPa":case["landing_worksheet_factor_1p5_DL_plus_LL_kPa"],
        "landing_worksheet_line_kN_per_m":
            case["landing_worksheet_full_width_line_load_kN_per_m"],
    }
    source_numbers={
        "step_area":.0216,"inclined_waist_area":.0458,
        "finish_area":.0215,"total_area":.0890,
        "dead_kPa":8.41,"step_cell_DL_kN_per_m":2.14,
        "service_kPa":11.41,"worksheet_factored_kPa":17.11,
        "worksheet_factored_line_kN_per_m":20.53,
        "landing_service_kPa":7.97,
        "landing_worksheet_kPa":11.95,
        "landing_worksheet_line_kN_per_m":14.34,
    }
    # Source table rounds to 2–4 decimals. This tolerance concerns matching
    # printed rounded values, not structural safety and NOT a code tolerance.
    diffs={k:checks[k]-source_numbers[k] for k in checks}
    source_arithmetic_reproduced=all(abs(v)<=.01000001 for v in diffs.values())
    design_load_difference=(
        case["flight_worksheet_factor_1p5_DL_plus_LL_kPa"]-
        case["flight_report_declared_1p2_DL_plus_1p5_LL_kPa"])
    draw_counterfactual=worksheet_geometry_and_loads(
        riser_mm=180.,tread_mm=255.,waist_mm=150.,
        finish_thickness_mm=50.8,flight_gamma_kN_m3=24.,
        flight_width_m=1.2,imposed_stair_kPa=3.,
        landing_waist_mm=150.,landing_gamma_kN_m3=25.,
        landing_finish_kPa=1.22,imposed_landing_kPa=3.)
    return {
        "schema":SCHEMA,
        "classification":"WORKSHEET_ARITHMETIC_REPRODUCED__REAL_CODE_AND_SPAN_HOLD",
        "source_report_url":REVISED_REPORT,
        "source_report_sha256":REPORT_SHA256,
        "source_report_physical_pdf_pages":[64,65],
        "source_drawing_url":DRAWING,
        "source_drawing_sha256":DRAWING_SHA256,
        "source_drawing_physical_pdf_page":16,
        "worksheet_original_printed_values":published,
        "report_170_254_worksheet_reconstruction":case,
        "source_arithmetic_absolute_differences":diffs,
        "source_numbers_reproduced_with_printed_precision":source_arithmetic_reproduced,
        "flight_combo_difference_kPa":design_load_difference,
        "flight_combo_difference_fraction_of_worksheet":
            design_load_difference/case["flight_worksheet_factor_1p5_DL_plus_LL_kPa"],
        "landing_combo_difference_kPa":
            case["landing_worksheet_factor_1p5_DL_plus_LL_kPa"]-
            case["landing_report_declared_1p2_DL_plus_1p5_LL_kPa"],
        "report_general_load_combo_source":"Revised report physical PDF page 19, section 2.8.1",
        "report_worked_stair_combos_source":"Revised report physical PDF page 64, section 6.4.1",
        "drawing_180_255_counterfactual_NOT_project_load":draw_counterfactual,
        "occupancy_description_conflict":{
            "drawing_STR16":"CLASS B (Residential+Commercial)",
            "revised_analysis_cover":"Residential building",
            "applicable_imposed_load_and_permit_occupancy_unresolved":True,
        },
        "different_material_densities_in_same_source":{
            "summary":20.,"source_materials_plain_concrete":24.,
            "source_materials_reinforced_concrete":25.,
            "worksheet_flight":24.,"worksheet_landing":25.,
            "reconciled_for_actual_project":False,
        },
        "manual_design_effects_unverified":{
            "AB_maximum_moment_kNm":20.88,
            "BC_maximum_moment_kNm":14.96,
            "AB_maximum_shear_kN":21.98,
            "BC_maximum_shear_kN":18.48,
            "reported_BC_line_load_kN_per_m":17.83,
            "effective_spans_and_support_condition_from_sources_verified":False,
            "not_recalculated_or_approved":True,
        },
        "code_references_for_qualified_engineer":{
            "NBC_105_2025_government":OFFICIAL_NBC105_PAGE,
            "NBC_103_imposed_government":OFFICIAL_NBC103_PAGE,
            "IS456_stair_clause_33":IS456_33_REFERENCE,
        },
        "resolved_research_items":[
            "REPRODUCE_FLIGHT_DEAD_LOAD_8P41_FROM_PRINTED_STEP_WAIST_FINISH_AREAS",
            "REPRODUCE_REPORTED_FLIGHT_17P11_FACTORED_INTENSITY",
            "REPRODUCE_LANDING_3P75_PLUS_1P22_PLUS_3_AND_11P95_FACTORED",
        ],
        "engineering_holds":[
            "SOURCE_REPORT_1P5_DL_PLUS_LL_VS_1P2_DL_PLUS_1P5_LL_DESIGN_BASIS",
            "CODE_LOAD_ENVELOPE_AND_NBC105_2025_NBC103_BUILDING_CLASS_VERIFICATION",
            "DRAWING_RESIDENTIAL_PLUS_COMMERCIAL_VS_REPORT_RESIDENTIAL_OCCUPANCY",
            "FINISH_AREA_INFERENCE_MATERIAL_DENSITY_AND_FINISH_ACTUAL_WEIGHT",
            "REPORT_20_VS_24_VS_25_KN_M3_CONCRETE_UNIT_WEIGHT_CONFLICT",
            "REPORT_170_254_VS_STR16_180_255_GEOMETRY",
            "SOURCE_150MM_WAIST_VS_WORKED_127MM_FLEXURAL_SECTION",
            "ABC_17P83_KN_PER_M_LANDING_FLIGHT_DISTRIBUTION_UNVERIFIED",
            "AB_AND_BC_BENDING_SHEAR_SPANS_SUPPORTS_NOT_RECONSTRUCTIBLE",
            "STAIRCASE_TO_LANDING_SUPPORT_XYZ_AND_3D_CONNECTION_NOT_VERIFIED",
            "ORIGINAL_F3_ONE_WAY_SHEAR_NOT_SAFE",
            "R6P36_SLAB_SP16_BENCHMARK_DISCREPANCY",
        ],
        "flight_or_landing_effective_span_m":None,
        "actual_staircase_FEM_completed":False,
        "construction_design_approved":False,
        "engineering_approval":False,
        "source_originals_preserved":True,
    }
