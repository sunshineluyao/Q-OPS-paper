# Numerical consistency audit

Status: PASS. Machine report: `release_consistency.json`.

- 32 canonical rows; 9 gate-positive; 30 strict cores; 27 composite-feasible incumbents; 0 disallowed-mode violations.
- Mean uniform optimum mass: 0.022278120276439495.
- Mean p=2 optimum mass: 0.1521904451831595.
- Ratio of means: 6.8313862792145175 across all 32 retained-core comparisons.
- Fresh locked rerun: 32 rows, 704/704 exact shared-field values, maximum absolute error 0; six targeted evidence tests passed.
- Archive-side diagnostic: 896/960 values match directly; the remaining 64 diversity values match after converting current raw distinct-state counts to the archived normalized fractions. This semantic drift is excluded from headline reproduction claims.
- The abstract, Introduction, Results, Table 2, appendices, and README were checked for the corrected estimand and distinct feasibility concepts.
- Exactly three RQ--contribution pairs and six numbered main-section inputs are enforced by `scripts/audit_release.py`.
