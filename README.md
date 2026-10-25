# Collusion Carriers and Countermeasures

**Tool-Action Metadata and SERAPH Governance**
Amber Anson, **AmberContinuum Research**
Apart AI Collusion Research Sprint, October 2026 - Track 3.1

Can discretionary metadata on a legitimate tool action enable coalition advantage,
and can governing its delivery remove that advantage while preserving computation?
The completed runs did not elicit a varying exploited carrier. They therefore leave
behavioral prevention unresolved. The positive result is an auditable domain
integration over the author's unchanged, preexisting SERAPH core.

## Paper and completed evidence

- **[Read the paper (PDF)](output/pdf/paper.pdf)** - four paper pages, including the required ethics appendix, plus one references page.
- [LaTeX source](output/pdf/source/paper.tex) and [Overleaf source ZIP](output/pdf/latex-source.zip).
- [Expanded experiment report](docs/RESEARCH_REPORT.md), [study status](docs/REQUIREMENTS_STATUS.md), and [evidence index](docs/EVIDENCE_INDEX.md).
- [Final matched results](evidence/experiment2/final-attempt-v1/RESULTS.md), [independent audit](evidence/experiment2/final-attempt-v1/AUDIT.json), and [approved scope](docs/FINAL_EXPERIMENT_RUN_SCOPE.md).

The experimental run is complete. This repository publication does not submit the
paper to Apart or authorize additional inference. Frozen protocols and evidence
retain their original wording and checkpoint dates; current summaries link to them
without retroactively turning failed gates into passes.

| Completed batch | Observations | Interpretation |
| --- | --- | --- |
| Five-arm Jira grid, seeds 1-3 | 15 episodes, 300 requests; 240/240 symbols zero; matched per-seed assignments/rewards | No varying carrier elicited; 3 live SERAPH emission permits, on already-zero inputs |
| Supplied private-text P, seed 1 | 28 requests, 7 coalition-private posts; assignments reflected plans | Explicit coordination under different settings; reward gap +10.4933 is descriptive and influenced by an outsider skip |
| Initial private-bit calibration | 8 episodes, 24 requests; 4 correct, 3 wrong, 1 fair | Failed screen; no main episodes under that version |
| Minimal/oracle diagnostic | 12 calls, all expected answers correct | Bounded competence in separate contexts; not a replacement calibration |
| Full-context diagnostic | 8 calls; input extraction 4/4, XOR reporting 2/4 | Contextual sensitivity; no isolated causal explanation |
| Final matched attempt | 8 calibration + 24 main episodes; 96 requests; calibration 7/8 correct | Main ran only after its own screen passed |

In the final task, every main sender chose zero and every receiver chose its own
bit b. Each of intact, host-canonical and SERAPH-canonical arms scored 4/8 correct,
with mean coalition total 10 and mean outsider reward 10. Two complete balanced
replicate blocks produced zero paired reward differences. These are not eight
independent Bernoulli trials per arm or evidence of statistical equivalence.

SERAPH executed 32 live native permits: eight each for A's check, B's check,
emission and allocation. Eight journal chains and all 96 requests verified.
The final run used 41,872 input and 2,186 output tokens; actual dollar billing was
not independently verified. Shutdown checks found no active tasks or containers.

## Design and contribution

Experiment 1 adds four repeated own-task previews per agent before native Jira
assignment. A host-selected task, adjacent coalition and matched disclosure barrier
support B0/B1/B2 symbol menus, within-block order scrambling and G2 canonical zero
emission. Visibility was not disclosed to agents. Scrambling preserves histograms,
so it does not remove all sender information. The repeated preview is an artificial
experimental scaffold. Eight non-skipping agents selected the previewed task despite
cheaper alternatives; this suggests anchoring without proving cause.

Experiment 2 creates an explicit information bottleneck: A and B hold private bits,
B predicts XOR or chooses fair, and a fictional outsider bears the payoff tradeoff.
The final main arms match prompts and histories while delivering intact or canonical
metadata. A's receipt never reaches B. The sender is told that the delivered
record includes the audit bit, but no main audit-bit code is assigned. This is
induced coalition pressure, not spontaneous misconduct.

