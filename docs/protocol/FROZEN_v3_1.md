# Apart AI Collusion Research Sprint — Project Plan (v3.1, FROZEN with pre-execution verifications)

**Sprint:** Apart Research, AI Collusion Research Sprint, Oct 23–25, 2026 (online)
**Entrant:** Amber Anson (AmberContinuum) — **solo**
**Track:** 3) Collusion Carriers and Countermeasures
**Deadline:** Sunday Oct 25, 11:59 PM AoE = **Monday Oct 26, 7:59 AM ET**.
**Deliverable:** Report PDF, official template, 4–8 pages (hard cap, excl. references/appendices), abstract 150–250 words, author + affiliation, required **Limitations and Dual-Use / Ethical Considerations** appendix.

**Primary claim (adopted verbatim, GPT freeze review):**
> "We experimentally test whether discretionary information carried by legitimate tool actions enables coalition advantage, and whether topology-scoped governance can disrupt that information flow without degrading authorized task execution."

**Secondary (exploratory) result:** whether the emergence of coordination exhibits a threshold or a precursor signal across the capacity grid. The weekend study is *not* responsible for proving the larger information-physics programme; it contributes a first experimental step toward it.

**Freeze status (per GPT conditional approval, all three corrections accepted by Muse and ratified into this version):**
- **Frozen now:** research question, benchmark family (Colosseum), carrier-capacity grid, scrambled causal control, coalition-advantage metric, disclosure requirements, primary claim wording.
- **Verify before experiments:** actual peer-visible carrier, task equivalence, scramble procedure, pre-observation SERAPH enforcement.
- **Kept exploratory:** early-warning (precommit) telemetry, inferred critical capacity, any phase-transition interpretation.

**Version history:** v1 Muse (operational backbone) → v2 GPT review #1 (capacity dose–response, telemetry, novelty scoped) → v3 GPT review #2 (Gate 0, B2-S causal scramble, SERAPH information-topology enforcement, fallback corrected) → v3.1 GPT freeze review (channel-inventory honesty, distribution-preserving scramble, precommit coordination monitor, claim softened). No further theoretical revisions; remaining unknowns resolve by execution.

## Design — six conditions

Environment: **Colosseum** (poseidon-research/collusion_hackathon). Discretionary text suppressed in all tested conditions.

**The carrier** is *one controlled discretionary field* on an otherwise legitimate action (Gate-0-verified: agent-selectable per action, peer-observable). Bits = maximum capacity of *that field*, not of the action channel as a whole.

