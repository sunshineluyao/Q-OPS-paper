# Venue policy audit

Verified against the official workshop sites on 2026-08-18.

| Requirement | Trustworthy AI for Good | SaTQuML | Unified manuscript decision |
|---|---|---|---|
| Format | NeurIPS workshop style; exact 2026 style details partly TBA | NeurIPS 2026 style | Official repository `neurips_2026.sty` retained |
| Main-text length | 2--8 pages, excluding references and appendices | long 9, short 4, tiny 2 pages; references and appendices excluded | 8-page maximum; current numbered main text and references occupy pages 1--8, with Section 6 ending on page 7 |
| Review | Double blind | Double blind | Anonymous author block, neutral workshop title, no identifying URL/commit in the PDF |
| Supplement | Appendices excluded from main limit | Supplementary material in the same PDF | One 20-page PDF: 8-page paper/references followed by appendices and checklist |
| Prior/parallel review | Non-archival; parallel workshop submission allowed | Non-archival; under-review work allowed | Simultaneous workshop submission appears compatible; authors must still disclose/comply with any OpenReview form-specific question |

Primary sources: https://trustworthy-ai-for-good.github.io/ and https://satquml.github.io/.

Unresolved issues: both workshops may later prescribe a venue-specific `\workshoptitle{}` string, so the source currently uses the neutral `NeurIPS 2026 Workshop Submission`. SaTQuML fit remains a scope risk because its center of gravity is secure/trustworthy quantum machine learning, whereas Q-OPS evaluates QAOA-based optimization. The paper's benchmarking, strong-baseline, negative-result, and trust-boundary contributions are relevant, but acceptance under that scope cannot be guaranteed.
