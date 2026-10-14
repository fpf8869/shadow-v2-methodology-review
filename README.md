# NCAAF Shadow V2 — volunteer methodological review

**Status: RESEARCH ONLY. Not independently approved, not predictively certified, no betting authority.**

This public repository requests unpaid independent review of a college-football joint-score distribution and draft prospective protocol. It is **not** the original Shadow production engine.

## Available for code review

- `joint_gamma_poisson.py`: exact tested research implementation of common-Gamma mixture with k=20 fixed provisionally.
- `test_joint_gamma_poisson.py`: tests for nonnegative support, mass, tail bound, event probabilities and symmetry.
- `prospective_protocol.json`: compact public protocol outline (draft, not signed off).
- `REVIEW_QUESTIONS.md`: six concrete statistical review questions.
- [Public review issue #1](https://github.com/fpf8869/shadow-v2-methodology-review/issues/1).

The full mean predictor, all its historical data and end-to-end score evaluation are **not yet published here**. Therefore reviewers can currently reproduce and critique the distribution component, but **cannot independently reproduce the claimed 58-game end-to-end metrics** from this repository. This limitation must not be interpreted as completed independent review.

### Research assumptions and observed diagnostics

- Common Gamma intensity: G~Gamma(k, rate=k); H|G~Poisson(mu_h G), A|G~Poisson(mu_a G).
- Mean scores are fixed externally; k=20 is not calibrated.
- Model cannot represent negative home/away covariance.
- Exposed October 5–11, 2026 58-game cohort: joint log loss approximately 9.213 for Gamma–Poisson, 11.481 independent Poisson, 11.399 shared Poisson. **These are not untouched validation.**
- Predicted home-win rate around 71% vs observed 55% in that cohort suggests calibration concern.

No production release, MGM EV, FIRE, or backdated forecast freeze is authorized. Volunteer comments are not automatically formal approval.
