"""R6.41 bounded reconstruction of the embedded Narayani AB/BC diagrams.

Revised report physical pp. 64 and 65: visually read the symmetric three-region
load labels and result-panel values. Assume the displayed load labels are
kN/m along a simply supported reference line; neither the actual staircase
nor the physical load widths, span, units or restraints are established.
Calibrate ONLY the central patch length from the displayed support shear.
The displayed peak moment is withheld from calibration and compared afterward.
This is an inverse statics diagnostic, not an independent reaction prediction.
"""
from __future__ import annotations
import math
from r6p30.staircase_geometry import finite, StaircaseGeometryHold, REVISED_REPORT, REPORT_SHA256

SCHEMA = "jp.sar.r6p41.staircase_diagram_reconstruction.v1"
SOURCE_DIAGRAMS = (
    {"flight": "AB", "physical_pdf_page": 64, "outer_load_label": 11.0,
     "central_load_label": 16.24, "source_peak_shear_signed_kN": -21.9791,
     "source_peak_moment_kNm": 20.8813, "source_peak_moment_station_m": 1.7526,
     "source_peak_deflection_mm": 0.267, "worksheet_full_width_line_load_kN_m": 20.53},
    {"flight": "BC", "physical_pdf_page": 65, "outer_load_label": 11.0,
     "central_load_label": 16.24, "source_peak_shear_signed_kN": -18.4810,
     "source_peak_moment_kNm": 14.9635, "source_peak_moment_station_m": 1.4986,
     "source_peak_deflection_mm": 0.138, "worksheet_full_width_line_load_kN_m": 17.83},
)


def section_response(x, *, L, q0, dq, a, b, R):
    """Left-face shear convention and sagging moment in the assumed line."""
    x = finite(x, "diagram station", positive=False)
    if not 0 <= x <= L:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: diagram station outside line")
    u, v = max(0., x-a), max(0., x-b)
    return {"x_m": x, "V_kN": R-q0*x-dq*(u-v),
            "M_kNm": R*x-q0*x*x/2-dq*(u*u-v*v)/2}


def reconstruct(*, q0, q1, moment_station, source_shear, source_moment):
    q0 = finite(q0, "outer diagram load")
    q1 = finite(q1, "central diagram load")
    xmid = finite(moment_station, "peak moment station")
    shear = finite(source_shear, "signed source shear", positive=False)
    M_source = finite(source_moment, "source peak moment")
    if shear >= 0 or q1 <= q0:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: symmetric diagram interpretation invalid")
    L, R, dq = 2*xmid, -shear, q1-q0
    c = (2*R-q0*L)/dq
    if not 0 < c < L:
        raise StaircaseGeometryHold("STAIRCASE SOURCE HOLD: central patch outside hypothetical span")
    a, b = (L-c)/2, (L+c)/2
    peak = q0*L*L/8 + dq*c*(2*L-c)/8
    # Independent segment resultant evaluation at the assumed center, not an
    # additional independent external reference.
    via_sections = R*xmid - q0*xmid*xmid/2 - dq*(xmid-a)**2/2
    total = q0*L + dq*c
    points = sorted(set([0., a, xmid, b, L]+[L*i/40 for i in range(41)]))
    return {
        "classification": "CONDITIONAL_INVERSE_STATIC_DIAGRAM_DIAGNOSTIC",
        "assumed_load_labels_kN_per_m": [q0,q1,q0],
        "inferred_line_span_m": L,
        "inferred_central_patch_m": c,
        "inferred_end_zone_each_m": a,
        "inferred_load_boundaries_m": [0.,a,b,L],
        "reaction_magnitude_used_to_calibrate_patch_kN": R,
        "assumed_support_reactions_kN": [R,R],
        "total_reconstructed_load_kN": total,
        "equilibrium_force_residual_kN": 2*R-total,
        "mean_reconstructed_line_load_kN_m": total/L,
        "predicted_peak_M_kNm": peak,
        "section_resultant_peak_M_kNm": via_sections,
        "source_peak_M_kNm_not_used_for_calibration": M_source,
        "moment_residual_kNm": peak-M_source,
        "moment_relative_difference_pct": 100*(peak-M_source)/M_source,
        "signed_shear_and_moment_diagram": [section_response(x,L=L,q0=q0,dq=dq,a=a,b=b,R=R) for x in points],
        "reaction_is_calibration_not_independent_validation": True,
        "actual_project_support_span_m": None,
        "actual_project_reactions_kN": None,
        "source_load_units_and_effective_width_verified": False,
        "actual_project_deflection_mm": None,
        "engineering_approval": False,
    }


def audit():
    cases = {}
    for d in SOURCE_DIAGRAMS:
        calc = reconstruct(q0=d["outer_load_label"], q1=d["central_load_label"],
                           moment_station=d["source_peak_moment_station_m"],
                           source_shear=d["source_peak_shear_signed_kN"],
                           source_moment=d["source_peak_moment_kNm"])
        cases[d["flight"]] = {"source_visual_readback": d, "conditional_static_reconstruction": calc}
    return {
        "schema": SCHEMA,
        "source_report_url": REVISED_REPORT,
        "source_report_sha256": REPORT_SHA256,
        "source_physical_pdf_pages": [64,65],
        "method": "Assume symmetric simply supported line and central piecewise UDL. Infer L=2*x_peak and c=(2*abs(V)-q0*L)/(q1-q0); evaluate peak M without using source M.",
        "cases": cases,
        "unresolved": [
            "Original diagram load labels lack a separately verified width and combination; the worksheet full-width intensities are different.",
            "The inferred line length is not a verified actual flight, landing or IS456 section 33 effective span.",
            "Load-zone boundaries are calibrated from the source shear, not independently dimensioned.",
            "Neither source deflection, actual support stiffness, actual landing/frame reactions nor 3D continuity is verified.",
            "Original STR-16 vs revised report geometry, occupancy, concrete density and load-factor conflicts remain.",
            "Original F3 one-way shear NOT SAFE and R6.36 slab benchmark disagreement remain.",
        ],
        "actual_staircase_FEM_completed": False,
        "engineering_approval": False,
    }
