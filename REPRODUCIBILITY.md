# Reproducing the exposed Shadow V2 evaluation (research only)

This repository contains the **original experimental mean predictor** `shadow_v2_research.py`, its tests, the separate Gamma–Poisson distribution module, and the frozen draft protocol. It does **not** contain any approved production model.

## Input data (published source hashes)
Retrieve these exact CSV files from the sportsdataverse GitHub releases and verify their SHA-256 bytes before running:

| File | Release tag | SHA-256 |
|---|---|---|
| cfb_schedule_2026.csv | espn_cfb_schedules | 56707a541720854b4b362b8879231adb9eb633c0829e1065a75aa59441752d80 |
| team_box_2026.csv | espn_cfb_team_box | 4e612b2056707d0cccdb8e6db69047e286e39316d561e4d686c59e5e85261b18 |
| adv_passing_2026.csv | espn_cfb_adv_passing | b5c174db6e50481b67aee40f5c24faa93c489b75d330db004e66339646eccaf4 |

Install Python with numpy, pandas, scipy, scikit-learn and pytest/unittest support. The original model imports pandas/numpy/scipy/scikit-learn.

## Model code review
The predictor is in `shadow_v2_research.py`. Its `load()` rejects incorrect input checksums and source pairing. The fitting method uses the 2026-only data, fixed alpha=0.01 and four prior same-season games for eight derived matchup rates, with missing-feature indicators. **There is no claim that this source definition matches the original Shadow production model.**

Example command for the saved pregame research calculation:
```bash
python shadow_v2_research.py --schedule cfb_schedule_2026.csv --box team_box_2026.csv --passing adv_passing_2026.csv --output local_research_forecast.json
python -m unittest -v test_shadow_v2 test_joint_gamma_poisson test_protocol
```

## Exposed diagnostic, NOT prospective
Oct 5–11, 2026: 58 completed games; training cutoff 2026-10-05 00:00 UTC, 390 earlier training games. Score MAE 10.2009 vs league mean 11.2514; margin MAE 14.0211 vs league 18.3172. Joint log loss independent Poisson 11.481; shared Poisson 11.399; common Gamma–Poisson k=20 9.213. Home-win Brier 0.3068 / 0.3099 / 0.3053 respectively. All results already examined and unsuitable for untouched model selection. The full per-game proper-score evaluation script and predictions are not yet committed; these figures cannot currently be independently reproduced end-to-end solely from this repository.

## What we want reviewed
- Mathematical correctness, tail truncation, shared-Gamma positive-only covariance and overdispersion.
- Why a fixed k=20 and fixed 10% shared Poisson should remain unapproved assumptions.
- Source revisions and original publication timestamps; same-day final scores must never enter earlier forecasts.
- High home-win predicted rate (~71%) versus realized (~55%) in exposed cohort.
- Whether 100 eligible future games across four distinct weeks is sufficient for stable calibration conclusions.
- Prespecified primary joint log loss, paired differences, uncertainty intervals and exclusion criteria.

No external approval, no eligible validation freezes, no MGM EV, no FIRE.
