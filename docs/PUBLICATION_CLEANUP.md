# Forward-only publication cleanup - October 25, 2026

Based on Claude's `public-repo-cleanup-for-codex.md`, supplied by Amber.
Review SHA-256: `51013a29b908dc3c57881be36d5c3f1d3232da767a0ace1121f953e18e83f7e3`.
Attribution records the supplied review, not a cryptographic authorship assertion.

- Redacted local output/temp paths in P configuration and log records; removed a
  pre-inference startup traceback. [Redaction note](../evidence/calibration/p-qwen3-4b-seed1-20261024/REDACTION_NOTE.json)
  retains old/new hashes; the updated flat manifest verifies all current files.
  Model requests/responses, native-results archive, scores and analysis are unchanged.
- Removed references to unrelated private work from current public overviews.
- Left the frozen plan and all provenance-linked handoffs in place. The frozen
  plan is byte-identical, including its historical organizer-email reference.
- Removed editor settings and ignored local editor configuration.
- Moved submission working documents to `docs/archive/`; rebased their links.
- Removed the redistributed organizer template PDF; its reference/hash record
  remains, linking to the sprint guidelines instead.
- Updated the expanded report to state that research tooling is public, without
  asserting an unmeasured low real-world uplift.

Checks: current tracked content has no matches for the reviewed local-path/private-
project patterns; all 18 P-manifest entries and pre-redaction hashes verify;
checked document links resolve; frozen-plan bytes unchanged. The paper PDF is
unchanged by this cleanup; the source ZIP is refreshed for build instructions.

Git history is **not rewritten**. Historical commit URLs in the paper remain valid,
and historical snapshots still contain their original content. This cleanup is
not a claim of complete erasure from Git history, caches or existing clones.
No private process records or scratchpad updates are published.
