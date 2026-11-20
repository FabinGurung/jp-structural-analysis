# R6.31 — Reusable rectangular beam flexure and shear, IS 456:2000

**Status:** working and source-tested isolated strength-calculation module for a **synthetic** benchmark, not approved real-building member design.

## What now actually calculates

\`beam_design.py\` takes a signed R6.23 OpenSeesPy record. It evaluates both \`FLEXIBLE_SHELL\` and \`RIGID_INPLANE_MPC\`, every real solved beam, both ends, and the two synthetic \`U_PLUS\`/\`U_MINUS\` combinations. Coverage: **32 × 2 × 2 × 2 = 256** reproducible checks.

At every single row, the vertical-plane **My and conjugate Vz** come from the **same beam, end, diaphragm mode and combination**. Its other \`N,Vy,T,Mz\` are preserved in the output, not silently treated as checked or zero.

- **Beam flexure:** IS456:2000 38.1/Annex G stress block, \`x_u<=x_u,max\`, min 0.85bd/fy, max 0.04bD. Computes As-required, assuming simple rectangle and provided top/bottom longitudinal steel; if singly reinforced limit is exceeded, refuses to invent bar count.
- **Vertical shear:** Clauses 40.1–40.4, Tables 19 and 20, min and maximum vertical stirrup spacing (26.5.1.5–.6). Looks up and linearly interpolates Table 19 by assumed continuous tensile bar percentage. Calculates stirrup required strength and spacing; caps effective stirrup fy to 415 MPa.
- **Demonstration:** M25/Fe500, 300×450 mm, assumed effective depth 405 mm, 3×Ø16 tension bars on each face, two-legged Ø8 stirrups at 150 mm. This is the synthetic model, not Narayani's M20/20kN/m³ source data.
- **Inputs:** independently solved \`data/r6p23-preview.json\`, itself SHA-checked to \`r6p23.runner.reference_fixture()\`.
- **Outputs:** six-chapter \`example-sar-report.html#design\`, machine-readable \`reports/example-sar/example-sar-numbers.json\` with all 256 detailed rows and a \`reports/example-sar/beam-end-checks.csv\`, each pinned in checksummed receipt.
- **Pure and integration tests:** \`python -m pytest -q r6p30/test_beam_design.py portal/test_engine_atlas.py\`. The second test actually solves the OpenSees source fixture fresh.
- **Code source:** https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf .

## Deliberate physical-design boundaries

Not calculated: actual critical shear section from support face, longitudinal bar continuity, real end detailing/anchorage, other-axis bending and shear, biaxial/torsional interactions, shear/torsion reinforcement per Clause 41, beam-column joint shear, ductile seismic reinforcement per IS13920 and NBC105, capacity combinations at actual site, deflection/crack control or a complete construction bar schedule.

The synthetic combination \`1.2DL+1.5LL±HX\` uses a **10kN lateral diagnostic**, not earthquake design actions. No Narayani real-project status or original F3 'NOT SAFE' verdict changes. A passing **isolated My/Vz section screen is not structural approval**.

## Roadmap without duplicate FE solvers

Keep current R6.23/R6.26 OpenSees codes as source of forces and add reusable, unit-tested design components sequentially: 1. critical sections + torsion/ductility for beams, 2. columns P–M–M, 3. two-way slab reinforcement, 4. real footing isolated/combined + settlement/punching, 5. staircase analysis/details, 6. complete original-equivalent report generator. Each module consumes source-provenance-carrying forces and declares governing code editions and limitations.
