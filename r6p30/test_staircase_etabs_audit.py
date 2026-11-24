"""R6.41 lexical source audit regression; original files are not vendored."""
import pytest
from r6p30.staircase_etabs_audit import audit_export, audit_pair

def fixture(extra_load="", missing_section=False):
    text = '''
$ POINT COORDINATES
POINT "1"  0 0
POINT "2"  0 1200
POINT "3"  1356 1200 846
POINT "4"  1356 0 846
POINT "5"  2556 1200 846
POINT "6"  2556 0 846
$ AREA CONNECTIVITIES
AREA "W6"  PANEL 4 "1" "2" "3" "4" 0 0 0 0
AREA "F21" FLOOR 4 "4" "3" "5" "6" 0 0 0 0
$ AREA ASSIGNS
AREAASSIGN "W6" "GF" SECTION "WAIST SLAB6"""  OBJMESHTYPE "AUTOMESH"
AREAASSIGN "F21" "GF" SECTION "WAIST SLAB6""" OBJMESHTYPE "MESHN1XN2"
AREAASSIGN "F21" "FF" SECTION "WAIST SLAB6""" OBJMESHTYPE "MESHN1XN2"
$ LINE ASSIGNS
LINEASSIGN "B7" "GF" SECTION "SEC BEAM 9X12"
$ LINE CONNECTIVITIES
LINE "B7" BEAM "5" "6" 0
$ SLAB PROPERTIES
SHELLPROP "WAIST SLAB6""" PROPTYPE "Slab" MATERIAL "M20" MODELINGTYPE "ShellThin" SLABTHICKNESS 152.4
$ LOAD PATTERNS
LOADPATTERN "STAIRCASE LOAD" TYPE "Dead" SELFWEIGHT 0
$ LOAD CASES
LOADCASE "STAIRCASE LOAD" TYPE "Linear Static"
$ MASS SOURCE
MASSSOURCELOAD "MsSrc1" "STAIRCASE LOAD" 0.3
$ LOAD COMBINATIONS
COMBO "1.2DL+1.5LL" LOADCASE "STAIRCASE LOAD" SF 1.5
$ POINT OBJECT LOADS
$ FRAME OBJECT LOADS
LINELOAD "B7" "GF" TYPE "UNIFF" DIR "GRAV" LC "WALL LOAD" FVAL 9.25
$ SHELL OBJECT LOADS
AREALOAD "W6" "GF" TYPE "UNIFF" DIR "GRAV" LC "Live" FVAL 0.003
AREALOAD "W6" "GF" TYPE "UNIFF" DIR "GRAV" LC "FLOOR FINISH" FVAL 0.0015
''' + extra_load + "\n$ END OF MODEL FILE\n"
    if missing_section:
        text = text.replace("$ POINT OBJECT LOADS\n", "")
    return text.encode()

def test_empty_named_case_does_not_mean_empty_stair_loading():
    result = audit_export(fixture())
    assert len(result["named_stair_load_pattern_definition"]) == 1
    assert result["zero_named_object_load_rows_observed"] is True
    assert result["named_stair_mass_source_rows"][0]["factor"] == .3
    assert result["named_stair_combination_rows"][0]["factor"] == 1.5
    assert result["object_load_inventory"]["$ SHELL OBJECT LOADS"]["load_pattern_counts"] == {"Live":1,"FLOOR FINISH":1}
    assert len(result["waist_object_loads"]) == 2
    assert len(result["waist_area_assignments"]) == 3
    assert result["actual_reactions_kN"] is None
    assert not result["engineering_approval"]

def test_shared_edge_is_per_story_only():
    result = audit_export(fixture())
    assert result["waist_shared_source_edges"] == [
        {"story":"GF","areas":["W6","F21"],"shared_raw_point_ids":["3","4"]}
    ]
    assert result["waist_raw_point_coordinates"]["3"]["raw_coordinates_mm"] == [1356.,1200.,846.]
    assert not result["physical_global_coordinates_verified"]
    assert not result["actual_support_restraints_verified"]

def test_explicit_assignment_is_not_silently_discarded():
    result = audit_export(fixture('AREALOAD "W6" "GF" TYPE "UNIFF" DIR "GRAV" LC "STAIRCASE LOAD" FVAL 0.002'))
    assert not result["zero_named_object_load_rows_observed"]
    assert len(result["explicit_named_stair_object_load_rows"]) == 1

def test_unparsed_load_or_missing_section_fails_zero_assignment_claim():
    result = audit_export(fixture("UNKNOWN ROW"))
    assert result["unparsed_object_load_rows"]
    assert not result["zero_named_object_load_rows_observed"]
    with pytest.raises(ValueError,match="Incomplete E2K"):
        audit_export(fixture(missing_section=True))

def test_original_fingerprint_gate_and_no_engineering_approval():
    with pytest.raises(ValueError,match="Source bytes differ"):
        audit_pair(fixture(),fixture())
    result = audit_pair(fixture(),fixture(),require_originals=False)
    assert result["selected_records_identical"]
    assert not result["fingerprint_verified"]
    assert not result["engineering_approval"]
    assert "ORIGINAL_F3_ONE_WAY_SHEAR_NOT_SAFE" in result["holds"]
