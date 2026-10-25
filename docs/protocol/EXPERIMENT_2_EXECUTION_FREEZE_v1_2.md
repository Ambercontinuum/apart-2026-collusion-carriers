# Experiment2 v1.2: approved transport amendment

Amber A049: "Approve amendment and run" in response to the explicitly presented
ignored-setting contract. V1 and v1.1 are preserved. Normative companion JSON
retains all exact messages, payoff rules, schedule, three arms and96-call cap.

Only change from v1.1: vLLM0.11.0 is known to ignore parallel_tool_calls. Sending
false therefore does not enforce one call during generation. Amber accepts
that limitation. Every response still requires exactly one schema-valid tool
call before native dispatch; multi-call responses fail without any call being
executed. No retries, repairs, splitting batches or replacements. Calibration's
first invalid response stops the entire live run. Main invalid episodes stop
only that episode, unless a hard integrity/transport/budget failure occurs.

Calibration delivers only private_note; audit_bit stays host-side. Unchanged
main arms: intact/host_canonical/seraph_canonical. Same pinned Qwen/model image,
temperature0,256 output tokens,96 maximum requests, one L4,1800 live seconds.
No new inference was required to identify the ignored-setting limitation.
Source basis: official vLLM v0.11.0 protocol.py426-427 and serving_chat.py90-96;
URLs and prior pre-inference stop retained in evidence/experiment2/v1_1/GATES.json.

All native/context/new SERAPH tests still required; runtime response validation
is not a claim of generation-level enforcement. Billing remains unverified.
Calibration results screen competence, not main-arm information transfer.
