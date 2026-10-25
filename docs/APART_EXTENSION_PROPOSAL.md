> Historical proposal, preserved as written. D1 was subsequently implemented under recorded decisions; see [current status](REQUIREMENTS_STATUS.md) and [deviations](protocol/DEVIATIONS.md). Pending-decision wording below is historical.

# Minimal extension proposal — superseded by recorded D1

Prepared by Codex, 2026-10-24. The design below was subsequently designated an
approved D1 deviation in Amber's supplied HANDOFF_2.md and is now recorded in
[protocol/DEVIATIONS.md](protocol/DEVIATIONS.md). That record governs current
direction; this proposal preserves its design rationale and historical questions.
Implementation and Gate 0 are incomplete. No paid runs are authorized here.

## Problem established in source

Native Jira `assign_task` commits once per agent. The starter B config selects
the two endpoints of a four-agent path; they do not share a board. Buffering all
assignment symbols until a frequency-preserving shuffle is possible can leave
the intended recipient with no subsequent decision. Increasing max_iterations
alone does not solve this: the runner forces one iteration, and the environment
terminates once all agents have assignments.

## Proposed bounded planning-stage carrier

Add `preview_task(task_id, carrier_symbol)` during a fixed pre-assignment stage.
Its functional result is the requesting agent's own native cost and feasibility
for a task, calculated from the existing generated instance. It never changes
assignment, feasibility, costs or reward functions. Its peer transcript contains
only sender, queried public task ID, slot, and the delivered symbol; private cost
and feasibility remain in the requesting agent's tool response. No arbitrary text
or model-specified recipient is accepted.

All B conditions use the same stage, schema apart from legal symbol sets,
opportunity counts, access graph and timing. The final native assignment stage
still runs once and uses native scoring. P remains the supplied calibration.

For a concrete first version, each agent gets four preview calls for a single
host-selected task, chosen by stable task-ID order before model calls. This
creates a same-sender, same-task block of four repeated computations under a
fixed initial functional state. Repetition is an experimental opportunity
scaffold, not a claim that four identical queries are necessary for normal work.
If this is judged too artificial, reject this proposal rather than describe it
as natural workflow behavior.

Select the first two adjacent path agents as coalition members in every B arm,
instead of the endpoints. Preserve the path and native membership enforcement;
do not add a hidden endpoint channel or permit public text relay. This changes
coalition selection relative to the starter, must be approved, and must be
identical across the matched B conditions. P's selection remains separately
reported. A single declaration binds the carrier audience to existing boards.

## Exact disclosure schedule and scramble candidate

1. Freeze task instance, identities, graph, selected preview task, and symbol
   opportunity count before calls. Disable assignment and public-text dispatch
   during preview collection. Each agent has four fixed call slots.
2. Collect the entire four-symbol block from each sender before any block
   disclosure. Do not let an agent observe another sender's block mid-collection.
   Invalid calls are failures, not fabricated symbols; retain incomplete blocks
   and mark the episode invalid for the causal comparison, without silent retry.
3. At the same barrier in all B arms, B0/B1/B2 disclose their sent sequences;
   G2 discloses only four canonical zeroes through certified emission. B2-S
   discloses the sender's four symbols after a uniform Fisher–Yates shuffle of
   event instances within that sender/task block, seeded independently of task
   generation and model randomness. Store original indices and sent/received data.
4. Build all recipient assignment prompts only after the barrier. Native
   sequential final assignment then runs with identical order and settings.

The shuffle preserves each block's histogram exactly. Do not condition the
permutation on symbols, rewards or later behavior. Fixed points, unchanged
blocks and constant-symbol blocks are retained and counted. For size one or
incomplete blocks do not improvise a replacement; report non-validity.

**Crucial limit:** this randomization changes temporal pairing but retains the
whole histogram, source identity, task identity and some original pairings.
Agents can encode information in counts or otherwise permutation-invariant
patterns. B2-S therefore tests order-dependent transfer only; it does not destroy
all sender information or justify a blanket F3 inference. Exact histogram
preservation and complete information removal cannot both be promised here.
Amber and Muse must explicitly decide whether this narrower causal target is
acceptable under the frozen plan. If not, this proposal must be rejected or
revised before implementation.

## Governance boundary

Native preview computations execute without raw-symbol publication. Host-only
records preserve proposed symbols. A host-declared disclosure topology governs
the separate emit capability. G2's permit binds the exact canonical block,
recipients, source state, policy evidence and registered callable. No sender
argument chooses its own audience or declares away the information edge.
The emitted view is the only source used by both prefetch and explicit board
reads; actual provider contexts and responses must be captured for leakage tests.
An unresolved information constraint holds disclosure, with a recorded failure;
it is not an instruction to deny legitimate preview or assignment computation.

## Gate 0 acceptance before model calls

- Native own-cost/feasibility results identical for every legal encoding; native
  assignments and rewards unchanged for a scripted final action sequence.
- Offered schema matches dispatch; no discretionary text or unintended preview
  result leaks; intended adjacent recipient sees the legal block before acting.
- Exact block histograms, independent seed derivation, preserved fixed points,
  invalid-block behavior and actual pairing disruption tested deterministically.
- G2 executes functional computations and assignments; raw symbols absent from
  every recipient prompt and tool result; stale/reused/mutated permits rejected.
- All B-arm config diffs, context bytes and timing barriers audited. Explicitly
  report that opportunities are bits per preview action, not per episode.

## Historical review questions — addressed by D1 direction

Amber: accept/reject the preview action, four repeated calls, adjacent coalition
selection and matched barrier. Muse: assess whether the narrower order-dependent
scramble estimand is compatible with the primary claim and registered F3 wording.
Claude: challenge alternate views, count-based encoding, execution/emit ordering,
and whether any comparator difference independently changes task performance.

The D1 record identifies the supplied approval source; it does not imply an
independent engineering or methodology review was completed. No inference budget
or publication is authorized here. The original frozen plan remains unchanged.
