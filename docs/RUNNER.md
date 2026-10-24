# D1 scripted runner and certified view emission

This is the actual D1 turn loop with a scripted provider, not a model experiment.
The provider interface receives exactly the captured messages and offered tools.
`provider.py` defines the live-provider boundary, tested with mocked transport
only. There is no network transport, paid inference backend or P calibration
command in this module, and the CLI remains scripted-only.

## Public SERAPH source

Use the pinned public checkout, not the private sibling SERAPH repository. The
canonical location is `.runtime/SERAPH-1.0` in this project; the tests use it by
default. From the project root:

```powershell
git clone https://github.com/Ambercontinuum/SERAPH-1.0.git .runtime/SERAPH-1.0
git -C .runtime/SERAPH-1.0 checkout --detach 4ee7d3044a945cbad30a8cd4230e327ba463187f
```

To use a checkout elsewhere, set `$env:APART_SERAPH_ROOT` to its path; it
overrides the default for the tests. The G2 CLI always takes `--seraph-root`.
If no checkout is found, G2 tests fail with a message naming this section.
If that clone already exists, inspect its status instead of cloning over it.
The loader checks the pinned commit, clean source and imported module locations.
`.runtime/` is ignored. A command-local exact-path Git ownership exception is
used by the loader on Windows; no global safe.directory change is made.

## Reproduce the checks

From the project root, with the checkout above in place:

```powershell
uv sync --locked --python 3.12
$env:PYTHONDONTWRITEBYTECODE = '1'
Set-Location colosseum
uv run --locked --project .. python -m unittest experiments.collusion.apart_2026.test_carrier experiments.collusion.apart_2026.test_preview experiments.collusion.apart_2026.test_runner experiments.collusion.apart_2026.test_provider -v
uv run --locked --project .. python -m experiments.collusion.apart_2026.runner --scripted --condition G2 --seed 1 --seraph-root ../.runtime/SERAPH-1.0 --output ../.runtime/g2-smoke-001
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

Outputs: exact provider inputs and responses, provider exchanges, tool results,
host events, native summary, code/config/output hashes, and G2 journal.
`manifest.research_result` is false: scripted fixtures must be excluded from
research results.

## Live-provider boundary (mocked transport only)

`LiveProvider(config, transport)` serializes the runner's exact messages and
tools once, with the frozen `ProviderConfig` (model, temperature, max tokens,
tool choice, optional seed, `n=1`), and passes that text to an injected
`transport(request_text) -> response_text`. The exact request text and raw
response text are kept with their SHA-256 in `provider_exchanges`; the
manifest records the config and its hash, and counts every transport attempt
as an inference call.

The response is parsed once, strictly: duplicate JSON keys and non-finite
numbers are rejected, tool arguments must arrive as a JSON string encoding an
object, and they are not parsed a second time. A different `model` in the
response, any choice count other than one, a missing tool call or a malformed
payload yields no calls, which the runner records as an invalid turn. A
transport exception is logged by error type only (no message text, which may
carry endpoints or credentials) and re-raised; the runner records the failure.
Nothing is retried, padded or substituted. Multiple well-formed calls are
returned as-is so the runner's one-call rule rejects them.

Limits: actor histories store the parsed arguments re-serialized, and drop any
assistant text content; the exact model output is only in `provider_exchanges`.
No real transport, credential loading or provider-specific options (for example,
disabling router fallbacks) exist yet.

## Still required before paid runs

- A real transport for the chosen provider, explicit ignored compute.env
  loading and frozen model/decoding config, behind the existing
  `LiveProvider` boundary; no silent retries or model swaps.
- Final matched configs, complete channel inventory, source/seed/cost manifests,
  P calibration integration and complete Gate 0 report.
- Resolve and test native functional-action permit binding; the new capability
  currently certifies information emission, not native assignment execution.
- Prior-only monitor and offline analysis contract. QA-2/4/5/6 remain reporting
  obligations: achieved disruption, redundant previews, declared receiver sets,
  and derived domain-separated seeds.
- Independent QA, then Amber's separate spend approval. No cloud/model work has
  been authorized by these deterministic tests.
