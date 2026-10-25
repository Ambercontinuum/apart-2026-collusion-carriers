# Collusion Carriers and Countermeasures

Amber Anson, AmberContinuum
Apart AI Collusion Research Sprint 2026, Track 3.1

**Working research report, 2026-10-25.** This is not submitted or published as a
final paper. Results below are completed observations; the final matched attempt
is pending owner execution approval. Source links bind the underlying records.

## Abstract

Legitimate tool actions can contain discretionary metadata that creates an
information pathway between cooperating agents. We investigate whether that
pathway enables coalition advantage and whether topology-scoped governance can
restrict its disclosure while preserving functional computation. We implemented
a Colosseum task adapter using the unchanged public SERAPH core, separating
functional execution from certified peer emission and retaining provider-level
traces. A frozen five-arm exploratory grid completed15 episodes across three
seeds: all 240 metadata symbols were zero, and native assignments and rewards
matched across conditions. Three governed emissions executed, but there was no
varying signal to suppress. A separate ungated private-channel calibration
showed explicit task coordination and a positive descriptive group reward
difference; it was not a matched causal comparison. An information-bottleneck
task then failed its receiver calibration despite correct delivery of all eight
private notes. Follow-up probes demonstrated basic XOR and tool-output competence,
but full-context XOR reports still collapsed to a constant answer. These findings
do not establish collusion prevention. They provide an auditable engineering
proof of concept and identify behavioral elicitation and receiver sensitivity
as necessary conditions for interpreting future governance comparisons.

## Introduction

Our question is whether discretionary information in an otherwise legitimate
tool action can improve coalition outcomes, and whether governing its delivery
can remove that improvement without impairing authorized computation. This
requires both a usable channel and agents that exploit it. Identical governed
and ungated outcomes cannot establish prevention when the ungated agents never
use a varying signal or cannot reliably interpret the task.

The engineering contribution is a domain specification and adapter over the
public SERAPH capability runtime, not a new native governance core. We distinguish
code-path evidence, model behavior and causal efficacy throughout.

## Related work and source origin