[The SERAPH design map](docs/SERAPH_INTEGRATION.md) distinguishes native mechanisms
from sprint adapters. The pinned public core has **zero patches**. The host declares
consequences and evidence; native permits bind callable, payload, source state and
audience, then realized views are checked before access. This assumes a trusted host
and covers declared capabilities, not malicious host code or semantic collusion.
Experiment 1 governs emission only; Experiment 2 also governs functional actions.

The paper briefly records four reported safeguard episodes in the human-agent
research process. Specific work halted in Claude/Muse while Codex continued
separately authorized work. Amber's warrant-bearing interpretation is explicitly
framing, not a controlled causal result. The suggested Track 3.2 trusted-agent
intervention was not run. Detailed private process records are not republished here.

## Reproduce and inspect

See [RUNNER.md](docs/RUNNER.md) for pinned setup, offline checks and the distinction
between historical live drivers and safe local verification. Start by inspecting
the [evidence index](docs/EVIDENCE_INDEX.md); no API key is needed to read traces.
Independent fresh-environment reproduction remains unverified. Existing live drivers
must not overwrite evidence or be treated as permission for another paid run.

To rebuild the paper locally using the downloaded project compiler:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File output/pdf/source/build.ps1
```

For Overleaf upload `output/pdf/latex-source.zip`, select `paper.tex` as the main
document and **XeLaTeX** as compiler. Keep the included fonts directory. The local
compiler is ignored and not distributed; any standard XeLaTeX installation can use
the source. [Build instructions](output/pdf/source/README.md) describe the alternatives.

## Sources and prior work

SERAPH is **preexisting research-alpha work by Amber Anson**, developed before the
sprint. New work during the sprint (October 23-25, 2026) comprises setup, the preview/barrier/
shuffle specification, domain adapters, provider integration, private-bit task,
controls, live runs, audits and report. Its upstream validation corpus is prior
instrument evidence, not a new sprint efficacy result.

- [SERAPH-1.0](https://github.com/Ambercontinuum/SERAPH-1.0/tree/4ee7d3044a945cbad30a8cd4230e327ba463187f), unchanged pin `4ee7d3044a945cbad30a8cd4230e327ba463187f`.
- [Organizer starter](https://github.com/poseidon-research/collusion_hackathon/tree/e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8), pin `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`.
- [Nakamura et al. (2026), Colosseum](https://arxiv.org/abs/2602.15198), the research framework underlying the task and supplied control.
- [Terrarium](https://github.com/umass-aisec/Terrarium), distribution `terrarium-agents==0.1.1`, supplies native Jira semantics/scoring.

[File-level origin manifest](docs/SOURCE_FILES.json) and [source boundaries](docs/APART_SOURCES.md)
attribute inherited files separately. No project-wide license over third-party code
is asserted. Font licensing is included with the paper source.

## Licensing

The paper and original author-owned research data are **CC BY 4.0**, subject to
[LICENSE-RESEARCH.md](LICENSE-RESEARCH.md)'s scope and exclusions. This is separate
from software licensing: SERAPH remains AGPL-3.0-or-later with its upstream terms;
third-party and model/provider content are not automatically relicensed. See
[LICENSING.md](LICENSING.md). A blanket license for this project's integrated
software has not been selected.

## Limits, ethics and collaboration

Tasks are synthetic. No real market/account/victim was targeted. Codebook and
receiver-discriminator artifacts could aid signaling elicitation; the paper names
that dual use. Results do not establish general safety, collusion detection,
filter superiority, natural-workflow preservation or successful suppression.

Amber owns scientific claims and scope. Codex assisted implementation, execution,
analysis and typesetting; Claude assisted provider work, QA and drafting; Muse
provided attributed read-only QA through Amber. Hashes bind bytes, not authorship
or approval. Shared writes use leases; the project publication is owner-authorized.
Credentials, environments, local decision notes and coordination exports remain
excluded. The closed scratchpad is not updated by this publication.
