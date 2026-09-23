"""Safety contracts for the evidence-bounded orchestration layer.

These tests deliberately exercise the current public Python interfaces. A future
Codex-hosted runner may replace ``EvidenceOnlyAnalyst``, but it must preserve these
contracts: model output is never evidence, and the gate remains conservative when
an orchestration result is unavailable.
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app import main
from app.agents import EvidenceOnlyAnalyst, MultiModelOrchestrator
from app.core import EvidenceGate, QuestionParser
from app.models import (
    Evidence,
    EvidencePool,
    ModelResult,
    OptionVerdict,
    SolveRequest,
    Status,
    Verdict,
)


def request() -> SolveRequest:
    return SolveRequest(question="下列说法正确的是", options={"A": "claim A"})


def direct_evidence() -> EvidencePool:
    return EvidencePool(
        evidence=[
            Evidence(
                evidence_id="e-1",
                claim_id="claim_A",
                stance="support",
                source_type="official",
                title="Primary source",
                url="https://example.test/source",
                source_name="Example authority",
                quote_or_fact="A direct, quoted fact.",
                direct_match=True,
                reliability_tier=1,
            )
        ]
    )


@pytest.mark.asyncio
async def test_model_results_reference_evidence_ids_but_cannot_contain_evidence_records():
    """An analyst may cite an ID, but the EvidencePool owns source content."""
    parsed = QuestionParser().parse(request())
    pool = direct_evidence()

    result = await EvidenceOnlyAnalyst("primary_solver").analyze(parsed, pool)

    assert "evidence" not in ModelResult.model_fields
    assert result.option_verdicts["A"].evidence_refs == ["e-1"]
    assert pool.evidence[0].url not in str(result.model_dump())
    assert pool.evidence[0].quote_or_fact not in str(result.model_dump())


@pytest.mark.asyncio
async def test_independent_core_roles_are_started_in_parallel(monkeypatch):
    """A blocked role must not prevent the other independent roles from starting."""
    parsed = QuestionParser().parse(request())
    pool = EvidencePool()
    all_started = asyncio.Event()
    release = asyncio.Event()
    started: set[str] = set()

    async def controlled_analyze(self, _parsed, _pool):
        started.add(self.role)
        if len(started) == 3:
            all_started.set()
        await release.wait()
        return ModelResult(agent_role=self.role)

    monkeypatch.setattr(EvidenceOnlyAnalyst, "analyze", controlled_analyze)
    task = asyncio.create_task(MultiModelOrchestrator().independent(parsed, pool))

    await asyncio.wait_for(all_started.wait(), timeout=0.25)
    release.set()
    results = await task

    assert started == {"primary_solver", "independent_critic", "search_verifier"}
    assert set(results) == started


def test_missing_orchestration_verdicts_fall_back_to_a_conservative_gate_result():
    """An external runner can submit empty results after failure without a pass."""
    parsed = QuestionParser().parse(request())

    status, grade, _reason = EvidenceGate().assess(parsed, EvidencePool(), {})

    assert status is Status.NEEDS_VERIFICATION
    assert grade == "U"


class _NoEvidenceResearchAgent:
    async def research(self, _parsed, _plans, _budget):
        return EvidencePool(), [], None


@pytest.mark.asyncio
async def test_final_solve_uses_primary_result_instead_of_a_majority_vote(monkeypatch):
    """Two dissenting roles cannot overrule the designated primary verdict."""
    class ControlledOrchestrator:
        async def independent(self, _parsed, _pool):
            return {
                "primary_solver": ModelResult(
                    agent_role="primary_solver",
                    option_verdicts={"A": OptionVerdict(verdict=Verdict.TRUE)},
                ),
                "independent_critic": ModelResult(
                    agent_role="independent_critic",
                    option_verdicts={"A": OptionVerdict(verdict=Verdict.FALSE)},
                ),
                "search_verifier": ModelResult(
                    agent_role="search_verifier",
                    option_verdicts={"A": OptionVerdict(verdict=Verdict.FALSE)},
                ),
            }

        async def red_team(self, _parsed, _pool):
            return ModelResult(
                agent_role="red_team",
                option_verdicts={"A": OptionVerdict(verdict=Verdict.FALSE)},
            )

    monkeypatch.setattr(main, "BrowserResearchAgent", _NoEvidenceResearchAgent)
    monkeypatch.setattr(main, "MultiModelOrchestrator", ControlledOrchestrator)

    response = await main.solve(request())

    assert response.option_verdicts["A"].verdict is Verdict.TRUE
    assert response.model_results["independent_critic"].option_verdicts["A"].verdict is Verdict.FALSE
    assert response.model_results["search_verifier"].option_verdicts["A"].verdict is Verdict.FALSE
    assert response.status is Status.NEEDS_VERIFICATION


@pytest.mark.asyncio
async def test_red_team_result_is_reported_but_has_no_vote_effect(monkeypatch):
    """A red-team challenge is visible separately and cannot change the answer."""
    class ControlledOrchestrator:
        async def independent(self, _parsed, _pool):
            return {
                role: ModelResult(
                    agent_role=role,
                    option_verdicts={"A": OptionVerdict(verdict=Verdict.FALSE)},
                )
                for role in ("primary_solver", "independent_critic", "search_verifier")
            }

        async def red_team(self, _parsed, _pool):
            return ModelResult(
                agent_role="red_team",
                option_verdicts={"A": OptionVerdict(verdict=Verdict.TRUE)},
            )

    monkeypatch.setattr(main, "BrowserResearchAgent", _NoEvidenceResearchAgent)
    monkeypatch.setattr(main, "MultiModelOrchestrator", ControlledOrchestrator)

    response = await main.solve(request())

    assert response.red_team is not None
    assert response.red_team.option_verdicts["A"].verdict is Verdict.TRUE
    assert response.option_verdicts["A"].verdict is Verdict.FALSE
    assert response.answer == []
