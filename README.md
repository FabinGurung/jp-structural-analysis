# JP Structural Analysis — Active Working Product

**Live website:** https://fabingurung.github.io/jp-structural-analysis/

**Complete historical archive in Google Drive:** https://drive.google.com/drive/folders/1ViudVSKVdDr7OPl-xFjJTankIDAEQJoO

The Drive archive preserves the full pre-cleanup source and Git history bundle, previous published website, responsive QA and source-design QA. The current source tree keeps only the working reporting components, not the experimental web pages and workflows.

## Active software
- \`r6p23/engine.py\`, \`r6p23/runner.py\`: actual OpenSeesPy ShellMITC4 + elastic beam/column benchmark, synthetic two-floor model.
- \`r6p30/beam_design.py\`: isolated IS456 My/Vz beam flexure + vertical shear, 256 matched signed end-result checks.
- `r6p30/column_pmm.py`: short-column numerical uniaxial reference (64 strips) with IS456 §39.1(a,b) strain regimes and §39.6 biaxial interaction. Signed OpenSees local I(+)/J(−) compression mapping; tensile rows excluded; §25.4 one-axis minimum eccentricity alternatives. These are **NOT** SP16-verified RC column capacities.
- `r6p30/column_validation.py`: independent analytical uniform-compression force and 32/64/128-strip convergence benchmarks; results available in the generated site's `data/column-verification.json`.
- \`site_builder.py\`: one six-chapter printable report; four simple site areas: Home / Studio Standard / Projects / More.
- Two Actions: \`ci.yml\` for tests, \`pages.yml\` for publishing. No research experiments scheduled.

## Reproduce
Python 3.12; \`pip install -r requirements.txt\`; \`pytest -q r6p30/test_beam_design.py r6p30/test_column_pmm.py tests/test_product.py\`; \`python site_builder.py\`.

## Governance
This is a *hypothetical* structural analysis and limited member calculation prototype, not Narayani construction approval. Column local signed N is interpreted by element-end convention for bottom I → top J in the synthetic model; tensile actions are not screened as compression. The actual member orientation and load signs must be verified for any real building. Beam flexure/shear is not an issued bar schedule. Original F3 one-way shear **NOT SAFE** is not cleared.

Original PDF: https://drive.google.com/file/d/1TpWUmOdrcQqOpkN6qvmhZ12KrYaNABBM/view

Design reference IS456: https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf
