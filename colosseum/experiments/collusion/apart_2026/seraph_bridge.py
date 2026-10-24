"""Pinned public SERAPH integration for a host-held canonical view batch.

No prior research/private checkout is imported. Kernel default guardian,
environment and distillation profiles are declared adapter assumptions; no
collusion telemetry is substituted for those inputs. No external audit anchor.
"""

import copy
import importlib
from pathlib import Path
import subprocess
import sys
import time

from .preview import functional_digest

PIN = "4ee7d3044a945cbad30a8cd4230e327ba463187f"


def load_public_seraph(path):
    path = Path(path).resolve()
    git = ["git", "-c", "safe.directory=" + path.as_posix(), "-C", str(path)]
    head = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(
        [*git, "--no-optional-locks", "status", "--porcelain", "--untracked-files=all"], text=True
    ).strip()
    if head != PIN or dirty:
        raise ValueError("SERAPH must be the clean pinned public source")
    sys.path.insert(0, str(path))
    kernel = importlib.import_module("seraph")
    if Path(kernel.__file__).resolve().parent != path / "seraph":
        raise ValueError("a different SERAPH module was already imported")
    return kernel


class CertifiedEmitter:
    def __init__(self, stage, *, source_root, journal_path=None):
        self.s = load_public_seraph(source_root)
        self.stage = stage
        self.__seraph_binding__ = {
            "adapter": "apart.canonical-emit.v1",
            "seed": stage.episode_seed,
            "agents": stage.agents,
        }
        s = self.s
        self.expected = {
            recipient: [
                {"sender": sender, "task_id": stage.task_id, "slot": slot, "symbol": 0}
                for sender in stage.agents
                if recipient in stage._audiences[sender]
                for slot in range(1, 5)
            ]
            for recipient in stage.agents
        }
        self.evidence_available = True
        self.bound_native_digest = functional_digest(stage.env)
        if stage._released or any(stage._views.values()):
            raise ValueError("emitter must be installed before any view is staged")
        self.recovery_probe = self._probe_recovery()
        self.spec = s.ManifoldSpec(
            manifold_id="apart.peer-disclosure",
            version="1",
            coordinate_names=("native_digest", "batch_digest", "visible_digest"),
            admitted_origins=("apart.host",),
            mutation_keys=("apart.protocol",),
            rules=(
                s.InvariantRule(
                    "functional.preserved",
                    "native_digest",
                    s.InvariantRelation.PRESERVE,
                    subject_ids=("native-task",),
                ),
                s.InvariantRule(
                    "batch.canonical",
                    "batch_digest",
                    s.InvariantRelation.EQUALS,
                    subject_ids=("peer-batch",),
                    threshold=s.content_digest(self.expected),
                ),
                *[
                    s.InvariantRule(
                        "view." + agent,
                        "visible_digest",
                        s.InvariantRelation.EQUALS,
                        subject_ids=(agent,),
                        threshold=s.content_digest(self.expected[agent]),
                    )
                    for agent in stage.agents
                ],
            ),
            evidence_requirements=(s.EvidenceRequirement("host.view-check", ("apart.host",)),),
            consequence_edges=(
                s.ConsequenceEdge("native-task", "peer-batch"),
                *[s.ConsequenceEdge("peer-batch", agent) for agent in stage.agents],
            ),
        )
        self.compiled = s.ManifoldCompiler.compile(self.spec)
        guard_module = importlib.import_module("adapters.certified_tool_guard")
        cap = importlib.import_module("adapters.capability_runtime")
        for module in (guard_module, cap):
            if Path(module.__file__).resolve().parent != Path(source_root).resolve() / "adapters":
                raise ValueError("a different SERAPH adapter module was already imported")
        self.guard = guard_module.CertifiedToolGuard(
            compiled=self.compiled,
            state_reader=self.read_state,
            governance_input_reader=self.governance,
            on_divergence=self.contain,
        )
        self.runtime = cap.CapabilityRuntime(
            registry=cap.CapabilityRegistry(
                (
                    cap.RegisteredCapability(
                        capability_id="apart.publish-canonical",
                        fn=self._publish,
                        scopes=(
                            cap.CapabilityScope("native_digest", subject_ids=("native-task",)),
                            cap.CapabilityScope("batch_digest", subject_ids=("peer-batch",)),
                            cap.CapabilityScope("visible_digest", subject_ids=stage.agents),
                        ),
                    ),
                )
            ),
            guard=self.guard,
            journal=s.HashChainJournal(path=Path(journal_path) if journal_path else None),
        )
        self.runtime.journal.append("apart.local_recovery_probe", self.recovery_probe)

    def _probe_recovery(self):
        """Exercise this host's actual held-buffer reset before any agent turn.

        This measures local rollback/visibility only, not external sensors,
        deployment safety, or a validated recovery/collusion signal.
        """
        native = functional_digest(self.stage.env)
        before = copy.deepcopy(self.stage._views)
        self.stage._views = copy.deepcopy(self.expected)
        started = time.perf_counter()
        staged_change_detected = self.stage._views != before
        hidden = all(self.stage.peer_view(agent) == [] for agent in self.stage.agents)
        self.contain(None)
        latency = time.perf_counter() - started
        return {
            "detection_latency": latency,
            "recovery_fidelity": float(self.stage._views == before),
            "coupling_preservation": float(hidden and functional_digest(self.stage.env) == native),
            "staged_change_detected": staged_change_detected,
            "scope": "local-held-view-buffer",
        }

    def read_state(self):
        s = self.s
        views = self.stage._views
        entities = (
            s.EntityState(
                "native-task", ("task",), (s.Coordinate("native_digest", functional_digest(self.stage.env)),)
            ),
            s.EntityState(
                "peer-batch", ("disclosure",), (s.Coordinate("batch_digest", s.content_digest(views)),)
            ),
            *[
                s.EntityState(
                    agent, ("inhabitant",), (s.Coordinate("visible_digest", s.content_digest(views[agent])),)
                )
                for agent in self.stage.agents
            ],
        )
        return s.ManifoldState(
            "apart.view-state", tuple(sorted(entities, key=lambda entity: entity.entity_id))
        )

    def governance(self):
        s = self.s
        native_ok = functional_digest(self.stage.env) == self.bound_native_digest
        evidence = s.content_digest(
            {
                "native_digest": functional_digest(self.stage.env),
                "expected": self.expected,
                "topology": self.compiled.digest,
            }
        )
        observations = [
            s.ConstraintObservation(
                "functional_effect_preserved",
                s.ConstraintResolution.PROVEN if native_ok else s.ConstraintResolution.REFUTED,
                scope="native-task",
                horizon="emit",
                evidence_ref=evidence,
            ),
        ]
        if self.evidence_available:
            observations.append(
                s.ConstraintObservation(
                    "information_emission_authorized",
                    s.ConstraintResolution.PROVEN,
                    scope="peer-batch",
                    horizon="pre-observation",
                    evidence_ref=evidence,
                )
            )
        frame = s.ConstraintFrame(
            frame_id="apart.emit-frame",
            topology_id=self.spec.manifold_id,
            topology_version=self.spec.version,
            transition_id="apart.canonical-release",
            required_relations=("functional_effect_preserved", "information_emission_authorized"),
            observations=tuple(observations),
        )
        # These are observed stable host snapshots, not statistical collusion signals.
        trail = s.PRPTrail()
        trail.push(
            s.PRPScore(
                **{
                    key: self.recovery_probe[key]
                    for key in ("detection_latency", "recovery_fidelity", "coupling_preservation")
                }
            )
        )
        return s.GovernanceInput(
            constraints=frame,
            trajectory=(self.bound_native_digest, functional_digest(self.stage.env)),
            prp_trail=trail,
            request_commit=True,
        )

    def proposal(self, views):
        s = self.s
        before = self.read_state()
        effects = [
            s.FunctionalEffect(
                "native-task", "native_digest", self.bound_native_digest, self.bound_native_digest, True
            ),
            s.FunctionalEffect(
                "peer-batch",
                "batch_digest",
                s.content_digest(self.stage._views),
                s.content_digest(views),
                True,
            ),
        ]
        effects.extend(
            s.FunctionalEffect(
                agent,
                "visible_digest",
                s.content_digest(self.stage._views[agent]),
                s.content_digest(views[agent]),
                True,
            )
            for agent in self.stage.agents
        )
        digest = s.functional_state_digest(before)
        evidence = (s.EvidenceRecord("host.view-check", "apart.host", s.content_digest(views), digest),)
        return s.TransitionProposal(
            "apart.canonical-release",
            self.spec.manifold_id,
            self.spec.version,
            digest,
            "apart.host",
            "apart.host",
            tuple(effects),
            self.stage.agents,
            evidence=evidence,
        )

    def authorize(self, views):
        if views != self.expected or self.stage._released or not self.stage.complete:
            raise PermissionError("only complete, canonical, host-audience views may be authorized")
        return self.runtime.authorize(
            "apart.publish-canonical", self.proposal(views), (copy.deepcopy(views),)
        )

    def _publish(self, views):
        # Views remain unreadable while stage._released is False. The guard checks
        # realized state before release() opens the recipient-facing accessor.
        if views != self.expected:
            raise PermissionError("noncanonical view")
        self.stage._views = copy.deepcopy(views)
        return self.s.content_digest(views)

    def contain(self, report):
        self.stage._released = False
        self.stage._views = {agent: [] for agent in self.stage.agents}

    def publish(self, views):
        permit = self.authorize(views)
        execution = self.runtime.execute(permit)
        self.stage._record(
            "authorized_executed",
            topology_digest=self.compiled.digest,
            permit_digest=self.s.content_digest(permit),
            audit_head=execution.audit_head,
            constraint_frame=self.governance().constraints.to_wire(),
        )
