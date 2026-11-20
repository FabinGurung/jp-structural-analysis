"""Full product integration against a fresh OpenSees solve."""
import csv
import json
from pathlib import Path
from site_builder import build,verify,DRIVE_ARCHIVE,NAV

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
  assert not data["original_project_engineering_approval"]
  assert data["original_narayani_F3_NOT_SAFE"]
  assert data["column_pmm_checks"]["source_SHA256"]==data["model_source_SHA256"]
  assert data["beam_checks"]["source_fixture_sha256"]==data["model_source_SHA256"]
  assert data["column_pmm_checks"]["approx_screen_ok_count"]<=64
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
  with (dest/"data/column-pmm-checks.csv").open() as f:
    assert len(list(csv.DictReader(f)))==64

def test_no_archived_experiment_pages_in_active_public_build(tmp_path):
  dest=tmp_path/"site"
  build(dest)
  files={p.name for p in dest.glob("*.html")}
  assert files=={"index.html","studio.html","projects.html","more.html","report.html"}
  assert not any(p.name.startswith("r6p") or "original-report-guide" in p.name
                 for p in dest.rglob("*.html"))
