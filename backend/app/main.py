from time import perf_counter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import *
from .core import QuestionParser,QueryPlanner,EvidenceGate
from .research import BrowserResearchAgent
from .agents import MultiModelOrchestrator
from .formal import FormalMathVerifier
app=FastAPI(title="AI Information Literacy Research Agent",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_methods=["*"],allow_headers=["*"])
async def solve(request):
 start=perf_counter();parsed=QuestionParser().parse(request);pool=FormalMathVerifier().evidence_pool(request.question,parsed.claims);trace=[];blocked=None
 if pool is None:pool,trace,blocked=await BrowserResearchAgent().research(parsed,QueryPlanner().plan(parsed),8)
 models=await MultiModelOrchestrator().independent(parsed,pool);verdicts=models["primary_solver"].option_verdicts;status,grade,_=EvidenceGate().assess(parsed,pool,verdicts);red=None
 if blocked:status=blocked;grade="U"
 if status in (Status.CONFLICT,Status.NEED_MORE_SEARCH,Status.NEEDS_VERIFICATION) or parsed.requires_counterexample_check:red=await MultiModelOrchestrator().red_team(parsed,pool)
 expected=Verdict.FALSE if parsed.polarity==Polarity.NEGATIVE else Verdict.TRUE
 return SolveResponse(answer=[key for key,v in verdicts.items() if v.verdict==expected],status=status,execution_mode="ESCALATED" if red else "FAST",evidence_grade=grade,route=parsed.suggested_routes,polarity=parsed.polarity,traps=parsed.traps,option_verdicts=verdicts,key_evidence=pool.evidence[:8],sources=list(dict.fromkeys(e.url for e in pool.evidence)),model_results=models,red_team=red,search_trace=trace,browser_trace=trace,latency_ms=round((perf_counter()-start)*1000))
@app.post("/api/solve",response_model=SolveResponse)
async def api_solve(request:SolveRequest):return await solve(request)
@app.post("/api/analyze")
async def analyze(request:SolveRequest):return QuestionParser().parse(request)
@app.post("/api/search")
async def search(request:SolveRequest):
 parsed=QuestionParser().parse(request);return {"routes":parsed.suggested_routes,"queries":QueryPlanner().plan(parsed)}
@app.post("/api/verify")
async def verify(request:SolveRequest):return await solve(request)
@app.post("/api/resume")
async def resume(request:SolveRequest):return await solve(request)
@app.get("/health")
async def health():return {"ok":True,"profile":".browser-profile","analysis_runtime":"local_evidence_only","codex_hosted_subagents":"requires an external CodexRoleRunner adapter"}
