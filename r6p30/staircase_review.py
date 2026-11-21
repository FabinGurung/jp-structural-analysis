"""R6.37 Narayani staircase source reconciliation and bounded hand-calculation audit.

NOT a modeled staircase, not an issued bar schedule, not engineering approval.
Original text-extracted drawing/report values are kept separate. A source
moment of 20.88 kN.m has an UNRESOLVED 1.2m-full-flight versus 1m-strip
normalization: both interpretations are shown, never silently selected.

Only IS456 singly-reinforced rectangular section flexure and geometric
dead-load arithmetic are calculated. No signed staircase OpenSees responses,
support condition, landing redistribution, deflection or actual loads.
"""
from __future__ import annotations

import math
from r6p30.staircase_geometry import observed_geometry_review

DRAWING = "https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
REVISED_REPORT = "https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
CODE = "https://www.cracindia.in/admin/uploads/IS-456.pdf"
SCHEMA = "jp.sar.r6p37.staircase_source_reconciliation.v1"


def finite(value, label, *, positive=True):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("STAIRCASE HOLD: " + label + " must be finite numeric")
    value = float(value)
    if positive and value <= 0:
        raise ValueError("STAIRCASE HOLD: " + label + " must be positive")
    return value


def flexural_strip(*, mu_kNm_m, D_mm, d_mm, bar_diameter_mm,
                  bar_spacing_mm, fck_MPa=20., fy_MPa=500.):
    """IS456 38.1/Annex G, b=1000mm. No dual-rebar or compression-steel theory."""
    M = finite(mu_kNm_m, "moment", positive=False)
    if M < 0:
        raise ValueError("STAIRCASE HOLD: negative moment not enveloped")
    D = finite(D_mm, "overall depth")
    d = finite(d_mm, "effective depth")
    phi = finite(bar_diameter_mm, "bar diameter")
    s = finite(bar_spacing_mm, "bar spacing")
    fck = finite(fck_MPa, "concrete grade")
    fy = finite(fy_MPa, "steel grade")
    if not (d < D and phi < s and phi <= D / 8 and fck in (20., 25.)
            and fy in (415., 500.)):
        raise ValueError("STAIRCASE HOLD: geometry, bar diameter or material scope")
    b = 1000.
    xulim = (.48 if fy == 415. else .46) * d
    Mlim = .36 * fck * b * xulim * (d - .42*xulim) / 1e6
    As = math.pi * phi**2 / 4 * (1000. / s)
    As_min = .0012 * b * D
    xu = .87 * fy * As / (.36 * fck * b)
    spacing_ok = s <= min(3*d, 300.)
    ductile_limit_ok = xu <= xulim + 1e-9
    Mres = (.87*fy*As*(d-.42*xu)/1e6) if ductile_limit_ok else None
    coeff = .42*(.87*fy)**2/(.36*fck*b)
    lin = .87*fy*d
    discr = lin**2 - 4*coeff*M*1e6
    As_req = ((lin-math.sqrt(max(discr,0.)))/(2*coeff))
    if M > Mlim+1e-10 or discr < -1e-5:
        As_req = None
    arithmetic_recovered_M = (
        .87*fy*As_req*(d - .42*(.87*fy*As_req/(.36*fck*b)))/1e6
        if As_req is not None else None
    )
    ok = (As_req is not None and spacing_ok and ductile_limit_ok
          and As >= As_min and Mres is not None and M <= Mres+1e-8)
    return {
        "source_moment_kNm_per_m_if_interpretation_valid": M,
        "D_mm": D, "d_mm": d, "width_mm": b,
        "As_provided_mm2_per_m": As, "As_min_mm2_per_m": As_min,
        "As_required_mm2_per_m": As_req,
        "back_substitution_Mu_kNm_per_m": arithmetic_recovered_M,
        "neutral_axis_xu_mm": xu, "xu_limit_mm": xulim,
        "provided_Mu_kNm_per_m_if_ductile": Mres,
        "M_lim_kNm_per_m": Mlim,
        "minimum_steel_ok": As >= As_min,
        "bar_spacing_ok": spacing_ok,
        "singly_reinforced_ductile_limit_ok": ductile_limit_ok,
        "bounded_section_flexure_ok": bool(ok),
        "status": "BOUNDED_SECTION_SCREEN_ONLY" if ok else "SECTION_HOLD",
        "engineering_approval": False,
    }


