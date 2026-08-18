# Double-blind anonymity audit

Status: **PASS** for `main.pdf` and the curated anonymous supplement.

- Visible author information is the official template's anonymous placeholder; PDF Author and Title metadata are empty.
- No personal repository owner, challenge name, institution, identifying URL, acknowledgement, full implementation commit, or repository history appears in the submitted source corpus, PDF text, or package.
- The full configuration SHA-256 remains because it identifies a frozen protocol, not an author. The implementation revision is retained only in the external Draft-PR record.
- The workshop title is neutral so the same paper can be submitted to either venue without naming the other venue.
- The deterministic ZIP uses an explicit source tree, excludes Git data, caches, temporary files, the identifying reproduction audit, and package self-checksum, and rejects external-file leakage through the repository regression suite.

Camera-ready action: add permanent repository/artifact coordinates and acknowledgements only after double-blind review.
