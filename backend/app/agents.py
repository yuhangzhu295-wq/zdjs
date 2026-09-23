"""Evidence-bounded analysis-role orchestration."""
from __future__ import annotations

import asyncio

from .codex_bridge import (
    DEFAULT_INDEPENDENT_ROLES,
    CodexCollaborationBridge,
    CodexRoleRunner,
    LocalEvidenceOnlyOrchestrator,
)
from .models import EvidencePool, ModelResult, ParsedQuestion


class EvidenceOnlyAnalyst:
    """One local role facade, retained for a safe standalone deployment."""

    def __init__(self, role: str) -> None:
        self.role = role
        self._fallback = LocalEvidenceOnlyOrchestrator()

    async def analyze(self, parsed: ParsedQuestion, pool: EvidencePool) -> ModelResult:
        result = await self._fallback.analyze_roles(
            question="", claims=parsed.claims, evidence_pool=pool, roles=(self.role,),
        )
        return result[self.role]


class MultiModelOrchestrator:
    """Run isolated roles; agreement is never evidence.

    A normal FastAPI process has no access to Codex's internal subagent tools. It
    uses a deterministic local fallback unless a Codex-hosted runner is supplied.
    """

    def __init__(self, runner: CodexRoleRunner | None = None) -> None:
        self._bridge = CodexCollaborationBridge(runner) if runner else None

    @property
    def runtime(self) -> str:
        return "codex_hosted" if self._bridge else "local_evidence_only"

    async def independent(
        self, parsed: ParsedQuestion, pool: EvidencePool
    ) -> dict[str, ModelResult]:
        if self._bridge:
            return await self._bridge.analyze_roles(
                question=parsed.original_question, claims=parsed.claims, evidence_pool=pool,
                roles=DEFAULT_INDEPENDENT_ROLES,
            )
        values = await asyncio.gather(
            *(EvidenceOnlyAnalyst(role).analyze(parsed, pool) for role in DEFAULT_INDEPENDENT_ROLES)
        )
        return dict(zip(DEFAULT_INDEPENDENT_ROLES, values, strict=True))

    async def red_team(
        self, parsed: ParsedQuestion, pool: EvidencePool
    ) -> ModelResult:
        if self._bridge:
            return (await self._bridge.analyze_roles(
                question=parsed.original_question, claims=parsed.claims, evidence_pool=pool, roles=("red_team",),
            ))["red_team"]
        result = await EvidenceOnlyAnalyst("red_team").analyze(parsed, pool)
        result.reasoning_summary = (
            "ATTACK_FAILED is never a vote; it only reflects evidence-backed attack results."
        )
        return result
