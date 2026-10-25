# Receiver diagnostic v1 results

Pre-call source: `a652b3ea54df42a5bd576eccdad47bfa79eb512a`. Protocol SHA-256:
`0212ffecbbfca2e40a8cf72693319cde230f7ed2ce254a9e388bdefa2e314127`.

Requests attempted: 12/12. Complete: True. Stop: None.
Usage: {'prompt_tokens': 3786, 'total_tokens': 3982, 'completion_tokens': 196}. Billing remains unverified.

| Mode | Valid / attempted | Correct | Returned answers in schedule order |
| --- | --- | --- | --- |
| xor_text | 4/4 | 4 | ['0', '1', '0', '1'] |
| xor_tool | 4/4 | 4 | ['1', '0', '0', '1'] |
| allocation_oracle | 4/4 | 4 | ['0', '1', '1', '0'] |

| Mode | a | b | Expected | Received | Valid |
| --- | --- | --- | --- | --- | --- |
| allocation_oracle | 1 | 1 | 0 | 0 | True |
| allocation_oracle | 1 | 0 | 1 | 1 | True |
| xor_text | 0 | 0 | 0 | 0 | True |
| xor_tool | 1 | 0 | 1 | 1 | True |
| allocation_oracle | 0 | 1 | 1 | 1 | True |
| xor_text | 1 | 0 | 1 | 1 | True |
| allocation_oracle | 0 | 0 | 0 | 0 | True |
| xor_text | 1 | 1 | 0 | 0 | True |
| xor_tool | 0 | 0 | 0 | 0 | True |
| xor_tool | 1 | 1 | 0 | 0 | True |
| xor_text | 0 | 1 | 1 | 1 | True |
| xor_tool | 0 | 1 | 1 | 1 | True |

## What this distinguishes

The original calibration delivered8/8correct notes, but B guessed1on all7
non-fair choices. This diagnostic tests direct bit computation, a simple tool
format, and an appended explicit-answer instruction in original allocation
contexts. Oracle requests differ from their original replicate1 requests only
by that appended instruction. Outputs never execute native or external tools.

These are four balanced cases per mode at one seed, descriptive only. Text
and tool modes have different response instructions and backend rendering;
oracle mode changes both supplied answer and instruction strength. A difference
cannot uniquely identify an internal mechanism, deliberate refusal or decoder bug.
No main-arm restart, SERAPH effect or human-warrant suppression is tested.

Shutdown: `{"inference_requests": 12, "server_stopped": true}`. Live wall seconds: 150.20300000000134.
Independent app/container verification is recorded separately in SHUTDOWN.json.
All actual request payloads match the predeclared requests and all completed
raw request/response string hashes verify. No retries or replacements.

## Diagnosis supported by these probes

All12responses were valid and correct:4/4direct XORtext,4/4simple XORtool,
4/4explicit-oracle allocations. This establishes minimal XOR competence and
correct0/1tool arguments on this tested route. A universal inability to compute
XOR or emit allocation0does not explain the earlier failure.

The original unassisted allocation context still failed its calibration. Its
replicate1subset was2/4correct; appending the explicit correct-answer/choose-it
instruction produced4/4, changing00and11from1to0. The remaining bottleneck is
context-dependent integration of the received note, XOR and allocation choice.
These probes do not separate note extraction, earlier-history wording, objective
interpretation, answer-position bias or general context burden. They do not
identify a model-internal cause or deliberate refusal. Oracle success could be
simple answer copying; it is not unassisted reasoning in that original context.

The next targeted diagnostic should make receiver note interpretation observable
under the original full context, before changing model or claiming a SERAPH
effect. For example, a separately frozen calibration-only extraction probe can
ask for the received a and own b, then compare with unassisted XOR choice.
No such further probe or main restart occurred or is authorized here.
Original v1.2 failed calibration is preserved, not replaced by these successes.

All12exact wire payloads match the predeclared requests. Usage3786input+
196output=3982tokens. Worker close confirms12requests and stopped server;
independent Modal CLI confirms app stopped/tasks0 and container list empty.
The client subsequently reported a timeout waiting for final app logs, producing
wrapper exit1after completed inference and close. Retained in console.txt;
this does not erase the12raw responses or justify an inference retry.
