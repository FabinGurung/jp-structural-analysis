"""Full product integration against a fresh OpenSees solve."""
import csv
import json
import pytest
from pathlib import Path
from site_builder import build,verify,DRIVE_ARCHIVE,NAV
from drive_sources import INPUT_HEADERS, SCHEMA, SourceError, project_inputs


def test_drive_summary_keeps_private_source_fields_out_of_pages(tmp_path):
  private_url = "https://drive.google.com/file/d/private-example/view"
  row = ["stair", "Staircase geometry", private_url, "mm", "drawing", "STR-16",
         "Review hold", "Confirm the governing drawing before closing review.", "Yes"]
  inputs = project_inputs([list(INPUT_HEADERS), row], {"drawing"})
  status = {
    "schema": SCHEMA, "engineering_approval": False, "inputs": inputs,
    "notes": ["The working report is a separate reference model."],
    "projects": [{"name": "Narayani", "native_reads": 3, "evidence_links": 4}],
    "read_at_utc": "2026-11-23T00:00:00+00:00",
  }
  dest = tmp_path / "site"
  build(dest, drive_sources=status)
  public = (dest / "data" / "drive-source-status.json").read_text()
  assert private_url not in public
  assert 'id="drive-sources"' in (dest / "projects.html").read_text()
  assert json.loads(public)["engineering_approval"] is False
  report = json.loads((dest / "data" / "report-results.json").read_text())
  assert report["synthetic"] and not report["original_project_engineering_approval"]
  row[7] = private_url
  with pytest.raises(SourceError):
    project_inputs([list(INPUT_HEADERS), row], {"drawing"})

