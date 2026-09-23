"""Evidence-bounded boundary for collaboration hosted by a Codex session.

This module deliberately does not call Codex internal tools.  A host that has access to
Codex subagents may implement ``CodexRoleRunner`` and pass only the serialized task
payload to each isolated role.  A normal FastAPI process has no such built-in bridge and
can use ``LocalEvidenceOnlyOrchestrator`` instead.
"""
from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError

from .models import Claim, Evidence, EvidencePool, ModelResult, OptionVerdict, Verdict


DEFAULT_INDEPENDENT_ROLES: tuple[str, ...] = (
    "primary_solver",
    "independent_critic",
    "search_verifier",
)

RawStructuredResult: TypeAlias = str | bytes | bytearray | Mapping[str, Any]


class StructuredOutputError(ValueError):
    """Raised when a role returns output outside the evidence-bounded contract."""


class CollaborationTask(BaseModel):
    """The complete, peer-isolated input a role is allowed to receive."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    question: StrictStr = Field(min_length=1)
    claims: tuple[Claim, ...]
    evidence: tuple[Evidence, ...]

    @classmethod
    def from_context(
        cls, question: str, claims: Sequence[Claim], evidence_pool: EvidencePool
    ) -> "CollaborationTask":
        """Copy only question, claims, and shared browser/search evidence into a task."""

        # Re-validate through JSON-compatible data so roles cannot mutate caller-owned models.
        return cls.model_validate(
            {
                "question": question,
                "claims": [claim.model_dump(mode="json") for claim in claims],
                "evidence": [evidence.model_dump(mode="json") for evidence in evidence_pool.evidence],
            }
        )


class _StrictOptionVerdict(BaseModel):
    """Wire-format verdict; extra fields such as generated Evidence are rejected."""

    model_config = ConfigDict(extra="forbid")

    verdict: Verdict
    evidence_refs: list[StrictStr] = Field(default_factory=list)
    rationale: StrictStr = ""


class _StrictModelResult(BaseModel):
    """Strict wire schema for a model-produced ``ModelResult``."""

    model_config = ConfigDict(extra="forbid")

    agent_role: StrictStr
    option_verdicts: dict[StrictStr, _StrictOptionVerdict]
    reasoning_summary: StrictStr = ""
    uncertainties: list[StrictStr] = Field(default_factory=list)
    missing_evidence: list[StrictStr] = Field(default_factory=list)
    requested_searches: list[StrictStr] = Field(default_factory=list)


class CodexRoleRunner(Protocol):
    """Adapter implemented by a Codex-hosted coordinator, never by FastAPI itself.

    ``task_json`` contains no peer output or private browsing state.  The runner should
    create a fresh subagent context for every invocation.
    """

    async def invoke_role(
        self, *, role: str, task_json: str
    ) -> RawStructuredResult: ...


def validate_model_result(
    raw: RawStructuredResult, *, expected_role: str, task: CollaborationTask
) -> ModelResult:
    """Parse a role result and prove it refers only to the supplied task evidence."""

    try:
        if isinstance(raw, (str, bytes, bytearray)):
            result = _StrictModelResult.model_validate_json(raw)
        elif isinstance(raw, Mapping):
            result = _StrictModelResult.model_validate(dict(raw))
        else:  # Kept for a clear error if an adapter violates its protocol at runtime.
            raise TypeError(f"unsupported structured result type: {type(raw).__name__}")
    except (ValidationError, TypeError, ValueError) as error:
        raise StructuredOutputError(f"{expected_role} returned invalid structured output: {error}") from error

    if result.agent_role != expected_role:
        raise StructuredOutputError(
            f"role mismatch: expected {expected_role!r}, received {result.agent_role!r}"
        )

    expected_options = {claim.option for claim in task.claims}
    received_options = set(result.option_verdicts)
    if received_options != expected_options:
        raise StructuredOutputError(
            "option verdicts must cover exactly the task options; "
            f"expected {sorted(expected_options)!r}, received {sorted(received_options)!r}"
        )

    known_evidence_ids = {evidence.evidence_id for evidence in task.evidence}
    for option, verdict in result.option_verdicts.items():
        unknown_refs = set(verdict.evidence_refs) - known_evidence_ids
        if unknown_refs:
            raise StructuredOutputError(
                f"{expected_role} referenced Evidence it was not given for {option!r}: "
                f"{sorted(unknown_refs)!r}"
            )

    return ModelResult.model_validate(result.model_dump())


class CodexCollaborationBridge:
    """Coordinate isolated Codex-hosted roles through an explicit external adapter.

    This class is a boundary, not an SDK for Codex internals: production deployments must
    supply a coordinator that actually has subagent access.  Each role receives an
    independently serialized copy of the same evidence-bounded task.
    """

    def __init__(self, runner: CodexRoleRunner) -> None:
        self._runner = runner

    async def analyze_roles(
        self,
        *,
        question: str,
        claims: Sequence[Claim],
        evidence_pool: EvidencePool,
        roles: Sequence[str] = DEFAULT_INDEPENDENT_ROLES,
    ) -> dict[str, ModelResult]:
        """Run roles concurrently without exposing any role's output to another."""

        role_names = tuple(roles)
        if not role_names or any(not role for role in role_names):
            raise ValueError("at least one non-empty role name is required")
        if len(set(role_names)) != len(role_names):
            raise ValueError("role names must be unique to preserve result isolation")

        task = CollaborationTask.from_context(question, claims, evidence_pool)
        results = await asyncio.gather(
            *(self._run_isolated(role, task) for role in role_names)
        )
        return dict(zip(role_names, results, strict=True))

    async def _run_isolated(self, role: str, task: CollaborationTask) -> ModelResult:
        # Serializing anew prevents a role adapter from sharing mutable task objects.
        task_json = task.model_dump_json()
        raw = await self._runner.invoke_role(role=role, task_json=task_json)
        return validate_model_result(raw, expected_role=role, task=task)


