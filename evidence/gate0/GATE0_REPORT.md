# Gate 0 — initial engineering checkpoint, 2026-10-24

All five gates remain UNKNOWN for the intended end-to-end experiment. No paid
episodes are eligible. Candidate-component evidence is recorded separately below.

| Gate | Status | Evidence / remaining obligation |
| --- | --- | --- |
| G0.1 Selectable and visible carrier | UNKNOWN | Candidate B wrapper test passes through real native blackboard formatter and Jira prompt builder; runner tool discovery is not wired. |
| G0.2 Task equivalence | UNKNOWN | Candidate sweep matches native tool results, assignment updates, and rewards across every generated task plus skip and 1/2/4 encodings at seed 1. Full integrated environment/config sweep remains. |
| G0.3 Channel inventory | UNKNOWN | Initial source inventory below; suppression and frozen runner configuration absent. |
| G0.4 Scramble | UNKNOWN | No implementation or approved context/schedule declaration yet. |
| G0.5 SERAPH pre-observation | UNKNOWN | Public baseline validates; sprint disclosure policy and certified emission not implemented. |

## Deterministic evidence

Original starter invocation, from its `colosseum/` directory:
`.venv/Scripts/python.exe -m unittest
experiments.collusion.apart_2026.test_carrier -v` — four tests pass.
Focused-project invocation is documented in the project README.
The focused repository was also installed in its own environment with its own
`uv.lock`; all four tests pass there. See `focused-project-component-tests.txt`
and `focused-project-environment.json`. This dependency resolution is distinct
from the historical starter environment; no experimental data were collected
in either environment.
Tests: `colosseum/experiments/collusion/apart_2026/test_carrier.py`.
Candidate: `colosseum/experiments/collusion/apart_2026/carrier.py`.
Portable raw test output: `evidence/gate0/carrier-component-tests.txt`.
The initial PowerShell capture under local notes contains shell-added stderr
formatting; the portable log captures the Python process streams directly.

Historical baseline command in the starter workspace (not a directory bundled
in this focused repository), from `vendor/SERAPH-1.0/`:
`../../colosseum/.venv/Scripts/python.exe
-m validation.runtime_governance --output
../../notes/apart_2026/seraph-runtime-governance.json` — 17/17 baseline cases pass.
This is upstream validation, not evidence of sprint G2 enforcement.
Portable report: `evidence/gate0/seraph-baseline-validation.json`.
Source commits: `docs/APART_SOURCES.md`.

## Initial channel inventory — source observations, not suppression proof

Paths below are relative to installed `.venv/Lib/site-packages/`, unless stated.

| Channel | Current behavior and boundary |
| --- | --- |
| Native task selection / skip | `envs/dcops/jira_ticket/jira_ticket_tools.py`: native schema contains only task_id. Assignment is public and affects rewards. |
| Task tags | Generated task properties read by scoring; neither selectable neutral metadata nor valid free bits. |
| Public text | `terrarium/blackboard.py`: post_message writes arbitrary content; still available in upstream B configuration. Must remove both offered schema and dispatch access. |
| Blackboard reads | Explicit get_blackboard_events plus automatic prefetch; access depends on membership. Both must receive only permitted views. |
| Action transcript | log_action_to_blackboards copies action_params and result details before peer prompt formatting. The wrapper suppresses native raw logging and publishes B metadata here. G2 must mediate before this boundary. |
| Shared state | Jira prompts display tasks and current assignment; native tool responses include task properties, assignment updates and counts; callback adds joint reward. Preserve and inventory these channels. |
| Order and timing | Sequential calls, prompt phase/iteration, transcript ordering and tool responses remain information-bearing. No claim of zero system capacity in B0. |
| Private state | Per-agent costs, skills and availability are placed in own prompt. No blanket claim that peers receive them; tool result/task transcript exposure requires end-to-end verification. |
| Prompts and identities | Coalition wrapper adds partner/role instructions. Existing prompt/tool affordances require normalization in B arms. Actual provider inputs not yet captured. |
| Host logs | LocalCommunicationProtocol.tool_events retains arguments/results; currently exported as research evidence. No assertion yet that every provider context excludes every secondary echo. |
| Private coalition text | P calibration enables it. B-arm pilot will not. Frozen plan's blanket text-suppression wording conflicts with explicit P definition; preserve the conflict for Amber's resolution. |

`experiments/common/local_protocol.py` constructs peer prefetch from native board
events, dispatches tools and applies state updates. `terrarium/agents/base.py`
discovers environment and blackboard schemas separately and appends tool results
to model context. A protocol wrapper alone is insufficient to change offered
schemas; the agent discovery and execution boundaries must agree.

## Open design obligation

Within-context frequency-preserving instance shuffling requires multiple
eligible events before release. Jira currently allows one assignment per agent
and the supplied coalition endpoints do not share a board. Context grouping,
buffering, eligible recipients, and whether a symbol can precede a receiver's
consequential action must be demonstrated before freezing the adapter. Do not
substitute a global label permutation or silently alter the communication graph.
