# Sources and prior work

Organizer: [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon),
commit `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`.
Only `colosseum/experiments/common/local_protocol.py` is copied into this
project at this checkpoint. Its exact file link and byte hash are in
[SOURCE_FILES.json](SOURCE_FILES.json). The organizer's full source tree and Git
history are not included. The source link records origin, not a newly granted
license; no project-wide license is asserted over third-party source.

Governance: [Ambercontinuum/SERAPH-1.0](https://github.com/Ambercontinuum/SERAPH-1.0),
commit `4ee7d3044a945cbad30a8cd4230e327ba463187f`, selected by Amber.
SERAPH source is not copied into this repository. Its preexisting validation
report is retained as baseline evidence with an explicit upstream label.

Runtime dependency: `terrarium-agents==0.1.1`, from
[Terrarium](https://github.com/umass-aisec/Terrarium).
The installed distribution supplies native Jira task semantics and scoring.
We inspect those files without modifying the installed dependency. Package
version is pinned; an upstream Git commit for the distribution is not asserted.

SERAPH is preexisting research-alpha work by Amber Anson. New sprint work began
October 24, 2026 and currently comprises the candidate carrier component, tests,
inspection evidence, and extension proposal. No completed experiment or collusion
finding is claimed. SERAPH baseline results do not establish sprint enforcement.

Source files inherited from the organizer, new sprint files and runtime package
dependencies remain distinguishable. Future copied or adapted files must add
their exact origin, pinned commit, original path, local hash and modification
description to the manifest.

The private sibling SERAPH was engineering background, not integration source.
Optimus scratchpad is outside this repository's write and coordination boundary.
