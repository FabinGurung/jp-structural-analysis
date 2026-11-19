"""Four-section source-first editorial structure for JP Structural Analysis.

This is a UI document, not a solver. Preserve previous research and reports.
"""
SOURCE="https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view"
REPO="https://github.com/FabinGurung/jp-structural-analysis"
PAGES={
"home":{
 "label":"Home","title":"How this structural-analysis website works",
 "eyebrow":"JP STRUCTURAL ANALYSIS / WEBSITE OVERVIEW",
 "deck":"One understandable entrypoint. What GitHub Pages displays, what GitHub Actions builds, where our code lives, and how to open a project.",
 "status":"Four clear areas · one source-first project",
 "sections":[
  ("welcome","What is this GitHub Pages website?", """
   <p>GitHub Pages is the public <strong>website</strong> for viewing project stages, reports, code explanations and research. It is not ETABS, OpenSees, a database, or a structural solver by itself. Calculations run in repository code and GitHub Actions; Pages displays the published output.</p>
   <div class="feature-panel"><div><h3>Start with the building, not the software</h3><p>For Narayani, read the original engineer's purpose, inputs, method, model, response and required design in order. The source-first project page is for manual learning; historical experimental engines are indexed under More.</p><div class="inline-links"><a href="example-sar-report.html">Open a real-solved assumed six-chapter report</a><a href="engine-explained.html">What each engine actually does</a><a href="projects.html#purpose">Narayani · Stage 1</a></div></div></div>
  """),
  ("four-areas","Our four main sections", """
   <div class="card-grid"><article class="mini-card"><h3><a href="index.html">Home</a></h3><p>Website purpose, system boundaries and navigation.</p></article><article class="mini-card"><h3><a href="studio.html">Studio Standard</a></h3><p>Repeatable rules every future structural project should follow.</p></article><article class="mini-card"><h3><a href="projects.html">Projects</a></h3><p>Only project-specific study and structural analysis work.</p></article><article class="mini-card"><h3><a href="more.html">More</a></h3><p>Resources, research comparisons, engines, developers, archives and codes.</p></article></div>
  """),
  ("connections","What is stored where?", """
   <div class="table-scroll"><table><thead><tr><th>System</th><th>Responsibility</th><th>What it is not</th></tr></thead><tbody>
   <tr><th>Google Drive</th><td>Original engineer's PDF, drawings, geotechnical evidence and file versions</td><td>Not an OpenSees solver</td></tr>
   <tr><th>Drawing Coordination</th><td>Building drawings, member positions, geometry and source revisions</td><td>Not the independent structural-analysis engine</td></tr>
   <tr><th>GitHub repository</th><td>Versioned code, calculation methods, tests, website source and manifests</td><td>Not itself the published website</td></tr>
   <tr><th>GitHub Actions</th><td>Run tests, regenerate calculation output, build and deploy website</td><td>Not an engineer's signature</td></tr>
   <tr><th>GitHub Pages</th><td>Show understandable documents, project stages and results</td><td>Does not run OpenSees dynamically in the browser</td></tr>
   <tr><th>A7</th><td>Links and ownership/provenance governance across repositories</td><td>Does not override the project engineering sources</td></tr>
   </tbody></table></div>
  """),
  ("next","What should I click first?", """
   <p><strong>For current Narayani work:</strong> go to <a href="projects.html#purpose">Projects → Narayani → 01 Purpose</a>. Read the source, verify its intended building use, then proceed to Inputs, Methods, Model, Response and Design.</p>
   <p><strong>For software/research history:</strong> use <a href="more.html">More</a>. The current independent FE reports are accessible but are no longer the mandatory first step.</p>
  """)],
 "right":{"title":"Navigation","status":"FOUR MAIN SECTIONS",
  "groups":[("Get oriented",[("Narayani manual Stage 1","projects.html#purpose"),("Studio Standard","studio.html"),("Resources and backward guides","more.html#resources")]),("Technical",[("Complete system map","system-map.html"),("GitHub Actions",REPO+"/actions")])],
  "note":"The website is presentation; original evidence and numerical engines retain separate owners."}
},
"studio":{
 "label":"Studio Standard","title":"A reusable standard for every new project",
 "eyebrow":"PROJECT STANDARD / SOURCE-FIRST TEMPLATE",
 "deck":"A common project structure and checklist. The detailed standard remains available for future human editing; Narayani's project data is not copied into a new template.",
 "status":"Standard framework · user refinement next",
 "sections":[
  ("standard-purpose","What the studio standard is for", """
   <p>One repeatable sequence for all structural projects: <strong>Purpose → Inputs → Methods → Model → Response → Design → Report</strong>. Every project will use its own documents, source IDs, approval history and calculations.</p>
   <p>The standard is a working instruction, not a replacement for design codes and not a pre-approved member schedule.</p>
  """),
  ("standard-stages","Required project study stages", """
   <div class="table-scroll"><table><thead><tr><th>Stage</th><th>Minimum contents</th></tr></thead><tbody>
   <tr><th>01 Purpose</th><td>Building use, floors, location, intended result and source revision</td></tr>
   <tr><th>02 Inputs</th><td>Geometry, soils, concrete, steel, occupancy loads, seismic criteria, code editions</td></tr>
   <tr><th>03 Methods</th><td>Original engineering procedure, analysis programs and calculation methods</td></tr>
   <tr><th>04 Model</th><td>Joints, beams, columns, shells, openings, boundary conditions, mass and load assignments</td></tr>
   <tr><th>05 Response</th><td>Axial force, shears, moments, reactions, displacements, modes and drifts</td></tr>
   <tr><th>06 Design</th><td>Footings, columns, beams, slabs, staircase, reinforcement and details</td></tr>
   <tr><th>07 Report</th><td>Traceable figures, original-versus-independent checks, reviewed output and revisions</td></tr>
   </tbody></table></div>
  """),
  ("standard-inputs","Project intake and evidence", """
   <p>Use the existing <a href="standards/project-input-template-v1.json">machine-readable project intake template</a>. Every reported value should identify an original document/page/drawing or a clearly stated independent assumption. Do not automatically borrow Narayani's geometry, materials or forces for another building.</p>
  """),
  ("standard-files","Existing baseline and future edits", """
   <p><a href="standards/studio-standard-v1.md">Read the current Studio Standard v1.0</a>. Its governance and AI guidance remain preserved. This simplified page is its navigation front door; no speculative new design template has been frozen.</p>
   <p>Start with <a href="projects.html#purpose">Narayani's six-stage source review</a> to decide which methods the next standard should require.</p>
  """)],
 "right":{"title":"Reusable documents","status":"NOT PROJECT-SPECIFIC",
  "groups":[("Templates",[("Studio Standard v1.0","standards/studio-standard-v1.md"),("Blank project intake JSON","standards/project-input-template-v1.json")]),("Example workflow",[("Narayani stages","projects.html"),("Original report reading guide","original-report-guide.html")])],
  "note":"Keep this shared template separate from Narayani's individual source and analysis."}
},
"projects":{
 "label":"Projects","title":"Narayani Parajuli — original report study",
 "eyebrow":"NARAYANI PARAJULI / ORIGINAL SOURCE STUDY",
 "deck":"Read the original Narayani structural report in six stages. Only titles and the source's scope are presented here; you decide each stage before we continue to independent analysis.",
 "status":"Current focus · Stage 01 Purpose",
 "sections":[
  ("purpose","01 — Purpose: which building is being designed?", """
   <p><strong>We begin with the original engineer's words—not OpenSees.</strong> In the revised source, the cover and Chapter 1 call this a <b>G+1.5-storey residential reinforced-concrete building</b> in Pokhara. Chapter 1 says the analysis/design report was prepared for an application for a construction permit; that does <em>not</em> establish that a permit was issued.</p>
   <div class="inline-links"><a href="SOURCE_URL">Read the original revised PDF</a><a href="original-report-guide.html#ch1">Read Chapter 1 backwards-study reference</a><a href="more.html#research">Compare original and our independent platform</a></div>
   <h3>What the original report actually records</h3>
   <div class="table-scroll"><table><thead><tr><th>Topic</th><th>Reported statement or number</th><th>Where to verify in the PDF</th></tr></thead><tbody>
   <tr><th>Intended use</th><td>Residential building, as identified on the report title and General Features table</td><td>Cover; Chapter 1 §1.1</td></tr>
   <tr><th>Study / permit purpose</th><td>Structural analysis and design submitted as part of an application to construct the building</td><td>Chapter 1 §1.1, Executive Summary</td></tr>
   <tr><th>Location</th><td>Pokhara; Leknath Metropolitan City is named in the source</td><td>Chapter 1 §1.1, General Features</td></tr>
   <tr><th>Building description</th><td>G+1.5 storey, with floor-plan illustrations for ground, first and second floors</td><td>Cover; Chapter 1 §1.1; Chapter 2 §2.5</td></tr>
   <tr><th>Vertical dimensions</th><td>3.048 m typical storey height; 9.144 m total building height</td><td>Chapter 1 §1.1, Architectural Features</td></tr>
   <tr><th>Structural system</th><td>Special Moment Resisting Frame (SMRF), reinforced concrete</td><td>Chapter 1 §1.1–§1.3</td></tr>
   <tr><th>Foundation families</th><td>Isolated pad, eccentric pad and combined footing</td><td>Chapter 1 §1.1, Structural Features</td></tr>
   </tbody></table></div>
   <h3>Different statements inside the same report</h3>
   <div class="table-scroll"><table><thead><tr><th>Question</th><th>Source A</th><th>Source B</th><th>What we need to establish</th></tr></thead><tbody>
   <tr><th>Residential or office?</th><td>Cover and Chapter 1: <b>Residential Building</b></td><td>Final Conclusion: <b>Office Building</b></td><td>Confirm intended use before selecting occupancy loads; do not quietly discard either source statement.</td></tr>
   <tr><th>What does G+1.5 denote here?</th><td>Report identifies the project as G+1.5 storey</td><td>Reports 9.144 m total at 3.048 m per storey, and shows ground/first/second plans</td><td>Confirm actual occupied levels, half-storey/terrace use and governing drawings, rather than interpreting the title alone.</td></tr>
   <tr><th>Where is the seismic site?</th><td>Project location: Pokhara/Leknath</td><td>Chapter 1 General Features also says 'Seismic Zone Kathmandu'; Chapter 2 associates Z = 0.35 with Leknath</td><td>Keep site and seismic parameters for Stage 02 Inputs; do not silently substitute a zone.</td></tr>
   </tbody></table></div>
   <h3>Stage 1 reading conclusion</h3>
   <p><strong>Source description:</strong> G+1.5 residential RC framed building, Pokhara/Leknath, prepared for a construction permit application. <strong>Actual approved use, level definitions and governing revision:</strong> to be confirmed against the client's intended building and issued architectural/structural drawings.</p>
   <div class="caution"><strong>Manual review point:</strong> does the project being studied match the residential G+1.5 building stated on the report cover and in Chapter 1? The 'Office Building' conclusion and seismic-site wording remain visible until reviewed. This page does not adopt a new structural model or mark an occupancy classification approved.</div>
   <p>After reading Stage 1, continue to <a href="#inputs">02 — Inputs</a>. No independent numerical solver is needed to complete this source reading.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("inputs","02 — Inputs: what information is required?", """
   <div class="project-facts"><div><small>Geometry</small><b>Grids · levels · dimensions</b></div><div><small>Material</small><b>Concrete · reinforcing steel · cover</b></div><div><small>Ground</small><b>Soil / geotechnical data</b></div><div><small>Loads</small><b>Dead · live · seismic · wind</b></div><div><small>Codes</small><b>Applicable standards and editions</b></div><div><small>Provenance</small><b>Original drawings and report</b></div></div>
   <p>Original PDF: <a href="SOURCE_URL">Chapter 2 — General Data for Structural Analysis</a>.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("methods","03 — Methods: how was the original analysis done?", """
   <div class="project-facts"><div><small>Analysis</small><b>ETABS — space frame, gravity and seismic</b></div><div><small>Foundation</small><b>SAFE and footing worksheets</b></div><div><small>Slab and stair</small><b>Spreadsheet calculations</b></div><div><small>Design codes</small><b>IS 456 · IS 13920 · NBC 105</b></div></div>
   <p>Original PDF: <a href="SOURCE_URL">Chapter 3 — Analysis and Design Procedure</a>. Distinguish which procedures are described from which numerical outputs are actually shown.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("model","04 — Model: what physical structure was represented?", """
   <div class="project-facts"><div><small>Space frame</small><b>Beam and column nodes</b></div><div><small>Slabs</small><b>Shells · openings · diaphragms</b></div><div><small>Loading</small><b>Floor finishes · live loads · masonry walls</b></div><div><small>Restraints</small><b>Foundation/support boundary conditions</b></div></div>
   <p>Original PDF: <a href="SOURCE_URL">Chapter 4 — Modeling in ETABS</a>.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("response","05 — Response: what did the structure experience?", """
   <div class="project-facts"><div><small>Forces</small><b>Axial · shear · bending · torsion</b></div><div><small>Movement</small><b>Displacements · interstorey drifts</b></div><div><small>Dynamic</small><b>Modes · base shear · irregularities</b></div><div><small>Supports</small><b>Base reactions and load transfer</b></div></div>
   <p>Original PDF: <a href="SOURCE_URL">Chapter 5 — Design Output and Structural Checks</a>.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("design","06 — Design: what finally needs to be constructed?", """
   <div class="project-facts"><div><small>Foundations</small><b>Footings · dimensions · reinforcement</b></div><div><small>Columns</small><b>Sections · longitudinal bars · ties</b></div><div><small>Beams</small><b>Sections · flexure · stirrups</b></div><div><small>Slabs</small><b>Panel thickness · reinforcement</b></div><div><small>Staircase</small><b>Flight / landing design and bars</b></div><div><small>Details</small><b>Joints · anchorage · construction drawings</b></div></div>
   <p>Original PDF: <a href="SOURCE_URL">Chapter 6 — Design of Structural Elements</a>. Reverse reading guides and old independent results live in <a href="more.html#resources">More → Resources</a>, not here.</p>
  """.replace("SOURCE_URL",SOURCE))],
 "right":{"title":"Original source","status":"STEP 01 · PURPOSE",
  "groups":[("Read before calculating",[("Original revised ETABS PDF",SOURCE),("Reverse reading reference","original-report-guide.html")]),("Separate worked example",[("Assumed OpenSees report","example-sar-report.html"),("Engines explained","engine-explained.html")]),("Manual study route",[("Start with purpose","#purpose"),("Next: inputs","#inputs"),("Study all six headings","projects.html")])],
  "note":"This is a manual learning page, not a recreated report, automatic engineering checklist or source revision approval."}
},
"more":{
 "label":"More","title":"Resource library, research and developer archive",
 "eyebrow":"INDEX / RESOURCES / RESEARCH / ENGINES / DEVELOPERS",
 "deck":"One organized library for everything outside the active project study: both backwards explanations, method comparisons, experimental engines, developer maps, releases and codes.",
 "status":"Historical technical work preserved and indexed",
 "sections":[
  ("resources","01 — Resources: understand reports backwards", """
   <div class="card-grid">
   <article class="mini-card"><span>ORIGINAL REPORT</span><h3><a href="original-report-guide.html">Original structural report — explained backwards</a></h3><p>Begin from construction design, trace member demands, model, methods and inputs, ending with building purpose (Chapter 6 → 1).</p></article>
   <article class="mini-card"><span>OUR OWN REPORT</span><h3><a href="independent-report-guide.html">Independent OpenSees report — explained backwards</a></h3><p>Start with what the project needs, then study our actual generated results, model assumptions, solver methods, inputs and gaps.</p></article>
   <article class="mini-card"><span>BUILD AND SYSTEM</span><h3><a href="system-map.html">Complete GitHub Pages / Actions / repository map</a></h3><p>Every tracked file, published page and workflow in a collapsible tree.</p></article></div>
  """),
  ("research","02 — Research: original report versus our product", """
   <p><a href="engine-explained.html"><strong>Open the exact engine inventory and line-by-line capability audit</strong></a> · <a href="example-sar-report.html"><strong>Open the solved example six-chapter report</strong></a></p><p>This table compares the <strong>revised G+1.5 ETABS report</strong> with the <strong>actual installed OpenSees and source-review capabilities</strong>. It distinguishes demonstrated output from missing physical-model equivalence.</p>
   <div class="table-scroll"><table><thead><tr><th>Stage</th><th>Original engineer's report</th><th>Our existing product</th><th>Difference to close</th></tr></thead><tbody>
   <tr><th>01 Purpose</th><td>Cover and Chapter 1: G+1.5 residential in Pokhara/Leknath; conclusion: Office Building</td><td>Original-source facts indexed in Narayani Stage 1; no assumed new FE model</td><td>Confirm intended occupancy, level definitions and governing drawings before load assignment</td></tr>
   <tr><th>02 Inputs</th><td>Original plans, M20/Fe500, soil, occupancy, loads and seismic parameters</td><td>Source-DXF 23 GF columns, 21 footing outlines, selected report/soil parameters; partial load ledger</td><td>Exact slab, walls, occupancy mass and material/source assumptions not fully reconciled</td></tr>
   <tr><th>03 Methods</th><td>ETABS v20 space-frame analysis, ETABS 21 detailed member examples, SAFE foundation and Excel slab/stair</td><td>OpenSeesPy linear elastic frame, separate experimental shell/frame engine and simple source-based RC arithmetic</td><td>No independent complete ETABS/SAFE/worksheet-equivalent design sequence yet</td></tr>
   <tr><th>04 Model</th><td>3D frame, shell and wall-load visuals; source describes ETABS/SAFE</td><td>R6.26 actual GF source locations extended with assumed upper levels and nearest-joint connections; R6.23 synthetic shells</td><td>Original full physical joints, slabs, diaphragm, openings and wall paths unproven</td></tr>
   <tr><th>05 Response</th><td>ULS/SLS base shear, modal participation, axial/shear/moment, reactions, drift and displacement</td><td>Four R6.26 elastic DL/LL/PX10/PY10 trial cases with 132 members, signed forces and equilibrium checks</td><td>Not the original seismic mass, combinations, dynamic response or full design envelopes</td></tr>
   <tr><th>06 Design</th><td>Column, beam, slab, footing and staircase checks/schedules</td><td>R6.27 footing quantities and bar-area checks, F3 worksheet source-verification module</td><td>No independently complete member strength, ductile detailing and foundation design output</td></tr>
   <tr><th>Final deliverable</th><td>Original assembled report and structural drawings</td><td>Versioned code, JSON/CSV, site report and audit trail with assumptions visible</td><td>Not yet a source-equivalent, professionally reviewed construction-design package</td></tr>
   </tbody></table></div>
   <p>Source: <a href="SOURCE_URL">Original PDF</a> · <a href="r6p26-report.html">Independent FE report</a> · <a href="r6p27-construction-review.html">Drawing arithmetic</a>.</p>
  """.replace("SOURCE_URL",SOURCE)),
  ("engines","03 — Engines and modules: what actually exists?", """
   <p><a href="engine-explained.html">Technical inventory: actual files, code, numeric output, boundaries and reproduction</a> · <a href="example-sar-report.html">Worked assumption-based OpenSees example</a></p><div class="table-scroll"><table><thead><tr><th>Software family</th><th>Concrete implementation</th><th>Role</th></tr></thead><tbody>
   <tr><th>Governed original engine</th><td>Existing pinned OpenSees SAR core and R5/R6 example scripts</td><td>Computational framework, benchmarks, report and experiment workflows; not a separate engine per Action</td></tr>
   <tr><th>R6.23</th><td><a href="REPO/tree/main/r6p23">Multi-floor ShellMITC4 frame/shell FE</a></td><td>Bounded research solver</td></tr>
   <tr><th>R6.26</th><td><a href="REPO/tree/main/r6p26">Narayani source-conditioned elastic 3D frame</a></td><td>Independent trial frame solver and report generator</td></tr>
   <tr><th>R6.25</th><td><a href="REPO/tree/main/r6p25">Source geometry/connection QA</a></td><td>NOT an independent FE solver</td></tr>
   <tr><th>R6.27 / 28</th><td><a href="REPO/tree/main/r6p27">Footing/cage arithmetic and F3 worksheet verifier</a></td><td>Deterministic source checks, NOT an independent FE solver</td></tr>
   <tr><th>Portal</th><td><a href="REPO/tree/main/portal">Site build, studies and browser QA</a></td><td>Presentation, NOT a structural solver</td></tr>
   </tbody></table></div>
   <p><strong>Count:</strong> two independently implemented OpenSees numerical modules in current main (R6.23 and R6.26), plus the pinned historic governed SAR core. R6.24/25/27/28 are numerical-comparison, source-intake and calculation-check modules, not additional general-purpose FE engines.</p>
  """.replace("REPO",REPO)),
  ("experiments","04 — Engineering research and calculation history", """
   <div class="card-grid">
   <article class="mini-card"><h3><a href="example-sar-report.html">Complete assumed demonstration report</a></h3><p>Original six-chapter layout, source-checked actual OpenSees forces, plus explicitly assumed sample beam/slab/footing calculations.</p></article><article class="mini-card"><h3><a href="engine-explained.html">All engines explained</a></h3><p>File-by-file computational scope and original-report parity table.</p></article><article class="mini-card"><h3><a href="r6p23.html">Shell, diaphragm and mesh research</a></h3><p>Source-bounded synthetic shell/frame model cases.</p></article>
   <article class="mini-card"><h3><a href="r6p25.html">Assumed connection review</a></h3><p>Source marks, hypothesized beam-column links and QA.</p></article>
   <article class="mini-card"><h3><a href="r6p26-report.html">R6.26 signed 3D frame report</a></h3><p>Original-source-conditioned calculations and reported limitations.</p></article>
   <article class="mini-card"><h3><a href="r6p27-construction-review.html">R6.27 drawing source takeoff</a></h3><p>Footing dimensions, columns and reinforcement arithmetic.</p></article>
   <article class="mini-card"><h3><a href="data/narayani-f3-oneway-verification.v1.json">R6.28 F3 one-way shear verification JSON</a></h3><p>Original p.61 source facts, recalculated demand and IS456 comparison; original verdict NOT SAFE IN ONE WAY SHEAR retained.</p></article></div>
  """),
  ("developers","05 — Developer reference and workflow map", """
   <p>Development material is <strong>here under More</strong>, not a separate primary section.</p>
   <div class="inline-links"><a href="system-map.html">Full repository / Pages / Actions inventory</a><a href="REPO/actions">Current Actions runs</a><a href="REPO/tree/main/portal">Portal source code</a><a href="REPO/tree/main/.github/workflows">Workflow definitions</a></div>
   <details><summary>What each workflow does</summary><p>Calculation and QA routines produce versioned reports, JSON and numerical receipts. Pages publication builds static site files and checks them after deployment. A successful website deployment alone does not approve the physical building.</p></details>
  """.replace("REPO",REPO)),
  ("archives","06 — Releases and preserved historical pages", """
   <p>Nothing from previous computational milestones has been deleted by this navigation change. Older viewer/report URLs remain accessible here.</p>
   <div class="inline-links"><a href="legacy-home.html">Historical Home</a><a href="legacy-more.html">Historical More</a><a href="report.html">Original chaptered report viewer</a><a href="projects/index.html">Earlier project viewer</a><a href="REPO/releases">All release tags</a><a href="REPO/releases/tag/r6.28-f3-source-verification">Frozen F3 R6.28 milestone</a></div>
   <p>Former top-level Developers and Research links point into the corresponding sections on this page.</p>
  """.replace("REPO",REPO)),
  ("codes","07 — Source and design reference library", """
   <div class="table-scroll"><table><thead><tr><th>Reference</th><th>Where it fits</th></tr></thead><tbody>
   <tr><th><a href="SOURCE_URL">Original revised structural report</a></th><td>Project-specific Chapters 1–6 and original engineering findings</td></tr>
   <tr><th><a href="https://drive.google.com/file/d/1zwmKrfwW9IN5ourLGFdfleJOCi7dcH2_/view">Original July 2026 drawing</a></th><td>Member positions, dimensions and schedules</td></tr>
   <tr><th><a href="https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view">Geotechnical report</a></th><td>Bearing and founding-source data</td></tr>
   <tr><th><a href="https://dudbc.gov.np/pages/building-code/">Nepal National Building Code directory</a></th><td>Applicable code editions and provisions</td></tr>
   <tr><th><a href="https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf">IS456 with amendments</a></th><td>RC strength and footing shear provisions used for bounded verification</td></tr>
   </tbody></table></div>
  """.replace("SOURCE_URL",SOURCE))],
 "right":{"title":"Research library index","status":"INDEXED UNDER MORE",
  "groups":[("Study materials",[("Original explained backwards","original-report-guide.html"),("Independent report explained backwards","independent-report-guide.html"),("Full system tree","system-map.html")]),("Preserved work",[("FE report","r6p26-report.html"),("F3 release",REPO+"/releases/tag/r6.28-f3-source-verification"),("More research","#research"),("Engine inventory","#engines")])],
  "note":"Separate original-source statements, independent calculations and software experiments. Do not treat a UI result as professional engineering approval."}
}
}
