"""R6.30: source-governed test of original-format report from real OpenSees FE.

Tests the exact R6.23 synthetic fixture, not a mocked/fabricated FE result.
"""
from __future__ import annotations
import json
from pathlib import Path

from r6p23.engine import build as solve, digest
from r6p23.runner import reference_fixture
from portal.engine_atlas import build,verify,flexural_steel

def test_genuine_solved_synthetic_report_and_engine_inventory(tmp_path):
    spec=reference_fixture()
    actual=solve(spec)
    assert actual["source_ledger"]["gravity_totals_kN"]["DL"]==339.
    assert actual["source_ledger"]["gravity_totals_kN"]["LL"]==62.
    assert not actual["engineering_approval"]
    d={
      "schema":"jp.structural.r6p24.pages_independent_shell_preview.v0.1",
      "case_id":spec["case_id"],"classification":"SYNTHETIC_REFERENCE",
      "source_SHA256":digest(spec),
      "topology":actual["topology"],
      "source_ledger":actual["source_ledger"],
      "solutions":actual["solutions"],
      "engineering_approval":False
    }
    site=tmp_path/"site"
    (site/"data").mkdir(parents=True)
    (site/"data/r6p23-preview.json").write_text(json.dumps(d,allow_nan=False))
    receipt=build(site)
    assert verify(site)==receipt
    nums=json.loads((site/"reports/example-sar/example-sar-numbers.json").read_text())
    assert nums["FE_is_really_computed"]
    assert nums["classification"]=="SOLVED_SYNTHETIC_REFERENCE_AND_SEPARATE_HAND_EXAMPLES"
    assert nums["loads_kN"]["DL"]==339 and nums["loads_kN"]["LL"]==62
    assert nums["topology"]["shell_elements"]==31
    assert nums["topology"]["beam_segments"]==32
    assert nums["topology"]["column_segments"]==8
    assert nums["FE_results"]["max_six_axis_equilibrium_residual"]<1e-3
    assert nums["FE_results"]["max_DL_vertical_disp_mm_flexible"]>0
    assert nums["FE_results"]["selected_signed_beam_envelope"]["absolute_kNm"]>0
    assert nums["sample_member_arithmetic"]["slab"]["As_required_mm2_per_m"]<524
    assert not nums["professional_approval"]
    assert not nums["construction_release"]
    assert nums["original_f3_not_safe_retained"] is True
    html=(site/"example-sar-report.html").read_text()
    for chapter in range(1,7):
        assert f"{chapter}.0 " in html
    assert "339.000" in html and "62.000" in html
    assert 'class="toc"' in html
    atlas=(site/"engine-explained.html").read_text()
    assert "R6.23" in atlas and "R6.28" in atlas
    assert "Original engineer" in atlas
    beam=nums["beam_rc_screens_R6p31"]
    assert beam["beam_count"]==32
    assert beam["rows_count"]==256
    assert len(beam["all_qualifying_beam_end_case_rows"])==256
    assert set(beam["modes"])=={"FLEXIBLE_SHELL","RIGID_INPLANE_MPC"}
    assert beam["source_fixture_sha256"]==nums["source_fixture_sha256"]
    assert beam["combination_factors"]["U_PLUS"]=={"DL":1.2,"LL":1.5,"HX":1.0}
    assert beam["combination_factors"]["U_MINUS"]=={"DL":1.2,"LL":1.5,"HX":-1.0}
    assert beam["governing_bending_row"]["flexure"]["Mu_abs_kNm"]>0
    assert beam["governing_vertical_shear_row"]["shear"]["Vu_abs_kN"]>0
    assert not beam["member_design_complete"]
    assert not beam["professional_engineering_approval"]
    assert not beam["construction_release"]
    assert beam["original_narayani_F3_NOT_SAFE_retained"]
    assert "6.1 Reusable beam flexure and vertical shear" in html
    assert "256 actual OpenSees beam-end combinations" in html
    assert "reports/example-sar/beam-end-checks.csv" in html
    csv=(site/"reports/example-sar/beam-end-checks.csv").read_text()
    assert len(csv.splitlines())==257
    assert "My_kNm" in csv.splitlines()[0] and "Vz_kN" in csv.splitlines()[0]
    assert "T_kNm" in csv.splitlines()[0]


def test_rectangular_RC_formula_closed_form_example():
    result=flexural_steel(16.8,1000,96)
    assert abs(result["As_req_mm2"]-443.9814099)<.01
    assert abs(result["Mu_lim_kNm"]-30.6432)<.0001
    assert flexural_steel(300,300,405)["As_req_mm2"] is None
