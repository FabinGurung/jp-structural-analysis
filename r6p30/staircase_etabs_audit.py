"""R6.41: read-only ETABS text-export staircase evidence audit.

The original E2K files stay in their restricted Drive directory. Run this
module with explicit local copies of the two source files. This is a
lexical source inventory, NOT an ETABS solve, physical model reconstruction,
load-code acceptance, effective span determination or construction approval.
Story-reference flags and raw point offsets are deliberately not converted
to global Z coordinates. A shared source edge is not a verified FE restraint.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import re

SCHEMA = "jp.sar.r6p41.etabs_staircase_source_audit.v1"
STAIR_PATTERN = "STAIRCASE LOAD"
WAIST = 'WAIST SLAB6'
OBJECT_LOAD_SECTIONS = ("$ POINT OBJECT LOADS", "$ FRAME OBJECT LOADS", "$ SHELL OBJECT LOADS")
REQUIRED_SECTIONS = OBJECT_LOAD_SECTIONS + (
    "$ LOAD PATTERNS", "$ LOAD CASES", "$ MASS SOURCE", "$ LOAD COMBINATIONS",
    "$ SLAB PROPERTIES", "$ AREA ASSIGNS", "$ AREA CONNECTIVITIES",
    "$ POINT COORDINATES", "$ LINE ASSIGNS", "$ LINE CONNECTIVITIES",
)
SOURCE_IDS = {
    "ULS": "1FdTJ_DPzKU8GYBY5R-WXjWCdOc4c9yL3",
    "SLS": "1XxzO4MGieQQakCjMI_4ffjyazrcRvX83",
}
SOURCE_HASHES = {
    "ULS": "8860223c80171cd7437b2d54841171f1bafe4ce98c71fd86024e2ec95d08aaa3",
    "SLS": "7b6ca674447e38302d0647d89fbca1830e7d120795ad260bcf926bb9d335227e",
}

def sections(raw: bytes) -> dict:
    """Do not normalize source bytes before fingerprinting."""
    out = defaultdict(list)
    current = ""
    for line_no, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        line = line.strip()
        if line.startswith("$"):
            current = line
            out.setdefault(current, [])
        elif line and current:
            out[current].append((line_no, line))
    missing = [name for name in REQUIRED_SECTIONS if name not in out]
    if missing:
        raise ValueError("Incomplete E2K source sections: " + ", ".join(missing))
    return out

def object_loads(sec: dict) -> tuple:
    inventory, assigned, unknown = {}, [], []
    for name in OBJECT_LOAD_SECTIONS:
        counts = Counter()
        for n, row in sec[name]:
            match = re.search(r'\bLC\s+"([^"]+)"', row)
            if not match:
                unknown.append({"section": name, "line": n})
                continue
            pattern = match.group(1)
            counts[pattern] += 1
            if pattern.upper() == STAIR_PATTERN:
                assigned.append({"section": name, "line": n, "source_row": row})
        inventory[name] = {"rows": len(sec[name]), "load_pattern_counts": dict(counts)}
    return inventory, assigned, unknown

def audit_export(raw: bytes) -> dict:
    sec = sections(raw)
    loads, named, unknown = object_loads(sec)
    definition = [
        {"line": n, "source_row": row}
        for n, row in sec["$ LOAD PATTERNS"]
        if re.match(r'LOADPATTERN\s+"STAIRCASE LOAD"', row)
    ]
    mass = [
        {"line": n, "source_row": row, "factor": float(m.group(1))}
        for n, row in sec["$ MASS SOURCE"]
        if (m := re.match(r'MASSSOURCELOAD\s+"[^"]+"\s+"STAIRCASE LOAD"\s+([0-9.eE+-]+)', row))
    ]
    combos = []
    for n, row in sec["$ LOAD COMBINATIONS"]:
        m = re.match(r'COMBO\s+"([^"]+)"\s+LOADCASE\s+"STAIRCASE LOAD"\s+SF\s+([0-9.eE+-]+)', row)
        if m:
            combos.append({"line": n, "name": m.group(1), "factor": float(m.group(2))})
    property_rows = [{"line": n, "source_row": row} for n, row in sec["$ SLAB PROPERTIES"]
                     if row.startswith('SHELLPROP  "WAIST SLAB6') or
                     re.match(r'SHELLPROP\s+"WAIST SLAB6', row)]
    area_defs, points = {}, {}
    for n, row in sec["$ AREA CONNECTIVITIES"]:
        m = re.match(r'AREA\s+"([^"]+)"\s+(\w+)\s+(\d+)\s+(.*)$', row)
        if not m:
            continue
        ident, kind, count, tail = m.groups()
        nodes = re.findall(r'"([^"]+)"', tail)
        flags = tail[tail.rfind('"')+1:].split()
        if len(nodes) == int(count):
            area_defs[ident] = {"line": n, "kind": kind, "point_ids": nodes, "raw_story_flags": flags}
    for n, row in sec["$ POINT COORDINATES"]:
        m = re.match(r'POINT\s+"([^"]+)"\s+(.+)$', row)
        if m:
            try:
                coord = [float(v) for v in m.group(2).split()]
            except ValueError:
                continue
            if len(coord) in (2, 3):
                points[m.group(1)] = {"line": n, "raw_coordinates_mm": coord}
    assignments = []
    for n, row in sec["$ AREA ASSIGNS"]:
        m = re.match(r'AREAASSIGN\s+"([^"]+)"\s+"([^"]+)"\s+SECTION\s+"WAIST SLAB6"""(?:\s|$)', row)
        if not m:
            continue
        ident, story = m.groups()
        if ident not in area_defs or any(p not in points for p in area_defs[ident]["point_ids"]):
            raise ValueError("Waist assignment references missing area or point")
        assignments.append({"area": ident, "story": story, "assignment_line": n,
                            "connectivity": area_defs[ident]})
    raw_nodes = sorted({p for a in assignments for p in a["connectivity"]["point_ids"]})
    area_loads = []
    keys = {(a["area"], a["story"]) for a in assignments}
    for n, row in sec["$ SHELL OBJECT LOADS"]:
        m = re.match(r'AREALOAD\s+"([^"]+)"\s+"([^"]+)"\s+TYPE\s+"([^"]+)"\s+DIR\s+"([^"]+)"\s+LC\s+"([^"]+)"\s+FVAL\s+([0-9.eE+-]+)', row)
        if m and (m.group(1), m.group(2)) in keys:
            area, story, load_type, direction, pattern, value = m.groups()
            area_loads.append({"line": n, "area": area, "story": story,
                               "type": load_type, "direction": direction, "pattern": pattern,
                               "raw_FVAL_N_mm2": float(value)})
    # Only perimeter edges, not diagonal pairs; story labels are not global Z.
    def edges(a):
        ids = a["connectivity"]["point_ids"]
        return {tuple(sorted((ids[i], ids[(i+1) % len(ids)]))) for i in range(len(ids))}
    adjacency = []
    for a,b in combinations(assignments,2):
        if a["story"] == b["story"]:
            for edge in sorted(edges(a) & edges(b)):
                adjacency.append({"story": a["story"], "areas": [a["area"], b["area"]],
                                  "shared_raw_point_ids": list(edge)})
    secondary = []
    for n, row in sec["$ LINE ASSIGNS"]:
        m = re.match(r'LINEASSIGN\s+"([^"]+)"\s+"([^"]+)"\s+SECTION\s+"SEC BEAM 9X12"', row)
        if m:
            secondary.append({"line": n, "line_object": m.group(1), "story": m.group(2)})
    return {
        "source_sha256": sha256(raw).hexdigest(),
        "source_line_count": len(raw.decode("utf-8-sig").splitlines()),
        "named_stair_load_pattern_definition": definition,
        "named_stair_mass_source_rows": mass,
        "named_stair_combination_rows": combos,
        "object_load_inventory": loads,
        "explicit_named_stair_object_load_rows": named,
        "unparsed_object_load_rows": unknown,
        "zero_named_object_load_rows_observed": not named and not unknown,
        "waist_property_rows": property_rows,
        "waist_area_assignments": assignments,
        "waist_raw_point_coordinates": {p: points[p] for p in raw_nodes},
        "waist_object_loads": area_loads,
        "waist_shared_source_edges": adjacency,
        "secondary_beam_assignments": secondary,
        "actual_support_restraints_verified": False,
        "actual_effective_span_verified": False,
        "physical_global_coordinates_verified": False,
        "actual_reactions_kN": None,
        "engineering_approval": False,
    }