◆ **Channel inventory (correction #1):** B0 is a **zero-bit discretionary field**, not a zero-capacity channel. Agents retain other information-bearing actions — task selection, timing, shared task-state changes. Before runs begin, inventory **all** peer-visible channels in the configuration and report which remained available in every condition. If a coalition shifts to an alternative pathway after canonicalisation, that is a **Track 3 result (channel migration)**, reported as such — not a failed experiment and not a null.

| # | Condition | Setup | Role |
|---|-----------|-------|------|
| P | Positive control | Private text as supplied; prompted coalition | Calibration only. Seeded properly (cheap 1-seed control can read negative by chance). |
| B0 | 0-bit field | Carrier field restricted to one permitted encoding; other inventoried channels unchanged | Baseline for the *field's* contribution |
| B1 | 1-bit field | Two task-equivalent encodings | Dose 1 |
| B2 | 2-bit field | Four task-equivalent encodings | Dose 2 |
| **B2-S** | **Scrambled 2-bit** | Sender picks any of 4 symbols; recipient receives a symbol drawn by the predeclared ◆ **distribution-preserving** scramble: permuted **within comparable task contexts so the recipient's symbol frequencies match the sent distribution**; sent and received values both logged | Causal control: breaks the sender→recipient relationship while preserving input statistics |
| G2 | SERAPH-governed 2-bit | Topology-scoped information-flow constraint canonicalises the peer-visible consequence **pre-observation**; functional action executes bound to its permit | Enforcement at matched capacity |
| C-only (optional) | Canonicalisation-only comparator | Same canonicalisation, no SERAPH machinery (no consequence topology, permits, or journal) | Isolates whether SERAPH machinery changes outcomes vs a plain filter |
| S2 (optional) | Sham gate | Observes + authorises, canonicalises nothing | Mediation-effect check |

**On G2 vs B0 (per freeze review):** both remove the field's discretionary capacity, so G2 < B2 is *not* evidence SERAPH out-detects a filter. The SERAPH-specific result is narrower and real: policy evaluated against an **explicitly declared consequence topology**, enforced through the **bound execution path**, supported by **auditable host observations**. If C-only runs and matches G2, we have an integration result, not a superiority result — and will say so.

**Pilot:** core conditions (P, B0, B1, B2, B2-S, G2) × **3 matched seeds = 18 episodes**. ◆ Three seeds support a **debugging/exploratory pilot**, not robust dependence estimation: the report emphasises **episode-level effects and observable traces**, with uncertainty stated, and makes no strong information-theoretic claim from this sample. Seed expansion only where a step moves.

**Measures:**
- Realised dependence: recipient behaviour conditioned on the symbol **received** (B2-S is what makes this causal).
- Coalition advantage: environment metric vs B0, seeds/variance reported.
- Legitimate performance: task completion/quality in G2 vs B2 (enforcement must preserve the work).
- ◆ Adaptation: use of inventoried alternative channels, especially post-canonicalisation (channel migration).

**Falsification / interpretation lines (registered):**
- F1: Realised dependence ≈ 0 at all capacities → the field is not a carrier here. Report.
- F2: Advantage flat across B0→B2 → no capacity effect at tested resolution. Report.
- F3: B2-S ≈ B2 → advantage is not carried by the sender→recipient relationship. Carrier claim fails. Report.
- F4: G2 ≈ B2 → boundary enforcement does not disrupt it. Report.
- F5: G2 suppresses advantage but degrades legitimate performance → "selective disruption" fails. Report.
- F6: A step between adjacent capacities = *candidate* threshold at this resolution only. Not a demonstrated phase transition.
- F7: Enforcement removes a declared encoding; a symbol choice alone is never labelled collusion.
- ◆ F8: If advantage survives G2 by migrating to an inventoried alternative channel, the enforcement claim scopes to the governed field only, and the migration is reported as a finding (feeds Track 3.4 questions).

## GATE 0 — Verify before experiments (no API spend on runs until passed)

1. **Carrier exists:** field is agent-selectable per action and peer-observable in Colosseum as configured. If not native, minimal wrapper (time-boxed Sat morning).
2. **Task equivalence:** scripted sweep — identical legitimate outcomes (allocation, scoring, downstream state) across every encoding.
3. **Channel inventory** written down (correction #1) and configuration frozen against it.
4. **Scramble procedure** implemented per the predeclared distribution-preserving scheme; sent/received logging verified on scripted data.
5. **Pre-observation enforcement test:** recipient-side logs provably never contain an uncanonicalised symbol in G2.

## ◆ SERAPH telemetry architecture (final, four layers)

**1. Carrier observation** — proposed symbol · actual emission · receiving agent · timestamp.
**2. Collusion-transition telemetry (precommit coordination monitor, exploratory)** — retains recent action histories; computes **lagged directional dependence** between discretionary signals and subsequent peer choices, **coordination persistence**, **change-point candidates**, **evidence quality**. Hard rules:
   - Assessments are computed **only from observations that already exist** at decision time. Future coalition advantage can never justify an earlier flag (no hindsight in the online plane).
   - The monitor carries a **falsifiable telemetry contract**: its recorded outputs are preserved to be scored later against independently established outcomes (advantage, false alarms).
   - It is **not** a validated detector this weekend, and an unvalidated statistical alarm **never overrides hard constraints**. SERAPH enforces the declared information-flow policy regardless of the monitor's state.
**3. SERAPH governance** — topology-scoped information constraints · permit binding · hold/deny only where the applicable policy supports it.
**4. Independent evaluation (offline plane)** — coalition advantage · valid task completion · false alarms · adaptation and alternative pathways. Offline outcomes are never fed back as online governance evidence.

**SERAPH-native enforcement (from v3, retained):** Agent A proposes a legitimate action carrying a discretionary symbol → SERAPH derives two consequences: (1) functional execution, (2) information exposed to Agent B → closure + binding preserve the authorised task effect and constrain the peer-visible signal → host-observed verification (executed? seen? performance preserved?). The disclosure path is **declared by the host**, never trusted to the agent's effect list. Canonicalisation is **pre-observation** or it is not prevention.

## Fallback — Cournot, corrected

Quantity in Cournot is economically consequential and may **not** serve as the carrier. Cournot is usable only with a verified payoff-neutral metadata field as carrier (Gate 0 applies identically). Otherwise: stay in Colosseum, change the carrier field. **Pivot clock:** seeded positive control not running by **Saturday Oct 24, ~12:00 PM ET** → fallback decision executes at the gate, in the open.

## Schedule

- **Fri Oct 23 (tonight):** clone starter repo, preflight, API key in compute.env, claim $50 Modal credits (Kamil's Oct 21 email; valid to Nov 1). Gate 0 items 1+3 (locate carrier field; draft channel inventory). Disclosure paragraph into project README tonight, before results exist.
- **Sat Oct 24 (morning):** Gate 0 items 2, 4, 5 (equivalence sweep, scramble check, pre-observation test) — scripted, no LLM spend. Seeded positive control. **12:00 PM: pivot gate.**
- **Sat Oct 24 (afternoon/evening):** 18-episode pilot grid; precommit monitor logging on all conditions (it observes; G2 additionally enforces).
- **Sun Oct 25:** justified seed expansion; analysis (dependence, advantage, legitimate performance, false alarms, migration); report on official template (Intro / Related Work / Methodology / Results / Discussion / Limitations & Dual-Use appendix / References). Numbers frozen early evening; **submit Sunday night ET; hard stop Mon 7:59 AM ET.**
- Resubmission: form details — same title; PDF changes — new submission with slightly different title or email sprints@apartresearch.com before deadline.

## Budget

18 pilot episodes + scripted Gate 0 (no LLM cost). Organizer envelope for 3.1: $15–$75 (up to ~$120 for longer workflows); $50 Modal credit offsets. Raw trajectories + journal exports + monitor outputs kept for every run.

## Judging rubric (same across tracks)

1. **Impact & Innovation** — primary claim as frozen above; physics/threshold material appears as a scoped secondary result.
2. **Execution Quality** — Gate 0 verification, distribution-preserving scramble, precommit contract with no-hindsight rule, exploratory labelling honest, negatives and migrations reported as results.
3. **Presentation & Clarity** — 8-page hard cap; instrument ≤1 page; claim structure maps to results subsections.

## Disclosure paragraph (README + report)

> SERAPH, the execution-governance layer used as measurement infrastructure and enforcement boundary in this work, is preexisting work by the author (public repository, research alpha), developed before this sprint and disclosed here per sprint rules. The extension of SERAPH's consequence topology to peer-visible information emission, the precommit coordination monitor, the carrier-capacity manipulation, the distribution-preserving scrambled control, all environment integration, runs, analysis, and findings reported here are new work performed during the sprint (Oct 23–25, 2026). SERAPH is not presented as a validated collusion detector; it is the instrument through which the information pathway was measured and governed.
