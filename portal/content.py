"""Editorially maintained portal content; no claim of engineering approval."""
from __future__ import annotations

PAGES = {
"home": {
    "label":"Home","title":"A structural engine you can trace.","eyebrow":"JP / STRUCTURAL ENGINEERING · 16 NOV 2026",
    "deck":"From project drawings to independent calculations and inspectable reports. One entrance to the source, the engine, the project evidence and every unresolved engineering decision.",
    "status":"Software milestone R6.26 released · Engineering design HOLD",
    "sections":[
      ("overview","What we have built", """
      <p>JP Structural Analysis is the first-party OpenSees/OpenSeesPy engine and reporting workstream. It works with Google Drive source records and our drawing repository, normalizes member and load evidence, runs independently computed structural response scenarios, and publishes an inspectable six-chapter report through GitHub Actions.</p>
      <div class="stat-grid"><div><small>Independently solved cases</small><strong data-num="cases">4</strong><span>Conditional 3D frame scenarios</span></div><div><small>Modeled frame members</small><strong data-num="members">132</strong><span>Source locations + assumed links</span></div><div><small>Member-end result rows</small><strong data-num="actionrows">1,056</strong><span>Signed forces / moments</span></div><div><small>Real projects onboarded</small><strong>1</strong><span>Narayani · PRJ-000007</span></div></div>
      <div class="lead-actions"><a class="primary-link" href="original-report-guide.html">Understand the original report first</a><a class="subtle-link" href="projects.html">Open the Narayani project</a><a class="subtle-link" href="studio.html">Read the reusable Studio Standard</a></div>
      """),
      ("workflow","How the system works", """
      <div class="flow-steps"><div><span>01</span><b>Sources</b><small>Original drawings, analysis and soil records in Drive</small></div><div><span>02</span><b>Normalize</b><small>Drawing axes, member IDs, provenance and conflicts</small></div><div><span>03</span><b>Calculate</b><small>OpenSees signed member actions and base reactions</small></div><div><span>04</span><b>Review</b><small>Equilibrium, source checks, design holds, exceptions</small></div><div><span>05</span><b>Publish</b><small>GitHub Actions, SHA256 evidence and Pages reports</small></div></div>
      <p class="micro-note">A passed software test proves that a specific model executes consistently. It does not prove all physical connections or code-based design checks are accepted.</p>
      """),
      ("current","Current product · Narayani", """
      <div class="feature-panel"><div><p class="eyebrow">PRJ-000007 · POKHARA · SOURCE-CONDITIONED</p><h3>Narayani Parajuli — six-chapter independent report</h3><p>Actual drawing-derived ground-floor columns and footings, traceable assumed 3D connections, four OpenSees cases, signed member-force CSV, support reactions, displacement tables, and source exceptions in one reviewable report.</p><div class="inline-links"><a href="original-report-guide.html">Original ETABS report · explained backwards</a><a href="r6p26-report.html">View engine-generated report</a><a href="r6p25.html">Inspect assumed connections</a><a href="reports/r6p26/narayani-verified-manifest.json">Verify SHA256 receipt</a></div></div><div class="feature-art" aria-hidden="true"><div class="beam-icon">⌗</div><span>SOURCE → FRAME → REPORT</span></div></div>
      <div class="caution"><strong>Do not treat the preview as design acceptance.</strong> Actual member continuity, slab and wall support, NBC 105:2025 seismic actions, foundation and reinforcement design are open. F3 remains <b>NOT SAFE IN ONE WAY SHEAR</b> in the source record.</div>
      """),
      ("milestones","Milestones and next work", """
      <div class="timeline"><div><time>2026-11-09</time><b>R6.10 · Shell/diaphragm software</b><span>Research prerelease, source-bounded.</span></div><div><time>2026-11-13</time><b>R6.24 · Independent FE mesh viewer</b><span>Synthetic multi-floor benchmark and mobile-tested workbench.</span></div><div><time>2026-11-14</time><b>R6.26 · Narayani source-derived report</b><span>Independent 3D frame, six-chapter report and source-ledger QA.</span></div><div><time>2026-11-16</time><b>R6.26 · Software release frozen</b><span>Immutable prerelease and new portal governance standard.</span></div></div>
      <p>The next engineering milestone is **real physical member and slab connectivity plus code-governed design**. Navigate <a href="research.html#open-debt">Research → Open debt</a> for the exact blocked checks.</p>
      """)
    ],
    "right":{
      "title":"At a glance",
      "status":"ONE ACTIVE PROJECT",
      "groups":[
        ("Start here",[("Understand the original report (NEW)","original-report-guide.html"),("Website + Actions system tree (NEW)","system-map.html"),("Latest project report","r6p26-report.html"),("Reusable studio standard","studio.html"),("Projects register","projects.html")]),
        ("Live evidence",[("R6.26 source/result manifest","reports/r6p26/narayani-verified-manifest.json"),("R6.26 Actions QA","https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43607241579"),("R6.26 software release","https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.26-report-preview")]),
      ],
      "note":"F3 safety HOLD persists. Release status applies to code and reproducibility only."
    }
},
"studio":{
    "label":"Studio Standard","title":"One standard. Every future project.","eyebrow":"STUDIO STANDARD · V1.0 · 2026-11-16",
    "deck":"The permanent intake, model, calculation, verification, review and publishing contract for this engine. Ask another AI to read this page and the versioned file before starting a new project.",
    "status":"Normative engine workflow · Not a structural design code",
    "sections":[
      ("contract","The studio contract", """
      <p>Every project starts from original human source evidence, not from a convenient existing demonstration. Our reusable standard is stored as a versioned text file and a machine-readable blank project input packet. The standard belongs to this repository; A7 is a reference directory, not an independent template writer.</p>
      <div class="lead-actions"><a class="primary-link" href="standards/studio-standard-v1.md">Read Studio Standard v1.0</a><a class="subtle-link" href="standards/project-input-template-v1.json">Blank JSON intake contract</a></div>
      <div class="mini-table"><div><strong>Authority</strong><span>Drive originals → pinned CAD drawing registers → structural engine sources</span></div><div><strong>Methods</strong><span>OpenSees/OpenSeesPy + cited code/manual checks</span></div><div><strong>Approval</strong><span>Independent engineer reviews source geometry, demands, capacity and site conditions</span></div></div>
      """),
      ("intake","What our engine needs", """
      <div class="item-grid">
        <article class="mini-card"><span>01 / IDENTITY</span><h3>Project and revisions</h3><p>Unique project ID, location, occupancy, source revisions and original file links.</p></article>
        <article class="mini-card"><span>02 / PHYSICAL</span><h3>Drawings and geometry</h3><p>Grids, elevations, columns, beams, slabs, joints, openings, stairs and supports with source handles.</p></article>
        <article class="mini-card"><span>03 / MATERIALS</span><h3>Grades and sections</h3><p>Concrete, steel, effective stiffness, cover, reinforcement, load-bearing wall sections.</p></article>
        <article class="mini-card"><span>04 / ACTIONS</span><h3>Loads and code cases</h3><p>Dead, walls, occupancy, seismic, wind, mass source, load combinations and code references.</p></article>
        <article class="mini-card"><span>05 / GROUND</span><h3>Soil and foundations</h3><p>Boreholes, soil class, allowable bearing conditions, settlement, footing dimensions and restraints.</p></article>
        <article class="mini-card"><span>06 / ACCEPTANCE</span><h3>Review evidence</h3><p>Conflicts, verified versus assumed fields, reviewer decisions, resolved/adverse findings.</p></article>
      </div>
      <p class="micro-note">An absent measurement is <code>null / UNRESOLVED</code>, not zero, and a code default cannot manufacture a physical beam or footing.</p>
      """),
      ("pipeline","Internal workflow", """
      <div class="flow-steps"><div><span>V1</span><b>Intake</b><small>Drive and CAD source identity</small></div><div><span>V2</span><b>Topology</b><small>Real 3D physical connections</small></div><div><span>V3</span><b>Loads</b><small>Source-classed code actions</small></div><div><span>V4</span><b>FE solve</b><small>OpenSees six-axis balance</small></div><div><span>V5</span><b>Design</b><small>Strength, drift and foundation</small></div><div><span>V6</span><b>Review</b><small>Engineer hold/pass decisions</small></div><div><span>V7</span><b>Publish</b><small>CI, hash, Pages and release</small></div></div>
      <div class="caution"><b>Fail closed:</b> passing V4 numerical equilibrium does not automatically pass geometry V2, source loads V3, member design V5 or review V6.</div>
      """),
      ("output","What the engine must output", """
      <div class="asset-table"><div><b>Input packet</b><code>input.normalized.json</code><span>Field-level provenance / revision</span></div><div><b>Physical crosswalk</b><code>source-crosswalk.json</code><span>Original drawing object ↔ actual FE element</span></div><div><b>Applied actions</b><code>loads.csv / loads.json</code><span>Mass, imposed loads, combos and omissions</span></div><div><b>Solver outputs</b><code>analysis-results.json</code><span>Forces, moments, reactions, displacements</span></div><div><b>Design checks</b><code>design-checks.csv</code><span>Demand, capacity, failures and holds</span></div><div><b>Human report</b><code>report.html / PDF</code><span>Six chapters + annex, linked sources</span></div><div><b>Reproducibility</b><code>manifest.json</code><span>SHA256, Git SHA, QA run and approval state</span></div></div>
      <p class="micro-note">Currently live for Narayani: source/assumption JSON, 3D elastic frame scenarios, signed member/reaction CSV, HTML report and manifest. Full seismic, true physical slab shells and RC/foundation capacity are <strong>not yet delivered</strong>.</p>
      """),
      ("governance","Safety, authorship and decision rule", """
      <div class="mini-table"><div><strong>Source verified</strong><span>Direct source page/element evidence, coordinates and units.</span></div><div><strong>User-approved assumption</strong><span>Explicit permission, affected calculations, date and alternative.</span></div><div><strong>Code-derived assumption</strong><span>Official clause, formula, edition and applicability.</span></div><div><strong>Unresolved</strong><span>Cannot be promoted without evidence; scenario only if flagged.</span></div></div>
      <p>Raw client files live in governed Drive. Derived public source-safe data and code live in GitHub. A7 records repository pointers only. Every software release freezes exact QA-tested source; an engineering-design release requires independent acceptance.</p>
      """),
      ("handover","Use this standard with a future AI", """
      <div class="prompt-box"><div class="prompt-top"><strong>Copy this handover instruction</strong><button class="copy-prompt" type="button" data-copy="#handover-text">Copy prompt</button></div><pre id="handover-text">Apply JP Structural Analysis Studio Standard v1.0 from https://fabingurung.github.io/jp-structural-analysis/standards/studio-standard-v1.md and the blank JSON project template. Find my project's authoritative Google Drive drawings, soil reports and analysis and its matching jp-drawing-coordination project record. Pin source SHA, reconcile revisions, normalize members and loads with field-level provenance, preserve assumptions and engineering holds, independently calculate using OpenSees with checks V1–V7, and publish this as a separate new Projects entry with full QA and sources. Do not copy Narayani project dimensions or numeric results into the new project. Do not modify A7 unless explicitly asked. Never claim a completed structural design without actual governing design checks and professional review.</pre></div>
      <p>Use this <a href="standards/studio-standard-v1.md">versioned source file</a> as the durable rule set, not merely this page's descriptive summary.</p>
      """),
      ("right-rail","What the right context pane can hold", """
      <p>The right pane is for <strong>the information needed to make a decision without leaving the current chapter</strong>. We support a fixed set of context modules; each one is marked <i>Live now</i> or <i>Planned</i> so the interface never invents data.</p>
      <div class="asset-table">
      <div><b>Source links</b><span>Live now</span><span>Drawing/register/report/soil source</span></div>
      <div><b>Input basis</b><span>Live now</span><span>Grade, unit weight, code and assumptions</span></div>
      <div><b>Approval &amp; holds</b><span>Live now</span><span>F3 and unfinished source/code checks</span></div>
      <div><b>Source SHA / model revision</b><span>Live now</span><span>Exact pinned commit and receipt</span></div>
      <div><b>Actions &amp; QA</b><span>Live now</span><span>Last audited successful numerical and Pages runs</span></div>
      <div><b>Related project outputs</b><span>Live now</span><span>HTML report, results JSON and force CSV</span></div>
      <div><b>Quick glossary</b><span>Live now</span><span>FE, ULS/SLS, conditional cases, source labels</span></div>
      <div><b>Cross-repository pointers</b><span>Live now</span><span>Drive, CAD, SAR, A7 boundaries</span></div>
      <div><b>Selected member reactions</b><span>Planned</span><span>Live source-to-section drilldown and design utilization</span></div>
      <div><b>Load combination switch</b><span>Planned</span><span>Approved NBC seismic/wind and design demand</span></div>
      <div><b>Review comments &amp; decisions</b><span>Planned</span><span>Version-controlled issue-to-source resolution</span></div>
      <div><b>Material quantities / BOQ</b><span>Planned</span><span>Verified geometry → Estimation engine handoff</span></div>
      <div><b>Drawing revision diff</b><span>Planned</span><span>Overlay source changes from CAD repository</span></div>
      <div><b>Mesh comparison</b><span>Partly live</span><span>Research benchmark only, not real Narayani convergence</span></div>
      </div>
      """)
    ],
    "right":{
      "title":"Reusable rules","status":"V1.0 CANONICAL",
      "groups":[("Reference files",[("Studio Standard v1.0","standards/studio-standard-v1.md"),("Blank project schema","standards/project-input-template-v1.json"),("Drawing repository","https://github.com/FabinGurung/jp-drawing-coordination")]),
      ("Engine acceptance",[("V1–V7 contract","#pipeline"),("Deliverables","#output"),("AI reuse prompt","#handover")])],
      "note":"Conventions help other projects start consistently; each project still requires its own original source, site hazards and engineering review."
    }
},
"projects":{
    "label":"Projects","title":"Projects, without the noise.","eyebrow":"PROJECT PORTFOLIO · SOURCE-VERIFIED STATUS",
    "deck":"One project is currently connected to this engine. Each future building will get its own source contract, working model, report, decisions, testing and history rather than duplicated demo data.",
    "status":"1 connected · Others require separate project intake",
    "sections":[
      ("active","Active project", """
      <article class="project-card"><div class="project-overline">PRJ-000007 / HISTEL BUILDERS · POKHARA-15</div><div class="project-card-head"><h3>Narayani Parajuli Residence</h3><span class="status-pill">Source-conditioned analysis · HOLD</span></div>
      <p>Only current real-project engine application. The source graph contains original ground-floor column and footing marks. Its upper-floor connections, applied loads and boundary conditions are assumed for the independent elastic-frame report.</p>
      <div class="project-facts"><div><small>Original GF columns</small><b>23</b></div><div><small>Original footing outlines</small><b>21</b></div><div><small>Modeled members</small><b data-num="members">132</b></div><div><small>Independent cases</small><b>4</b></div></div>
      <div class="lead-actions"><a class="primary-link" href="original-report-guide.html">First: understand the original structural report</a><a class="subtle-link" href="r6p27-construction-review.html">Next: inspect drawing calculations</a><a class="subtle-link" href="r6p26-report.html">Original R6.26 OpenSees report</a><a class="subtle-link" href="r6p25.html">Connection QA</a></div></article>
      """),
      ("project-map","The project workspace", """
      <div class="link-list"><a href="original-report-guide.html"><span>00 / LEARN · REVISED ETABS REPORT · 2026-11-17</span><b>Understand the original structural report: results → calculations → codes → inputs</b><small>Deep beginner-readable explanation, Chapters 6 to 1, worked example and original Drive sources</small></a>
      <a href="r6p27-construction-review.html"><span>01 / SOURCE-DERIVED CALCULATIONS · 2026-11-16</span><b>21 actual footings, column steel, trial actions and corrected design decisions</b><small>Concrete quantities, 21→23 support mapping, F3/G1/C4 issues with cited sources</small></a>
      <a href="r6p26-report.html"><span>02 / ENGINE NUMERICS · R6.26</span><b>Independent six-chapter structural report</b><small>Signed elastic frame member and base reactions, unresolved full building design</small></a>
      <a href="r6p25.html"><span>02 / SOURCE REVIEW</span><b>Connection QA viewer</b><small>Original axis marks and assumed nearest-column ties</small></a>
      <a href="reports/r6p26/narayani-independent-frame-source.json"><span>03 / INPUTS</span><b>Normalized model and assumptions</b><small>Review exact model that the solver consumed</small></a>
      <a href="reports/r6p26/narayani-independent-frame-results.json"><span>04 / COMPUTATION</span><b>Independent numerical casebook</b><small>Full member actions, support reactions and displacements</small></a>
      <a href="reports/r6p26/narayani-verified-manifest.json"><span>05 / INTEGRITY</span><b>SHA256 report receipt</b><small>Exact verified source, output and artifact digests</small></a>
      <a href="https://docs.google.com/document/d/1_YD1CdbeeylbgEaJrb44ITAcDI8g0rjMn6d0I-Nqp34/edit"><span>06 / HUMAN AUDIT</span><b>Controlled Drive audit · V000004</b><small>Input choices, geotechnical conflicts and engineering holds</small></a></div>
      """),
      ("actual-vs-assumed","What is sourced and what is only assumed", """
      <div class="mini-table"><div><strong>Verified original source</strong><span>GF column XY marks, footing outlines, original beam-line candidates, soil report, original structural analysis references.</span></div>
      <div><strong>User-approved modelling basis</strong><span>Pokhara; NBC105:2025; concrete selfweight 20 kN/m³; 160 kPa provisional soil bearing scenario.</span></div>
      <div><strong>Assumed for calculations</strong><span>23 vertical column continuations through 3 floors; rigid beam-column joints, nearest-column source ties, area-proxy loads, fixed-base supports.</span></div>
      <div><strong>Not verified/solved</strong><span>Actual wall/slab/stair 3D shell geometry, governing earthquake/wind, ductility, demand/capacity of RC members and soil foundations.</span></div></div>
      <div class="caution"><b>Adverse source finding:</b> F3 remains NOT SAFE IN ONE WAY SHEAR. No field/permit approval is implied by an equilibrium-pass report.</div>
      """),
      ("new-project","How other projects join", """
      <div class="flow-steps"><div><span>01</span><b>Register</b><small>Existing project ID + Drive sources</small></div><div><span>02</span><b>Crosswalk</b><small>CAD register + original drawing SHA</small></div><div><span>03</span><b>Model</b><small>Real physical members + input statuses</small></div><div><span>04</span><b>Solve</b><small>Independent analysis + QA</small></div><div><span>05</span><b>Publish</b><small>Own project page, report and history</small></div></div>
      <p><b>No other building is displayed as using the engine yet.</b> Other projects may already have drawings in Drive or in the drawing repository, but onboarding into this structural-analysis engine is a separate source-governed task.</p>
      <div class="lead-actions"><a class="subtle-link" href="studio.html#handover">Reuse AI handover prompt</a><a class="subtle-link" href="standards/project-input-template-v1.json">Start with blank JSON packet</a></div>
      """)
    ],
    "right":{"title":"Narayani context","status":"ENGINEERING HOLD",
      "groups":[("Working evidence",[("Original report explained (START HERE)","original-report-guide.html"),("Drawings → actual calculations","r6p27-construction-review.html"),("Read R6.26 engine report","r6p26-report.html"),("Review connections","r6p25.html"),("View source JSON","reports/r6p26/narayani-independent-frame-source.json")]),
      ("Authoritative files",[("Drawing-derived Narayani geometry","https://github.com/FabinGurung/jp-drawing-coordination/tree/main/public/data/projects/narayani-parajuli"),("Geotechnical report","https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"),("Controlled decisions · V000004","https://docs.google.com/document/d/1_YD1CdbeeylbgEaJrb44ITAcDI8g0rjMn6d0I-Nqp34/edit")])],
      "note":"Source geometry is not the same thing as professionally accepted connectivity. Unresolved safety findings remain visible."
    }
},
"developers":{
    "label":"Developers","title":"Make every result reproducible.","eyebrow":"ENGINEERING / DEVELOPMENT CONTROL ROOM",
    "deck":"Where to find the code, independent numerical QA, live Pages checks, audit trails, release milestones and source boundaries—without hunting through anonymous R-numbers.",
    "status":"Numerical pipeline: PASS · Construction approval: HOLD",
    "sections":[
      ("environments","System map and source authority", """
      <p><a href="system-map.html"><strong>Open the full tree of the current repository, GitHub Pages and all 13 Actions workflows.</strong></a> The explorer links each tracked source file and published file; it does not require knowing release numbers.</p><div class="flow-steps"><div><span>DRIVE</span><b>Originals</b><small>Human-approved sources</small></div><div><span>CAD</span><b>Drawing graph</b><small>Original DXF / member registers</small></div><div><span>SAR</span><b>Engine</b><small>OpenSees and source checks</small></div><div><span>CI</span><b>Actions</b><small>Re-run + fail on source drift</small></div><div><span>WEB</span><b>Pages</b><small>Review only, not acceptance</small></div></div>
      <p><a href="https://github.com/FabinGurung/jp-structural-analysis">This GitHub repository</a> owns the structural engine and report. <a href="https://github.com/FabinGurung/jp-drawing-coordination">Drawing Coordination</a> owns geometric models. <a href="https://github.com/FabinGurung/jp-a7-system-registry">A7 Registry</a> is only the federated directory, not a writer for this repository.</p>
      """),
      ("qa","Numerical QA and browser test runs", """
      <div class="link-list"><a href="https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43607241579"><span>2026-11-14 · QA</span><b>R6.26 — independent Narayani report tests</b><small>26 tests · signed 3D frame output · mobile/desktop Chromium PASS</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43607241584"><span>2026-11-14 · DEPLOY</span><b>R6.26 — published Pages live verification</b><small>81 build steps · successful deploy · live F3/source receipt checks</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43591081391"><span>2026-11-14 · QA</span><b>R6.25 — source and assumed-connection browser QA</b><small>Original-DXF source marks, 390px selection and gap review</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43437254183"><span>2026-11-13 · RELEASE</span><b>R6.24 — synthetic ShellMITC4 / mesh software preview</b><small>Numerical and responsive UI verification</small></a></div>
      <p class="micro-note">These are source-linked verified historical runs. Future runs are available in <a href="https://github.com/FabinGurung/jp-structural-analysis/actions">all Actions</a>. A green run proves the declared tests passed, not the actual building is safe.</p>
      """),
      ("engines","What the engine contains now", """
      <div class="asset-table">
      <div><b>R6.10</b><span>2026-11-09 · Released research preview</span><span>Shell/diaphragm study and first-party FE development.</span></div>
      <div><b>R6.17–R6.18</b><span>Source bounded</span><span>Support graph, disconnected shell investigations and mesh feasibility.</span></div>
      <div><b>R6.23</b><span>Solved synthetic</span><span>Independent 3D elastic ShellMITC4, openings, frames, diaphragms.</span></div>
      <div><b>R6.24</b><span>2026-11-13 · Prerelease</span><span>Source-equivalent two-grid sensitivity and research viewer.</span></div>
      <div><b>R6.25</b><span>2026-11-14 · Integrated</span><span>Narayani actual GF drawing element intake and assumed-connection review.</span></div>
      <div><b>R6.26</b><span>2026-11-16 · Prerelease</span><span>Independent 132-member source-conditioned elastic frame, six-chapter report, signed CSV/JSON.</span></div></div>
      <div class="lead-actions"><a class="subtle-link" href="https://github.com/FabinGurung/jp-structural-analysis/tree/main/r6p26">R6.26 calculation code</a><a class="subtle-link" href="https://github.com/FabinGurung/jp-structural-analysis/tree/main/r6p23">R6.23 shell source</a></div>
      """),
      ("releases","Milestones, tags and frozen software baselines", """
      <div class="timeline"><div><time>2026-11-09</time><b>r6.10 · software research</b><span>Historic scoped prerelease. <a href="https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.10">Release record</a></span></div>
      <div><time>2026-11-13</time><b>r6.24-preview · mesh/shell software</b><span>Immutable scoped prerelease. <a href="https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.24-preview">Release record</a></span></div>
      <div><time>2026-11-16</time><b>r6.26-report-preview · independent report software</b><span>Frozen Narayani report output and exact historical QA. <a href="https://github.com/FabinGurung/jp-structural-analysis/releases/tag/r6.26-report-preview">Release record</a></span></div></div>
      <p>Changes to the website are versioned separately from frozen solver tags. Engineering final IFC/approval cannot be awarded by software CI alone.</p>
      """),
      ("audit","Audit, decisions and source history", """
      <div class="link-list"><a href="https://docs.google.com/document/d/1_YD1CdbeeylbgEaJrb44ITAcDI8g0rjMn6d0I-Nqp34/edit"><span>2026-11-14 · GOOGLE DRIVE · V000004</span><b>Narayani source normalization and engineering audit</b><small>Verified geotechnical filing, user-approved values, conflicts and source status</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/issues/7"><span>CONTINUING ISSUE LOG</span><b>Structural research and design HOLD register</b><small>Progress comments with source and QA runs. Not a closed design approval.</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/pull/41"><span>2026-11-14 · MERGED</span><b>R6.26 source-to-report implementation history</b><small>OpenSees frame, report and UI changes</small></a>
      <a href="https://github.com/FabinGurung/jp-structural-analysis/pull/40"><span>2026-11-14 · MERGED</span><b>R6.25 mobile source connection QA implementation</b><small>Physical assumptions and original DXF traceability</small></a></div>
      """),
      ("data","Developer data catalogue", """
      <div class="asset-table"><div><b>Source model</b><code>r6p26/narayani-independent-frame-source.json</code><span>Model assumptions and member IDs.</span></div>
      <div><b>Calculation results</b><code>r6p26/narayani-independent-frame-results.json</code><span>4 cases, signed actions, 6-axis equilibrium.</span></div>
      <div><b>Forces</b><code>narayani-member-forces.csv</code><span>1,056 I/J end rows.</span></div>
      <div><b>Reactions</b><code>narayani-base-reactions.csv</code><span>92 support records.</span></div>
      <div><b>Receipt</b><code>narayani-verified-manifest.json</code><span>SHA256 source/outputs, safety flags.</span></div>
      <div><b>Studio template</b><code>studio-standard-v1.md</code><span>Next AI source/engine guardrails.</span></div></div>
      """)
    ],
    "right":{"title":"Developer quicklinks","status":"SOFTWARE QA GREEN",
      "groups":[("Repository",[("Source tree","https://github.com/FabinGurung/jp-structural-analysis"),("All Actions","https://github.com/FabinGurung/jp-structural-analysis/actions"),("Releases","https://github.com/FabinGurung/jp-structural-analysis/releases")]),
      ("Verifiable numbers",[("Signed results JSON","reports/r6p26/narayani-independent-frame-results.json"),("Member forces CSV","reports/r6p26/narayani-member-forces.csv"),("SHA256 manifest","reports/r6p26/narayani-verified-manifest.json")])],
      "note":"Provenance / exact run / SHA receipts are displayed separately from engineering acceptance."
    }
},
"research":{
    "label":"Research","title":"Solved, investigated, and still open.","eyebrow":"RESEARCH · PHYSICAL MODEL QUALITY",
    "deck":"An evidence-led record of computational advances and unresolved structural engineering debt. A software experiment stays visibly different from code-compliant building design.",
    "status":"F3 unresolved · Real geometry and member design on HOLD",
    "sections":[
      ("completed","Completed scoped research", """
      <div class="timeline"><div><time>R6.10 / 2026-11-09</time><b>Research baseline</b><span>First-party source-bounded shell/diaphragm calculations and engineering hold framework.</span></div>
      <div><time>R6.17–18</time><b>Actual source topology investigations</b><span>Source graph connectivity, 12 unsupported shells and 77 ambiguous beam-perimeter cases explored as research debt; not accepted to final design.</span></div>
      <div><time>R6.23–24 / 2026-11-13</time><b>Independent synthetic 3D shell/frame FE</b><span>Real ShellMITC4, two diaphragm modes, 31→124 shell source-equivalent refinement, benchmark-specific tests.</span></div>
      <div><time>R6.25 / 2026-11-14</time><b>Narayani source element intake</b><span>23 GF source column marks, 21 footing outlines and 66 source line candidates with 19 endpoint distance-screen exceptions.</span></div>
      <div><time>R6.26 / 2026-11-14</time><b>Real source-conditioned independent frame</b><span>132 assumed-frame members, 4 real OpenSees scenarios, member forces and full six-axis equilibrium in report structure.</span></div></div>
      """),
      ("open-debt","Outstanding structural debt (not suppressed)", """
      <div class="risk-list">
      <div><span class="risk-marker">01</span><div><b>Physical support and GF→FF→SF continuity</b><p>Verify individual beams, column stacks, slab/beam contacts, stairs and actual wall-bearing paths from current original drawings, not just a nearest-column hypothesis.</p></div></div>
      <div><span class="risk-marker">02</span><div><b>F3 is NOT SAFE IN ONE WAY SHEAR</b><p>Recompute governing factored reactions and geometry-specific capacity; professional redesign and acceptance required.</p></div></div>
      <div><span class="risk-marker">03</span><div><b>Full gravity/load zoning</b><p>Prove wall line assignments, slab shell areas, stair/corridor/terrace live loads and source-to-mass conservation.</p></div></div>
      <div><span class="risk-marker">04</span><div><b>NBC 105:2025 site seismic actions</b><p>Resolve geotechnical 2020 Type B versus older structural report Type D, apply current site class, spectrum, ductility, irregularity and displacement checks.</p></div></div>
      <div><span class="risk-marker">05</span><div><b>Actual frame/shell FE and mesh convergence</b><p>Real Narayani slab/opening shape, shell supports and physically equivalent 3-resolution sensitivity—not only synthetic 31→124 shell research.</p></div></div>
      <div><span class="risk-marker">06</span><div><b>RC and foundation design capacity</b><p>Member/joint beam-column checks, reinforcement and development, slab/stair shear, G1 discrepancy, combined footing CF1 eccentricity, bearing and settlement.</p></div></div>
      </div>
      """),
      ("models","Distinguish the research models", """
      <div class="mini-table"><div><strong>Synthetic shell reference</strong><span>R6.23/24: real numerics on a deliberately small synthetic 2-floor grid. Does not represent Narayani physical geometry.</span></div>
      <div><strong>Source drawing hypothesis</strong><span>R6.25: actual Narayani GF drawing positions + explicitly assumed three-level connections. QA geometry, no FE forces.</span></div>
      <div><strong>Independent assumed frame</strong><span>R6.26: actual GF sourced positions + assumed member and load inputs; 3D elastic frame solved for bounded scenarios. Not full slab FE.</span></div>
      <div><strong>Engineering accepted SAR</strong><span>NOT AVAILABLE: requires source topology, code loads, capacity/design and independent professional review.</span></div></div>
      """),
      ("next","Next development priority", """
      <div class="feature-panel"><div><p class="eyebrow">NEXT · R6.27 RESEARCH GATE</p><h3>Physical geometry → governing code design</h3><p>Build the actual source-registered irregular frame-and-shell graph, assign wall and occupancy loads, solve source-equivalent FE refinements, then validate NBC105:2025 seismic, member/footing capacity, and F3 remediation. Keep a separate exception register for every unsupported member.</p><div class="inline-links"><a href="studio.html#pipeline">Follow Studio V1–V7</a><a href="projects.html#actual-vs-assumed">Review Narayani evidence</a></div></div></div>
      <p>Additional experiments may be added under Research, but they cannot automatically advance the current building's approval status.</p>
      """)
    ],
    "right":{"title":"Research evidence","status":"PHYSICAL DESIGN HOLD",
      "groups":[("Research tools",[("Synthetic FE workbench","r6p23.html"),("Narayani assumptions","r6p25.html"),("Independent R6.26 report","r6p26-report.html")]),
      ("Reference and review",[("Official DUDBC codes","https://dudbc.gov.np/pages/building-code/"),("Original soil report","https://drive.google.com/file/d/13y0b0v8BiL2ooMXy0BFn2dtdSHWNOg2N/view"),("Research issue/decision log","https://github.com/FabinGurung/jp-structural-analysis/issues/7")])],
      "note":"A solver result can be useful research while remaining unacceptable as construction design."
    }
},
"more":{
    "label":"More","title":"Everything preserved. Nothing buried.","eyebrow":"MORE · LEGACY, ARCHIVE & REFERENCES",
    "deck":"The important product routes are on Home and Projects. Historical reports, experiments, alternate viewers, underlying evidence and tools remain indexed here with plain-language names and dates.",
    "status":"Historical routes preserved · No destructive migration",
    "sections":[
      ("library","Preserved historic website pages", """
      <div class="link-list"><a href="system-map.html"><span>CURRENT / SYSTEM EXPLAINER · 2026-11-17</span><b>Full repository, Pages and GitHub Actions hierarchy</b><small>All public generated paths and all workflow files; clear roles and links</small></a>
      <a href="original-report-guide.html"><span>CURRENT / EDUCATION · 2026-11-17</span><b>Original Narayani structural report explained backwards</b><small>What final result requires, section by section</small></a>
      <a href="legacy-home.html"><span>ARCHIVE / PRE-PORTAL</span><b>Previous structural-analysis homepage</b><small>Original pre-redesign navigation and landing content</small></a>
      <a href="legacy-more.html"><span>ARCHIVE / PRE-PORTAL</span><b>Earlier methods and learning guide</b><small>Long educational information, historic workflow explanations</small></a>
      <a href="report.html"><span>HISTORICAL · ORIGINAL ENGINE</span><b>Six-chapter legacy report book</b><small>Earlier first-party report experiments and detailed annex history</small></a>
      <a href="projects/index.html"><span>HISTORICAL / PROJECT INDEX</span><b>Previous project reports listing</b><small>Kept for existing links; only Narayani uses new project intake</small></a>
      <a href="project-lab.html"><span>HISTORICAL · LAB</span><b>Original visual engineering lab</b><small>Earlier plan/3D/solver presentation, not latest main report</small></a>
      <a href="g15-3d.html"><span>HISTORICAL · 3D</span><b>Original interactive 3D research viewer</b><small>Legacy bounded structural visualizations</small></a></div>
      """),
      ("tool-index","Working calculators, research and study tools", """
      <div class="item-grid">
      <article class="mini-card"><span>2026-11-13 / RESEARCH</span><h3>Synthetic 3D shell viewer</h3><p>OpenSees research floors, cases and two-grid 31→124 shell demonstration.</p><a href="r6p23.html">Open workbench</a></article>
      <article class="mini-card"><span>2026-11-14 / SOURCE</span><h3>Narayani connection reviewer</h3><p>Original DXF traceability and assumed 66 beam/source candidates, nearest-column gaps.</p><a href="r6p25.html">Open source QA</a></article>
      <article class="mini-card"><span>2026-11-14 / ENGINE</span><h3>Narayani numerical report</h3><p>4 real frame scenarios, forces and base reactions, six chapters.</p><a href="r6p26-report.html">Open report</a></article>
      <article class="mini-card"><span>HISTORICAL / CALCULATIONS</span><h3>Hand worked source calculations</h3><p>Older reference checks and engineering learning examples.</p><a href="worked-calculations.html">Open archive</a></article></div>
      """),
      ("capabilities","What GitHub Pages and Actions can host", """
      <p>Keep all these capabilities indexed even when they are not ready as final engineering products. Status labels tell you which are operational today.</p>
      <div class="asset-table">
      <div><b>Source and version register</b><span>Live</span><span>Original-drive provenance and pinned CAD/analysis commits</span></div>
      <div><b>Source model and assumption inspector</b><span>Live</span><span>GF axes, footing outlines, candidate connections, source statuses</span></div>
      <div><b>OpenSees model and signed actions</b><span>Live, bounded</span><span>R6.26 elastic frame and synthetic 3D shell benchmark</span></div>
      <div><b>Project report and printable views</b><span>Live, bounded</span><span>Six-chapter HTML, CSV, JSON and manifest</span></div>
      <div><b>Actions QA and deployment logs</b><span>Live</span><span>Numerical tests, browser mobile tests, Pages publishing</span></div>
      <div><b>Releases and historical audit</b><span>Live</span><span>Immutable software milestones and Drive/issue history</span></div>
      <div><b>Project switcher / templates</b><span>Live, 1 project</span><span>Studio reusable standard + blank input contract</span></div>
      <div><b>True irregular shell and 3D section viewer</b><span>Planned</span><span>Project physical shell/beam graph and reinforcement details</span></div>
      <div><b>Seismic, wind and load combination workspace</b><span>Planned</span><span>Site-class verification, code spectra and design cases</span></div>
      <div><b>RC member and footing code checker</b><span>Planned</span><span>Demand/capacity, detailing, bearing, settlement and F3 redesign</span></div>
      <div><b>Drawing revision / model diff</b><span>Planned</span><span>Source CAD/version delta and geometric reanalysis</span></div>
      <div><b>Material quantity and estimation integration</b><span>Planned</span><span>Verified members → costing engine, not guessed takeoff</span></div>
      <div><b>Reviewer approvals and exception triage</b><span>Planned</span><span>Tracked evidence, reviewer, date, approval stage</span></div>
      <div><b>Portfolio reports by project and date</b><span>Planned</span><span>Source-independent project pages after onboarding</span></div>
      </div>
      """),
      ("glossary","Terms and reading shortcuts", """
      <div class="mini-table"><div><strong>SAR</strong><span>Structural Analysis Report; a document format, not necessarily an approved design.</span></div><div><strong>FE / FEM</strong><span>Finite-element modelling and solution; validity depends on source geometry and boundary conditions.</span></div><div><strong>DL / LL</strong><span>Dead and imposed/live loads; some current Narayani loads are proxies.</span></div><div><strong>PX10 / PY10</strong><span>10 kN per floor numerical probes, not seismic design actions.</span></div><div><strong>ULS / SLS</strong><span>Ultimate and serviceability limit states; not complete in R6.26.</span></div><div><strong>HOLD</strong><span>Unresolved source/physical/engineering approval, not a software run failure.</span></div><div><strong>SHA256</strong><span>Cryptographic output checksum used to read back exact model and report artifacts.</span></div></div>
      """),
      ("external","Connected systems and official code references", """
      <div class="link-list"><a href="https://github.com/FabinGurung/jp-drawing-coordination"><span>CAD / SOURCE GEOMETRY</span><b>Drawing Coordination repository</b><small>Independent drawing source registers and project geometry</small></a>
      <a href="https://github.com/FabinGurung/jp-a7-system-registry"><span>A7 / DIRECTORY</span><b>Federated source and service registry</b><small>Lookup only; structurally separate repository</small></a>
      <a href="https://dudbc.gov.np/pages/building-code/"><span>CODE / GOVERNMENT</span><b>DUDBC building codes</b><small>Check correct edition, occupancy and site applicability</small></a>
      <a href="https://openseespydoc.readthedocs.io/en/stable/src/elasticBeamColumn.html"><span>ENGINE / REFERENCE</span><b>OpenSeesPy elastic frame documentation</b><small>Solver API used in independent R6.26 report</small></a></div>
      """)
    ],
    "right":{"title":"Archive guide","status":"PRESERVED HISTORY",
      "groups":[("Most visited",[("Latest Narayani report","r6p26-report.html"),("Past report book","report.html"),("Old homepage","legacy-home.html")]),("Governing files",[("Reusable studio rules","standards/studio-standard-v1.md"),("Research and holds","research.html"),("Developer QA","developers.html")])],
      "note":"Archive means superseded navigation, not invalid research. Historical URLs remain addressable and can still contain unfinished engineering."
    }
}
}