def test_clean_four_route_chaptered_report_and_recovery_links(tmp_path):
  dest=tmp_path/"site"
  receipt=build(dest)
  assert receipt==verify(dest)
  assert len(NAV)==4
  assert set(receipt["pages"])=={
     "index.html","studio.html","projects.html","more.html","report.html"}
  assert receipt["beam_rows"]==256 and receipt["column_rows"]==64
  data=json.loads((dest/"data/report-results.json").read_text())
  assert data["source_loads_kN"]["DL"]==339.
  assert data["source_loads_kN"]["LL"]==62.
  assert data["beam_checks"]["rows_count"]==256
  assert data["column_pmm_checks"]["row_count"]==64
  slab=data["slab_reinforcement_screen"]
  assert slab["rows_count"]==496
  assert slab["shell_cells"]==31
  assert slab["source_SHA256"]==data["model_source_SHA256"]
  assert not slab["engineering_approval"]
  assert not slab["complete_crackwidth_deflection_checked"]
  assert not slab["actual_project_slab_geometry_and_rebar_verified"]
  assert slab["published_oneway_nptel_benchmark"]["computed_analytic_Mu_kNm_m"]==pytest.approx(21.533203125)
  assert slab["published_oneway_nptel_benchmark"]["our_relative_chart_capacity_difference"]<-.03
  assert (dest/"data/slab-checks.csv").exists()
  assert (dest/"data/slab-benchmark.json").exists()
  stair=data["staircase_source_reconciliation"]
  assert stair["drawing"]["waist_D_mm"]==150
  assert stair["revised_report"]["waist_D_used_in_flexure_mm"]==127
  assert stair["report_moment_normalization_unresolved"] is True
  assert stair["staircase_present_in_active_opensees_reference_model"] is False
  assert stair["engineering_approval"] is False
  assert (dest/"data/staircase-source-review.json").exists()
  assert "6.5 Narayani staircase" in (dest/"report.html").read_text()
  assert "6.5.2 Original drawing geometry" in (dest/"report.html").read_text()
  load=data["staircase_worksheet_load_reconciliation"]
  assert "6.5.3 Staircase load worksheet" in (dest/"report.html").read_text()
  assert load["source_numbers_reproduced_with_printed_precision"]
  assert load["flight_combo_difference_kPa"]>2
  assert load["occupancy_description_conflict"]["applicable_imposed_load_and_permit_occupancy_unresolved"]
  assert not load["engineering_approval"]
  assert (dest/"data/staircase-worksheet-loads.json").exists()
  geo=stair["source_geometry_and_support_gate"]
  assert geo["original_drawing"]["drawing_sheet_label"]=="STR-16"
  assert geo["original_drawing"]["pdf_page_1_based"]==16
  assert geo["original_drawing"]["grid_bay_C_to_D_mm"]==4965.
  assert geo["grid_bay_is_not_FEM_effective_span"]
  assert geo["actual_staircase_model_ready"] is False
  assert geo["engineering_approval"] is False
  assert (dest/"data/staircase-geometry.json").exists()
  bm=stair["published_nptel_stair_waist_section_benchmark"]
  assert bm["within_predeclared_1pct_research_band"]
  assert bm["source_required_steel_mm2_m"]==pytest.approx(920.64)
  assert bm["independent_required_steel_mm2_m"]==pytest.approx(921.2607899924,abs=.001)
  assert not bm["engineering_approval"]
  assert "6.5.1 External NPTEL staircase" in (dest/"report.html").read_text()
  assert "1MVWeuQEEqKlcngzOFyU3JShvJE-7_yByvWJYiQJRd90" in (dest/"report.html").read_text()
  assert "1MVWeuQEEqKlcngzOFyU3JShvJE-7_yByvWJYiQJRd90" in (dest/"more.html").read_text()
  assert "6.4 Slab reinforcement" in (dest/"report.html").read_text()
  assert "Slab bending and transverse-shear evidence" in (dest/"more.html").read_text()
  assert "https://drive.google.com/drive/folders/1u-vkOxS7VuOQMKe908HeeP-VlGmRxTfn" in (dest/"more.html").read_text()
  assert "https://drive.google.com/file/d/1Jppw9fFZ9p28IQbmBN3ezpVMTvJXJOyG/view" in (dest/"more.html").read_text()
  assert "Full slab QA engineering review in Drive" in (dest/"report.html").read_text()

  assert not data["original_project_engineering_approval"]
  assert data["original_narayani_F3_NOT_SAFE"]
  assert data["column_pmm_checks"]["source_SHA256"]==data["model_source_SHA256"]
  assert data["beam_checks"]["source_fixture_sha256"]==data["model_source_SHA256"]
  assert data["column_pmm_checks"]["approx_screen_ok_count"]<=64
  assert data["column_pmm_checks"]["axial_tension_rows_excluded"]==0
  assert data["column_pmm_checks"]["local_column_I_J_force_sign_reviewed_on_fixture"]
  assert data["column_capacity_verification"]["relative_pure_axial_error"]<.001
  ext=data["column_capacity_verification"]["external_sp16_nptel_reference"]
  assert ext["reference_major_M_kNm"]==246.376
  assert ext["reference_minor_M_kNm"]==215.156
  assert ext["both_axes_within_benchmark_band"] is True
  assert abs(ext["major_relative_difference"])<.03
  assert abs(ext["minor_relative_difference"])<.03
  assert ext["full_SP16_chart_verification"] is False
  assert data["column_capacity_verification"]["external_sp16_nptel_twenty_bar_reference"]["published_Mu_kNm"]==pytest.approx(116.04,abs=.01)
  assert abs(data["column_capacity_verification"]["external_sp16_nptel_twenty_bar_reference"]["relative_difference"])<.03
  assert data["column_capacity_verification"]["steel_stress_at_uniform_epsilon_0002_MPa"]<400
  f3=data["f3_proposed_concentric_redesign_study"]
  assert f3["original_report_F3_status"]=="NOT SAFE IN ONE WAY SHEAR"
  assert f3["historical_not_safe_preserved"]
  assert not f3["approved_for_construction"]
  assert f3["preferred_uniform_revision_550mm"]["uniform_thickness_m"]==.55
  assert f3["preferred_uniform_revision_550mm"]["listed_concentric_checks_pass"]
  assert not f3["original_report_adopted_uniform_trial_450mm"]["concentric_check_flags"]["source_report_tau_0p20"]
  assert (dest/"data/f3-trial.json").exists()
  assert "6.3 Narayani F3" in (dest/"report.html").read_text()
  assert "R6.35 engineer-review PDF" in (dest/"more.html").read_text()
  assert "NOT SAFE" in (dest/"projects.html").read_text()
  assert "550mm" in (dest/"projects.html").read_text()

  assert ext["construction_approval"] is False
  assert "M20" in ext["source_conflict_preserved"]
  assert "M25" in ext["source_conflict_preserved"]
  assert "6.2.2 Independent published SP16-chart example" in (dest/"report.html").read_text()
  assert "NPTEL SP16 column example" in (dest/"more.html").read_text()
  assert not data["column_capacity_verification"]["sp16_verified"]
  assert (dest/"data/column-verification.json").exists()
  checks=data["column_pmm_checks"]["rows"]
  assert all(x["compression_signed_kN"]>0 for x in checks)
  assert all(x["compression_signed_kN"]==pytest.approx(
       x["signed_local_actions"]["N"] if x["end"]=="I"
       else -x["signed_local_actions"]["N"]) for x in checks)
  assert all(x["PMM"]["minimum_eccentricity_rule"]==
       "ONE_AXIS_AT_A_TIME_WORST_ALTERNATIVE_IS456_25_4" for x in checks)

  assert data["beam_checks"]["isolated_screen_flexure_ok_count"]<=256
  assert DRIVE_ARCHIVE in (dest/"more.html").read_text()
  assert "R6P" not in (dest/"index.html").read_text()
  assert "database id" not in (dest/"projects.html").read_text().lower()
  report=(dest/"report.html").read_text()
  assert all(str(i)+".0 " in report for i in range(1,7))
  assert report.count('class="toc"')==1
  assert "column" in report.lower() and "interaction" in report.lower()
  assert "NOT SAFE" in report
  with (dest/"data/beam-checks.csv").open() as f:
    assert len(list(csv.DictReader(f)))==256
  with (dest/"data/slab-checks.csv").open() as f:
    assert len(list(csv.DictReader(f)))==496
  with (dest/"data/column-pmm-checks.csv").open() as f:
    assert len(list(csv.DictReader(f)))==64

def test_no_archived_experiment_pages_in_active_public_build(tmp_path):
  dest=tmp_path/"site"
  build(dest)
  files={p.name for p in dest.glob("*.html")}
  assert files=={"index.html","studio.html","projects.html","more.html","report.html"}
  assert not any(p.name.startswith("r6p") or "original-report-guide" in p.name
                 for p in dest.rglob("*.html"))
