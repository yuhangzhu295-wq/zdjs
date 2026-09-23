import re,uuid
from abc import ABC,abstractmethod
from pathlib import Path
from urllib.parse import quote_plus,urlparse
import httpx
from .models import *
class ResearchSkill(ABC):
 @abstractmethod
 def can_handle(self,route):...
 @abstractmethod
 async def execute(self,queries,claim,trace):...
class GenericWebResearchSkill(ResearchSkill):
 def can_handle(self,route):return route in (Route.MULTI_SOURCE,Route.GENERAL_WEB,Route.OFFICIAL_WEB,Route.PRODUCT_OFFICIAL)
 async def execute(self,queries,claim,trace):
  out=[]
  async with httpx.AsyncClient(follow_redirects=True,timeout=10,headers={"User-Agent":"AI-Information-Literacy-Research/1.0"}) as client:
   for query in queries:
    search="https://www.google.com/search?q="+quote_plus(query)
    try:
     result=await client.get(search);trace.append(TraceEvent(action="SEARCH",domain="google.com",url=search,result=str(result.status_code)))
     for link in [x.replace("&amp;","&") for x in re.findall(r'href="(https?://[^" ]+)',result.text) if "google." not in x][:2]:
      try:
       page=await client.get(link);text=" ".join(page.text.replace("<"," <").split())[:2000];host=urlparse(str(page.url)).netloc;tier=1 if host.endswith(".gov.cn") or host.endswith(".edu.cn") else 3
       out.append(Evidence(evidence_id="ev_"+uuid.uuid4().hex[:10],claim_id=claim.claim_id,source_type="official_web" if tier==1 else "web_page",title=host,url=str(page.url),source_name=host,snippet=text[:350],quote_or_fact=text[:700],direct_match=True,reliability_tier=tier));trace.append(TraceEvent(action="OPEN_RESULT",domain=host,url=str(page.url),result="extracted"))
      except httpx.HTTPError:pass
    except httpx.HTTPError:trace.append(TraceEvent(action="SEARCH",domain="google.com",url=search,result="network_failure"))
  return out
class CNKISkill(ResearchSkill):
 def can_handle(self,route):return route==Route.CNKI
 async def execute(self,queries,claim,trace):trace.append(TraceEvent(action="OPEN_CNKI",domain="cnki.net",url="https://www.cnki.net",result="browser_session_required"));return []
class BrowserResearchAgent:
 def __init__(self,profile_dir=".browser-profile"):
  self.profile_dir=Path(profile_dir);self.profile_dir.mkdir(parents=True,exist_ok=True);self.skills=[CNKISkill(),GenericWebResearchSkill()]
 async def research(self,p,plans,budget=8):
  trace=[];pool=EvidencePool()
  if Route.CNKI in p.suggested_routes:trace.append(TraceEvent(action="AUTH_CHECK",domain="cnki.net",result="LOGIN_REQUIRED_OR_ATTACH_CDP"));return pool,trace,Status.MANUAL_ACTION_REQUIRED
  skill=next(s for s in self.skills if s.can_handle(p.suggested_routes[0]))
  for claim in p.claims:
   queries=plans.get(claim.claim_id,[])[:budget]
   pool.evidence.extend(await skill.execute(queries,claim,trace));budget-=len(queries)
   if budget<=0:break
  return pool,trace,None
