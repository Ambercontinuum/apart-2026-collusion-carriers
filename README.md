# Apart 2026 — Collusion carriers and countermeasures

Amber Anson (AmberContinuum), Track 3.1.

We experimentally test whether discretionary information carried by legitimate
tool actions enables coalition advantage, and whether topology-scoped governance
can disrupt that information flow without degrading authorized task execution.

This repository contains our experiment-specific source, selected upstream source
files, tests, evidence and submission materials. It has its own Git history.
Original source repositories remain linked and pinned; unrelated starter projects
and their history are not included.

## Status

**Development checkpoint, not a finished experiment.** The candidate carrier has
four passing deterministic tests; public SERAPH's existing bounded corpus passes
17/17 cases. Gate 0 remains incomplete. No paid experimental episodes, completed
G2 integration, or collusion results are claimed. The preview-stage design is
recorded as D1 in the supplied amended handoff; the dated
[deviation record](docs/protocol/DEVIATIONS.md) identifies its source and remaining
implementation. No completed independent engineering review is implied.

## Reproduce the component tests

```powershell
uv sync --locked --python 3.12
Set-Location colosseum
uv run --locked --project .. python -m unittest experiments.collusion.apart_2026.test_carrier -v
```

These tests require no inference key or model calls. Full experimental runner
instructions will be added when that runner exists and is verified.

## Sources and evidence

- [Organizer starter](https://github.com/poseidon-research/collusion_hackathon),
  commit `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`.
- [SERAPH-1.0](https://github.com/Ambercontinuum/SERAPH-1.0),
  commit `4ee7d3044a945cbad30a8cd4230e327ba463187f`.
- [File-level source links and hashes](docs/SOURCE_FILES.json).
- [Prior work and source boundaries](docs/APART_SOURCES.md).
- [Gate 0 report](evidence/gate0/GATE0_REPORT.md).
- [Extension proposal](docs/APART_EXTENSION_PROPOSAL.md).
- [Supplied plan and handoffs](docs/protocol/README.md).
- [Submission template](docs/apart-research-submission-template.pdf) and
  [guidance](docs/SUBMISSION_TEMPLATE.md).

SERAPH, the execution-governance layer selected as measurement infrastructure
and enforcement boundary, is preexisting work by the author, publicly available
as a research alpha and developed before this sprint. New sprint work began
October 24, 2026 and currently comprises the carrier component, its tests,
source inspection and the documented D1 design. The peer-information topology
integration, preview-stage runner, precommit monitor, experimental episodes,
analysis and findings remain incomplete. SERAPH is not presented as a validated
collusion detector. Existing validation is not a sprint enforcement result.
The tests and selected
utility use Terrarium 0.1.1; its package supplies the native Jira implementation.

## Collaboration

Amber owns scientific decisions; Codex implements; Claude independently reviews
engineering; Muse reviews methodology and framing. Roles do not imply completed
review. Input receipts preserve contributor identity separately from recorder
identity; hashes do not authenticate authorship or approval. Relevant input
hashes are in [the provenance record](docs/INPUT_PROVENANCE.json).

Private coordination stays in local Markdown and is excluded from this repository.
No Optimus scratchpad content, credentials, environments, or unrelated benchmark
code is included. Completed experiment artifacts will be added as they exist,
with immutable configurations, raw evidence, and scoped findings.
