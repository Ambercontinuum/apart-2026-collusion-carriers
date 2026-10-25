# Experiment2 v1.1 preflight: stopped before inference

Amber authorized the bounded experiment (A048). Seven deterministic test methods
pass, including exhaustive payoff/policy checks, request secrecy/matching and
native/SERAPH capability equivalence and attacks. This is engineering evidence,
not behavioral data. Public SERAPH remains unchanged at its recorded pin.

The required transport gate fails: official vLLM0.11.0 source says the
parallel_tool_calls option is ignored. Both v1 and this narrow v1.1 clarification
require support or stop; sending false is not proof the backend honors it.
No remote image byte inspection was made; this cannot establish its support.

**0 requests,0 tokens,0 workers started. Calibration and main were not run.**
No claimed competence/collusion/prevention result. Existing Experiment1 intact.
The live driver is not released; modal_experiment2.py is a fail-closed preflight.
Billing was not independently reconciled in this attempt.

Next concrete option: amend only the generation contract to explicitly accept
that this pinned backend ignores parallel_tool_calls, retaining the false field,
exactly-one-call validation, no execution of invalid batches, zero retries,
first-invalid calibration stop and96-request cap. This is a protocol change,
not an existing approval. Alternatively verify a backend that honors the field;
that changes the pinned route and requires fresh compatibility/gate evidence.
Do not silently choose either or claim an ignored flag enforces one call.

Source evidence: official vLLM v0.11.0 protocol.py426-427 and
serving_chat.py90-96; exact URLs are in GATES.json. Test output in console.txt.
