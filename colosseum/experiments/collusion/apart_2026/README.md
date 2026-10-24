# Apart 2026 deterministic adapter work

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

Passing these tests does not establish the five Gate 0 obligations. Runner
schema discovery, free-text suppression, matched scramble scheduling, certified
G2 emission, and complete agent-input capture remain to be implemented and tested.
Do not run paid episodes with this package as a completed experiment adapter.