def audit_pair(uls: bytes, sls: bytes, *, require_originals=True) -> dict:
    exports = {"ULS": audit_export(uls), "SLS": audit_export(sls)}
    if require_originals and any(exports[k]["source_sha256"] != SOURCE_HASHES[k] for k in exports):
        raise ValueError("Source bytes differ from the 5 July 2026 original fingerprints")
    for v in exports.values():
        if not v["named_stair_load_pattern_definition"] or not v["waist_area_assignments"]:
            raise ValueError("Required source staircase definitions absent")
    # Compare only these selected lexical records, not the entire ETABS models.
    keys = ("waist_area_assignments", "waist_raw_point_coordinates", "waist_object_loads",
            "waist_shared_source_edges", "named_stair_mass_source_rows",
            "named_stair_combination_rows", "secondary_beam_assignments")
    return {
        "schema": SCHEMA,
        "classification": "SOURCE_INVENTORY_ONLY__ENGINEERING_HOLD",
        "source_ids": SOURCE_IDS if require_originals else None,
        "fingerprint_verified": require_originals,
        "exports": exports,
        "selected_records_identical": all(exports["ULS"][k] == exports["SLS"][k] for k in keys),
        "holds": [
            "NAMED_LOAD_CASE_IS_NOT_PROOF_OF_APPLIED_LOAD",
            "RECONCILE_DEAD_SELFWEIGHT_STEPS_FINISH_LIVE_AND_MASS_BASIS",
            "VERIFY_STORY_REFERENCE_FLAGS_AND_GLOBAL_3D_COORDINATES",
            "VERIFY_LANDING_AND_BEAM_RESTRAINTS_AND_MESH_CONTINUITY",
            "NO_ACTUAL_REACTIONS_OR_STAIRCASE_FE_SOLVE",
            "ORIGINAL_F3_ONE_WAY_SHEAR_NOT_SAFE",
            "R6P36_SLAB_SP16_BENCHMARK_DISCREPANCY",
        ],
        "engineering_approval": False,
    }

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--uls", type=Path, required=True)
    cli.add_argument("--sls", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    result = audit_pair(args.uls.read_bytes(), args.sls.read_bytes())
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
