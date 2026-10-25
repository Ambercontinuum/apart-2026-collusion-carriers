# Runner setup, offline verification and historical live drivers

The study is complete. The D1 CLI below remains a scripted local fixture; actual
model runs used the separate bounded Modal drivers in `tools/`. Do not confuse
scripted results with live evidence or rerun a paid driver to inspect the records.
See [the evidence index](EVIDENCE_INDEX.md) and [current paper](../output/pdf/paper.pdf).
No new inference is authorized by these instructions.

## Final-task offline checks

After the pinned environment and SERAPH checkout below are ready, from the project
root run:

```powershell
.venv/Scripts/python.exe tools/test_final_attempt.py
```

This uses scripted responses only and imports no Modal worker. It does not call a
model, rewrite the frozen protocol or replace archived evidence. The published
final audit is at `evidence/experiment2/final-attempt-v1/AUDIT.json`. The source,
wire requests, records and journal chains are retained alongside it.

Historical live entrypoints include `modal_frozen_grid.py`, `modal_p_calibration.py`
and `modal_final_attempt.py`. They are archived execution code, not a current
recommendation to spend credits. The final driver refuses existing run evidence.
Independent reproduction needs separate output paths, setup review and approval;
it must not alter or overwrite the published run.

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

## Provider interface (D1 boundary; live transport supplied by external drivers)

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
The interface itself injects transport. The completed live runs supplied transport
through the bounded Modal drivers. Route-specific completed `stop` acceptance and
exactly-one-call dispatch were frozen separately; ignored parallel-call generation
settings are not represented as guarantees.

## Uncompleted original obligations

The original complete six-condition pilot and prior-only monitor were not completed
as planned. Their historical Gate 0 UNKNOWN entries remain intact. Separate approved
exploratory runs and private-bit gates do not retrospectively pass those obligations.
Experiment 1 certifies emission only; Experiment 2 additionally executed functional
check/allocation permits. The [requirements map](REQUIREMENTS_STATUS.md) is the
current interpretation. No additional paid run is scheduled or authorized.
