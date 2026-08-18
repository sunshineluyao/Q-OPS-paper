# Claim--evidence audit

Status: PASS after correction of the frozen estimand.

| Claim | Evidence | Allowed wording | Prohibited extrapolation |
|---|---|---|---|
| 32 held-out cases | Frozen C1.2 CSV and locked rerun | all cases retained, including nulls | population estimate for workplaces |
| 9/32 (28.13%) | Recorded gate column | post-simulation evidence-gate rate | prospective adoption/routing rate or saved quantum calls |
| 6.831386x | ratio of mean p=2 optimum mass 0.1521904452 to mean uniform mass 0.0222781203 across all 32 retained-core comparisons | matched-budget optimum-mass ratio across all 32 | adopted-only mean; per-instance ratio; runtime/optimization advantage |
| 704/704, max error 0 | 22 shared fields x 32 rows in fresh locked rerun | exact shared-field reproduction | byte-identical CSV reproduction |
| 0/32 violations | `alns_hard_violations` | zero disallowed-mode violations | total feasibility, safety, fairness, or welfare |
| 27/32 feasible | archived composite predicate | composite-feasible classical incumbents | every output feasible |
| 30/32 strict cores | retained-core enumeration | strict feasible core exists | full-problem optimality |
| p=1 > p=2 on 28/32 | frozen descriptive comparison | adverse-depth evidence under unequal searches | causal depth conclusion |

The quantum branch audits a noiseless retained-state distribution and never replaces the classical incumbent. The supported evidence-ladder position is L2 conditional algorithmic evidence. QPU, noise, wall-clock, energy, scaling, production, application-level, safety, fairness, and welfare advantage claims are expressly excluded.

The full implementation commit is intentionally absent from the anonymous PDF and supplement. The external audit maps the frozen study to commit `ae6a85f52fb5808e631bc0c4cfa43220c10ce9aa`; the locked configuration digest is `7f07459abc9e686934be1ee022768eb82a9687137cc86d4d7ea0b7727715e53c`.
