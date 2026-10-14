# NCAAF Shadow V2 — open volunteer methodology review

**Research-only. No independent reviewer sign-off, no production release, no MGM EV, no FIRE.**

This repository publishes the experimental mean predictor and three score-distribution implementations, along with a script to regenerate the already-exposed 58-game diagnostic from authenticated public data. It is **not** the original Shadow production engine.

## Files
- `shadow_v2_research.py` — unchanged separate V2 experimental score-mean model.
- `test_shadow_v2.py` — mean-predictor software checks.
- `shadow_joint_poisson_v1.py` — independent and 10% shared Poisson score baselines.
- `joint_gamma_poisson.py` — fixed k=20 common-Gamma bivariate score model.
- `test_joint_gamma_poisson.py` — mathematical distribution tests.
- `evaluate_exposed.py` — regenerates Oct 5–11, 2026 scores and proper metrics from public input files.
- `prospective_protocol.json`, `test_protocol.py` — **draft**, not approved prospective gate.
- `REVIEW_QUESTIONS.md`, `REPRODUCIBILITY.md` — independent review questions and source hashes.
- [Volunteer review issue #1](https://github.com/fpf8869/shadow-v2-methodology-review/issues/1).

## Reproduce (Python 3.11+)
```bash
python -m pip install numpy pandas scipy scikit-learn
python -m unittest -v test_shadow_v2 test_joint_gamma_poisson test_protocol
python evaluate_exposed.py --schedule cfb_schedule_2026.csv --box team_box_2026.csv --passing adv_passing_2026.csv --out reproduced
```

The input files must match SHA-256 values embedded in `shadow_v2_research.py`; fetch from sportsdataverse GitHub releases. Do not use newer revised files without independently checking and recording differences.

The **October 5–11 evaluation is already exposed** and cannot select model parameters or count toward untouched validation. The model was not externally timestamp-attested for each historical game. We invite mathematical and code criticisms, including parameter choice, missing features, source-vintage leakage, calibration, and uncertainty intervals.

The prospective cohort remains 0 eligible / 100 required across four weeks pending independent review and external source/timestamp gates. An issue comment is not automatic approval.