def published_nptel_staircase_benchmark():
    """IIT Kharagpur NPTEL Lesson 20 Example 9.1, stair waist only.

    Published 102.08 kN.m is the 1.5m full-width flight moment, NOT a
    one-metre strip moment. Published steel area is 920.64 mm2 per metre.
    Compare independent IS456 strain-block quadratic using declared d=224,
    D=250, M20/Fe415 and provided 12mm @120. Never use these values for
    Narayani nor assert validated entire longitudinal staircase load path.
    """
    source="https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m9l20.pdf"
    width_m=1.5
    source_Mu_kNm=102.08
    source_As_mm2_m=920.64
    x=flexural_strip(
        mu_kNm_m=source_Mu_kNm/width_m,D_mm=250,d_mm=224,
        bar_diameter_mm=12,bar_spacing_mm=120,fck_MPa=20,fy_MPa=415)
    deviation=(x["As_required_mm2_per_m"]-source_As_mm2_m)/source_As_mm2_m
    return {
        "source":source,
        "source_organization":"IIT Kharagpur / NPTEL",
        "source_lesson":"Lesson 20 Example 9.1, waist slab reinforcement",
        "source_total_factored_moment_kNm_for_1p5m_width":source_Mu_kNm,
        "source_waist_width_m":width_m,
        "moment_normalized_kNm_per_m":source_Mu_kNm/width_m,
        "source_effective_depth_mm":224.,
        "source_waist_overall_depth_mm":250.,
        "source_fck_MPa":20.,"source_fy_MPa":415.,
        "source_required_steel_mm2_m":source_As_mm2_m,
        "independent_required_steel_mm2_m":x["As_required_mm2_per_m"],
        "independent_provided_steel_mm2_m":x["As_provided_mm2_per_m"],
        "relative_stress_block_vs_SP16_difference":deviation,
        "within_predeclared_1pct_research_band":abs(deviation)<.01,
        "independent_bar_section_screen_ok":x["bounded_section_flexure_ok"],
        "not_complete_staircase_loading_or_reactions_benchmark":True,
        "not_a_Narayani_building_design":True,
        "engineering_approval":False,
    }


