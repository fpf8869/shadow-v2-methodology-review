# Public reproduction audit — 2026-10-13 (America/New_York)

## Verified in the original research runtime
- The preserved experimental mean predictor `shadow_v2_research.py` ran unchanged with the three publisher-hash-matched 2026 source CSVs.
- `python -m unittest -q test_shadow_v2 test_joint_gamma_poisson test_protocol`: **28 tests passed** in the research runtime.
- Exposed evaluation cohort: Oct 5–11, 2026; 390 training games strictly before Oct 5, 58 later games.
- Refitting the same research code on the identical authenticated inputs reproduced all **58 home and away score means** against the earlier exposed evaluation file to maximum absolute error **7.11e-15**.
- These are engineering reproduction results, not an independent GitHub-hosted CI run or prospective predictive validation.

## Source files
Original CSVs are not rehosted. Download exact source revisions using SHA-256 values in `REPRODUCIBILITY.md`. The new `test_source_reproduction.py` can run after setting `NCAAF_SCHEDULE_CSV`, `NCAAF_BOX_CSV`, and `NCAAF_PASSING_CSV`.

## Limitations
- The evaluator script `evaluate_exposed.py` was published but has not yet been independently executed from a clean clone on an external machine.
- The already-exposed 58-game evaluation is **not** untouched validation.
- The fixed k=20 dispersion and 10% shared scoring settings are not validated.
- Independent external methodological review and source publication-time attestation are outstanding.
- Eligible prospective observations: **0**.
- No production release, MGM EV, or FIRE.
