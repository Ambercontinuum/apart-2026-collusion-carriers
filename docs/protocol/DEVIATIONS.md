# Protocol deviations

## D1 — preview-stage carrier, recorded 2026-10-24

Decision owner: Amber. Recorded by: Codex under Amber's instruction to reconcile
the project documentation. Source: Amber-supplied [HANDOFF_2.md](HANDOFF_2.md),
section 9b, explicitly designated an approved deviation. Exact source hash is in
[INPUT_PROVENANCE.json](../INPUT_PROVENANCE.json). The original decision time is
not established by this record; this is the recording date, not a backdated event.
The original [frozen v3.1 plan](FROZEN_v3_1.md) remains unchanged.

Status: protocol direction recorded; implementation and Gate 0 remain incomplete.
This record does not authorize model spend, publication, or claims of results.

The source's assertion that D1 already appeared in the frozen plan was inaccurate
for the file actually supplied. This separate entry resolves the documentation
placement discrepancy without editing the frozen artifact.

### Adopted changes

- Add `preview_task(task_id, carrier_symbol)` before final assignment. Return
  only the caller's native cost/feasibility; leave task state and scoring intact.
- Four preview slots per agent for one host-selected task, selected in stable
  task-ID order before model calls. This repeated-query scaffold is artificial
  and must be disclosed as such.
- Use the first two adjacent path agents as coalition members in all matched B
  arms. P remains the supplied private-text calibration with separate selection.
- Collect complete blocks before any peer disclosure. Every B arm has the same
  barrier. B0/B1/B2 emit sent sequences; G2 emits only four canonical zeroes via
  certified emission; B2-S applies a uniform Fisher–Yates event-instance shuffle
  inside each sender/task block, with independent seed derivation.
- Retain fixed points and unchanged blocks; preserve sent/received values and
  permutation indices in host evidence. Do not expose the original-index mapping
  to recipients. Invalid calls are failures; incomplete blocks are retained and
  marked invalid for causal comparison. No fabricated symbols or silent retries.
- Preserve host-declared information consequences, bound permits and registered
  execution. Unresolved information constraints hold disclosure, not legitimate
  computation. Public discretionary text is suppressed in B arms; P is the
  explicitly different text-channel calibration.

### Amended F3 and capacity

B2-S approximately equal to B2 means no detected order-dependent pathway effect.
This is a possible null for the tested effect; count-based or other
permutation-invariant information transfer remains untested, not demonstrated.
B2-S below B2 supports an order-dependent pathway interpretation only with matched
conditions and observable dependence. No blanket information-removal claim follows.

Report 0/1/2 bits of opportunity per preview action; four slots give 0/4/8 bits
per sender. With four agents, aggregate episode opportunity is 0/16/32 bits.
Neither is realized or delivered information. Episode is the replication unit:
three per arm and three seed pairs per B-arm comparison, not eighteen replicates
per effect. P is separate calibration.

### Historical checkpoint and remaining gates

The original Saturday-morning/noon targets were missed. No paid episode or fallback
was executed at those times; do not imply otherwise. Current design work follows
D1 in Colosseum. Next sequence: deterministic integration and Gate 0; independent
review and fixed run configurations; Amber's spend approval; P calibration and
the matched exploratory pilot if feasible; offline analysis and report. Reassess
feasibility against the remaining submission window without inventing a new
scientific pivot or treating the old schedule as a completed event.
