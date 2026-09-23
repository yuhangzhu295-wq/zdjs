# State Machine（contest-runner）

## 状态

```
DETECT_CURRENT_QUESTION   识别当前页面是否含题目、题号
READ                      提取 question_number / question_text / question_type / options
PARSE                     调用 question-router 解析题型/极性/风险/路由
ROUTE                     得到 route 与 search_targets
RESEARCH                  调用 research Skill 收集 Evidence
VERIFY                    协议校验（evidence id、AgentResult）
EVIDENCE_GATE             调用 evidence-judge 得到 Gate 结果
SELECT                    回答题页选择答案
VERIFY_SELECTION          重读页面，确认 actual_selected == expected_selected
NEXT                      点击下一题
WAIT_FOR_NEW_QUESTION     等待 question_hash 变化
```

## 循环伪代码

```
while contest_active:
    q = read_question()
    h = question_hash(q)
    if h in processed:
        recover_navigation(); continue
    parsed = route(q)
    evidence = research(route, parsed, claims)      # 每题只检索一次
    decision = evidence_gate(parsed, evidence, models)
    if decision == NEED_MORE_SEARCH: evidence += research_again(search_requests)
    if decision == ESCALATE: decision = critic_or_verifier(...)
    if decision == CONFLICT: red_team(...)
    answer = answer_composer(parsed, verdicts)
    if decision == PASS and answer VERIFIED:
        select(answer); verify_selection(); next()
    elif MANUAL_REQUIRED:
        pause()
    else:
        stop_or_escalate()
```

## 去重

`question_hash = SHA256(normalized_question + normalized_options)`。
已处理集合记录 question_hash / answer / status / timestamp；命中则不得重复作答。

## 默认配置

- auto_select = true
- auto_next = true
- auto_final_submit = false（最终提交默认关闭，须显式打开）

## Escalation

- MAX_ESCALATION_ROUNDS = 2，超过 → NEEDS_VERIFICATION。
