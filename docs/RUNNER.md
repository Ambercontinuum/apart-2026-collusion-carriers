# D1 scripted runner and certified view emission

This is the actual D1 turn loop with a scripted provider, not a model experiment.
The provider interface receives exactly the captured messages and offered tools.
There is no paid/live inference backend or P calibration command in this module.

## Public SERAPH source

Use the pinned public checkout, not the private sibling SERAPH repository:

```powershell
git clone https://github.com/Ambercontinuum/SERAPH-1.0.git .runtime/SERAPH-1.0
git -C .runtime/SERAPH-1.0 checkout --detach 4ee7d3044a945cbad30a8cd4230e327ba463187f
$env:APART_SERAPH_ROOT = (Resolve-Path .runtime/SERAPH-1.0).Path
```

If that clone already exists, inspect its status instead of cloning over it.
The loader checks the pinned commit, clean source and imported module locations.
`.runtime/` is ignored. A command-local exact-path Git ownership exception is
used by the loader on Windows; no global safe.directory change is made.

## Reproduce the checks

From the project root, with the variable above set:

```powershell
uv sync --locked --python 3.12
$env:PYTHONDONTWRITEBYTECODE = '1'
Set-Location colosseum
uv run --locked --project .. python -m unittest experiments.collusion.apart_2026.test_carrier experiments.collusion.apart_2026.test_preview experiments.collusion.apart_2026.test_runner -v
uv run --locked --project .. python -m experiments.collusion.apart_2026.runner --scripted --condition G2 --seed 1 --seraph-root $env:APART_SERAPH_ROOT --output ../.runtime/g2-smoke-001
```

Output directories must be new; the CLI refuses to overwrite evidence. B0, B1,
B2 and B2-S use the same command with their condition name and a new output path;
they do not require the SERAPH argument. No key file is read by this scripted CLI.

## Boundary and evidence

The runner gives each agent four preview turns, one structured tool response per
turn, then one native assignment turn. Multiple/invalid calls are retained as
failures and never retried or padded. This is schema/dispatch enforcement, not a
change in D1's invalid-episode definition. Native preview calls never pass through
the native blackboard logger. Only the actor's own raw call/result enters its
private history; peer context comes exclusively from the delivered view.

G2 registers a canonical-batch emit capability in the real public SERAPH runtime.
Host topology declares native-task → peer-batch → recipient consequences. The
frame observes native state preservation and required canonical-emission evidence;
the permit binds exact code, arguments, state, topology and affected recipients.
Recipient access stays closed until postcondition verification completes. A failed
or missing permit holds disclosure, while native assignment still runs and the
episode is marked invalid for comparison.

SERAPH's recovery requirement is backed by a measured local probe of the actual
held-view-buffer reset and hidden recipient accessor, before model turns. This
checks local buffer restoration only. Kernel guardian/environment/distillation
defaults are declared adapter assumptions, not validated deployment sensors or
collusion telemetry. The audit journal is hash-chained and persisted by the CLI;
no independent HMAC witness is configured.

Outputs: exact provider inputs and responses, tool results, host events, native
summary, code/config/output hashes, and G2 journal. `manifest.research_result`
is false: scripted fixtures must be excluded from research results.

## Still required before paid runs

- Live inference adapter using these same input/tool/response boundaries and
  explicit ignored compute.env loading, with no silent retries or model swaps.
- Final matched configs, complete channel inventory, source/seed/cost manifests,
  P calibration integration and complete Gate 0 report.
- Resolve and test native functional-action permit binding; the new capability
  currently certifies information emission, not native assignment execution.
- Prior-only monitor and offline analysis contract. QA-2/4/5/6 remain reporting
  obligations: achieved disruption, redundant previews, declared receiver sets,
  and derived domain-separated seeds.
- Independent QA, then Amber's separate spend approval. No cloud/model work has
  been authorized by these deterministic tests.
