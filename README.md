# JP Structural Analysis

**Public showcase:** https://fabingurung.github.io/jp-structural-analysis/

Governed structural-analysis and Structural Analysis Report (SAR) engine with
OpenSees/OpenSeesPy as the primary computational engine, explicit source
provenance, normalized model contracts, fail-closed QA, transparent benchmarks,
validation records, and reproducible reporting.

## Current portal and project study — 2026-11-18 (R6.29 navigation)

**Four primary website sections:** [Home](https://fabingurung.github.io/jp-structural-analysis/), [Studio Standard](https://fabingurung.github.io/jp-structural-analysis/studio.html), [Projects](https://fabingurung.github.io/jp-structural-analysis/projects.html), [More](https://fabingurung.github.io/jp-structural-analysis/more.html). The former Developers and Research routes redirect to the corresponding well-indexed sections inside More; their underlying files and historic reports are preserved.

**Narayani PRJ-000007 is a manual source-first study.** Projects lists the original report's **Purpose → Inputs → Methods → Model → Response → Design** stages; the user evaluates the source and approves each stage before independent OpenSees work advances. No R6.26 experimental report dominates the main project page. Original source report: https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view .

**More → Resources** contains [original engineer's report explained backwards](https://fabingurung.github.io/jp-structural-analysis/original-report-guide.html) and [our independent report explained backwards](https://fabingurung.github.io/jp-structural-analysis/independent-report-guide.html), as well as a complete [repository/Pages/Actions system map](https://fabingurung.github.io/jp-structural-analysis/system-map.html). **More → Research** directly compares original ETABS/SAFE/worksheet requirements against actually implemented OpenSees and source-audit capabilities, and inventories three computational code families plus supporting modules.

**Reusable standard:** [Studio Standard v1.0](portal/STUDIO_STANDARD.md) and [blank intake](portal/project-input-template-v1.json). The user's next detailed Standard redesign is not presumed complete. The active new editorial owner is [portal/curated_four.py](portal/curated_four.py), rendered by [portal/build.py](portal/build.py), with [portal/learning_system.py](portal/learning_system.py) for both backward-reading guides and the system inventory. The earlier six-section editorial [portal/content.py](portal/content.py) is retained for historical traceability, not current site navigation.

**New inspectable product proof (R6.30):** [What each structural engine actually does](https://fabingurung.github.io/jp-structural-analysis/engine-explained.html) and [Fully assumed six-chapter OpenSees worked example](https://fabingurung.github.io/jp-structural-analysis/example-sar-report.html). The worked example uses the *already solved* R6.23 synthetic 4m×4m, two-floor ShellMITC4/elasticBeamColumn model (31 shell elements, 32 beam segments, 8 column segments) with actual OpenSees result records; independently source-reconciled dead 339 kN and live 62 kN. It calculates signed member-end forces, fixed base reactions, displacements and selected hypothetical beam/slab/footing arithmetic. The output mirrors the original engineer's six chapter structure but does not pretend to be a complete design, earthquake analysis or professional approval. Programmatic author: [portal/engine_atlas.py](portal/engine_atlas.py); genuine solver regression: [portal/test_engine_atlas.py](portal/test_engine_atlas.py). Public structured numbers: [example-sar-numbers.json](https://fabingurung.github.io/jp-structural-analysis/reports/example-sar/example-sar-numbers.json).

**Current independent analysis remains preserved:** [R6.26 four-case OpenSees source-conditioned report](https://fabingurung.github.io/jp-structural-analysis/r6p26-report.html) has 132 elastic trial members, 1,056 signed member-end rows and 92 reaction records. It is NOT the same ETABS/SAFE project structural design. [R6.28 F3 source verification prerelease](https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.28-f3-source-verification) freezes the report's historical **NOT SAFE IN ONE WAY SHEAR** finding and independently checks worksheet geometry, demand and conditional code comparator, without physical design acceptance.

**Development source:** The historic governed engine's pinned workflow baseline is `f39c89ad55af18ea390a699af159f67f5fc8b517`; current `main` additionally contains independent `r6p23/` through `r6p26/` and the `portal/` presentation standard. Neither software milestone nor UI changes imply engineering approval or replace source Drive records.

## Public demo

The deployed showcase builds the sanitized two-span benchmark during GitHub
Actions and publishes:

- interactive project/showcase landing page
- sanitized Structural Analysis Report
- analysis results JSON
- validation results JSON
- report manifest

The benchmark preserves its known support-reaction reconciliation discrepancy
as `ENGINEER_REVIEW_REQUIRED`; a successful CI/deployment is not represented
as professional engineering approval.

[Open the live showcase](https://fabingurung.github.io/jp-structural-analysis/) ·
[Browse the engine branch](https://github.com/FabinGurung/JP_Structural_Analysis/tree/engine/opensees-sar-v0.1)

## Federated repository boundary — A7 is an index, not this product's template owner

**This repository owns** its domain-specific source, templates, workflows, documentation, tests and release history: OpenSees/OpenSeesPy structural-analysis code, model/benchmark contracts, SAR validation and engineer review states. The catalogue at [A7](https://github.com/FabinGurung/JP_A7_System_Registry_and_Knowledge_Graph) is only the **federated service directory / metadata index** of where repositories, websites, version pointers, statuses and cross-module relationships are found. A7 is **not** a parent codebase, shared template writer, or administrator of this module's content.

**Agent and automation rule:** Never create, update, synchronize or “repair” A7 code, policy, templates, catalogue records, READMEs, website or history as a side effect of work in this repository. An A7 modification requires a **separate task explicitly authorized by the user for A7**, with its own versioning and review. If an A7 listing appears stale, leave A7 unchanged and note a pending pointer correction **locally**. Resolve this repository's own live sources and approvals; do not duplicate its canonical domain files into A7. The CAD/AAD design-and-drawing template is owned by [CAD/AAD](https://github.com/FabinGurung/JP_Computer-Aided-Drawings/tree/main/governance/aad), never by A7. Existing independent domain and private-provider authorities still apply.



## R6.23 independently runnable multi-floor structural FE preview (development only)

The user-authorized R6.23 integration is available **on `main` as an isolated,
source-controlled numerical research component**, independently of the older
publication/Pages dispatcher:

- [R6.23 module and calculation documentation](r6p23/README.md)
- [Independent OpenSeesPy multistorey shell engine](r6p23/engine.py)
- [Source-safe command line report generator](r6p23/runner.py)
- [Numerical/geometry/manifest regression tests](r6p23/test_engine.py)
- [R6.23 standalone verification workflow](.github/workflows/r6p23-preview.yml)

It computes connected 3D ShellMITC4/beam/column systems over multiple rectangular
floors, actual shell openings, source-dependent gravity/line loads and both
flexible-shell / rigid in-plane diaphragm branches, with signed support and
member actions. It is a **synthetic, bounded research feature**, not an
accepted actual-building structural design, permit, full SAR engine release,
or professional approval. The previous F3 one-way-shear FAIL is unresolved.

Run `python -m r6p23.runner --reference --output-dir build/r6p23` after
installing `openseespy==3.8.0.0`; actual source-derived models, drawings
and reports must stay out of this public repository.

This integration **does not** merge/release the rest of the research branch,
repin Pages, change the canonical governed working branch, or tag V0.1.

## R6.23/R6.24 published independent OpenSees explorer

The separate R6.24 numerical/publishing QA passed and the existing GitHub
Pages workflow publishes a synthetic, source-hashed independent structural
shell/frame viewer at:

https://fabingurung.github.io/jp-structural-analysis/r6p23.html

The interface allows per-floor, per-case and per-diaphragm viewing of actual
OpenSees-solved beam and shell force components, base reactions and a 4x4
versus 8x8 mesh-sensitivity screen. It is based on the self-contained main
r6p23 package, checked out at the invoking commit; the historic pinned
full engine, existing report pages and navigation remain preserved.

Only synthetic calculations are published. Static Pages cannot run arbitrary
Python/OpenSees input from visitors, and this integration is NOT a certified
engineering design, project-specific SAR, full engine release or approval.
The original F3 one-way shear unsafe finding remains visible and unresolved.

## R6.24 governed software-preview milestone

- [Software-only R6.24 prerelease with Engineering HOLD](https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.24-preview)
- [Consolidated R6.10–R6.24 milestone report and limitations](audit/R6P24_SOFTWARE_PREVIEW_MILESTONE_REPORT__20261113.md)
- [R6.24 release notes](audit/R6P24_SOFTWARE_PRERELEASE_NOTES__20261113.md)
- [One-shot verified release workflow](.github/workflows/r6p24-software-prerelease.yml)

The release tag freezes the corrected, mobile-tested source commit `c9a4ad136ee70e000150026d0f0e1c049ff143df`; subsequent audit/report/workflow commits do not rewrite that tag. A software prerelease is not a complete independent structural design, a project-specific accepted SAR, or professional/municipal approval. The original F3 one-way-shear adverse finding is preserved.
