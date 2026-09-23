"""Tests for the Codex-hosted collaboration boundary."""

import asyncio
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.codex_bridge import (
    CodexCollaborationBridge,
    CollaborationTask,
    StructuredOutputError,
    validate_model_result,
)
from app.models import Claim, Evidence, EvidencePool


def context():
    claim = Claim(claim_id="claim_A", option="A", text="A claim")
    evidence = Evidence(
        evidence_id="ev_1", claim_id="claim_A", stance="support",
        source_type="official", title="Source", url="https://example.test",
        source_name="Authority", direct_match=True, reliability_tier=1,
    )
    task = CollaborationTask.from_context("question", [claim], EvidencePool(evidence=[evidence]))
    return claim, task


def valid_result(role: str):
    return {
        "agent_role": role,
        "option_verdicts": {
            "A": {"verdict": "TRUE", "evidence_refs": ["ev_1"], "rationale": "quoted evidence"}
        },
    }


def test_bridge_rejects_generated_evidence_or_unknown_references():
    _, task = context()
    raw = valid_result("primary_solver")
    raw["evidence"] = [{"evidence_id": "invented"}]
    with pytest.raises(StructuredOutputError):
        validate_model_result(raw, expected_role="primary_solver", task=task)

    raw = valid_result("primary_solver")
    raw["option_verdicts"]["A"]["evidence_refs"] = ["invented"]
    with pytest.raises(StructuredOutputError):
        validate_model_result(raw, expected_role="primary_solver", task=task)


@pytest.mark.asyncio
async def test_codex_bridge_parallel_roles_receive_no_peer_outputs():
    claim, _task = context()
    pool = EvidencePool(evidence=[Evidence(
        evidence_id="ev_1", claim_id="claim_A", stance="support", source_type="official",
        title="Source", url="https://example.test", source_name="Authority",
        direct_match=True, reliability_tier=1,
    )])
    entered: set[str] = set()
    released = asyncio.Event()
    all_entered = asyncio.Event()

    class Runner:
        async def invoke_role(self, *, role: str, task_json: str):
            payload = json.loads(task_json)
            assert set(payload) == {"question", "claims", "evidence"}
            assert "model_results" not in task_json
            entered.add(role)
            if len(entered) == 3:
                all_entered.set()
            await released.wait()
            return valid_result(role)

    task = asyncio.create_task(CodexCollaborationBridge(Runner()).analyze_roles(
        question="question", claims=[claim], evidence_pool=pool,
    ))
    await asyncio.wait_for(all_entered.wait(), timeout=0.25)
    released.set()
    results = await task
    assert set(results) == {"primary_solver", "independent_critic", "search_verifier"}
