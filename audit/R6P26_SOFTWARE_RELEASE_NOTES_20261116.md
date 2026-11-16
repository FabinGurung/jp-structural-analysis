# R6.26 — Narayani independent structural report (Software Preview)

**Classification: SOFTWARE RESEARCH PRERELEASE · ENGINEERING HOLD · NOT FOR PERMIT OR CONSTRUCTION**

Frozen QA-passed software commit: `1d6394d1d871b070d17f056b6eec4c74efdfb3af` (14 November 2026).

### Achievement delivered

- Source-derived proposed Block B frame using **23 original GF drawing column marks**, provisional 3-storey continuation, individually source-linked beam connection hypotheses, and original geotechnical provenance.
- Independent OpenSeesPy 3D elastic frame: **132 modeled members**, **four independently solved scenarios**, **1,056 signed I/J force records**, **92 base support reactions**, floor displacements and six-axis equilibrium checks.
- Original-source-structured, six-chapter HTML report with interactive frame inspector, case-by-case force/reaction tables, reproducible JSON and CSV with SHA256 receipt.
- Source-reconstruction and report QA: **26 passing tests**, verified real 390px mobile and 1440px desktop browser interaction, successful deployed Pages build with 81 steps and live CDN integrity verification.

### Verifiable links

- [Published six-chapter report](https://fabingurung.github.io/jp-structural-analysis/r6p26-report.html)
- [Source and calculation model](https://fabingurung.github.io/jp-structural-analysis/reports/r6p26/narayani-independent-frame-source.json)
- [Independent numerical OpenSees results](https://fabingurung.github.io/jp-structural-analysis/reports/r6p26/narayani-independent-frame-results.json)
- [Signed member-end CSV](https://fabingurung.github.io/jp-structural-analysis/reports/r6p26/narayani-member-forces.csv)
- [Signed support-reaction CSV](https://fabingurung.github.io/jp-structural-analysis/reports/r6p26/narayani-base-reactions.csv)
- [SHA256 manifest](https://fabingurung.github.io/jp-structural-analysis/reports/r6p26/narayani-verified-manifest.json)
- [Independent numerical and browser QA run](https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43607241579)
- [Successful Pages build/deploy and live verification](https://github.com/FabinGurung/jp-structural-analysis/actions/runs/43607241584)
- [Source PR #41](https://github.com/FabinGurung/jp-structural-analysis/pull/41)

### Protected exclusions

The GF drawing positions are sourced but **actual FF/SF columns, beam ends, slabs, wall supports, diaphragms, staircases and foundations have unresolved physical connectivity**. Applied floor finishes and imposed load distribution use declared proxies. Main/partition wall loads have **not** been applied. The 10 kN per floor lateral PX10/PY10 loads are numerical probes, **not NBC105:2025 seismic design**. There is no full site-specific earthquake/wind action, strength/ductility, reinforcement, slab, footing, bearing/settlement or professional engineering approval. Historical footing **F3 is NOT SAFE IN ONE WAY SHEAR** and remains adverse.

Release only the software/reproducible report, not a full building structural analysis/design approval. Raw private Drive sources are not bundled.

### Next milestone

R6.27 real-source member and slab connectivity reconciliation, code-governed loads including seismic/wind, true source-compatible frame/shell FE, independent convergence and complete RC/foundation capacity checking under professional review. Existing r6.24-preview tag remains unchanged.
