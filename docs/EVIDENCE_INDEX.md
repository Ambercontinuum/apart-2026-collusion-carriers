# Completed study evidence index

The [submission paper](../output/pdf/paper.pdf) is the concise current account.
The [expanded report](RESEARCH_REPORT.md) preserves more experimental detail.
Batches below are distinct protocols, not pooled trials. Raw records and their
manifests are preserved; this index does not rewrite historical evidence.

| Batch | Entry point | Status |
| --- | --- | --- |
| B0/B2 shakedown | [Results](../evidence/shakedown/b0-b2-seed1-20261024/RESULTS.md) | 40 requests, constant symbols, matched outcomes |
| Explicit codebook | [Results](../evidence/calibration/explicit-codebook-seed1-20261024/RESULTS.md) | Six calls; encoding succeeded, receiver control failed |
| X1 discriminator | [Results](../evidence/calibration/receiver-discriminator-20261024/RESULTS.md) | Stopped on fourth response; whole multi-call response rejected |
| Five-arm grid | [Results](../evidence/exploratory-grid/freeze-20261024/RESULTS.md) | 15 episodes, 300 calls, 240 zero symbols, 3 live emission permits |
| Supplied P | [Results](../evidence/calibration/p-qwen3-4b-seed1-20261024/RESULTS.md) | 28 calls, explicit coordination; unmatched to grid |
| Initial private-bit calibration | [Results](../evidence/experiment2/v1_2/RESULTS.md) | 24 calls; failed 7/8 screen; main not run for this version |
| Minimal/oracle diagnostic | [Results](../evidence/experiment2/xor-diagnostic-v1/RESULTS.md) | 12 calls; separate interventions |
| Full-context diagnostic | [Results](../evidence/experiment2/context-diagnostic-v1/RESULTS.md) | 8 calls; extraction 4/4, XOR report 2/4 |
| Final attempt | [Results](../evidence/experiment2/final-attempt-v1/RESULTS.md) | 96 calls; calibration 7/8; 24 main episodes completed |

## Final attempt provenance

- Pre-call source `42b3251e9ad147895b6453b034a179950c4e0951`; candidate `0357265`.
- Published result snapshot `f09bb230924223187de0f2a3db6db42efd869d7f`.
- Protocol SHA-256 `5d25e727bb64530bb5b10acdd3596f92b7f0e7c09da8aad7df4aac4887553ab4`.
- [Audit](../evidence/experiment2/final-attempt-v1/AUDIT.json) verifies reconstruction, strict acceptance, scoring, receipt isolation and journal execution heads.
- The final evidence folder retains exact transport, raw episode records, native journals, shutdown checks and manifest. Read its original results for field definitions and filenames.

Historical Gate 0 UNKNOWN entries remain historical. The original complete
six-condition study and monitor were not completed as originally planned. Separate,
bounded approved runs and task-specific offline gates do not retroactively pass
those original obligations. All-zero carrier outcomes do not prove prevention.

## Publication redaction

The supplied P evidence has a dated forward-only [redaction note](../evidence/calibration/p-qwen3-4b-seed1-20261024/REDACTION_NOTE.json). Local paths were removed and a pre-inference startup traceback omitted; original hashes are retained. Requests, responses, native results and scores are unchanged. Historical commits were not rewritten and still contain their original bytes.
