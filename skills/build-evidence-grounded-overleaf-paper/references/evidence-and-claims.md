# Evidence and claim control

## Evidence hierarchy

Use the highest available level and disclose gaps:

| Rank | Evidence | Typical use |
| --- | --- | --- |
| 1 | Direct rerun from pinned code/config/data | Headline empirical values |
| 2 | Frozen machine-readable output with checksum | Audit and figure regeneration |
| 3 | Tests, logs, environment records | Implementation and reproducibility claims |
| 4 | Official venue/source/publisher/standards page | Rules and external factual claims |
| 5 | Repository report or README | Orientation; verify against levels 1–3 |
| 6 | Prior manuscript or conversation summary | Leads only; never final authority |

## Claim ledger

Create one row per material claim:

| Field | Required content |
| --- | --- |
| `claim_id` | Stable identifier used in notes/report |
| `paper_location` | Abstract, section, table, figure, or appendix |
| `claim_text` | Proposed wording |
| `status` | Verified fact, observed result, method design, interpretation, limitation, or future work |
| `evidence_source` | File, table/row, script, test, official page, or paper |
| `version` | Commit, checksum, date, or document version |
| `verification` | Rerun, exact comparison, tolerance, manual inspection, or citation check |
| `supported_wording` | Strongest defensible statement |
| `forbidden_wording` | Likely overclaim |
| `caveat` | Scope, population, budget, measurement, or external-validity limit |

## Result wording rules

- Report numerator and denominator with rounded rate: `30/32 (93.8%)`.
- Distinguish descriptive values from inferential estimates and pre-specified from exploratory analyses.
- For paired designs, use paired differences and a paired uncertainty method.
- State how failures, misses, fallbacks, missing values, and timeouts are coded.
- Treat a confidence interval crossing the null as inconclusive for the directional claim.
- Report adverse depth, subgroup, robustness, or baseline comparisons when they constrain the headline result.
- Distinguish probability/sample efficiency from wall-clock, cost, energy, or asymptotic scaling.
- Distinguish narrow hard-constraint legality from composite feasibility or deployment safety.
- Distinguish a post-result eligibility partition from a prospective invocation or abstention policy.

## Novelty wording rules

Build novelty from a component-by-component map:

1. Identify established component A and its primary citations.
2. Identify established component B and its primary citations.
3. Identify the documented gap at their intersection.
4. State the paper's integration and evidence contribution.
5. Bound the search by databases, keywords, and date when making a priority claim.

Prefer:

> To our knowledge, prior work has studied A, B, and C separately, but we are not aware of a reproducible evaluation that combines them under D and audits E.

Avoid “first,” “seminal,” “breakthrough,” “state of the art,” “advantage,” or “safe” unless the evidence and literature search establish the exact meaning.

## Traceability in artifacts

- Generate result charts from frozen machine-readable data.
- Record the generating script and input checksum.
- Put detailed formula-to-code and claim-to-evidence tables in appendices.
- Keep a narrow paper-critical test record separate from whole-repository health.
- State exact shared-field reproduction when schemas differ; never call it byte-identical reproduction.
