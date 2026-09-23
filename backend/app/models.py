from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field

class QuestionType(StrEnum): SINGLE="single_choice"; MULTIPLE="multiple_choice"; TRUE_FALSE="true_false"; UNKNOWN="unknown"
class Polarity(StrEnum): POSITIVE="positive"; NEGATIVE="negative"
class Verdict(StrEnum): TRUE="TRUE"; FALSE="FALSE"; UNKNOWN="UNKNOWN"; CONFLICT="CONFLICT"
class Status(StrEnum): ANALYZING="ANALYZING"; SEARCHING="SEARCHING"; VERIFYING="VERIFYING"; RED_TEAM="RED_TEAM"; VERIFIED="VERIFIED"; NEED_MORE_SEARCH="NEED_MORE_SEARCH"; NEEDS_VERIFICATION="NEEDS_VERIFICATION"; CONFLICT="CONFLICT"; MANUAL_ACTION_REQUIRED="MANUAL_ACTION_REQUIRED"; FAILED="FAILED"
class Route(StrEnum): CNKI="CNKI"; OFFICIAL_WEB="OFFICIAL_WEB"; SCHOLARLY_WEB="SCHOLARLY_WEB"; PRODUCT_OFFICIAL="PRODUCT_OFFICIAL"; GENERAL_WEB="GENERAL_WEB"; INFORMATION_LITERACY_DB="INFORMATION_LITERACY_DB"; AI_LITERACY_DB="AI_LITERACY_DB"; MULTI_SOURCE="MULTI_SOURCE"
class SolveRequest(BaseModel): question:str; type:QuestionType=QuestionType.UNKNOWN; options:dict[str,str]=Field(default_factory=dict)
class Claim(BaseModel): claim_id:str; option:str; text:str
class ParsedQuestion(BaseModel):
 question_type:QuestionType; polarity:Polarity; domain:str; original_question:str=""; entities:list[str]=[]; keywords:list[str]=[]; years:list[int]=[]; dynamic:bool=False; target:str|None=None; traps:list[str]=[]; requires_counterexample_check:bool=False; claims:list[Claim]=[]; suggested_routes:list[Route]=[]
class Evidence(BaseModel):
 evidence_id:str; claim_id:str|None=None; stance:str="neutral"; source_type:str; title:str; url:str; source_name:str; snippet:str=""; quote_or_fact:str=""; retrieved_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc)); published_at:str|None=None; dynamic:bool=False; direct_match:bool=False; database:str|None=None; fields:dict[str,Any]=Field(default_factory=dict); reliability_tier:int=5; browser_trace_id:str|None=None
class EvidencePool(BaseModel):
 evidence:list[Evidence]=Field(default_factory=list)
 def for_claim(self,claim_id:str): return [e for e in self.evidence if e.claim_id in (None,claim_id)]
class OptionVerdict(BaseModel): verdict:Verdict; evidence_refs:list[str]=[]; rationale:str=""
class ModelResult(BaseModel): agent_role:str; option_verdicts:dict[str,OptionVerdict]={}; reasoning_summary:str=""; uncertainties:list[str]=[]; missing_evidence:list[str]=[]; requested_searches:list[str]=[]
class TraceEvent(BaseModel): timestamp:datetime=Field(default_factory=lambda:datetime.now(timezone.utc)); action:str; domain:str=""; page_title:str=""; url:str=""; result:str=""
class SolveResponse(BaseModel):
 answer:list[str]=[]; status:Status; execution_mode:str; evidence_grade:str; route:list[Route]; polarity:Polarity; traps:list[str]=[]; option_verdicts:dict[str,OptionVerdict]={}; key_evidence:list[Evidence]=[]; sources:list[str]=[]; model_results:dict[str,ModelResult]={}; red_team:ModelResult|None=None; search_trace:list[TraceEvent]=[]; browser_trace:list[TraceEvent]=[]; latency_ms:int
