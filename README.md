# Collusion Carriers and Countermeasures

**Apart AI Collusion Research Sprint 2026 · Track 3.1**

Amber Anson · AmberContinuum

> We experimentally test whether discretionary information carried by legitimate
> tool actions enables coalition advantage, and whether topology-scoped governance
> can disrupt that information flow without degrading authorized task execution.

This exploratory study uses Colosseum's Jira-style task-allocation environment.
We vary one discretionary metadata field on a legitimate tool action, then compare
intact, scrambled and governed delivery to peers. The intended contribution is
pathway-specific evidence and an auditable governance integration.

## Current implementation

**No model-driven experimental episodes have run. There are no collusion findings
or completed G2 enforcement results.** This is a deterministic component checkpoint.

| Component | Current state |
| --- | --- |
| Historical carrier candidate | Metadata wrapper on native `assign_task`; four tests pass. Retained as feasibility evidence, not the selected D1 experiment. |
| D1 preview action | Component schema and dispatch for `preview_task(task_id, carrier_symbol)`; native own-cost/feasibility without changing task state. |
| Barrier and peer views | Four-slot blocks collected before release; peer fields limited to sender, public task ID, delivered slot and symbol; path-neighbor audiences. |
| Scramble | Seeded Fisher–Yates event-instance shuffle per sender/task block; counts preserved, fixed points retained, index mapping host-only. |
| Tests | **15 component tests pass:** four historical-candidate tests and eleven D1 tests. Checks cover all agents/encodings at seeds 1–3 and all 256 four-symbol blocks for histogram preservation. |
| SERAPH baseline | Public upstream corpus passes 17/17 cases; prior-instrument validation, not sprint G2 evidence. |
| G2 | Functional previews work; release is held because certified canonical emission is not integrated. |
| Runner and analysis | Actual model-runner integration, full provider-input capture, exploratory monitor and offline analysis remain to be built. |

All five full [Gate 0 obligations](evidence/gate0/GATE0_REPORT.md) remain
**UNKNOWN**. Passing component tests does not make the experiment ready to run.
The [requirements map](docs/REQUIREMENTS_STATUS.md) separates implemented work
from remaining proof obligations.

## Current design: D1 preview stage

[Deviation D1](docs/protocol/DEVIATIONS.md) records the selected design, preserving
the original frozen plan. Native `assign_task` had no verified selectable neutral
field; its one-assignment workflow also did not support the required buffered control.

1. Generate a native Jira instance with four agents on a path. Before model calls,
   select the first task in stable task-ID order. In each B arm, the first two
   adjacent agents form the assigned coalition; P retains its supplied setup.
2. Give every agent four `preview_task` slots for that task. The legitimate result
   is only the caller's own native cost and feasibility. It does not reserve or
   assign tasks, alter costs, advance native task RNG, or change scoring. The
   caller also selects a permitted research `carrier_symbol`.
3. Collect complete blocks before peer disclosure. All B arms use the same barrier
   and opportunity count. Invalid calls and incomplete blocks remain failed/invalid
   comparisons; they are not padded or silently retried into successful episodes.
4. Release condition-specific views to existing path neighbors. Build recipient
   assignment prompts only after the barrier.
5. Run native final assignment once with its original task and reward semantics.

```text
preview_task(task_id, carrier_symbol)
    +-- functional result --> caller's native cost / feasibility
    +-- host-held symbol block --> disclosure barrier --> peer view
                                                            |
                                                            v
                                               native final assignment
```

The preview, shuffle and view accessor exist as components; actual model turns,
provider inputs and final-assignment scheduling are not yet connected to them.
Four repeated previews are an **experimental scaffold**, not a claim about natural
workflow behavior. Other channels, including task selection, shared assignment
state and action ordering, remain to be inventoried and controlled as declared.

## Planned experiment arms

The core pilot is **six conditions × three seed identifiers = 18 episodes**.
It has not run. P is standalone calibration; each B-arm contrast has three matched
seed pairs. Actions and slots within an episode are not independent replicates.

| Arm | Sender menu | Intended peer delivery | Purpose |
| --- | --- | --- | --- |
| **P** | Supplied private-text setup | Private coalition text | Pipeline/coalition calibration only; no D1 preview manipulation |
| **B0** | `{0}` | Sent sequence | Zero-bit field baseline, not a no-communication system |
| **B1** | `{0,1}` | Sent sequence | One-bit opportunity per preview |
| **B2** | `{0,1,2,3}` | Sent sequence | Two-bit opportunity per preview |
| **B2-S** | `{0,1,2,3}` | Within-sender/task instance shuffle at the matched barrier | Order-dependent causal control preserving block counts |
| **G2** | `{0,1,2,3}` | Four canonical zeroes authorized before observation | Enforceability and legitimate-work preservation |

