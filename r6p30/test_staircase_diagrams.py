import pytest
from r6p30.staircase_diagrams import audit, reconstruct
from r6p30.staircase_geometry import StaircaseGeometryHold


def test_readback_and_withheld_moment_comparison():
    a=audit()
    assert a["source_physical_pdf_pages"]==[64,65]
    ab=a["cases"]["AB"]["conditional_static_reconstruction"]
    bc=a["cases"]["BC"]["conditional_static_reconstruction"]
    assert ab["inferred_line_span_m"]==pytest.approx(3.5052)
    assert bc["inferred_line_span_m"]==pytest.approx(2.9972)
    assert ab["inferred_central_patch_m"]==pytest.approx(1.0307251908396942)
    assert bc["inferred_central_patch_m"]==pytest.approx(.7619847328244282)
    assert ab["predicted_peak_M_kNm"]==pytest.approx(20.930865135534347)
    assert bc["predicted_peak_M_kNm"]==pytest.approx(14.963409239847326)
    assert abs(ab["moment_relative_difference_pct"])<.25
    assert abs(bc["moment_relative_difference_pct"])<.01
    for c in (ab,bc):
        assert c["equilibrium_force_residual_kN"]==pytest.approx(0,abs=1e-10)
        assert c["predicted_peak_M_kNm"]==pytest.approx(c["section_resultant_peak_M_kNm"])
        d=c["signed_shear_and_moment_diagram"]
        assert d[0]["M_kNm"]==pytest.approx(0,abs=1e-10)
        assert d[-1]["M_kNm"]==pytest.approx(0,abs=1e-10)
        assert d[0]["V_kN"]==pytest.approx(-d[-1]["V_kN"])
        assert min(abs(p["V_kN"]) for p in d)<1e-10
        assert c["reaction_is_calibration_not_independent_validation"]
        assert c["actual_project_support_span_m"] is None
        assert c["actual_project_reactions_kN"] is None
        assert c["actual_project_deflection_mm"] is None
        assert not c["engineering_approval"]
    assert not a["actual_staircase_FEM_completed"]
    assert not a["engineering_approval"]


def test_withheld_moment_does_not_change_calibrated_geometry():
    x=dict(q0=11,q1=16.24,moment_station=1.7526,source_shear=-21.9791)
    a=reconstruct(**x,source_moment=20.8813)
    b=reconstruct(**x,source_moment=99)
    for k in ("inferred_line_span_m","inferred_central_patch_m","predicted_peak_M_kNm"):
        assert a[k]==b[k]
    assert a["moment_residual_kNm"]!=b["moment_residual_kNm"]


@pytest.mark.parametrize("key,value",[
    ("q0",0),("q1",11),("q1",float("nan")),
    ("source_shear",21.9791),("source_shear",-2),
    ("source_shear",-80),("moment_station",0),("source_moment",False)])
def test_inconsistent_inputs_rejected(key,value):
    x=dict(q0=11,q1=16.24,moment_station=1.7526,source_shear=-21.9791,source_moment=20.8813)
    x[key]=value
    with pytest.raises(StaircaseGeometryHold):
        reconstruct(**x)