class LocalEvidenceOnlyOrchestrator:
    """Deterministic fallback for deployments without a Codex-hosted coordinator.

    It derives each verdict solely from the supplied EvidencePool.  It does not simulate
    independent model reasoning and it does not manufacture evidence.
    """

    async def analyze_roles(
        self,
        *,
        question: str,
        claims: Sequence[Claim],
        evidence_pool: EvidencePool,
        roles: Sequence[str] = DEFAULT_INDEPENDENT_ROLES,
    ) -> dict[str, ModelResult]:
        """Produce evidence-only results for the requested named roles."""

        del question  # The fallback deliberately makes no inference from question wording.
        role_names = tuple(roles)
        if not role_names or any(not role for role in role_names):
            raise ValueError("at least one non-empty role name is required")
        if len(set(role_names)) != len(role_names):
            raise ValueError("role names must be unique to preserve result isolation")

        return {
            role: self._analyze_evidence(role, claims, evidence_pool)
            for role in role_names
        }

    @staticmethod
    def _analyze_evidence(
        role: str, claims: Sequence[Claim], evidence_pool: EvidencePool
    ) -> ModelResult:
        verdicts: dict[str, OptionVerdict] = {}
        missing: list[str] = []
        for claim in claims:
            matching = evidence_pool.for_claim(claim.claim_id)
            support = any(evidence.stance == "support" for evidence in matching)
            counter = any(evidence.stance == "counter" for evidence in matching)
            verdict = (
                Verdict.CONFLICT
                if support and counter
                else Verdict.TRUE
                if support
                else Verdict.FALSE
                if counter
                else Verdict.UNKNOWN
            )
            if not matching:
                missing.append(claim.claim_id)
            verdicts[claim.option] = OptionVerdict(
                verdict=verdict,
                evidence_refs=[evidence.evidence_id for evidence in matching],
                rationale="Local fallback derives this verdict solely from shared evidence.",
            )
        return ModelResult(
            agent_role=role,
            option_verdicts=verdicts,
            missing_evidence=missing,
        )
