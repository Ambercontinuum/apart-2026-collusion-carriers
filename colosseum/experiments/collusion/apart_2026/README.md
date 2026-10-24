# Apart 2026 deterministic adapter work

## Latest: scripted runner and canonical G2 emission

The prior component-only notes below are historical. `runner.py` now connects
schema/dispatch, private histories, the barrier and native final assignment.
`seraph_bridge.py` uses the pinned public topology/frame and capability runtime
to certify canonical views before the recipient accessor opens. Twenty-four
tests pass in total. See [runner instructions](../../../../docs/RUNNER.md) for
the public source prerequisite, complete test command and zero-spend CLI.

This remains a scripted integration fixture, not a live-model experiment or a
full Gate 0 PASS. Live inference, native functional-action permit binding,
final configs and inventory, monitor and analysis remain incomplete.

This package is not yet wired into the collusion runner. `CarrierTools` adds a
required integer `carrier_symbol` to native `assign_task` for candidate B arms.
It strips that metadata before native execution and publishes it separately in
the native action transcript. No G2 or scrambled delivery is implemented here.

From `colosseum/`, run:

```powershell
.venv/Scripts/python.exe -m unittest experiments.collusion.apart_2026.test_carrier -v
```

The four deterministic tests inspect the native schema, exercise all seven
encoding opportunities (one/two/four), compare native results and rewards for
every generated task plus skip, render peer-visible metadata through the native
blackboard formatter and Jira prompt builder, and reject illegal symbols.
These tests use a generated seed-1 environment and no model calls.

## D1 preview components

`PreviewStage` offers the bounded preview schema and dispatch, uses the caller's
native cost/feasibility, accumulates four-slot sender/task blocks, and publishes
path-neighbor views only at the common barrier. `shuffle_block` uses the declared
Fisher–Yates algorithm with a domain-separated seed and host-only index mapping.
Invalid or incomplete blocks cannot be repaired by padding or silent retries.

Run both component suites from `colosseum/`:

```powershell
uv run --locked --project .. python -m unittest experiments.collusion.apart_2026.test_carrier experiments.collusion.apart_2026.test_preview -v
```

The D1 tests compare native state and final native scoring across seeds 1–3,
check the no-early-view barrier and audience fields, exhaust all 256 four-symbol
blocks for histogram preservation, and retain constant/unchanged permutations.
G2 previews can compute, but `release()` holds with NotImplementedError until
the certified emitter is integrated. This is not evidence that G2 works.
Neither preview schema discovery nor view construction is wired into the actual
model runner yet. Full Gate 0 remains incomplete.

Passing these tests does not establish the five Gate 0 obligations. Runner
schema discovery, free-text suppression, matched scramble scheduling, certified
G2 emission, and complete agent-input capture remain to be implemented and tested.
Do not run paid episodes with this package as a completed experiment adapter.
