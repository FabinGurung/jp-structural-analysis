"""Contract and source-fidelity tests for four-section public portal."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import PAGES,PRIMARY,ROUTE,load_approved_results,build,verify,VERSION,SCHEMA

def test_exact_four_primary_sections_and_reusable_contract():
    assert PRIMARY==("home","studio","projects","more")
    assert set(ROUTE)==set(PAGES)==set(PRIMARY)
    assert all(len(PAGES[p]["sections"])>=4 for p in PRIMARY)
    assert "Narayani" in str(PAGES["projects"])
    assert "NOT SAFE IN ONE WAY SHEAR" in str(PAGES["more"])
    assert "Approved" not in PAGES["projects"]["status"]
    for file in ("STUDIO_STANDARD.md","project-input-template-v1.json"):
        assert (Path(__file__).parent/file).is_file()
    text=(Path(__file__).parent/"STUDIO_STANDARD.md").read_text()
    assert all(f"V{i}" in text for i in range(1,8))
    assert "Do not copy Narayani" in text
    template=json.loads((Path(__file__).parent/"project-input-template-v1.json").read_text())
    assert template["project_id"] is None
    assert template["review"]["engineering_approval"] is False
    assert template["basis"]["soil_bearing"]["value"] is None
    assert template["qa"]["engineer_review_status"]=="HOLD"

@pytest.fixture
def site(tmp_path):
    s=tmp_path/"site"
    reports=s/"reports/r6p26"
    reports.mkdir(parents=True)
    # Exact public readback fixture as available in an actually running Pages
    # site is supplied by portal CI; otherwise lightweight synthetic, source-
    # classification-preserving fixture exercises only the portal renderer.
    fixture=Path("site-from-live")/"reports/r6p26"
    if fixture.is_dir():
        results=(fixture/"narayani-independent-frame-results.json").read_bytes()
        receipt=(fixture/"narayani-verified-manifest.json").read_bytes()
    else:
        import hashlib
        d={"project_id":"PRJ-000007","professional_engineering_approval":False,
           "construction_release":False,"original_F3_unsafe_status_retained":True,
           "model_counts":{"source_GF_columns":23,"independent_3D_elastic_frame_scenarios":4},
           "source_members":[{"id":f"TEST-{i}"} for i in range(132)],
           "cases":{name:{"signed_local_member_forces":[{"id":f"TEST-{i}"} for i in range(132)],
                          "base_support_reactions":[{"id":f"TEST-{j}"} for j in range(23)]}
                    for name in ("DL","LL","PX10","PY10")}}
        results=(json.dumps(d,sort_keys=True)+"\n").encode()
        m={"engineering_approval":False,"F3_one_way_shear_unsafe_preserved":True,
           "independent_engine_recalculated":True,
           "files_sha256":{"reports/r6p26/narayani-independent-frame-results.json":
               hashlib.sha256(results).hexdigest()}}
        receipt=(json.dumps(m,sort_keys=True)+"\n").encode()
    (reports/"narayani-independent-frame-results.json").write_bytes(results)
    (reports/"narayani-verified-manifest.json").write_bytes(receipt)
    for n in ("index.html","more.html"):
        (s/n).write_text(f"<!doctype html><nav><a href='report.html'>Legacy {n}</a></nav>")
    for f in ("report.html","projects/index.html","r6p23.html","r6p25.html","r6p26-report.html"):
        p=s/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("<h1>Preserved legacy engine route</h1>")
    return s

def test_portal_emits_all_routes_and_preserves_legacy(site):
    older_index=(site/"index.html").read_text()
    older_more=(site/"more.html").read_text()
    m=build(site)
    assert verify(site)==m
    assert (site/"legacy-home.html").read_text()==older_index
    assert (site/"legacy-more.html").read_text()==older_more
    assert all((site/path).is_file() for path in ROUTE.values())
    assert m["version"]==VERSION
    assert m["schema"]==SCHEMA
    assert m["active_real_projects"]==["PRJ-000007"]
    assert m["numeric_scope"]["members"]==132
    assert m["numeric_scope"]["cases"]==4
    assert m["numeric_scope"]["member_end_records"]==1056
    assert m["numeric_scope"]["supports"]==92
    assert m["real_building_engineering_approval"] is False

def test_four_pages_have_clear_navigation_toc_sticky_left_right_and_adjacent(site):
    build(site)
    for k,path in ROUTE.items():
        s=(site/path).read_text()
        assert '<meta name="viewport"' in s
        assert 'id="primary-nav"' in s and 'id="menu-toggle"' in s
        assert 'class="top-toc"' in s
        assert 'class="left-toc"' in s
        assert 'class="right-pane"' in s
        assert 'class="page-adjacent"' in s
        assert f'data-page="{k}"' in s
        assert len([a for a in ROUTE.values() if f'href="{a}"' in s])==4
        for section_id,_,_ in PAGES[k]["sections"]:
            assert s.count(f'data-toc-for="{section_id}"')==2

def test_source_safety_hold_and_release_not_misclassified(site):
    build(site)
    h=(site/"index.html").read_text()
    research=(site/"more.html").read_text()
    assert "GitHub Pages" in h and "Narayani" in h
    assert "NOT SAFE IN ONE WAY SHEAR" in research
    assert "engineer" in research.lower()
    assert "independent-report-guide.html" in research
    assert "engine-explained.html" in research
    assert "example-sar-report.html" in research
    m=json.loads((site/"portal-manifest.json").read_text())
    assert m["frozen_engine_software_sha"]=="1d6394d1d871b070d17f056b6eec4c74efdfb3af"
    assert m["historical_F3_one_way_shear_safe"] is False
    assert m["verified_source_model_ready_for_full_design"] is False
    assert (site/"report.html").read_text().startswith("<h1>Preserved")
    assert len(m["navigation"])==4
    assert "r6p26-report.html" not in (site/"projects.html").read_text()
    assert "Narayani" in (site/"projects.html").read_text()
    assert (site/"independent-report-guide.html").is_file()

def test_mutated_portal_file_must_fail_readback(site):
    build(site)
    p=site/"studio.html"
    p.write_text(p.read_text()+"<p>Unauthorized silent modification</p>")
    with pytest.raises(ValueError,match="tampered"):
        verify(site)

def test_guide_preserves_visually_verified_f3_and_teaches_c4_code_scope():
    from learning_system import SECTIONS
    pages={slug:body for slug, _, body in SECTIONS}
    footing=pages["worked-foundation"]
    chapter6=pages["ch6"]
    assert "NOT SAFE IN ONE WAY SHEAR" in footing
    assert "visually checked" in footing and "PDF page 61" in footing
    assert "571 kN" in footing and "600 kN" in footing
    assert "194.22 kN/m²" in footing and "172.3 kN" in footing
    assert "182.13 kN" in footing and "9.83 kN difference" in footing
    assert "0.9404%" in chapter6 and "1.0%" in chapter6
    assert "applicability of §4.2" in chapter6
    assert "approved redesign" in chapter6


def test_narayani_stage01_has_original_report_facts_and_visible_contradictions(site):
    build(site)
    project=(site/"projects.html").read_text(encoding="utf8")
    part=project.split('id="purpose"',1)[1].split('id="inputs"',1)[0]
    assert "G+1.5" in part and "Residential" in part
    assert "Office Building" in part
    assert "Pokhara" in part and "Leknath" in part
    assert "3.048 m" in part and "9.144 m" in part
    assert "Seismic Zone Kathmandu" in part
    assert "construction permit" in part
    assert "review point" in part.lower()
    assert "application" in part
    assert 'href="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"' in part
    assert "r6p26-report.html" not in part
    assert "actual approved" in part.lower()
    assert (site/"more.html").read_text().count("Office Building")>=1
