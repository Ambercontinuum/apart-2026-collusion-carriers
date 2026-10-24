"""Native assignment capability component; not yet wired into the runner.

Uses the emitter's existing local-buffer recovery evidence and declared kernel
assumptions. That evidence does not establish recovery of native task mutations.
On divergence this component halts; it does not claim rollback of task effects.
"""

import copy
import importlib

from envs.dcops.jira_ticket.jira_ticket_tools import JiraTicketTools

from .preview import functional_digest


def model_digest(env):
    snapshot = copy.copy(env)
    snapshot.assignment = {}
    return functional_digest(snapshot)


def native_assignment(env, agent, arguments):
    """The runner's native tool/update/callback sequence, with no board logger."""
    result = JiraTicketTools(None).handle_tool_call(
        "assign_task", agent, arguments, phase="execution", iteration=1,
        env_state=env.get_serializable_state(),
    )
    if result.get("status") == "success":
        updates = result["result"]["state_updates"]
        env.apply_state_updates(updates)
        env.post_tool_execution_callback(updates, result)
    return result


class CertifiedAssignment:
    def __init__(self, emitter):
        self.emitter = emitter
        self.env = emitter.stage.env
        self.s = s = emitter.s
        self.halted = False
        self.last_result = None
        self.__seraph_binding__ = {
            "adapter": "apart.native-assignment.v1",
            "seed": emitter.stage.episode_seed,
            "agents": emitter.stage.agents,
        }
        self.spec = s.ManifoldSpec(
            manifold_id="apart.native-assignment", version="1",
            coordinate_names=("native_digest", "result_digest", "model_digest", "public_digest"),
            admitted_origins=("apart.host",), mutation_keys=("apart.protocol",),
            rules=(s.InvariantRule("native.model-preserved", "model_digest",
                                   s.InvariantRelation.PRESERVE,
                                   subject_ids=("native-task",)),),
            evidence_requirements=(s.EvidenceRequirement("host.native-projection", ("apart.host",)),),
            consequence_edges=tuple(
                s.ConsequenceEdge("native-task", agent) for agent in emitter.stage.agents
            ),
        )
        self.compiled = s.ManifoldCompiler.compile(self.spec)
        guard = importlib.import_module("adapters.certified_tool_guard")
        cap = importlib.import_module("adapters.capability_runtime")
        self.runtime = cap.CapabilityRuntime(
            registry=cap.CapabilityRegistry((cap.RegisteredCapability(
                capability_id="apart.assign-native", fn=self._assign,
                scopes=(
                    cap.CapabilityScope("native_digest", subject_ids=("native-task",)),
                    cap.CapabilityScope("result_digest", subject_ids=("native-task",)),
                    cap.CapabilityScope("model_digest", subject_ids=("native-task",)),
                    cap.CapabilityScope("public_digest", subject_ids=emitter.stage.agents),
                ),
            ),)),
            guard=guard.CertifiedToolGuard(
                compiled=self.compiled, state_reader=self.read_state,
                governance_input_reader=self.governance, on_divergence=self.contain,
            ),
            journal=emitter.runtime.journal,
        )

    def read_state(self):
        s = self.s
        entities = [s.EntityState("native-task", ("task",), (
            s.Coordinate("model_digest", model_digest(self.env)),
            s.Coordinate("native_digest", functional_digest(self.env)),
            s.Coordinate("result_digest", s.content_digest(self.last_result)),
        ))]
        entities.extend(s.EntityState(agent, ("inhabitant",), (
                            s.Coordinate("public_digest", s.content_digest(self.env.assignment)),))
                        for agent in self.emitter.stage.agents)
        return s.ManifoldState("apart.assignment-state",
                               tuple(sorted(entities, key=lambda entity: entity.entity_id)))

    def governance(self):
        s = self.s
        frame = s.ConstraintFrame(
            frame_id="apart.assignment-frame", topology_id=self.spec.manifold_id,
            topology_version="1", transition_id="apart.native-assignment",
            required_relations=("native_execution_available",),
            observations=(s.ConstraintObservation(
                "native_execution_available",
                s.ConstraintResolution.REFUTED if self.halted else s.ConstraintResolution.PROVEN,
                scope="native-task", horizon="execution",
                evidence_ref=s.functional_state_digest(self.read_state()),
            ),),
        )
        return s.GovernanceInput(
            constraints=frame, prp_trail=self.emitter.governance().prp_trail,
            trajectory=(functional_digest(self.env), functional_digest(self.env)),
            request_commit=True,
        )

    def authorize(self, agent, arguments):
        if self.halted:
            raise PermissionError("native execution halted after divergence")
        if agent not in self.emitter.stage.agents or not isinstance(arguments, dict) or (
            set(arguments) != {"task_id"} or type(arguments["task_id"]) is not str
        ):
            raise ValueError("exact native assignment arguments required")
        args = copy.deepcopy(arguments)
        before = self.read_state()
        # Host-only prediction uses an isolated native environment. No projection
        # result is returned to an actor or substituted for actual execution.
        predicted = copy.deepcopy(self.env)
        result = native_assignment(predicted, agent, args)
        s = self.s
        digest = s.functional_state_digest(before)
        proposal = s.TransitionProposal(
            "apart.native-assignment", self.spec.manifold_id, "1", digest,
            "apart.host", "apart.host", (
                s.FunctionalEffect("native-task", "native_digest",
                                   functional_digest(self.env), functional_digest(predicted), True),
                s.FunctionalEffect("native-task", "result_digest",
                                   s.content_digest(self.last_result), s.content_digest(result), True),
                s.FunctionalEffect("native-task", "model_digest",
                                   model_digest(self.env), model_digest(predicted), True),
                *[s.FunctionalEffect(recipient, "public_digest",
                                     s.content_digest(self.env.assignment),
                                     s.content_digest(predicted.assignment), True)
                  for recipient in self.emitter.stage.agents],
            ), self.emitter.stage.agents,
            evidence=(s.EvidenceRecord("host.native-projection", "apart.host",
                                       s.content_digest(result), digest),),
        )
        return self.runtime.authorize("apart.assign-native", proposal, (agent, args))

    def _assign(self, agent, arguments):
        if self.halted:
            raise PermissionError("native execution halted")
        self.last_result = native_assignment(self.env, agent, arguments)
        return copy.deepcopy(self.last_result)

    def contain(self, report):
        self.halted = True

    def execute(self, permit):
        return self.runtime.execute(permit).execution.result

    def assign(self, agent, arguments):
        return self.execute(self.authorize(agent, arguments))
