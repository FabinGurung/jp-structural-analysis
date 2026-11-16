"""Independent original-DXF footings / source SAR / OpenSees reaction crosswalk QA."""
from __future__ import annotations
import os,json
from pathlib import Path
import pytest
from r6p27.source_design import make_crosswalk,publish,verify,SCHEMA,SCHEDULE,interp_square

def test_exact_original_scheduled_takeoff():
    assert sum(n*l*b*.5 for n,l,b in SCHEDULE.values()) == pytest.approx(36.915)
    assert sum(n for n,_,_ in SCHEDULE.values()) == 21
    assert interp_square(1.8) == pytest.approx(172.6)
    assert interp_square(2.1) == pytest.approx(179.8)
    assert interp_square(2.4) == pytest.approx(187.6)

@pytest.fixture(scope="module")
def inputs():
    cad=os.environ.get("R6P25_CAD_ROOT")
    site=os.environ.get("R6P27_SITE")
    if not cad or not site:
        pytest.skip("Run with pinned CAD checkout and solved R6.26 output")
    return Path(cad),Path(site)

def test_source_21_footings_all_23_columns_and_g1_difference(inputs):
    d=make_crosswalk(*inputs)
    assert d["schema"]==SCHEMA
    assert len(d["footings"])==21
    colrefs=[s for f in d["footings"] for s in f["source_support_column_ids"]]
    assert len(colrefs)==23 and len(set(colrefs))==23
    assert d["footing_quantities"]["source_scheduled_concrete_m3"]==36.915
    assert d["footing_quantities"]["original_dxf_drawn_concrete_m3"]==36.33
    g1=[f for f in d["footings"] if f["grid_axes"]==["G1"]]
    assert len(g1)==1 and g1[0]["area_discrepancy_m2"]==-1.17
    assert all(f["trial_DL_column_reactions_kN"]>0 for f in d["footings"])
    assert all(not f["actual_construction_permission"] for f in d["footings"])

def test_original_sar_c4_longitudinal_ratio_below_nbc_2025_minimum(inputs):
    d=make_crosswalk(*inputs)
    c4=next(c for c in d["column_schedule"] if c["family"]=="C4")
    assert c4["count"]==6 and c4["reported_schedule_pct"]==pytest.approx(.940,abs=.0005)
    assert c4["minimum_NBC105_2025_gross_pct"]==1.0
    assert c4["code_comparison"].startswith("BELOW_1_PERCENT")
    assert d["original_F3_unsafe_retained"] and not d["construction_release"]
    sections=d["source_beam_slab_reinforcement_arithmetic"]
    assert len(sections)==6 and all(x["construction_issue_approved"] is False for x in sections)
    assert sections[0]["nominal_rebar_area_mm2"]==pytest.approx(339.292,abs=.001)
    assert sections[1]["nominal_rebar_area_mm2"]==pytest.approx(1005.31,abs=.01)
    assert sections[2]["nominal_rebar_area_mm2"]==pytest.approx(515.22,abs=.01)
    assert sections[3]["nominal_rebar_area_mm2"]==pytest.approx(565.487,abs=.001)
    assert sections[-1]["nominal_rebar_area_mm2"]==pytest.approx(335.103,abs=.002)

def test_publish_data_and_html_are_source_derived_and_hash_locked(inputs):
    cad,site=inputs
    m=publish(cad,site)
    assert verify(site)==m
    assert m["C4_code_minimum_ratio_failure"] and m["historical_F3_unsafe"]
    assert m["construction_approved"] is False
    page=(site/"r6p27-construction-review.html")
    text=page.read_text()
    for term in ("36.915","36.330","0.940","G1","NOT SAFE IN ONE WAY SHEAR",
                 "id='loads'","id='members'","R6.26 OpenSees","Plinth beam","GF main beam","Slab top and bottom"):
        assert term in text,term
    data=json.loads((site/"reports/r6p27/source-design-crosswalk.json").read_text())
    assert len(data["footings"])==21 and data["source_Gf_column_count"]==23
    assert data["source_original_DXF_sha"]=="259d11e1543e4ba7040373a752b823396e12d7f8"
    page.write_text(text+"NOT_VERIFIED")
    with pytest.raises(ValueError,match="SHA256"):
        verify(site)
