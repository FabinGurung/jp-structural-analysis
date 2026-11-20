"""Regression: original failed F3, revised concentric trial and missing loads must stay explicit."""
import math
import pytest
from r6p30.footing_f3 import trial,study,SCHEMA
def test_original_footing_failed_but_preferred_revision_is_only_trial():
 z=study()
 assert z["schema"]==SCHEMA
 assert z["original_report_F3_status"]=="NOT SAFE IN ONE WAY SHEAR"
 assert z["historical_not_safe_preserved"]
 assert not z["approved_for_construction"]
 before=z["original_report_adopted_uniform_trial_450mm"]
 after=z["preferred_uniform_revision_550mm"]
 assert before["footing_B_m"]==2.1 and before["uniform_thickness_m"]==.45
 assert before["oneway_tau_v_MPa"]==pytest.approx(.248,abs=.002)
 assert not before["concentric_check_flags"]["source_report_tau_0p20"]
 assert after["footing_B_m"]==2.1 and after["uniform_thickness_m"]==.55
 assert after["oneway_tau_v_MPa"]==pytest.approx(.156,abs=.002)
 assert after["punching_tau_MPa"]==pytest.approx(.443,abs=.002)
 assert after["listed_concentric_checks_pass"] is True
 assert after["oneway_tau_v_MPa"]<.2
 assert after["bending_Mr_kNm_per_m"]>after["bending_Mu_kNm_per_m"]
 assert not after["actual_Mx_My_Vx_Vy_seismic_combinations_verified"]
 assert not after["actual_footing_survey_and_source_slope_verified"]
 assert not after["construction_approval"]
 assert "UNIFORM" in after["this_trial_geometry"]
 assert "SLOPED" in after["original_source_footing_geometry"]
 assert "source 2.1m vs G1 1.8m" in " ".join(z["unresolved_engineering_gates"])
def test_soil_eccentricity_and_cover_sensitivity_remain_gated():
 z=study()
 a=z["cover_75mm_sensitivity_550mm"]
 b=z["preferred_uniform_revision_550mm"]
 assert a["effective_depth_upper_layer_mm"]==pytest.approx(b["effective_depth_upper_layer_mm"]-25.)
 assert a["oneway_tau_v_MPa"]>b["oneway_tau_v_MPa"]
 assert a["listed_concentric_checks_pass"]
 assert b["eccentricity_limit_single_axis_m_if_other_axis_zero"]>.04
 assert b["eccentricity_limit_both_equal_axes_m"]<.03
 assert z["wider_alternative_2250x600mm"]["listed_concentric_checks_pass"]
 assert trial(soil_allow_kPa=100.)["concentric_check_flags"]["soil_concentric"] is False
 assert trial(P_kN=1000.)["listed_concentric_checks_pass"] is False
def test_fail_closed_on_nonphysical_dimensions():
 for kwargs in ({"D_m":.01},{"B_m":.2},{"cover_mm":1000.},
                {"P_kN":float("nan")},{"soil_allow_kPa":-1.}):
  with pytest.raises(ValueError):trial(**kwargs)
