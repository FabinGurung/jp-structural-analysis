"""Original Narayani revised ETABS PDF p61 F3: independently auditable shear screen.

Original verdict is NOT SAFE. Screen assumes a centred column and uniform soil
pressure; not physical-model acceptance, not a construction release.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

PDF="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
PDF_SHA="f122904444a2e2f75230d9d4e41da0093d050da25c6e8140c86d466b7e37cc52"
CODE="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf"
def calc():
    length=2.10
    breadth=2.10
    column=.36
    depth=450.0
    cover=50.0
    bar=12.0
    spacing=150.0
    original_p=571.0
    w_self=600.0
    report_v=172.3
    q=1.5*original_p/(length*breadth)
    area_m=math.pi*bar**2/4*1000/spacing
    projection=(length-column)/2
    cases={}
    for label,d_mm in (("worksheet_steel_formula_d_not_verified",423.46278),
                       ("bottom_mesh_lower_bar_layer",depth-cover-bar/2),
                       ("bottom_mesh_upper_crossing_layer",depth-cover-bar/2-bar)):
        d=d_mm/1000
        Vu=q*breadth*(projection-d)
        stress=Vu*1000/(breadth*1000*d_mm)
        pt=100*area_m/(1000*d_mm)
        cases[label]=dict(d_mm=round(d_mm,5),Vu_kN=round(Vu,5),
                          tau_v_MPa=round(stress,6),
                          provided_bar_steel_percent=round(pt,6),
                          shear_demand_over_printed_0p2=round(stress/.2,5),
                          M20_table19_minimum_tau_c_MPa=.28,
                          below_table19_minimum=stress<.28)
    assert round(q,2)==194.22
    assert round(cases["bottom_mesh_lower_bar_layer"]["Vu_kN"],2)==194.14
    assert all(x["tau_v_MPa"]>.2 and x["below_table19_minimum"] for x in cases.values())
    implied=(projection-report_v/(q*breadth))*1000
    assert implied>440
    return dict(schema="jp.structural.narayani.f3_shear_source_verification.v1",
        source_pdf=PDF,source_pdf_sha256=PDF_SHA,source_printed_page=61,
        source_original_kN=dict(axial=original_p,allowance=w_self,
              reported_one_way_Vu=report_v,reported_two_way_Vu=730.6),
        source_original_geometry_mm=dict(footing_L=2100,footing_B=2100,column=360,overall_D=450),
        source_reported_q_factored_kPa=194.22,
        source_reported_steel_calc_effective_d_mm=423.46278,
        source_reported_printed_tau_allowable="0.2 [printed N/m2; stress intended N/mm2]",
        source_one_way_verdict="NOT SAFE IN ONE WAY SHEAR",
        code_reference=CODE, code_clauses=["IS 456:2000 34.2.4.1","IS 456:2000 Table 19 M20"],
        assumptions=["centred square column and uniform net factored upward soil pressure",
                     "original 50mm bottom clear cover; bottom Ø12 bars at 150mm",
                     "orthogonal bar stacking changes effective depth by one bar diameter",
                     "continuity/anchorage and section geometry unconfirmed",
                     "no eccentric moment or uplift; actual original factored reactions unavailable"],
        source_selfweight_average_kPa=round(w_self/(length*breadth),5),
        reconstructed_factored_q_kPa=round(q,5),
        assumed_bar_area_mm2_per_m_per_direction=round(area_m,5),
        worksheet_printed_steel_area_mm2_per_m=464.9673,
        one_way_cases=cases,
        source_Vu_implied_d_mm=round(implied,5),
        original_minus_bottom_layer_Vu_kN=round(report_v-cases["bottom_mesh_lower_bar_layer"]["Vu_kN"],5),
        independently_verified_result="WORKSHEET_Q_REPRODUCED__SHEAR_VU_NOT_REPRODUCED",
        conditional_IS456_result="CONCENTRIC_ASSUMED_CASE_STRESS_BELOW_M20_TABLE19_LOWEST_ROW",
        source_discrepancies=["original F3 Vu=172.3 kN implies d≈447.55mm vs physical 394/382mm from stated cover",
          "worksheet nominal and permissible stress 0.2 with wrong unit label",
          "M20 Table19 lowest τc 0.28MPa vs worksheet 0.2 value",
          "worksheet d423.46 appears in steel area block, not verified actual bar centre",
          "worksheet 464.9673mm2/m vs Ø12@150 prescribed 753.982mm2/m"],
        engineering_approval=False,construction_release=False,
        original_f3_not_safe_preserved=True,
        physical_footing_code_compliant=None)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    d=calc()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
    print("F3_ORIGINAL_SOURCE_Q_VERIFIED_SHEAR_DISCREPANCY_REPRODUCED",
          d["one_way_cases"]["bottom_mesh_lower_bar_layer"])
if __name__=="__main__":main()