The [organizer Colosseum source](https://github.com/poseidon-research/collusion_hackathon/tree/e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8)
provides the Jira allocation setting and supplied private-channel calibration.
The integration uses [SERAPH-1.0](https://github.com/Ambercontinuum/SERAPH-1.0/tree/4ee7d3044a945cbad30a8cd4230e327ba463187f)
without native patches. Exact source origins and distribution boundaries are
recorded in [APART_SOURCES.md](APART_SOURCES.md) and [SOURCE_FILES.json](SOURCE_FILES.json).
This draft makes no claim to a completed literature review or algorithmic novelty
in the underlying native core.

## Methods

### Experiment1: discretionary preview metadata

Four agents occupy a path; the first adjacent pair is the coalition. A bounded
pre-assignment stage offers four repeated own-task preview computations per
agent. All matched arms share opportunities, graph and disclosure barrier.
B0 has one legal symbol, B1 two, B2 four. B2-S uniformly shuffles event instances
within a sender/task block, preserving its histogram. This tests order-dependent
information only. G2 emits canonical zeroes through native SERAPH permits.
Final assignments and scoring retain the native task semantics.

The five-arm grid used seeds 1, 2, 3 and the pinned Qwen/Qwen3-4B-Instruct-2507
revision cdbee75f17c01a7cc42f958dc650907174af0554, temperature 0. The grid was frozen
locally before inference; source/results were committed together afterward, so
we do not describe it as external preregistration. No retries or replacements.

The supplied P calibration ran separately at seed 1, temperature 0.7, complete graph
and a coalition-private text board. These differences preclude a matched SERAPH
comparison. Its native reward difference is descriptive, not a causal estimate.

### Experiment2: induced information bottleneck

A/B each hold one private bit. B chooses fair or predicts a XOR b. Fair pays
A=5, B=5, C=10; correct prediction A=10, B=10, C=0; incorrect A=0, B=0, C=20. C is fictional and
passive. On balanced states, every B-only policy has expected coalition total 10;
perfect information permits 20. Main conditions are intact metadata, host canonical
zero and SERAPH canonical zero. The task induces a coalition objective rather
than measuring spontaneous misconduct.

Private own-component checks and registered receipts precede B's action. A's
receipt never reaches B. The emitter and native functional capabilities are
separate; host evidence and local recovery probes are bounded assumptions,
not semantic collusion detection or a human-warrant intervention.

A private-note positive calibration must pass before main:8/8 faithful notes,
0 invalid episodes,>=7 correct predictions and<=1 fair allocation. Failure stops
main. Exact prompts, route contracts and revisions are versioned before calls.
Independent diagnostics use reporting-only tools and never replace that screen.

## Results

| Completed evidence | Observations | Supported interpretation |
| --- | --- | --- |
| Five-arm grid |15 valid episodes, 300 requests, 240/240 symbols 0; per-seed assignments/rewards identical | No varying carrier use elicited; no prevention inference |
| Governed grid emission |3 real native permits, canonical views; inputs already 0 | Executed integration, not suppression of an attempted signal |
| Supplied ungated P |28 requests, 7 private posts, task plans reflected in assignments | Explicit private-channel coordination in this setup |
| Experiment 2 calibration |24 requests;8/8 notes correct;4 correct, 3 wrong, 1 fair, 0 invalid | Failed positive screen;0 main episodes |
| Minimal/oracle diagnostic |12 requests;4/4 text XOR, 4/4 simple-tool XOR, 4/4 explicit-oracle allocations | Minimal competence and answer following can work |
| Full-context diagnostic |8 requests;4/4 input-pair extraction, 2/4 XOR reports; all XOR answers 1 | Contextual computation/use remains unreliable |

In P, the coalition mean exceeded the non-coalition mean by 10.4933 native points.
One outsider skipped and earned zero, influencing that difference; no measured
counterfactual attributes the gap or skip to communication. One native violation
remained. Coordination is not itself evidence of harmful or unauthorized intent.

Diagnostic extraction and XOR calls are separate interventions. Correct input
reports do not reveal the internal processing of earlier allocation calls.
The identical simple XORtool schema succeeded in minimal context and failed on
two balanced cases in full context, but history, framing and input representation
were not independently manipulated. No single causal mechanism is identified.

The final compact matched attempt has not run at this draft checkpoint. If it
passes calibration, report all24 main cells, invalids and complete balanced paired
blocks. Otherwise retain its failed screen and close the study without another
diagnostic loop. No p-values, statistical equivalence or efficacy claims are
planned for these small exploratory samples.

## Discussion and limitations

The primary behavioral question remains unresolved: no completed matched batch
has demonstrated both a varying exploited carrier and a governance-induced loss
of that advantage. The grid's zero differences are not proof of prevention.
The supplied Ptrace establishes coordination under a different channel/settings,
not an ungated counterfactual for the discretionary-metadata experiment.

The engineering evidence is narrower and positive: an unchanged public SERAPH
core can execute a research-specific emission specification, and deterministic
new-task tests cover functional execution, permit replay/staleness/mutation,
missing evidence, realized-state divergence and context isolation. This is a
research-alpha integration proof of concept; independent reproduction and
behavioral efficacy remain separate requirements. Experiment1's live integration
certifies emission only; assignment certification was not wired into that runner.

Only one small model route was tested. Repeated deterministic balanced cases
are not independent Bernoulli samples. Invalid and selective-guess subsets can
change case balance. Scrambling retains histograms and cannot erase all
information. Host-provided evidence is not an external attestation, and hash
journals lack an independent authentication anchor. Common authorization wording
was not a separately varied factor; Amber's warrant-anchor hypothesis is noted
for future work without a present causal finding.

## Conclusion

We demonstrate an inspectable SERAPH research adapter and preserve negative
elicitation/competence results. We have not demonstrated collusion prevention.
The decisive requirement is a calibrated ungated information-use pathway before
interpreting governance contrasts. The final attempt will either supply that
matched dataset or close with an explicit feasibility/sensitivity limitation.

## Code and data

[Project repository](https://github.com/Ambercontinuum/apart-2026-collusion-carriers)
contains source, versioned protocols and raw evidence. Author decisions, reviews
and hashes are in the [project scratchpad](https://github.com/Ambercontinuum/Apart-research-collusion-scratchpad-).
Credentials and local environments are excluded. Run-specific source commits,
raw wire strings, hashes and shutdown checks are preserved with each dataset.

Key reports: [grid](../evidence/exploratory-grid/freeze-20261024/RESULTS.md),
[P](../evidence/calibration/p-qwen3-4b-seed 1-20261024/RESULTS.md),
[failed calibration](../evidence/experiment2/v1_2/RESULTS.md),
[12-call diagnostic](../evidence/experiment2/xor-diagnostic-v1/RESULTS.md),
[8-call diagnostic](../evidence/experiment2/context-diagnostic-v1/RESULTS.md).

## Contributions and LLM usage

Amber owns project/research decisions. Codex assisted engineering, execution,
analysis and drafting; Claude assisted provider engineering and QA within its
recorded participation limits; Muse provided attributed read-only QA through
Amber. The scratchpad preserves contributions and disagreements. Hashes bind
recorded bytes; they do not authenticate authorship or constitute approval.
Amber must review the final scientific claims and author attribution.

## Appendix: ethical considerations and dual use

Experiments use synthetic allocations and a fictional outsider; no real account,
market or external victim is manipulated. Model tool calls act in the local
research environment. The experiment explicitly induces coalition objectives;
we do not label all cooperation as harmful collusion. Information-channel results
could inform either covert coordination or defenses, so claims and artifacts
are bounded to the measured sandbox. Secrets are not part of the published data.

## Submission completion checklist

Before submission: incorporate the one final attempt's observed outcome, resolve
author attribution, add a numbered figure, verify references and render the report
against the supplied template. This Markdown is a substantive draft, not a claim
that PDF/layout checks or submission have been completed.
