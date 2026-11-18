import math
from r6p27.f3_oneway_verification import calc
def test_exact_source_and_pressure():
 d=calc()
 assert d["source_printed_page"]==61
 assert d["source_pdf_sha256"]=="f122904444a2e2f75230d9d4e41da0093d050da25c6e8140c86d466b7e37cc52"
 assert d["source_one_way_verdict"]=="NOT SAFE IN ONE WAY SHEAR"
 assert math.isclose(d["reconstructed_factored_q_kPa"],194.21769,abs_tol=.00001)
 assert math.isclose(d["source_selfweight_average_kPa"],136.05442,abs_tol=.00001)
def test_shear_vs_effective_depth_and_code_table():
 d=calc(); c=d["one_way_cases"]
 assert c["bottom_mesh_lower_bar_layer"]["d_mm"]==394
 assert c["bottom_mesh_upper_crossing_layer"]["d_mm"]==382
 assert math.isclose(c["bottom_mesh_lower_bar_layer"]["Vu_kN"],194.14,abs_tol=.001)
 assert math.isclose(c["bottom_mesh_lower_bar_layer"]["tau_v_MPa"],.234639,abs_tol=.000002)
 assert math.isclose(c["bottom_mesh_upper_crossing_layer"]["tau_v_MPa"],.248111,abs_tol=.000002)
 assert d["source_Vu_implied_d_mm"]>440
 assert d["assumed_bar_area_mm2_per_m_per_direction"]>750
 assert all(x["below_table19_minimum"] for x in c.values())
def test_original_unsafe_retained_and_no_construction_approval():
 d=calc()
 assert d["original_f3_not_safe_preserved"]
 assert d["engineering_approval"] is False and d["construction_release"] is False
 assert d["physical_footing_code_compliant"] is None