def review():
    """Source-led numerical audit; moments/support paths are not design-approved."""
    # Visually reviewed July 2026 original structural PDF page 16, sheet STR-16.
    drawing = {
        "source": DRAWING, "source_sheet": "STR-16, July 2026",
        "riser_mm": 180., "tread_mm": 255., "waist_D_mm": 150.,
        "main_bar_diameter_mm": 12., "main_spacing_mm": 125.,
        "distribution_bar_diameter_mm": 8., "distribution_spacing_mm": 150.,
        "number_of_identified_flight_details": 3,
        "concrete_grade_MPa": 20., "steel_grade_MPa": 500.,
    }
    # Revised analysis page 64/65 extraction, with contradictory design depth.
    source_report = {
        "source": REVISED_REPORT, "section": "6.4.1 STAIRCASE DESIGN",
        "riser_mm": 170., "tread_mm": 254., "flight_width_mm": 1200.,
        "waist_D_declared_mm": 150., "waist_D_used_in_flexure_mm": 127.,
        "worked_effective_depth_mm": 106.,
        "main_bar_diameter_mm": 12., "main_spacing_mm": 127.,
        "reported_maximum_BM_kNm": 20.88,
        "reported_required_As_number_mm2": 383.62,
        "reported_flight_dead_kPa": 8.41,
        "reported_flight_live_kPa": 3.,
        "worksheet_unit_weight_kN_m3": 24.,
        "summary_unit_weight_kN_m3": 20.,
        "concrete_grade_MPa": 20., "steel_grade_MPa": 500.,
    }
    # 15mm clear stair cover is a report-declared number, NOT independently
    # confirmed on the drawing or inspected on the constructed staircase.
    assumed_clear_cover = 15.
    drawing_d = drawing["waist_D_mm"] - assumed_clear_cover - drawing["main_bar_diameter_mm"]/2
    report_d = source_report["worked_effective_depth_mm"]
    full_moment = source_report["reported_maximum_BM_kNm"]
    report_width_m = source_report["flight_width_mm"] / 1000.
    variants = {
        "if_20p88_is_a_full_1p2m_flight_moment":
            flexural_strip(mu_kNm_m=full_moment/report_width_m,
                          D_mm=127., d_mm=report_d, bar_diameter_mm=12.,
                          bar_spacing_mm=127.),
        "if_20p88_is_already_per_one_metre_strip":
            flexural_strip(mu_kNm_m=full_moment,
                          D_mm=127., d_mm=report_d, bar_diameter_mm=12.,
                          bar_spacing_mm=127.),
    }
    drawing_conditional = flexural_strip(
        mu_kNm_m=full_moment, D_mm=150., d_mm=drawing_d,
        bar_diameter_mm=12., bar_spacing_mm=125.)
    angle = math.atan(source_report["riser_mm"]/source_report["tread_mm"])
    density = source_report["worksheet_unit_weight_kN_m3"]
    waist_dead_kPa = density * .15 / math.cos(angle)
    step_dead_kPa = density * (.170 / 2)
    reported_As = source_report["reported_required_As_number_mm2"]
    return {
        "schema": SCHEMA, "classification": "RESEARCH_HOLD",
        "drawing": drawing, "revised_report": source_report,
        "assumed_clear_cover_mm_for_drawing_case": assumed_clear_cover,
        "assumed_drawing_effective_depth_mm": drawing_d,
        "report_moment_normalization_unresolved": True,
        "report_moment_interpretations": variants,
        "source_report_As_value_without_verified_strip_units_mm2": reported_As,
        "computed_As_minus_source_number_if_same_units_mm2_per_m": {
            key: x["As_required_mm2_per_m"]-reported_As
            for key,x in variants.items()},
        "drawing_150mm_waist_conditional_overlay_NOT_actual_demand":
            drawing_conditional,
        "independent_geometric_load_checks": {
            "riser_tread_angle_degrees": math.degrees(angle),
            "waist_weight_per_horizontal_area_kPa": waist_dead_kPa,
            "triangular_step_weight_per_horizontal_area_kPa": step_dead_kPa,
            "subtotal_excluding_finishes_kPa": waist_dead_kPa+step_dead_kPa,
            "reported_flight_total_dead_kPa": source_report["reported_flight_dead_kPa"],
            "finishes_and_report_DL_reconciliation": "HOLD",
            "not_a_verified_project_load_combination": True,
        },
        "open_holds": [
            "DRAWING_VS_REPORT_RISER_TREAD_CONFLICT",
            "DECLARED_150MM_WAIST_VS_WORKED_127MM_SECTION",
            "REPORT_GAMMA_20_VS_WORKSHEET_GAMMA_24_KN_M3",
            "SOURCE_20P88_MOMENT_1P2M_VS_1M_UNIT_UNRESOLVED",
            "REPORTED_383P62_REINFORCEMENT_AREA_UNIT_AND_FORMULA_UNRECONCILED",
            "DRAWING_COVER_AND_BAR_CENTROID_NOT_FIELD_VERIFIED",
            "FLIGHT_LANDING_SPANS_BOUNDARIES_SUPPORT_STRIPS_AND_LOAD_PATH_UNKNOWN",
            "LANDING_AND_STAIRCASE_NOT_IN_SYNTHETIC_OPENSEES_MODEL",
            "REAL_SITE_ACTION_COMBINATIONS_SHEAR_DEFLECTION_CRACKING_AND_ANCHORAGE_UNCHECKED",
            "COMPLETE_STAIRCASE_AND_LANDING_FEM_EXTERNAL_BENCHMARK_PENDING",
            "DETAILED_STAIR_SUPPORT_AND_LANDING_COORDINATES_PENDING",
            "F3_ORIGINAL_NOT_SAFE_REMAINS_OPEN",
        ],
        "source_geometry_and_support_gate": observed_geometry_review(),
        "resolved_evidence_items": ["STR-16_DRAWING_PAGE_VISUAL_READBACK",
                                    "STR15_SHEET_MISIDENTIFICATION_CORRECTED"],
        "published_nptel_stair_waist_section_benchmark":
            published_nptel_staircase_benchmark(),
        "staircase_present_in_active_opensees_reference_model": False,
        "staircase_design_approved": False, "engineering_approval": False,
        "source_originals_preserved": True,
        "code_reference": CODE,
    }
