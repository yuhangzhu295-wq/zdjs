import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"backend"))
from app.models import *
from app.core import QuestionParser,SearchRouter,EvidenceGate
from app.formal import FormalMathVerifier
def req(q,options={"A":"a","B":"b"},kind=QuestionType.SINGLE):return SolveRequest(question=q,options=options,type=kind)
def test_negative_question():assert QuestionParser().parse(req("以下说法中不正确的是")).polarity==Polarity.NEGATIVE
def test_double_negative():assert "DOUBLE_NEGATION" in QuestionParser().parse(req("下列没有不能说明的选项")).traps
def test_absolute_wording():
 p=QuestionParser().parse(req("所有情况必须如此"));assert p.requires_counterexample_check and "ABSOLUTE_WORDING" in p.traps
def test_dynamic_fact_detection():assert QuestionParser().parse(req("截至目前有多少篇文章")).dynamic
def test_cnki_routing():assert SearchRouter().route("中国知网被引次数")==[Route.CNKI]
def test_policy_routing():assert SearchRouter().route("教育部政策")==[Route.OFFICIAL_WEB]
def test_each_option_is_independent_claim():assert [x.claim_id for x in QuestionParser().parse(req("题",{"A":"one","B":"two","C":"three"})).claims]==["claim_A","claim_B","claim_C"]
def test_multichoice_unknown_blocks_pass():assert EvidenceGate().assess(QuestionParser().parse(req("题",kind=QuestionType.MULTIPLE)),EvidencePool(),{"A":OptionVerdict(verdict=Verdict.UNKNOWN)})[0]==Status.NEED_MORE_SEARCH
def test_llm_output_is_not_evidence():assert ModelResult(agent_role="x").model_dump().get("evidence") is None
def test_three_models_agree_without_evidence_cannot_pass():assert EvidenceGate().assess(QuestionParser().parse(req("题")),EvidencePool(),{"A":OptionVerdict(verdict=Verdict.TRUE),"B":OptionVerdict(verdict=Verdict.FALSE)})[0]==Status.NEEDS_VERIFICATION
def test_dynamic_cnki_requires_live_evidence():assert EvidenceGate().assess(QuestionParser().parse(req("CNKI 当前被引次数")),EvidencePool(),{"A":OptionVerdict(verdict=Verdict.TRUE)})[0]==Status.NEEDS_VERIFICATION
def test_formal_arithmetic_uses_deterministic_evidence():
 parsed=QuestionParser().parse(req("1加1等于多少？",{"A":"1","B":"2","C":"3","D":"4"}))
 pool=FormalMathVerifier().evidence_pool("1加1等于多少？",parsed.claims)
 assert pool is not None
 assert {e.claim_id:e.stance for e in pool.evidence}=={"claim_A":"counter","claim_B":"support","claim_C":"counter","claim_D":"counter"}
 assert all(e.source_type=="formal_verification" and e.direct_match for e in pool.evidence)
def test_formal_arithmetic_rejects_non_math_question():assert FormalMathVerifier().evaluate_question("教育部政策是什么？") is None
def test_evidence_gate_does_not_confuse_different_option_stances_as_conflict():
 parsed=QuestionParser().parse(req("题",{"A":"one","B":"two"}))
 pool=EvidencePool(evidence=[Evidence(evidence_id="a",claim_id="claim_A",stance="support",source_type="formal",title="t",url="formal://",source_name="v",direct_match=True,reliability_tier=1),Evidence(evidence_id="b",claim_id="claim_B",stance="counter",source_type="formal",title="t",url="formal://",source_name="v",direct_match=True,reliability_tier=1)])
 verdicts={"A":OptionVerdict(verdict=Verdict.TRUE),"B":OptionVerdict(verdict=Verdict.FALSE)}
 assert EvidenceGate().assess(parsed,pool,verdicts)[0]==Status.VERIFIED
