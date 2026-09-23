import re
from .models import *
NEGATIVE=("不正确","错误的是","不属于","不能说明","未体现","没有","不符合")
ABSOLUTE=("全部","所有","任何","唯一","必须","一定","绝不","从不","完全","只能")
DYNAMIC=("截至","当前","最新","现有","目前","多少篇","被引","下载","排名")
CNKI=("CNKI","中国知网","篇名","主题","作者","关键词","期刊","学位论文","被引","下载","参考文献","高级检索","专业检索")
OFFICIAL=("国务院","教育部","法律","法规","标准","政府统计","政策","国家机构")
PRODUCT=("当前支持模型","产品菜单","产品能力","当前功能")
class AntiMisleadingAnalyzer:
 def analyze(self,text):
  traps=[]
  if any(w in text for w in NEGATIVE):traps.append("NEGATION")
  if sum(w in text for w in ("不","没有","不能"))>=2:traps.append("DOUBLE_NEGATION")
  absolute=any(w in text for w in ABSOLUTE)
  if absolute:traps.append("ABSOLUTE_WORDING")
  if any(w in text for w in ("导致","因为","因此","相关")):traps.append("CAUSE_CORRELATION")
  if any(w in text for w in ("部分","有些","之一","可能")):traps.append("PARTIAL_TRUTH")
  return traps,absolute
class SearchRouter:
 def route(self,text):
  if any(x.lower() in text.lower() for x in CNKI):return [Route.CNKI]
  if any(x in text for x in OFFICIAL):return [Route.OFFICIAL_WEB]
  if any(x in text for x in PRODUCT):return [Route.PRODUCT_OFFICIAL]
  return [Route.MULTI_SOURCE]
class QuestionParser:
 def parse(self,r):
  text=" ".join([r.question,*r.options.values()]);traps,counter=AntiMisleadingAnalyzer().analyze(text)
  pol=Polarity.NEGATIVE if any(w in r.question for w in NEGATIVE) else Polarity.POSITIVE
  years=[int(x) for x in re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)",text)]
  qtype=r.type if r.type!=QuestionType.UNKNOWN else (QuestionType.MULTIPLE if "多选" in r.question else QuestionType.SINGLE)
  claims=[Claim(claim_id="claim_"+key,option=key,text=value) for key,value in r.options.items()]
  target=next((name for name,word in (("CITATION_COUNT","被引"),("DOWNLOAD_COUNT","下载"),("RESULT_COUNT","数量"),("COAUTHOR","合作者")) if word in text),None)
  keywords=list(dict.fromkeys(re.findall(r"[A-Za-z]{2,}|[\u4e00-\u9fff]{2,}",text)))[:12]
  return ParsedQuestion(question_type=qtype,polarity=pol,domain="information_literacy",original_question=r.question,keywords=keywords,years=years,dynamic=any(w in text for w in DYNAMIC),target=target,traps=traps,requires_counterexample_check=counter,claims=claims,suggested_routes=SearchRouter().route(text))
class QueryPlanner:
 def plan(self,p):
  plans={}
  for c in p.claims:
   if Route.CNKI in p.suggested_routes:plans[c.claim_id]=[c.text+" site:cnki.net",c.text+" 中国知网",c.text+" 被引 下载"]
   elif Route.OFFICIAL_WEB in p.suggested_routes:plans[c.claim_id]=["site:gov.cn "+c.text,"site:moe.gov.cn "+c.text,c.text+" 发布时间"]
   else:plans[c.claim_id]=[c.text+" 官方",c.text+" 原始来源",c.text+" 反例"]
  return plans
class EvidenceGate:
 def assess(self,p,pool,verdicts):
  primary=[e for e in pool.evidence if e.reliability_tier<=2 and e.direct_match]
  if p.dynamic and not any(e.dynamic for e in primary):return Status.NEEDS_VERIFICATION,"U","dynamic fact lacks live primary evidence"
  if Route.CNKI in p.suggested_routes and (p.dynamic or p.target in {"RESULT_COUNT","CITATION_COUNT","DOWNLOAD_COUNT"}) and not any(e.database=="CNKI" and e.dynamic for e in pool.evidence):return Status.NEEDS_VERIFICATION,"U","CNKI live evidence required"
  if any(v.verdict in (Verdict.UNKNOWN,Verdict.CONFLICT) for v in verdicts.values()):return Status.NEED_MORE_SEARCH,"D","critical option unresolved"
  if not primary:return Status.NEEDS_VERIFICATION,"U","no direct primary evidence"
  claim_stances={}
  for evidence in pool.evidence:claim_stances.setdefault(evidence.claim_id,set()).add(evidence.stance)
  if any({"support","counter"}.issubset(stances) for stances in claim_stances.values()):return Status.CONFLICT,"X","direct evidence conflicts for one claim"
  return Status.VERIFIED,"A","direct primary evidence supports each decision"
