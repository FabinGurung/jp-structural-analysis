# JP Structural Analysis — Active Working Product

**Live website:** https://fabingurung.github.io/jp-structural-analysis/

**Complete historical archive in Google Drive:** https://drive.google.com/drive/folders/1ViudVSKVdDr7OPl-xFjJTankIDAEQJoO

The Drive archive preserves the full pre-cleanup source and Git history bundle, previous published website, responsive QA and source-design QA. The current source tree keeps only the working reporting components, not the experimental web pages and workflows.

## Active software
- \`r6p23/engine.py\`, \`r6p23/runner.py\`: actual OpenSeesPy ShellMITC4 + elastic beam/column benchmark, synthetic two-floor model.
- \`r6p30/beam_design.py\`: isolated IS456 My/Vz beam flexure + vertical shear, 256 matched signed end-result checks.
- `r6p30/column_pmm.py`: short-column numerical uniaxial reference (64 strips) with IS456 §39.1(a,b) strain regimes and §39.6 biaxial interaction. Signed OpenSees local I(+)/J(−) compression mapping; tensile rows excluded; §25.4 one-axis minimum eccentricity alternatives. These are **NOT** SP16-verified RC column capacities.
- `r6p30/column_validation.py`: independent analytical uniform-compression force and 32/64/128-strip convergence benchmarks; results available in the generated site's `data/column-verification.json`.
- **Independent NPTEL SP16 chart example:** A 450 × 500 mm M25 Fe415 column with 12Ø16 bars, 56 mm centre cover and Pu=1,600 kN, compared against IIT Kharagpur Lesson 26 Q.5/A.5. Published chart-derived major/minor moments are 246.376/215.156 kN·m. We perform an independent numerical strain-compatibility calculation; a predeclared 3% research agreement band applies to both directions. The figure's M20 caption conflicts with the M25 problem and worked answer, so that discrepancy remains recorded. Details in the report and data/column-verification.json. One worked example is NOT complete SP16 chart certification. Source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l26.pdf .
- \`site_builder.py\`: one six-chapter printable report; four simple site areas: Home / Studio Standard / Projects / More.
- Two Actions: \`ci.yml\` for tests, \`pages.yml\` for publishing. No research experiments scheduled.


## Current design verification and Drive archive

R6.35 F3: `r6p30/footing_f3.py` preserves the original Narayani page-61 NOT SAFE IN ONE WAY SHEAR verdict. A NEW proposed 2.10 m square UNIFORM 550 mm deep footing with 12mm @150 bottom mat passes the listed one-way shear, punching, bending, minimum steel, and gross concentric bearing screens under the original 571 kN service-load assumption. This DOES NOT establish safety for unknown foundation moments, seismic actions, 1.8 m versus 2.1 m source location conflict, soil eccentricity/settlement, actual sloped geometry, or field construction. Original version is not overwritten. The eight-page research report and detailed calculation spreadsheets/scripts live **only in Drive**: https://drive.google.com/drive/folders/1qX-FJkPw8p9EF1yINTcPf5kAMxJIMJzU .

R6.35 SP16: active numerical code now uses interpolated IIT Kharagpur NPTEL Lesson23 SP16 Table A steel stress points instead of the erroneous optimistic bilinear steel. CI checks 12- and 20-bar independent NPTEL chart examples. The Drive research audit has 13 individually published reference values within a predeclared 3% *research* band, plus 720 internal mesh-refinement calculations across 3 chart families and Fe250/415/500; 720 is NOT 720 independent chart comparisons. The full SP16 source chart suite and actual building design have NOT been formally certified. Source: https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m10l23.pdf .

## Reproduce
Python 3.12; \`pip install -r requirements.txt\`; \`pytest -q r6p30/test_beam_design.py r6p30/test_column_pmm.py r6p30/test_footing_f3.py tests/test_product.py\`; \`python site_builder.py\`.

## Governance
This is a *hypothetical* structural analysis and limited member calculation prototype, not Narayani construction approval. Column local signed N is interpreted by element-end convention for bottom I → top J in the synthetic model; tensile actions are not screened as compression. The actual member orientation and load signs must be verified for any real building. Beam flexure/shear is not an issued bar schedule. Original F3 one-way shear **NOT SAFE** is not cleared.

Original PDF: https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view

Design reference IS456: https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf
