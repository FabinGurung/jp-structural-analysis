# JP Structural Analysis — Studio Standard v1.0

**Effective:** 2026-11-16 · **Owner:** `FabinGurung/jp-structural-analysis` · **Scope:** all future projects using this structural engine · **State:** reusable software workflow, NOT a structural design code or replacement for licensed engineer review.

**Canonical human entrypoint:** [Studio Standard on GitHub Pages](https://fabingurung.github.io/jp-structural-analysis/studio.html)  
**Machine-readable input template:** [project-input-template-v1.json](./project-input-template-v1.json)  
**Project source of truth:** approved Google Drive project sources. **Code:** this repository. **CAD models:** `FabinGurung/jp-drawing-coordination`. **A7:** federated directory only; never edit without explicit instruction.

## 01 — Mission and scope

Build independently reproducible structural models, calculations, reports, checks and auditable design decisions from a project's source documents. Distinguish four things at all times:

- `SOURCE_VERIFIED`: exact field and page/entity/drawing dimension supported by controlled source.
- `USER_APPROVED_ASSUMPTION`: explicit provisional user choice, with reason, date and scope.
- `CODE_DERIVED_ASSUMPTION`: applicable official clause, formula, units, site/occupancy applicability and calculation.
- `UNRESOLVED`: physically missing or conflicting evidence; may be *tested* as a scenario but never silently overwritten or approved.

Do not pass an assumed geometry as measured member continuity, or an OpenSees equilibrium pass as reinforcement/footing capacity approval.

## 02 — Intake packet per project (minimum)

1. Canonical `project_id`, legal project name, location (municipality, ward, district, country) and source revision.
2. Links to current architectural, structural, reinforcement, geotechnical, loading, and previous analysis/permit documents with Drive IDs and source SHA256 when available.
3. Source drawing-register commit SHA, grid/datum, plan/section dimensions, number of floors, storey elevations, member IDs, sectional properties, material grades, slab/wall/stair openings, foundations and original entity handles.
4. Dead, superimposed, wall, imposed, seismic, wind, snow/water and construction loads as applicable; section and provenance for each.
5. Geotechnical evidence including boreholes, allowable bearing conditions, settlement, uplift, liquefaction and 2025 seismic soil class; missing data must be held.
6. Engineer decisions, review status, outstanding contradictions, geotechnical constraints and baseline code edition.

The UI must visibly show source provenance and governing contradiction for any input that materially affects safety.

## 03 — Responsibility boundary

- **Drive:** original human documents and approved controlled decisions.
- **CAD repository:** versioned machine-readable geometry and visual drawing work; original DXF/schedules must not be replaced by inference.
- **Structural repository:** normalized source schema, physical source mapping, OpenSees/OpenSeesPy calculations, independent check engines, tests, report templates and Pages presentation.
- **GitHub Actions:** deterministic CI and regeneration, data/source SHA checks, screenshots, build/deploy, live link readback, failure as a blocker.
- **GitHub Pages:** human-review display only; no promise that website availability certifies structural engineering.
- **A7 registry:** pointers, relations, identities and status directory only. Do not synchronize code or mutate A7 without explicit approval.
- **Engineer:** physical validity, contradictory drawings, code applicability and signed final acceptance.

## 04 — Mandatory pipeline

```text
Drive approved originals
  -> identify/reconcile source revision and project id
  -> pin CAD source SHA; normalize exact axes/dimensions/member topology
  -> flag SOURCE_VERIFIED / ASSUMED / UNRESOLVED per field
  -> validate material, load and code inputs
  -> generate physical 3D frame/shell/foundation graph
  -> FE solve (signed 6-axis equilibrium, member I/J actions)
  -> independent mesh refinement + stability and source-mass checks
  -> design demand/capacity (NBC/IS as properly applicable)
  -> full casebook and exceptions (F3 etc.)
  -> engineer review HOLD/PASS/revision
  -> GitHub Actions QA and Pages deploy
  -> freeze source/engine/manifest/release only for achieved scope
```

Every stage records immutable source IDs, exact units, input hashes, algorithm versions, outputs, fail-closed violations and review state. Incomplete physical connectivity is **not** repaired by snapping nearest axes unless the result is explicitly a research scenario labelled `ASSUMED`.

## 05 — Model engine input contract and outputs

### Inputs

Use the [machine template](./project-input-template-v1.json); fields with `null` remain unresolved, **not zero**. For each numeric field preserve `value`, `unit`, `source_kind`, `source_uri`, `page_or_entity`, `code_clause`, `approval`. Separate physical elements, restraints, support/ground conditions and effective stiffness. Do not treat software synthetic demo as a project model.

### Outputs

- `input.normalized.json`: original-provenance model + assumption register.
- `source-crosswalk.json`: CAD entity ↔ frame/shell/support element mapping; gaps retained.
- `loads.csv/json`: categories, mass, directions, combinations, unit-source ledgers.
- `model-qa.json`: connected graph, stability, constraints, gap and overlap tests.
- `analysis-results.json`: signed member forces/reactions/deformations, applied loads, six-axis residuals, solver metadata.
- `mesh-sensitivity.json`: true 2–3 resolution physical-equivalent comparisons, not fake duplication.
- `design-checks.csv/json`: every member/slab/stair/footing code rule, demand, capacity, governing combo and explicit exceptions.
- `report.html/pdf`: source-linked six-chapter design report, printable and mobile.
- `manifest.json`: SHA256 of input/casebook/results/report plus Git SHA, Actions run, release and approval flags.
- `review-log`: numbered evidence holds, resolution, reviewer and date.

Only publish public-safe derivatives to Pages. Never expose confidential client PDFs, native CAD, account identifiers or geotechnical reports in an artifact.

## 06 — Validation gates (fail closed)

- **V1 identity:** same project, revision, drawing source SHA and coordinates, all sources linked.
- **V2 topology:** physical cross-floor continuity, beams to columns, shell-to-beam/support contacts and foundations established, otherwise labelled research-only.
- **V3 loads:** floor and wall source areas/volumes, densities, openings, complete live-load zones, seismic/wind parameters, case combinations; no invented 2025 site class.
- **V4 solver:** deterministic run, six-component force/moment equilibrium, signed end action and reactions, physically equivalent mesh stability, no fabricated constraints.
- **V5 design:** strength/serviceability, RC flexure, shear, torsion, ductility, joints, footing bearing/settlement/punching, stairs, slab and governing NBC requirements.
- **V6 review:** source contradictions resolved, engineer validates, historic adverse safety issues closed only with traced redesign.
- **V7 publication:** numerical and browser CI, live Pages source verification, source/manifest hashing and immutable versioned milestone.

A PASS of V4 **does not imply** V2/V3/V5/V6 pass. Original **F3 NOT SAFE IN ONE WAY SHEAR** stays adverse until independently recalculated design evidence supports resolution.

## 07 — Required user-facing studio navigation

Use exactly **Home · Studio Standard · Projects · Developers · Research · More** as the six primary pages. Every page must provide top table-of-contents links, sticky left chapter navigation on desktop, contextual right review/reference panel, and previous/next bottom navigation. On phones prefer a compact menu, horizontally scrolling contents and collapse right context; no page-width overflow. Historic routes and artifact links remain available through **More**, never silently deleted.

## 08 — Version and naming convention

Human labels: `YYYY-MM-DD · Stage · Plain-language name`; examples:
- `2026-11-16 · R6.26 Report Engine Preview`
- `2026-11-13 · R6.24 Mesh Research Preview`
- `2026-11-09 · R6.10 Shell Software Preview`

Machine ID: `PRJ-000007/r6p26/<source-sha>/<run-id>`; audited source SHA remains immutable. Never create `final`/ `approved` filename for an unapproved product.

Preserve PRE/POST under controlled archive, change log and release notes; no destructive replacement of historical original files. Release software milestones as **prerelease** while engineering approval remains false.

## 09 — Paste-ready handover prompt for another project

> Apply **JP Structural Analysis Studio Standard v1.0** from `https://fabingurung.github.io/jp-structural-analysis/standards/studio-standard-v1.md` and the JSON input template. Locate my new project's authoritative Google Drive documents and the matching `jp-drawing-coordination` project register, pin its source SHA and reconcile project identity, architecture/structure/soils and revisions. Normalize element-wise geometry, load and code fields with per-value provenance, explicitly distinguish verified evidence from provisional/code-derived assumptions and unresolved safety inputs. Execute the independent OpenSees engine only on a model whose assumptions are clearly disclosed, run all applicable gates V1–V7, and publish a dedicated project page under **Projects** with numerical JSON/CSV, independent design checks, engineer holds, Actions QA and links to source. Do not modify A7 without my separate instruction. Do not copy Narayani's coordinates, loads, report outputs or permissions into this project.

## 10 — Current reference project and known limits

**Only Narayani Parajuli PRJ-000007 is presently onboarded as a real-project preview.** Its R6.26 report has 4 independent 3D elastic frame cases, 132 members, 1,056 local I/J result rows and 92 fixed-base reactions, **all conditional**. No governing NBC105 seismic case, physically complete slab/wall/stair loads, verified GF→FF/SF joints or foundation design. The R6.23/24 model is a **separate synthetic test benchmark**. Never claim Narayani's engineering approval from software QA alone.