P's supplied runner is not bundled here. B-arm delivery exists only at component
level; G2's intended delivery is unimplemented. Public discretionary text must be
suppressed in B arms through both offered schemas and dispatch. P is the explicit
private-text calibration exception. Full matched run configurations and model
settings are not frozen yet.

The intended matched B arms hold the model/provider, decoding settings, task
instances, agent identities/order, seed list, opportunity counts and disclosure
timing fixed. Prompt differences are limited to the controlled tool/policy
descriptions; unavoidable differences must be recorded rather than silently repaired.

Optional **C-only** (canonicalization without SERAPH) and **S2** (sham gate without
canonicalization) are later comparators, not additions to the core pilot.

| Opportunity bound | B0 | B1 | B2 / B2-S / G2 sender menu |
| --- | --- | --- | --- |
| Per preview | 0 bits | 1 bit | 2 bits |
| Four slots per sender | 0 bits | 4 bits | 8 bits |
| Aggregate across four agents | 0 bits | 16 bits | 32 bits |

These are encoding opportunities, not demonstrated delivered or used information.
G2 is intended to remove peer-visible discretion despite its four-choice sender
menu. B2-S retains count-based/permutation-invariant information: it does not
remove all sender information. Equal B2-S and B2 outcomes mean no detected
order-dependent effect, while other mechanisms remain untested.

## Governance and evaluation

The intended G2 integration separates functional computation from information
emission. The host declares disclosure consequences. SERAPH must evaluate real
scoped constraints and bind the exact canonical block, recipients, callable,
arguments and state before release. Unresolved information evidence holds
emission rather than denying legitimate computation. Actual prompts and tool
results must demonstrate that secondary echoes cannot reveal raw symbols.

Planned telemetry has four separate layers: carrier events; a prior-observations-only
exploratory monitor; SERAPH policy/permit evidence; and offline evaluation. The
monitor observes and does not authorize or deny. Future rewards cannot become
evidence for an earlier decision.

Evaluation will report received-symbol-to-subsequent-action dependence, native
coalition advantage and individual rewards, legitimate task performance, and
migration to inventoried alternative channels. Planned contrasts are B2−B0,
B2−B2-S and B2−G2, with B0→B1→B2 descriptive. The small pilot does not support
significance, filter-superiority, general safety, detector-validation or
phase-transition claims. Null and negative findings remain results.

## Run the existing tests

From this repository root in PowerShell:

```powershell
uv sync --locked --python 3.12
Set-Location colosseum
uv run --locked --project .. python -m unittest experiments.collusion.apart_2026.test_carrier experiments.collusion.apart_2026.test_preview -v
```

No inference key or model calls are required. [Captured test output](evidence/gate0/preview-component-tests.txt)
records this checkpoint. There is no completed six-arm runner command yet.
Paid episodes require all five Gate 0 proofs and Amber's separate spend approval.

## Sources and prior-work disclosure

This project has its own Git history and contains selected attributed source,
not the full starter history or unrelated benchmark projects.

- [Organizer starter](https://github.com/poseidon-research/collusion_hackathon),
  commit `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`.
- [SERAPH-1.0](https://github.com/Ambercontinuum/SERAPH-1.0),
  commit `4ee7d3044a945cbad30a8cd4230e327ba463187f`.
- [Terrarium](https://github.com/umass-aisec/Terrarium), distribution
  `terrarium-agents==0.1.1`, supplying native Jira implementation and scoring.

[File-level origins and hashes](docs/SOURCE_FILES.json) distinguish copied files,
new sprint code and runtime dependencies. [Source boundaries](docs/APART_SOURCES.md)
provide further attribution.

SERAPH is preexisting research-alpha work by the author, developed before this
sprint and selected as measurement infrastructure and an enforcement boundary.
New work began October 24, 2026 and currently comprises the historical candidate,
D1 preview/barrier/shuffle components, their tests, inspection and design records.
Peer-information topology integration, certified G2 emission, model-driven runs,
the monitor, analysis and findings remain incomplete. SERAPH is not presented
as a validated collusion detector. Upstream validation is separate from sprint claims.

## Submission and collaboration

The intended submission is a 4–8-page report, 150–250-word abstract, required
Limitations and Dual-Use/Ethical Considerations appendix, and LLM usage statement.
See the [official template](docs/apart-research-submission-template.pdf),
[template guidance](docs/SUBMISSION_TEMPLATE.md), and
[source plan and handoffs](docs/protocol/README.md).

Amber owns scientific decisions, scope, budget, claims and submission. Codex
implements; Claude independently reviews engineering; Muse reviews methodology
and framing. Roles do not imply completed review. [Input provenance](docs/INPUT_PROVENANCE.json)
separates contributor and recorder identity; hashes are not signatures or approval.
Shared writes use leases. Commit and push actions require approval.

Decision and architecture notes stay in the local Markdown scratchpad. Private
coordination, credentials, environments and Optimus scratchpad content are not
automatically included in this repository.
