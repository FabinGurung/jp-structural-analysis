# JP Structural Analysis — Active Working Product

**Live website:** https://fabingurung.github.io/jp-structural-analysis/

**Complete historical archive in Google Drive:** https://drive.google.com/drive/folders/1ViudVSKVdDr7OPl-xFjJTankIDAEQJoO

The Drive archive preserves the full pre-cleanup source and Git history bundle, previous published website, responsive QA and source-design QA. The current source tree keeps only the working reporting components, not the experimental web pages and workflows.

## Google Drive source publishing

[Structural project source status](https://fabingurung.github.io/jp-structural-analysis/projects.html#drive-sources) shows the most recent verified read. The Narayani workbook and companion guide are in the Structural Analysis folder under `01_JP / 09 GitHub Repositories`.

- In **Inputs and Review**, record the observed value, units, source section, evidence keys and review state. Use the public summary and publish flag for material intended for the Projects page.
- In the companion Google Doc, paragraphs beginning with `[PUBLIC] ` feed the project's public review notes. Other working notes and original evidence stay in Drive.
- [Publish Structural Report](https://github.com/FabinGurung/jp-structural-analysis/actions/workflows/pages.yml) validates source permissions, identities, revisions and publication fields before deployment. Run it manually to pick up Drive edits. The staging workflow can build a preview without updating Pages.
- The worked OpenSees report uses the repository's reference model. Reviews and source-read receipts document custody and open engineering questions.

## Active software
- \`r6p23/engine.py\`, \`r6p23/runner.py\`: actual OpenSeesPy ShellMITC4 + elastic beam/column benchmark, synthetic two-floor model.
- \`r6p30/beam_design.py\`: isolated IS456 My/Vz beam flexure + vertical shear, 256 matched signed end-result checks.
- `r6p30/column_pmm.py`: short-column numerical uniaxial reference (64 strips) with IS456 §39.1(a,b) strain regimes and §39.6 biaxial interaction. Signed OpenSees local I(+)/J(−) compression mapping; tensile rows excluded; §25.4 one-axis minimum eccentricity alternatives. These are **NOT** SP16-verified RC column capacities.
- `r6p30/column_validation.py`: independent analytical uniform-compression force and 32/64/128-strip convergence benchmarks; results available in the generated site's `data/column-verification.json`.
- **Independent NPTEL SP16 chart example:** A 450 × 500 mm M25 Fe415 column with 12Ø16 bars, 56 mm centre cover and Pu=1,600 kN, compared against IIT Kharagpur Lesson 26 Q.5/A.5. Published chart-derived major/minor moments are 246.376/215.156 kN·m. We perform an independent numerical strain-compatibility calculation; a predeclared 3% research agreement band applies to both directions. The figure's M20 caption conflicts with the M25 problem and worked answer, so that discrepancy remains recorded. Details in the report and data/column-verification.json. One worked example is NOT complete SP16 chart certification. Source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l26.pdf .
- \`site_builder.py\`: one six-chapter printable report; four simple site areas: Home / Studio Standard / Projects / More.
- Actions cover engine tests, the Drive source preview and the live Pages publisher.


## Current design verification and Drive archive

R6.35 F3: `r6p30/footing_f3.py` preserves the original Narayani page-61 NOT SAFE IN ONE WAY SHEAR verdict. A NEW proposed 2.10 m square UNIFORM 550 mm deep footing with 12mm @150 bottom mat passes the listed one-way shear, punching, bending, minimum steel, and gross concentric bearing screens under the original 571 kN service-load assumption. This DOES NOT establish safety for unknown foundation moments, seismic actions, 1.8 m versus 2.1 m source location conflict, soil eccentricity/settlement, actual sloped geometry, or field construction. Original version is not overwritten. The eight-page research report and detailed calculation spreadsheets/scripts live **only in Drive**: https://drive.google.com/drive/folders/1qX-FJkPw8p9EF1yINTcPf5kAMxJIMJzU .

R6.35 SP16: active numerical code now uses interpolated IIT Kharagpur NPTEL Lesson23 SP16 Table A steel stress points instead of the erroneous optimistic bilinear steel. CI checks 12- and 20-bar independent NPTEL chart examples. The Drive research audit has 13 individually published reference values within a predeclared 3% *research* band, plus 720 internal mesh-refinement calculations across 3 chart families and Fe250/415/500; 720 is NOT 720 independent chart comparisons. The full SP16 source chart suite and actual building design have NOT been formally certified. Source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l23.pdf .


## R6.36 — slab reinforcing steel from genuine OpenSees ShellMITC4 plate resultants

The live report exports four Gauss-point section-resultant vectors per real ShellMITC4 panel from `ops.eleResponse(tag,"stresses")`: p11,p22,p12,m11,m22,m12,q1,q2; with model units kN and m, plate moments are kN·m/m, shear kN/m. The signed *simultaneous* values are superposed across the synthetic combinations, then a Wood–Armer-style ±|M12| adjustment is applied to each assumed top/bottom X/Y face and screened with an IS456 Annex G one-metre strip. The assumed 120 mm M25 Fe500 slab and 8mm @150 top/bottom cage are NOT the original Narayani 125mm/8mm@150 geometry and are not construction approved. This adds 496 face/axis/cell/combination checks, `data/slab-checks.csv`, and the NPTEL one-way independently derived bending benchmark in `data/slab-benchmark.json`. The original NPTEL example's SP16 Table41 steel strength 22.26kNm/m differs from our simplified Annex G 21.35kNm/m; the disagreement is explicit and unresolved. No seismic, deflection, cracking, anchorage, opening edge steel, top/bottom sign or project-specific safety approval is implied. Academic source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m8l18.pdf .


## R6.37 — Narayani staircase source reconciliation (NOT approved)

The original July 2026 drawing stair sheet declares 180 mm riser, 255 mm tread, 150 mm waist, Ø12 @125 main and Ø8 @150 distribution. The revised analysis states 170 mm/254 mm and a 150 mm waist, but its actual flexure worksheet uses a 127 mm overall section/d=106 mm, Ø12 @127 main and an ambiguous 20.88 kN.m source moment for a 1.2m wide flight. The worksheet also declares 383.62 mm² of required reinforcement without verified one-metre-strip units. R6.37 preserves *both possible moment interpretations*, recomputes IS456 Annex G one-metre steel demand, detects the over-reinforced neutral-axis limit in the 127mm worksheet section, and keeps a separate assumed 150mm drawing-section overlay. No actual staircase loads, continuity, supports, landing shear, deflection, anchorage or stair OpenSees shell model have been verified. The full source-linked open-holds ledger is published as `data/staircase-source-review.json` inside existing Chapter 6, Section 6.5; **engineering approval remains false**. The original F3 failure and slab benchmark disagreement remain open.

## R6.38 — independent published staircase waist section benchmark

IIT Kharagpur/NPTEL Lesson 20, Example 9.1: independently calculated the published stair-waist reinforcement section using M20/Fe415, d=224mm, overall depth=250mm, source moment 102.08 kN.m **across full 1.5m stair width**. After normalization to one metre, independent IS456 Annex G steel demand is approximately 921.261 mm²/m versus its SP16 Table 2 result 920.64 mm²/m (0.0674% deviation). Source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m9l20.pdf . This benchmark tests **only** bending section arithmetic and correct normalization of the full-width published moment. It does not verify the full staircase and landings, finite-element model, reactions or actual Narayani inputs. All physical engineering holds remain. A separate research QA Google Doc with source conflict and benchmark history is archived in Drive and linked from Chapter 6.5 and More; no original files are modified.

## R6.39 — source-verified STR-16 geometry and a fail-closed staircase model gate

**Important erratum:** Earlier R6.37 source-audit text misidentified the staircase drawing as `STR-15`. The original July 2026 structural drawing is **STR-16**, physical PDF page **16 of 20**. The R6.39 source reconciliation is based on direct visual inspection of that page, preserving the original PDF unchanged. The drawing shows grid **C–D = 4,965 mm**, **1–2 = 4,275 mm**, flight details **first X–X / second Y–Y / third X–X**, riser/tread **180/255 mm**, waist **150 mm**, Ø12 @125 and Ø8 @150 reinforcement, a **9×12-inch secondary-beam annotation at one landing**, and **720 mm flight-end notes**. None of the grid or 720 mm callouts is an established flight effective span.

`r6p30/staircase_geometry.py` preserves exact source identifiers and SHA-256 of the original drawing and revised report, performs independent slope and theoretical solid-step/waist dead-load arithmetic with all assumptions exposed, and records full required stair/landing geometry, support and loading evidence as **held**. The revised worksheet's **170/254 mm** stair remains a separate version; a 3,048 mm report-level height is at most a contextual sensitivity, not proof of riser count or a built staircase level. A gate rejects any proposed real-staircase OpenSees analysis without verified XYZ flight/landing/support geometry and engineering sign-off; even a complete-looking input mapping cannot invoke a non-implemented solver. There are **no new actual staircase OpenSees predictions**. The source-verified evidence and holds are in the existing Chapter 6.5.2 and `data/staircase-geometry.json`. The append-only R6.39 source drawing erratum and research QA record are retained in the established [structural Drive study](https://docs.google.com/document/d/1MVWeuQEEqKlcngzOFyU3JShvJE-7_yByvWJYiQJRd90/edit). Earlier slab SP16 and F3 safety issues remain open.

## R6.40 — original staircase worksheet arithmetic and unresolved load-basis discrepancy

Directly checked the revised Narayani analysis PDF physical pages 64–65 (2026), not an invented stair FE model. The 170mm riser, 254mm tread, 150mm waist and 50.8mm finish can reproduce the printed **8.41 kN/m²** flight dead load if the worksheet's finish section area is interpreted as thickness × (horizontal tread + vertical riser). The individual cross-sections, 0.0216m² step, 0.0458m² inclined waist, 0.0215m² finishes and total about 0.0890m² are independently reconstructed, with the finish-area explanation expressly marked *inferred*. The source flight gamma=24 kN/m³, landing gamma=25 kN/m³, 1.2m flight width, flight live=3 kN/m² and landing finish=1.22 kN/m² are kept separate.

The source worksheet uses **1.5(DL+LL)** to produce flight ~17.11 kN/m² and landing ~11.95 kN/m². The SAME revised report §2.8.1 lists **1.2DL+1.5LL**, yielding ~14.59 kN/m² for the flight and ~10.46 kN/m² for the landing, before any seismic or other load combinations. This numerical discrepancy is NOT resolved as a design-code acceptance decision; the applicable NBC and full combination envelope require a qualified review. Original drawing sheet STR-16 describes **Class B Residential+Commercial**, while the report covers *Residential building*, so correct occupancy and imposed loads are also HELD. Beam/landing reactions, 17.83 kN/m BC load, stated AB/BC moments and physical effective spans remain unverifiable from the visible worksheet alone. The genuine synthetic OpenSees model has **no physical staircase**. F3 original **NOT SAFE** and R6.36 slab benchmark disagreement remain open.

Source-linked calculations and unresolved assumptions are generated in existing Chapter 6.5.3 and `data/staircase-worksheet-loads.json`. Independent source PDF SHA-256 are preserved in the result. Government code directory for independent professional validation: https://dudbc.gov.np/pages/building-code/ . This is **arithmetic audit only**, not permission, construction approval, or a justified real-building structural analysis.

## Reproduce
Python 3.12; \`pip install -r requirements.txt\`; \`pytest -q r6p30/test_beam_design.py r6p30/test_column_pmm.py r6p30/test_footing_f3.py r6p30/test_slab_design.py r6p30/test_staircase_review.py r6p30/test_staircase_geometry.py r6p30/test_staircase_loads.py tests/test_product.py\`; \`python site_builder.py\`.

## Governance
This is a *hypothetical* structural analysis and limited member calculation prototype, not Narayani construction approval. Column local signed N is interpreted by element-end convention for bottom I → top J in the synthetic model; tensile actions are not screened as compression. The actual member orientation and load signs must be verified for any real building. Beam flexure/shear is not an issued bar schedule. Original F3 one-way shear **NOT SAFE** is not cleared.

Original PDF: https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view

Design reference IS456: https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf
