"""Public educational reading guide + complete source-backed site/repository/Actions map.

This file is website *presentation*, not a structural analysis solver. Numerical
examples are explicitly labelled as quoted source or explanatory arithmetic.
Only public file paths are listed. Original Drive PDFs remain in Drive.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent.parent
SOURCE_REPORT="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
SOURCE_OLD="https://drive.google.com/file/d/1PoxRsUtb_3yDqEoEVY8knzUPVGMo6Nfu/view"
SOURCE_DRAWING="https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view"
SOURCE_SOIL="https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"
NBC105="https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf"
CODES="https://dudbc.gov.np/pages/building-code/"
REPO="https://github.com/FabinGurung/jp-structural-analysis"
BASE="https://fabingurung.github.io/jp-structural-analysis/"
VERSION="2026-11-17"
WORKFLOW_ROLES={
 "pages.yml":("PUBLICATION", "Canonical build → site generation → Pages upload → deployment → live source/HTML/JSON verification"),
 "portal-v1-qa.yml":("WEBSITE QA", "Test six-tab navigation, accessibility/layout, 390/768/1440px Chromium and source receipts"),
 "r6p27-source-design-qa.yml":("PROJECT ENGINEERING INPUT QA", "Pin real Narayani drawing source, regenerate OpenSees, map 21 footings to 23 columns and verify sourced quantities/code-area screens"),
 "r6p26-report-qa.yml":("PROJECT FE QA", "Recalculate source-conditioned Narayani signed FE actions; verify equilibrium and 390px report UI"),
 "r6p25-narayani-intake.yml":("SOURCE QA", "Check exact drawing snapshot, columns, footings, provenance and assumptions"),
 "r6p25-assumed-connectivity-qa.yml":("SOURCE QA", "Check assumptions in Narayani connection viewer and actual desktop/mobile interactions"),
 "r6p23-preview.yml":("FE RESEARCH QA", "Synthetic multi-floor shell/diaphragm/mesh-convergence numerical and browser checks"),
 "portal-frame-analysis.yml":("ON-DEMAND RESEARCH", "Authorized GitHub issue or manual dispatch runs pinned 3D frame trial and posts artifacts"),
 "g15-open-3d-analysis.yml":("ON-DEMAND RESEARCH", "Authorized [JP G15 3D] issue or manual dispatch runs original pinned G15 OpenSees study"),
 "g15-diaphragm-fe-analysis.yml":("ON-DEMAND RESEARCH", "Authorized [JP G15 G12] issue or manual dispatch runs pinned diaphragm comparison"),
 "r6p10-software-prerelease.yml":("RELEASE FREEZE", "Re-run/verify historical R6.10 software-only research prerelease"),
 "r6p24-software-prerelease.yml":("RELEASE FREEZE", "Guard immutable R6.24 synthetic-only software prerelease tag"),
 "r6p26-release.yml":("RELEASE FREEZE", "Guard immutable R6.26 report-preview software prerelease and QA evidence"),
}

SECTIONS=[
("orientation","Begin with the final answer—not Chapter 1", """
<p class="lead">You want to know <strong>what must be built, the exact numbers on its drawings, and why those numbers were chosen</strong>. That is the <em>end</em> of structural design. To understand the original structural report, read its argument <strong>backwards: Chapter 6 → Chapter 5 → Chapter 4 → Chapter 3 → Chapter 2 → Chapter 1.</strong></p>
<div class="steps"><div><b>6 · DESIGN</b><small>Which concrete member and bars?</small></div><div><b>5 · RESPONSE</b><small>What actions and movements must it resist?</small></div><div><b>4 · MODEL</b><small>What physical building did the software represent?</small></div><div><b>3 · METHOD</b><small>How were demands computed and checked?</small></div><div><b>2 · INPUTS</b><small>Which dimensions, material, loads and codes?</small></div><div><b>1 · PURPOSE</b><small>Which project, use, height and framing system?</small></div></div>
<p>We are reading <a href="%s">the revised Narayani G+1.5 ETABS report</a> (printed chapters 1–6 and annex). The <a href="%s">older G+2.5 report</a> is a historical alternative, not the same design revision. This page explains what the <em>original report says</em>; our OpenSees output is a separate independent product. We do not quietly mix their numbers.</p>
""" % (SOURCE_REPORT,SOURCE_OLD)),
("deliverables","The final construction outputs we are working towards", """
<p>Imagine visiting the site with the approved design. You should have a complete <strong>issued-for-construction (IFC) structural drawing set</strong> and calculations, not just a result saying SAFE.</p>
<div class="table-scroll"><table><thead><tr><th>Physical output</th><th>What an actual accepted report/drawing must contain</th><th>What calculation decides it?</th></tr></thead><tbody>
<tr><th>Footings &amp; soil</th><td>F1/IF1–IF4/CF1 locations, L×B×depth, actual founding elevation, bearing/settlement, top/bottom bars, cover, dowels and connections</td><td>Per-support load combinations → contact pressure/eccentricity → flexure, one-way shear and two-way punching</td></tr>
<tr><th>Columns</th><td>Every grid column size and longitudinal ties by storey, splice/anchorage, joint and confinement details</td><td>Factored Pu, Mu2, Mu3, shear and P–M–M interaction plus ductile design rules</td></tr>
<tr><th>Beams</th><td>Each span's depth/width, top/bottom reinforcement at both supports and midspan, stirrup zones, joint anchorage</td><td>Governing moment, shear, torsion, deflection and beam–column capacity ratio</td></tr>
<tr><th>Slabs &amp; openings</th><td>Actual two-way/one-way slab panels, thickness, top/bottom bar maps, negative moment strips, penetration and stair opening edges</td><td>Panel support conditions → slab actions, crack control, deflection and punching/shear where relevant</td></tr>
<tr><th>Staircases</th><td>Flight and landing sections, waist thickness, main/distribution bars, edge/landing anchorage</td><td>Geometry and inclined load → flexure, shear, serviceability and support reactions</td></tr>
<tr><th>Whole building</th><td>Governing seismic/wind resistance, lateral load path, diaphragm action, foundations and drift stability</td><td>Material mass + spectrum + FE model → modes, base shear, storey drifts, member demands, regularity and capacity</td></tr>
<tr><th>Field issue documents</th><td>Numbered plans/sections, design calculations, bar-bending schedules, quantities, inspection/testing requirements, signed revisions</td><td>All the above cross-checked and professionally approved; quantity alone never establishes safety</td></tr>
</tbody></table></div>
<p class="source-note">The original revised report discusses these categories in Chapter 6, but the detailed issued drawing and independent design checks are different deliverables. The presently published R6.27 source calculation page is a review aid, not signed construction approval.</p>
"""),
("reverse-map","Reverse-engineer each result into calculations, codes and inputs", """
<p>For every number shown on a structural sheet, follow this chain <b>Result → checks → solver output → source inputs → code requirement</b>. If a link is missing, we know exactly what the calculation needs—not just that the chapter is incomplete.</p>
<div class="table-scroll"><table><thead><tr><th>Result you want</th><th>Engineering calculations</th><th>Required input from drawings/report</th><th>Code family used</th></tr></thead><tbody>
<tr><td>Footing 2.1m or 2.4m?</td><td>P/A, qmax/min with Mx/My eccentricity, bearing, settlement, bending, one-way and punching shear</td><td>Each real column ULS/SLS reaction, geometry, founding level, geotechnical tests, nearby boundary</td><td>Geotechnical report, accepted shallow-foundation method, NBC105:2025 seismic combinations, applicable RC code</td></tr>
<tr><td>400mm square or 350mm circular column?</td><td>Pu–Mux–Muy, stability, P–M–M interaction, confinement and joint shear</td><td>Member grid, height, column force envelopes, concrete/steel, frames at each end</td><td>NBC105:2025 Annex A, NBC110 and applicable IS456/13920</td></tr>
<tr><td>Beam top/bottom bars?</td><td>Mu+/Mu−, Vu, Tu, stirrup spacing, anchorage, BCC ratio</td><td>Each actual span, supports, distributed wall/slab loads and seismic combination envelope</td><td>RC code, NBC105:2025 joint/ductile clauses</td></tr>
<tr><td>Slab Ø8 at 150mm?</td><td>Two-way coefficient/shell forces, serviceability, flexural steel minimum and support anchorage</td><td>Panel short/long span, continuity, thickness, finishes, occupancy and openings</td><td>IS456/NBC110; imposed load NBC103/IS875</td></tr>
<tr><td>Stair waist slab?</td><td>Dead/live on inclined flight and landing, BM, shear and required bar area</td><td>Riser, tread, flight width, slab thickness, landing support</td><td>IS456/NBC110; NBC103 occupancy loading</td></tr>
<tr><td>Safe during earthquake?</td><td>Seismic weight, periods, site spectrum, base shear, distribution, modal response, torsion, drifts, member capacity</td><td>Municipality, occupancy class, site soil class, gravity mass and complete 3D structural model</td><td>NBC105:2025; NBC108 for seismic site hazards</td></tr>
</tbody></table></div>
<div class="equation"><span>THE WHOLE LOGIC</span><strong>Geometry + loads + soil + material + code → structural model → P/V/M/drift/reactions → capacities → reinforcement and dimensioned drawings</strong></div>
"""),
("worked-foundation","Worked backwards: why a footing can bear load but still be unsafe", """
<h3>Step A — read the original footing drawing and report</h3>
<p>The revised report's Chapter 6 combined footing example uses a <b>4.00 × 1.50 m</b> footing under two unequal columns. It lists service loads <b>46 kN</b> and <b>409 kN</b>, gives <b>501 kN</b> as total load including its stated allowance, then uses factored column loads <b>69 kN</b> and <b>614 kN</b>. These are <em>original source values</em>, not new OpenSees results.</p>
<div class="calc"><span>Explanatory arithmetic from the report's factored loads</span><strong>A = 4.0 × 1.5 = 6.0 m²</strong><strong>q ≈ (69 + 614) / 6.0 = 113.83 kPa</strong><p>The printed report lists about <b>114 kN/m²</b> upward pressure. This simple calculation assumes its idealized net uniform pressure; a real combined footing also needs load-resultant/eccentricity and contact-pressure verification.</p></div>
<h3>Step B — the load becomes bending, shear and reinforcement</h3>
<p>The original combined-footing worksheet reports a maximum moment of <b>50.9 kN·m</b> in one computed side, column-face moment <b>237.1 kN·m</b> at B, nominal longitudinal reinforcement <b>Ø16 @150 mm</b> and a nominal <b>450 mm</b> thick combined footing. This demonstrates why bearing area by itself does <em>not</em> produce the reinforcement drawing.</p>
<h3>Step C — another footing shows why separate checks matter</h3>
<p>The original isolated footing <b>F3</b> worksheet contains <b>571 kN</b> axial load, <b>600 kN</b> with its self-weight allowance and a <b>2.10 × 2.10 m</b> adopted plan. A quick <em>concentric service average</em> would be <b>600/(2.1²) ≈ 136.1 kPa</b>. The source uses 160 kPa in its bearing calculation—yet explicitly concludes <strong>NOT SAFE IN ONE WAY SHEAR</strong> for F3. A pressure smaller than an allowable does not make a footing safe in shear or punching, or prove the load case correct.</p>
<p>Read these sequentially: <b>support reaction → area and eccentricity → soil pressure/settlement → bending and rebar → one-way shear → punching → anchorage → final drawing</b>. The report names the steps, so our engine should produce each step's numerical demand and capacity, not a single label.</p>
<div class="note">Source: revised report Chapter 6, pp. 57–63; original July 2026 STR-01 footing schedule. These calculations explain the reported assumptions; they must not be used as instructions to cast the footing.</div>
"""),
("ch6","Chapter 6 first: design of the physical structural elements", """
<p><b>Read this first</b> because it is closest to the decisions that a constructor sees. Chapter 6 is called <em>Design of Structural Elements</em> (printed p. 36 onward). Its subsections do different jobs:</p>
<div class="table-scroll"><table><thead><tr><th>Original section</th><th>What it tries to produce</th><th>What is actually shown in the revised PDF</th><th>How to read it</th></tr></thead><tbody>
<tr><th>6.1 Columns · pp.36–39</th><td>Section and cage for every column</td><td>Example ETABS C24 at top level: Pu 174.694 kN, biaxial moments −121.528 and −37.820 kN·m, required steel 2,134 mm²; schedules C1–C4</td><td>A single example is not all 23 columns; read unique member ID, storey, load combination, reinforcement and ties together</td></tr>
<tr><th>6.2 Beams · pp.40–42</th><td>Span-by-span top/bottom bars and shear links</td><td>Example GF B46: M3 −99.485 kN·m, V2 129.672 kN, torsion 10.760 kN·m, top steel 865 mm², bottom 432 mm², plus schedules</td><td>Different positions and load cases control support vs midspan; section size and joint must match drawings</td></tr>
<tr><th>6.3 Slabs · pp.43–45</th><td>Panel thickness, top/bottom steel and deflection</td><td>One two-way sample between grids 1–2–F–G: Lx 3.60m, Ly 4.97m, D=125mm, 8mm bars and 20mm cover; source recommendation Ø8 @150</td><td>Check that the panel, support continuity, load and openings are for the exact slab being constructed</td></tr>
<tr><th>6.4 Footings · pp.46–52</th><td>Size, steel, bearing, bending, one-way and punching</td><td>4×1.5m combined footing with unequal column loads; F1–F4 isolated footing worksheets and a family summary</td><td>A footprint and a bearing pressure do not replace the independent one-way and punching shear checks</td></tr>
<tr><th>6.5 Staircase · pp.53–54</th><td>Flight/landing thickness, flexural bars and shear</td><td>Riser 170mm, tread 254mm, width 1.20m, waist slab 150mm initially; source also adopts 127mm during trial calculations, provides Ø12 @5in for main flight</td><td>Follow one coherent geometric section and load path; the differing thickness entries require interpretation</td></tr>
</tbody></table></div>
<div class="source-fact"><strong>How the original chapter is organised</strong><p>Design output tables mix ETABS v20 headings with some ETABS 21 detailed design summaries; slabs/stairs are Excel-style worksheets and footings reference SAFE. They are separate calculation sources assembled into one report, not six identical engine outputs.</p></div>
<div class="calc"><span>OUR SOURCE-BASED TAKEOFF, NOT A NUMBER PRINTED IN THE REVISED SAR</span><strong>IF1–IF4 and CF1, 21 footings × drawing nominal 0.50m thickness = 36.915 m³ per footing schedule</strong><p>The original native DXF outlines yield <strong>36.330 m³</strong> because G1 is drawn 1.8×1.8m instead of the IF3 schedule's 2.1×2.1m; difference 0.585 m³. These are quantities computed from the July 2026 drawings, not certified final casting instructions.</p></div>
<p><a href="r6p27-construction-review.html">See our derived column/footing source takeoff and steel-area checks</a> while keeping the original report numbers separate from our independent trial results.</p>
"""),
("ch5","Chapter 5: how the whole building responds", """
<p>After Chapter 6, ask <b>where did the bending moments, axial forces, shears and seismic demands come from?</b> Chapter 5 (original printed pp.24–35) supplies the building-response results.</p>
<div class="table-scroll"><table><thead><tr><th>Original section(s)</th><th>Result and physical meaning</th><th>Reported example</th></tr></thead><tbody>
<tr><th>5.1 Auto seismic</th><td>Earthquake floor forces/base shear calculated from seismic coefficient and seismic weight</td><td>Weight 6,831.9109 kN; reported ULS EQX/EQY base shear ≈ 894.9803 kN, SLS ≈ 860.8208 kN</td></tr>
<tr><th>5.2–5.4 Axial, shear, moment diagrams</th><td>Member force distribution; inputs to Chapter 6</td><td>Drawings/figures of P, V and M rather than a complete member-by-member table in the PDF text</td></tr>
<tr><th>5.5 Modal participation</th><td>How many vibration shapes capture seismic mass</td><td>Source says at least 90%; cumulative mode 6: UX 0.934 and UY 0.956</td></tr>
<tr><th>5.6 Displacement</th><td>Total horizontal movement of a floor level</td><td>ULS maximum 22.9069mm vs source's 57.150mm limit; SLS maximum 12.846306mm vs 54.864mm source limit</td></tr>
<tr><th>5.7 Storey drift</th><td>Relative horizontal movement between consecutive floors divided by height</td><td>ULS drift 0.00288 vs reported 0.00625; SLS 0.002174 vs reported 0.006</td></tr>
<tr><th>5.8–5.10 Irregularities</th><td>Torsion, soft-storey and mass discontinuities</td><td>Source gives torsional edge displacement ratios around 1.06–1.20; stiffness/mass tables</td></tr>
<tr><th>5.11–5.15 Shape, base reactions, sections and centres</th><td>Load path ending at supports; mass centre vs rigidity centre, member check views</td><td>Source base shear entries −894.9803kN for EQX/EQY ULS and three diaphragm centre coordinates</td></tr>
</tbody></table></div>
<div class="calc"><span>Read a seismic result backwards</span><strong>V<sub>base</sub> = seismic coefficient × seismic weight</strong><strong>≈ 0.131 × 6,831.9109 = 894.98 kN</strong><p>This reconstructs the original table, not a fresh NBC105:2025 spectral design. The report also mixes 2025 headings with older 2020 coefficients, which must be interpreted from the selected code edition.</p></div>
<p><strong>Difference to remember:</strong> displacement is movement relative to the global reference; drift is <em>difference</em> between neighbouring floors relative to a storey height. Small displacement alone cannot demonstrate beam or footing capacity.</p>
"""),
("ch4","Chapter 4: what the ETABS 3D model represents", """
<p>Chapter 4 (original printed pp.20–23) shows a <b>3D rendered frame</b>, floor shell load assignments (live load + finishes), and <b>wall loads</b>. This is the bridge between the physical plan and the analytical response.</p>
<div class="steps"><div><b>JOINTS</b><small>3D coordinates at column/beam intersections</small></div><div><b>FRAME ELEMENTS</b><small>Columns and beams carrying P, V, M and torsion</small></div><div><b>SHELLS</b><small>Slab areas, diaphragms and openings</small></div><div><b>LOAD PATTERNS</b><small>DL / LL / EQX / EQY / other actions</small></div><div><b>SUPPORTS</b><small>Base restraints transferred to soil footings</small></div></div>
<p>The original report says ETABS 3D frame and SAFE foundation were used. A screenshot can help visualise an input, but <b>it does not contain the complete coordinates, connectivity, mass and stiffness needed to reproduce the numerical results</b>. Our CAD repository supplies drawing-derived entities; our OpenSees study is a separately documented interpretation.</p>
<p>When analysing a span, trace <b>slab patch → beam line → column joint → footing and soil</b>; when analysing an earthquake, trace <b>floor mass → diaphragm → vertical lateral system → base</b>. Never assign a physical connection purely because two drawing endpoints appear near each other.</p>
"""),
("ch3","Chapter 3: the calculation procedure", """
<p>Chapter 3 (original printed p.19) explains how the source authors intended to calculate and design:</p>
<ol><li><strong>Analysis:</strong> ETABS v20.0.0 space-frame analysis for all load combinations; static/dynamic earthquake methods discussed earlier.</li>
<li><strong>Beam and column sizing:</strong> report says IS456:2000 and IS13920-based concrete design; detailed example tables embed some ETABS 21 outputs.</li>
<li><strong>Foundation:</strong> report says SAFE 2016 and gives combined/isolated footing manual worksheets.</li>
<li><strong>Slab/stair:</strong> Excel worksheet calculations and original source drawing details.</li>
<li><strong>Adoption:</strong> select member thickness and reinforcement from worst governing design stresses and code detailing.</li></ol>
<p><b>Our comparable first-party chain:</b> the CAD registry defines original source positions; <a href="r6p26-report.html">R6.26</a> computes independently signed OpenSees elastic frame actions under declared assumptions; <a href="r6p27-construction-review.html">R6.27</a> checks source dimensions/rebar arithmetic. This is not proof we have recreated every ETABS/SAFE/Excel design check or validated their original section assumptions.</p>
<div class="source-fact"><strong>Method versus result</strong><p>A named program such as ETABS, SAFE or OpenSees is only the calculating tool. The engineering result still depends on correct source geometry, loads, support conditions, code interpretation and separate capacity design.</p></div>
"""),
("ch2","Chapter 2: all input parameters and references", """
<p>Read this after seeing Chapters 6–3. It explains <em>where all those numerical demands came from</em>. Chapter 2 (original pp.5–18) contains materials, cover, source codes, geometry, loads, seismic criteria, irregularity intent and combinations.</p>
<h3>2.1–2.4 Materials, cover, and original source codes</h3>
<div class="table-scroll"><table><thead><tr><th>Parameter in the revised report</th><th>Original reported value</th><th>Why it matters</th></tr></thead><tbody>
<tr><td>Concrete and steel</td><td>M20, fck=20 MPa; Fe500, fy=500 MPa</td><td>Section strength, required steel and detailing</td></tr>
<tr><td>Elastic modulus</td><td>Concrete E=5,000√fck, table says 25,000 MPa; steel line displays 200 MPa</td><td>Stiffness and deflection; check printed units rather than silently assuming they are correct</td></tr>
<tr><td>Nominal cover</td><td>Footing 50mm top/bottom in Ch.2; columns 40mm; beams 25mm; slabs 20mm</td><td>Effective depths, durability, bar placement; source Ch.1 gives 75mm footing sides</td></tr>
<tr><td>Geometrical framing</td><td>Storey height 3.048m, reported total 9.144m; 400mm column/main beams of varied sizes</td><td>Element length, stiffness, mass and storey drift</td></tr>
<tr><td>Original codes</td><td>IS875 loading, IS456 RC, IS13920 ductile detailing, NBC105 seismic</td><td>Which limit-state, load and detailing rules the source authors intended</td></tr>
</tbody></table></div>
<h3>2.5–2.6 Gravity and imposed loads</h3>
<p>The report prints <b>bedrooms/kitchens/living/toilets 2 kN/m²</b>; <b>terrace 1.5 kN/m²</b>; <b>corridors and staircases 3 kN/m²</b>. These are source-assumed live loads, not an approved mixed-use occupancy survey.</p>
<p>Its brickwork table assumes storey height 3.05m, brick unit weight 19.20 kN/m³, 230mm main wall, 110mm partition, 0.40m beam depth and 21%/20% opening adjustments. It arrives at <b>9.24 kN/m</b> for main wall load with openings and <b>4.47 kN/m</b> for a partition wall with openings. Formula shown in source: <b>w = γ(H−D)t × (1−opening fraction)</b>.</p>
<h3>2.6.4 Earthquake inputs</h3>
<p>The source adopts <b>zone factor Z=0.35</b>, <b>importance I=1</b>, <b>ductility factor 4</b>, <b>overstrength ULS 1.5</b>, assumed soil <b>Type D</b>, period <b>0.493 s</b>, ULS coefficient about <b>0.131</b> and SLS about <b>0.126</b>. It refers to a seismic basis and distribution by level, and prints both 2025 headings and 2020 parameter references; quote these as original input, not proven current NBC2025 values.</p>
<h3>2.7–2.8 Irregularities and load combinations</h3>
<p>The original says no soft storey and prints example combinations such as <b>1.2DL + 1.5LL</b>, <b>DL + λLL ± E</b>, <b>0.9DL ± E</b>, and an additional-load term. DL is permanent load; LL is imposed live load; E is earthquake. Different combinations govern different elements and limit states. The report's older clause notations should be compared with the authoritative 2025 code before design approval.</p>
"""),
("ch1","Chapter 1 last: why and for which project?", """
<p>The report opens (printed pp.3–4) by identifying its assignment: a <b>G+1.5-storey residential building in Pokhara</b> analysed with ETABS v20, with a <b>special moment-resisting frame (SMRF)</b>, about <b>9.144m</b> total height and <b>3.048m</b> storey height.</p>
<p>The authors describe isolated, eccentric and combined footings, 14×14-inch columns, multiple main beam types, brick infills, M20 concrete and Fe500 steel, and a stated <b>160 kPa at 1.5m</b> soil bearing assumption. Chapter 1 is the <em>design brief</em>, not evidence that every later computation is internally consistent.</p>
<div class="note"><strong>Understand the document history:</strong> the <a href="%s">older original file</a> calls the building G+2.5, commercial and semi-residential; the <a href="%s">July 2026 structural drawing</a> calls it residential-plus-commercial; the revised report calls it G+1.5 residential. Treat each as a separate revision and project-use claim until the issued approved scope is established. Do not combine floors, loads or sections across them just to make a complete table.</div>
""" % (SOURCE_OLD,SOURCE_DRAWING)),
("annex","Annex and conclusion: source evidence, not another design stage", """
<p>The report closes with illustrations of <b>column P–M–M interaction ratio</b>, <b>beam–column capacity ratio</b>, <b>shear reinforcement</b>, a reference list and a paragraph asserting overall safe design. These are presented in its source context. A safety conclusion is only as sound as the member-by-member evidence and applicable revision behind it.</p>
<p>For example, its own F3 worksheet explicitly contains <b>NOT SAFE IN ONE WAY SHEAR</b>, while its prose conclusion calls the whole building safe. This is a reason to understand what each section computes, not to ignore the conclusion or blindly repeat it.</p>
<p>Other source markers worth learning: <b>Pu</b> axial design force; <b>Mu</b> bending moment; <b>Vu</b> shear force; <b>Tu</b> torsional moment; <b>Ast</b> steel area; <b>q</b> soil contact pressure; <b>ULS</b> ultimate (strength) state; <b>SLS</b> serviceability (movement/cracking) state; <b>P–M–M</b> combined axial/biaxial section strength check.</p>
"""),
("code-directory","Where each code enters the calculation", """
<p>We need two visibly different sets of references: <strong>codes named by the original report</strong> and <strong>official standards to verify applicability today</strong>. The latter do not retroactively rewrite a number that the report actually printed.</p>
<div class="table-scroll"><table><thead><tr><th>Reference</th><th>What it governs in this reading</th><th>How to use it</th></tr></thead><tbody>
<tr><td><a href="%s">NBC105:2025</a></td><td>Seismic input, soil category, spectrum, combinations, drift, ductility and RC frame seismic detailing (Annex A)</td><td>Official approved 2025 code; do not reuse earlier 2020 soil Type D merely because it appears in the revised report</td></tr>
<tr><td><a href="%s">NBC103 / NBC104</a></td><td>Imposed occupancy loads / wind loads</td><td>Official code directory; determine actual zoning and applicable load cases</td></tr>
<tr><td><a href="%s">NBC110</a> + the report's IS456:2000</td><td>RC flexure/shear, durability, cover, serviceability, concrete and reinforcement</td><td>Confirm governing acceptance requirements before final design</td></tr>
<tr><td>Report's IS875 Parts I/II/V</td><td>Dead, imposed and special combination loads</td><td>Identify historical original load assumptions; check against the current local regulatory framework</td></tr>
<tr><td>Report's IS13920:2016 and older 1993 reference</td><td>Ductile confinement, column beam joints, bar anchorage and stirrups</td><td>Do not treat different editions as interchangeable</td></tr>
<tr><td><a href="%s">Narayani geotechnical report</a></td><td>Boreholes, founding levels, groundwater observations, bearing under settlement</td><td>Use its actual Df/footing-size-specific table rather than a single sitewide generic capacity</td></tr>
</tbody></table></div>
<p>Example: <a href="%s">NBC105:2025 Annex A, clause 4.2.2(b)</a> specifies a minimum longitudinal column reinforcement ratio of 0.01. The revised report's listed 8Ø12 for 350mm diameter C4 computes 0.9404%%, explaining our separate R6.27 arithmetic flag. It does not tell us whether another issued drawing uses a different cage.</p>
""" % (NBC105,CODES,CODES,SOURCE_SOIL,NBC105)),
("source-trail","Source order and how to use the engine after studying", """
<p><strong>Study the document in this order</strong> for Narayani: <a href="%s">revised structural report</a> (learn its own results) → <a href="%s">July 2026 drawings</a> (locate every member and footing) → <a href="%s">soil investigation</a> (understand site-specific foundation criteria) → <a href="%s">official code</a> (examine applicable formulas) → <a href="r6p26-report.html">our independent R6.26 solver report</a> (compare our model response) → <a href="r6p27-construction-review.html">R6.27 measured source/design arithmetic</a>.</p>
<p>For a future project the same logic is reusable: identify its own source revision and geometry first; record individual numerical input provenance; then make a physical 3D model, calculate signed demands, perform design capacities and issue an independently reviewed construction report. Read the <a href="studio.html">Studio Standard</a> as the AI/engine guardrail.</p>
<p>For a purely conceptual first reading, begin at <a href="#deliverables">final deliverables</a> and continue down. For a practical original-report reading, open Chapter 6 of the source PDF and move through this guide's sections 6→1 beside it.</p>
""" % (SOURCE_REPORT,SOURCE_DRAWING,SOURCE_SOIL,NBC105))
]

SOURCES=[
 ("Revised original ETABS report, G+1.5",SOURCE_REPORT),
 ("Earlier historical G+2.5 report",SOURCE_OLD),
 ("July 2026 Narayani structural drawing",SOURCE_DRAWING),
 ("Narayani site geotechnical report",SOURCE_SOIL),
 ("Government NBC105:2025",NBC105),
 ("Official Nepal building codes",CODES),
 ("R6.26 independent report", "r6p26-report.html"),
 ("R6.27 drawing-source calculations", "r6p27-construction-review.html"),
 ("System map and complete file trees","system-map.html")
]

LEARNING_STYLE=r"""
<style>
:root{--l-ink:#282941;--l-sub:#5c6579;--l-border:#e1e2e9;--l-purple:#3e338f;--l-red:#be3f5a;--l-green:#137d75;--l-paper:#fbfaf7}
body{background:var(--l-paper)}
.guide-wrap{max-width:1420px;margin:0 auto;padding:0 22px 44px}
.guide-hero{padding:46px 2px 16px}
.guide-overline{font-size:11px;font-weight:850;letter-spacing:.12em;color:#327c74}
.guide-hero h1{font-family:system-ui,sans-serif;font-weight:850;line-height:1.07;letter-spacing:-.052em;font-size:clamp(34px,5vw,63px);max-width:1000px;margin:14px 0 16px;color:var(--l-ink)}
.guide-hero>p{max-width:900px;font-size:17px;color:var(--l-sub)}
.guide-topnav{display:flex;gap:7px;overflow-x:auto;padding:10px 0 15px;white-space:nowrap;margin-bottom:18px}
.guide-topnav a{font-size:12px;font-weight:700;color:var(--l-purple);border:1px solid #dedbe9;background:white;border-radius:30px;padding:8px 12px;text-decoration:none}
.guide-columns{display:grid;grid-template-columns:minmax(180px,220px) minmax(0,1fr) minmax(185px,220px);gap:20px;align-items:start}
.guide-left,.guide-right{position:sticky;top:15px;max-height:calc(100vh - 30px);overflow:auto}
.guide-rail{background:#fff;border:1px solid var(--l-border);padding:15px;border-radius:12px}
.guide-rail h2{font-size:11px;letter-spacing:.12em;color:#787886;margin:0 0 11px}
.guide-rail a{display:block;text-decoration:none;color:var(--l-purple);padding:9px 5px;font-size:12px;border-bottom:1px solid #f0eef3}
.guide-rail a:last-child{border-bottom:0}.guide-rail small{display:block;color:var(--l-sub);font-size:11px;margin:8px 0}
.guide-content{min-width:0}.guide-section{margin:0 0 15px;background:white;border:1px solid var(--l-border);border-radius:13px;padding:clamp(18px,3vw,31px);scroll-margin-top:15px}
.guide-section h2{font-size:clamp(23px,3vw,32px);line-height:1.19;letter-spacing:-.028em;color:var(--l-ink);margin:4px 0 18px}
.guide-section h3{font-size:17px;margin:24px 0 8px;color:var(--l-ink)}.guide-section p,.guide-section li{line-height:1.67;color:#4f5971;font-size:14px}.guide-section .lead{font-size:16px}
.guide-section b,.guide-section strong{color:#262b46}
.guide-section a{color:var(--l-purple);overflow-wrap:anywhere}
.guide-index{display:flex;justify-content:space-between;gap:10px;font-size:10px;font-weight:850;letter-spacing:.1em;color:#337b75;margin-bottom:13px;text-transform:uppercase}
.table-scroll{overflow-x:auto;width:100%;border:1px solid #e9e7ef;border-radius:8px;margin:14px 0}
.guide-section table{min-width:680px;width:100%;border-collapse:collapse;font-size:12px;line-height:1.5}
.guide-section th,.guide-section td{padding:11px 9px;border-bottom:1px solid #e9e9ef;text-align:left;vertical-align:top}
.guide-section thead th{font-size:11px;font-weight:800;letter-spacing:.03em;color:#52526d;background:#f2f1f7}.guide-section tbody th{color:#343451}
.guide-section td{color:#535e73}
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:19px 0}.steps div{padding:15px 10px;border:1px solid #dfdce9;border-radius:10px;background:#f8f6fc}
.steps b{font-size:13px;display:block;color:#40348e}.steps small{color:#5b6480;font-size:11px;line-height:1.6;display:block;margin-top:5px}
.calc,.equation{background:#f6f3fb;border-left:4px solid #6656a3;border-radius:8px;padding:17px 19px;margin:16px 0}
.calc span,.equation span{font-size:10px;font-weight:850;letter-spacing:.08em;color:#615880;display:block;margin-bottom:9px}
.calc strong,.equation strong{font-size:16px;display:block;line-height:1.65;color:#312d62}
.calc p{margin:8px 0 0}
.source-note,.note{background:#f3f7f6;border-left:3px solid #338b82;border-radius:5px;padding:12px;margin:12px 0}
.source-fact{padding:15px;background:#faf4f2;border:1px solid #ecd4d1;border-radius:9px;margin:18px 0}
.guide-bottom{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:20px 0}.guide-bottom a{padding:12px 16px;background:white;border:1px solid var(--l-border);border-radius:10px;text-decoration:none;color:var(--l-purple);font-size:13px;font-weight:750}
.guide-section pre,.guide-tree{background:#f4f4f8;border:1px solid #e1e1e9;padding:15px;border-radius:8px;white-space:pre;overflow-x:auto;font:12px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace;color:#353752}
.guide-rail .quick{padding:9px;background:#f5f3fa;border-radius:7px;margin:7px 0;font-size:12px;color:#545c71}
.guide-rail .quick strong{color:#3e338f}
.tree-group{margin:10px 0;border:1px solid #e1e1ea;border-radius:9px;overflow:hidden}
.tree-group summary{cursor:pointer;padding:12px 15px;background:#faf9fd;font-weight:800;color:#3c3782;font-size:13px}
.tree-group ul{padding:8px 15px 14px 36px;margin:0}.tree-group li{font-size:12px;line-height:1.9;overflow-wrap:anywhere}
.tree-group li span{color:#73788c;font-size:11px}
@media(max-width:1080px){.guide-columns{grid-template-columns:minmax(170px,210px) minmax(0,1fr)}.guide-right{position:static;grid-column:2}.guide-right .guide-rail{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:15px}}
@media(max-width:720px){.guide-wrap{padding:0 13px 28px}.guide-hero{padding-top:24px}.guide-columns{display:block}.guide-left{display:none}.guide-right{display:block;max-height:none}.guide-right .guide-rail{display:block}.guide-section{padding:16px}.steps{grid-template-columns:repeat(2,minmax(0,1fr))}.guide-section table{min-width:650px}}
@media print{.global-header,.guide-topnav,.guide-left,.guide-right,.guide-bottom{display:none!important}.guide-columns{display:block}.guide-section{break-inside:avoid;border:0}.guide-wrap{padding:0}}
</style>
"""

def nav():
    pages=[("Home","index.html"),("Studio Standard","studio.html"),
           ("Projects","projects.html"),("Developers","developers.html"),
           ("Research","research.html"),("More","more.html")]
    return '<header class="global-header"><div class="header-inner">'+(
      '<a class="brand" href="index.html"><span class="brand-mark">JP</span>'
      '<span class="brand-copy">STRUCTURAL<span> ANALYSIS</span><small>EDUCATION · SOURCE · ENGINE</small></span></a>'
      '<button type="button" id="menu-toggle" class="menu-toggle" aria-expanded="false" aria-controls="primary-nav"><span>Menu</span><span aria-hidden="true">☰</span></button>'
      '<nav id="primary-nav" class="primary-nav" aria-label="Main sections">'
      +''.join(f'<a href="{link}">{escape(name)}</a>' for name,link in pages)+'</nav></div></header>')

def render(title,subtitle,blocks,right_links,kind):
    top="".join(f'<a href="#{id}">{escape(name)}</a>' for id,name,_ in blocks)
    left="".join(f'<a href="#{id}"><span>{i:02d}</span> {escape(name)}</a>' for i,(id,name,_) in enumerate(blocks,1))
    right="".join(f'<a href="{escape(url,quote=True)}">{escape(label)}</a>' for label,url in right_links)
    parts=[]
    for i,(id,name,body) in enumerate(blocks,1):
        parts.append(f'<section class="guide-section" id="{id}"><div class="guide-index">'
           f'<span>{i:02d} / {len(blocks):02d}</span><span>{escape(kind)}</span></div>'
           f'<h2>{escape(name)}</h2>{body}</section>')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<title>'+escape(title)+' · JP Structural Analysis</title>'
      '<meta name="description" content="'+escape(subtitle,quote=True)+'">'
      '<link rel="stylesheet" href="site-system.css"><script src="site-system.js" defer></script>'
      +LEARNING_STYLE+'</head><body><a class="skip-link" href="#guide-main">Skip to guide</a>'+nav()
      +'<div class="guide-wrap"><div class="guide-hero"><span class="guide-overline">'
      +escape(kind)+' / VERSION '+VERSION+'</span><h1>'+escape(title)+'</h1><p>'
      +escape(subtitle)+'</p></div><nav class="guide-topnav" aria-label="Jump to topic">'+top+'</nav>'
      +'<div class="guide-columns"><aside class="guide-left"><nav class="guide-rail" aria-label="Sticky topic navigation">'
      +'<h2>ON THIS PAGE</h2>'+left+'</nav></aside><main id="guide-main" class="guide-content">'
      +''.join(parts)+'<nav class="guide-bottom" aria-label="Neighbouring study pages">'
      +'<a href="projects.html">← Narayani Projects</a><a href="system-map.html">System file trees →</a>'
      +'<a href="studio.html">Reuse Studio Standard →</a></nav></main>'
      +'<aside class="guide-right"><div class="guide-rail"><h2>SOURCES AND NEXT STEPS</h2>'+right
      +'<p class="quick"><strong>Remember:</strong> an original-report value, an explanatory calculation, and a new verified design result are different things.</p>'
      +'<small>Original files remain in Drive. This study page republishes explanatory text and selected short facts, not the private PDFs or DXFs.</small>'
      +'</div></aside></div></div></body></html>')

def git_files()->list[str]:
    try:
        r=subprocess.check_output(["git","-C",str(ROOT),"ls-files","-z"],stderr=subprocess.DEVNULL)
        return sorted(s.decode() for s in r.split(b"\0") if s)
    except (OSError,subprocess.CalledProcessError):
        return sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()
                      and ".git" not in p.parts and "__pycache__" not in p.parts)

def detail_tree(paths:list[str],url_prefix:str|None=None)->str:
    """Complete nested file listing with independently collapsible subfolders."""
    root={}
    for p in paths:
        cur=root
        parts=p.split("/")
        for folder in parts[:-1]:
            cur=cur.setdefault(folder,{})
        cur[parts[-1]]=None
    def render_children(node,depth=0)->str:
        out=[]
        for name,child in sorted(node.items(),key=lambda kv:(kv[1] is None,kv[0].lower())):
            if child is None:
                href=quote(name,safe="")
                # Use URL path based on full recursion outside for correct links
                out.append('<li>'+escape(name)+'</li>')
            else:
                out.append(f'<li><details class="tree-group"{ " open" if depth<1 else ""}>'
                           f'<summary>📂 {escape(name)}</summary><ul>{render_children(child,depth+1)}</ul></details></li>')
        return "".join(out)
    return '<ul>'+render_children(root)+'</ul>'

def flat_groups(paths:list[str],is_public:bool)->str:
    by=defaultdict(list)
    for p in paths:
        parts=p.split("/")
        group=parts[0] if len(parts)>1 else "(site root)" if is_public else "(repository root)"
        by[group].append(p)
    out=[]
    for group,files in sorted(by.items(),key=lambda kv:(kv[0]!="(site root)" and kv[0]!="(repository root)",kv[0])):
        lis=[]
        for p in files:
            url=(quote(p,safe="/") if is_public else REPO+"/blob/main/"+quote(p,safe="/"))
            lis.append(f'<li><a href="{url}">{escape(p)}</a></li>')
        out.append('<details class="tree-group"><summary>📁 '+escape(group)+' · '
                   +str(len(files))+' files</summary><ul>'+"".join(lis)+'</ul></details>')
    return "".join(out)

def source_map_blocks(repo_files:list[str],site_files:list[str]):
    flows=[
      ("1. SOURCE AUTHORITY","Original human documents and engineer decisions","Google Drive, project-specific register, soil and previous SAR"),
      ("2. GEOMETRY AUTHORITY","Original drawings / original member IDs","jp-drawing-coordination; pinned SHA, DXF handles, building levels"),
      ("3. ANALYSIS CODE","OpenSees engine and bounded source assumptions","jp-structural-analysis/r6p23–r6p27, portal/"),
      ("4. TEST AUTOMATION","Recalculate, check invariants, build and deploy","13 versioned .github/workflows/*.yml jobs"),
      ("5. PUBLIC PRESENTATION","What you are reading in a browser","GitHub Pages HTML + JS + structured JSON/CSV"),
      ("6. APPROVAL","Professional engineering accept/revise decision","Licensed review and signed working drawings, not GitHub status")
    ]
    cards=''.join('<div><b>'+a+'</b><small>'+b+' — '+c+'</small></div>' for a,b,c in flows)
    site_main=r"""JP Structural Analysis · GitHub Pages
├── CURRENT NAVIGATION / six tabs
│   ├── index.html              Home / what the engine is
│   ├── studio.html             Reusable studio standard and guardrails
│   ├── projects.html           Only Narayani is onboarded
│   ├── developers.html         CI, QA, release/audit catalog
│   ├── research.html           Experiments, completed/held research
│   └── more.html               Legacy tools and preserved history
├── LEARNING / start here
│   ├── original-report-guide.html   Original ETABS report explained backwards
│   └── system-map.html             This complete system map
├── NARAYANI / independent results
│   ├── r6p27-construction-review.html   Source dimensions, footing and rebar calculations
│   ├── r6p26-report.html               6-chapter independent OpenSees trial report
│   ├── r6p25.html                      Drawing-source and connection hypotheses
│   └── reports/r6p26/ + reports/r6p27/ (reproducible JSON/CSV/receipts)
├── FE RESEARCH / not this project's construction approval
│   ├── r6p23.html                Synthetic model and mesh comparison
│   └── Historical G15, diagrams and earlier experiment pages
├── STANDARDS + CONTROL
│   ├── standards/studio-standard-v1.md
│   ├── standards/project-input-template-v1.json
│   ├── portal-manifest.json + build-meta.json
│   └── site-file-inventory.json (complete generated public path index)
└── PRESERVED LEGACY / older design and tools
    ├── legacy-home.html + legacy-more.html
    ├── report.html + projects/index.html
    └── project-lab.html, g15-3d.html and related historic outputs"""
    return [
      ("authority","Who owns what? The actual pipeline",
       '<div class="steps">'+cards+'</div><p><strong>Repository ≠ Actions ≠ Pages:</strong> GitHub repository holds source code and versioned tests; Actions are temporary execution runs of that code; Pages is the read-only published result. A successful run can verify it built correctly. It is not an engineering permit.</p>'),
      ("page-tree","Current GitHub Pages: the reader-facing tree",
       '<p>This is the <b>main route and grouped purpose tree</b>. The next section provides the <em>complete actual file inventory captured during the Pages build</em> instead of losing legacy files.</p>'
       +'<pre class="guide-tree">'+escape(site_main)+'</pre>'
       +'<p><a href="site-file-inventory.json">Open complete machine-readable list of every generated public file</a></p>'),
      ("all-pages","Complete published file inventory, generated from the current build",
       '<p><b>'+str(len(site_files))+' public files</b> were present when this tree was generated; each is linked below. Expand a folder to see its exact paths. This includes preserved historic assets and machine-readable outputs, not just six new navigation pages.</p>'
       +flat_groups(site_files,True)),
      ("actions-tree","All 13 GitHub Actions workflow definitions",
       '<p>Each YAML file defines a repeatable workflow. It can create numerous <em>runs</em>, so 13 files does <b>not</b> mean 13 analysis runs or pages. The list below is read directly from the <code>.github/workflows/</code> files in this checkout.</p>'
       +'<div class="table-scroll"><table><thead><tr><th>Workflow file</th><th>Category</th><th>What it executes or verifies</th></tr></thead><tbody>'
       +''.join('<tr><th><a href="'+REPO+'/blob/main/.github/workflows/'+quote(n)+'">'+escape(n)+'</a></th><td>'+escape(WORKFLOW_ROLES.get(n,("OTHER",""))[0])+'</td><td>'+escape(WORKFLOW_ROLES.get(n,("OTHER","Repository workflow"))[1])+'</td></tr>'
                for n in sorted(n for n in repo_files if n.startswith(".github/workflows/") and n.endswith(".yml"))
                for n in [n.rsplit("/",1)[-1]])
       +'</tbody></table></div>'
       +'<p><a href="'+REPO+'/actions">All workflow runs and statuses</a> · <a href="'+REPO+'/releases">Versioned software releases</a></p>'),
      ("actions-pipeline","What happens inside the main Pages Actions run",
       '<pre class="guide-tree">'+escape(r"""push/main or manual trigger
  └─ pages.yml
      ├─ BUILD job
      │   ├─ check out source and install OpenSees/tests
      │   ├─ re-run historic bounded structural research checks
      │   ├─ generate original SAR / source-trace views
      │   ├─ pinned R6.23/24 mesh study; R6.25 drawing QA
      │   ├─ independent R6.26 report + derived forces
      │   ├─ R6.27 drawing/reinforcement/footing design arithmetic
      │   ├─ six-tab Portal + educational original-report/system pages
      │   └─ package the entire static site
      └─ DEPLOY job
          ├─ publish to fabingurung.github.io
          ├─ check live URLs, JSON and SHA fingerprints
          └─ enforce historic F3 unsafe / no engineering approval false claim""")+'</pre>'
       +'<p>Other workflows are <b>independent guardrails</b>: PRs run tests before merge; issue-driven workflows run explicitly authorized analyses; software prerelease workflows freeze tested versions. GitHub Actions does not run an engineer inside the website.</p>'),
      ("repo-tree","The repository: the source-controlled file tree",
       '<p><b>'+str(len(repo_files))+' tracked files</b> appear in the checkout (including these new source files at build). Expand the root groups to see the complete exact paths. The source is code, tests and report templates; it is not the output site.</p>'
       +flat_groups(repo_files,False)),
      ("find-results","Where to go for any specific question",
       '<div class="table-scroll"><table><thead><tr><th>If your question is…</th><th>Go here</th><th>Why</th></tr></thead><tbody>'
       '<tr><td>What did the original engineer calculate?</td><td><a href="original-report-guide.html">Original report explained</a></td><td>Walk source chapter 6→1</td></tr>'
       '<tr><td>What are the recorded footing sizes and steel?</td><td><a href="r6p27-construction-review.html">R6.27 drawing calculation</a></td><td>Source dimension/rebar tables and trial actions</td></tr>'
       '<tr><td>What did our independent numerical model solve?</td><td><a href="r6p26-report.html">R6.26 FE report</a></td><td>Member-end force and reaction data with assumptions</td></tr>'
       '<tr><td>Was it deployed and tested?</td><td><a href="'+REPO+'/actions">GitHub Actions</a></td><td>Actual job and live site log status</td></tr>'
       '<tr><td>What is the permanent AI-engine rule?</td><td><a href="studio.html">Studio Standard</a></td><td>Intake, modelling, solver, QA, gate, approval</td></tr>'
       '<tr><td>How do I view old studies?</td><td><a href="more.html">More and historical archives</a></td><td>Superseded results preserved with labels</td></tr>'
       '</tbody></table></div>'),
    ]

def sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def build(site:Path)->dict:
    site.mkdir(exist_ok=True,parents=True)
    repo_paths=git_files()
    workflows=[x for x in repo_paths if x.startswith(".github/workflows/") and x.endswith(".yml")]
    if len(workflows)<13 or set(x.rsplit("/",1)[-1] for x in workflows)!=set(WORKFLOW_ROLES):
        raise ValueError("System map workflow inventory changed; update workflow meanings before publish")
    # Portal's isolated browser QA builds only the six navigation pages and
    # downloads R6.26 JSON; the full Pages publishing job builds all reports.
    # Verify full source/report routes later in the production live CDN gate.
    for name in ("index.html","studio.html","projects.html","developers.html","research.html","more.html"):
        if not (site/name).is_file():raise ValueError("System map missing required published site source "+name)
    guide=site/"original-report-guide.html"
    guide.write_text(render(
        "Original structural report, explained backwards",
        "Narayani, Pokhara · What must the constructor receive, what computations produce it, and what the original ETABS report actually says in Chapters 6 → 1.",
        SECTIONS,SOURCES,"ORIGINAL REPORT · UNDERSTANDING BEFORE REDESIGN"),encoding="utf8")
    map_page=site/"system-map.html"
    # Create map placeholder for self-inclusion in site inventory
    map_page.write_text("<!doctype html><title>System map building</title>",encoding="utf8")
    inv=site/"site-file-inventory.json"
    # Counts and paths deliberately include this manifest and both new pages.
    paths=sorted(str(p.relative_to(site)) for p in site.rglob("*") if p.is_file()
                 and not p.name.startswith(".") and "__pycache__" not in p.parts)
    # portal-manifest is produced later in this builder, build-meta in the
    # immediately subsequent Pages workflow step. Both become public files.
    for planned in ("site-file-inventory.json","portal-manifest.json","build-meta.json"):
        if planned not in paths:paths.append(planned)
    paths=sorted(set(paths))
    index={
      "schema":"jp.structural.portal.public_file_inventory.v1",
      "build_source":"Pages BUILD site directory (public static files only)",
      "date":VERSION,"count":len(paths),"files":paths,
      "engineering_approval":False,
      "notes":"This is a filename inventory, not evidence of construction design acceptance. New additions after this generation require another run."
    }
    inv.write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    map_page.write_text(render(
        "Our repository, Pages and Actions — full system map",
        "Exactly what lives in the source repository, what GitHub Actions executes, and what GitHub Pages publishes. Expand folders for every source/public file.",
        source_map_blocks(repo_paths,paths),
        [("Original report study","original-report-guide.html"),
         ("Source-controlled GitHub repository",REPO),
         ("Latest GitHub Actions runs",REPO+"/actions"),
         ("Published GitHub Pages",BASE),
         ("Six-section Studio Standard","studio.html"),
         ("Source calculation review","r6p27-construction-review.html")],
        "STRUCTURAL SOFTWARE · BUILD AND PUBLISH TREE"),encoding="utf8")
    verify(site)
    return {"guide":"original-report-guide.html","map":"system-map.html",
            "files":index["count"],"workflows":len(workflows),
            "checksum":{x:sha(site/x) for x in ("original-report-guide.html","system-map.html","site-file-inventory.json")}}

def verify(site:Path)->dict:
    src=(site/"original-report-guide.html").read_text(encoding="utf8")
    m=(site/"system-map.html").read_text(encoding="utf8")
    i=json.loads((site/"site-file-inventory.json").read_text())
    req=["36.915","0.9404","6,831.9109","894.9803","NOT SAFE IN ONE WAY SHEAR",
         "Chapter 6","Chapter 5","Chapter 4","Chapter 3","Chapter 2","Chapter 1",
         "original ETABS","NBC105:2025","r6p26-report.html","r6p27-construction-review.html"]
    for token in req:
        if token.lower() not in src.lower():raise ValueError("Original source reading guide lost "+token)
    if src.count('class="guide-section"')!=len(SECTIONS):
        raise ValueError("Original guide topic count drift")
    if i.get("schema")!="jp.structural.portal.public_file_inventory.v1" or i.get("engineering_approval") is not False:
        raise ValueError("Public inventory no longer source/governance controlled")
    if i["count"]!=len(i["files"]) or i["files"]!=sorted(set(i["files"])):
        raise ValueError("Full site tree incomplete/duplicated")
    # Isolated portal QA has ~20 files; the full published Pages build has
    # many more research artifacts and is separately tested live at >=30.
    if i["count"]<15 or "original-report-guide.html" not in i["files"] or "system-map.html" not in i["files"]:
        raise ValueError("Source file tree incomplete")
    for name in WORKFLOW_ROLES:
        if name not in m:raise ValueError("GitHub Actions workflow missing from complete tree "+name)
    for name in ("reports/r6p26","r6p27-construction-review.html",
                 "r6p23.html","legacy-home.html","portal-manifest.json"):
        if name not in m:raise ValueError("Main GitHub Pages hierarchy missing "+name)
    if m.count('class="guide-section"')!=len(source_map_blocks(git_files(),i["files"])):
        raise ValueError("System tree sections not rendered")
    return {"files":len(i["files"]),"workflows":len(WORKFLOW_ROLES),
            "guide_sections":len(SECTIONS),
            "engineering_approval":False}
