# 引擎 C · 自我批判迭代引擎（Self-Critique Iteration）——「打磨问题意识」

> 本文档由 C·引擎部产出，是「创意分身」三引擎中的**第三引擎 / 终端引擎**，也是输出前的**质量闸门**。
> 定位：AI 切换为**严苛审稿人**人格，对引擎 B 的每个候选逐题挑毛病、按 6 条硬约束裁决，不达标就修改或淘汰，迭代 2–3 轮，确保输出的是「具体可回答的问题」而不是「宽泛主题」。
> 流水线总览见 [`engine_saturation_scan.md`](./engine_saturation_scan.md) 第 0 节；裁决依据见 [`bad_topic_blacklist.md`](./bad_topic_blacklist.md)；通过后格式见 [`output_template.md`](./output_template.md)。

---

## 1. 引擎目标

| 项 | 内容 |
|----|------|
| 一句话目标 | 在选题交付给用户前，先由一个「以拒稿为乐、只认硬标准」的审稿人，把每个题从标题到方法拷问一遍，直到挑不出实质毛病。 |
| 解决的竞品缺陷 | 「重新颖，轻严谨」——看似新颖却逻辑断裂、大而空、落不了地（PRD 2.3）。 |
| 核心产出 | ① 逐题审稿结论 `verdicts[]`（含每轮问题与精修）；② 通过闸门的候选集 `final_candidates[]`；③ 需回灌引擎 B 的修改意见 `reloop_request`（如有）。 |
| 不做什么 | 不凭空新增与用户画像无关的方向；不放宽闸门凑数；不直接做四要素排版（交给 formatter）。 |
| 机制溯源 | 直接落地 Anthropic **Evaluator-Optimizer 模式**（生成器与评估器分离、按明确标准循环到达标或达上限）与 **adversarial-review**（换新鲜视角批判，直到「只剩吹毛求疵」）；并借 OpenAI Deep Research 的「可随时纠偏」思想，形成回灌循环。 |

---

## 2. 上下游数据契约

```
引擎 B 输出 candidates[]（每个含 why_link / method_hint）
              │
              ▼
 ┌──────────────────────────────────────────────┐
 │ 引擎 C：审稿人按 6 条硬约束 + 黑名单 5 类逐条裁决 │
 │   每轮：判定 → 精修 → 再判（默认 2–3 轮）         │
 │   质量闸门：pass_all（6 条全过才放行）            │
 └──────────────────────────────────────────────┘
   │ 通过                        │ 不通过 / 数量不足
   ▼                             ▼
final_candidates[]        reloop_request（逐题 issues）
   │                             │ 回灌引擎 B 调整碰撞域
   ▼                             └──────────────► 外层总循环 ≤3 轮
Step 5 formatter 输出四要素
```

**输入（JSON）**：

```json
{
  "scene_config": {
    "scene_id": "academic_paper",
    "tone_rules": { "base_tone": "严肃学术", "allow_humor": false },
    "constraint_list": ["…"],
    "exclusion_rules": ["…"]
  },
  "candidates": [
    {
      "candidate_id": "cand_1",
      "title": "《从<文明>系列游戏看大众对罗马帝国的认知偏差——以某高校30名非历史专业本科生为例》",
      "question": "《文明》系列对罗马帝国的呈现使玩家形成了哪些认知偏差？",
      "object": "《文明》系列罗马文明设定 + 非历史专业玩家",
      "method_hint": "游戏文本分析 + 玩家问卷/访谈",
      "why_link": "同对象在史书与游戏中呈现差异可比较、可证伪",
      "fills_gap": null
    }
  ],
  "profile_snapshot": {
    "base": { "resources": ["学校图书馆数据库", "每周 12 小时"] }
  },
  "critique_settings": {
    "rounds": 2,
    "quality_gate": "pass_all",
    "target_count": 5,
    "max_outer_loops": 3
  }
}
```

---

## 3. 工作流程

### 3.1 第一步：切换「严苛审稿人」人格

进入审稿模式后，**默认每篇都想拒稿**，由证据说服自己放行。审稿人只对题目本身负责，不照顾作者（模型自己）的面子，也不堆客套。

对每个候选，先抛出 PRD 规定的 **5 个尖锐问题**：

1. 这个题目是不是**太大了**？能不能再缩小到一个具体对象 / 个案？
2. 这个问题真的有**增量**吗？别人没说过吗？换掉热词还剩什么？
3. 以用户的资源 / 能力 / 周期，**真的做得出来**吗？
4. 这是个**假问题**吗？它**能不能被证据证伪**？
5. 它的**语气分寸**符合当前场景吗（严肃场不油、轻松场不端）？

### 3.2 第二步：按审稿清单 6 条硬约束逐条判定

这是 PRD 锁定的 **6 条硬约束（checklist）**，逐条给「通过 / 不通过 + 具体理由」，不得笼统打分：

| # | 硬约束 | 通过的判据 | 不通过的典型表现 |
|---|--------|------------|------------------|
| C1 | ✅ 有具体研究对象 | 对象可识别、可观测、有边界（含个案/人群/平台/时间） | 「短视频」「青年」「中西文化」等无边界大词 |
| C2 | ✅ 有明确的问题（不是主题） | 是可回答、**可证伪**的问句，且不是假问题 | 「关于…的研究」「浅谈…」；问题预设不成立 |
| C3 | ✅ 有可操作的研究方法 | 方法写得清、与问题匹配、材料可得 | 只写「综合分析」；方法与问题脱节 |
| C4 | ✅ 在用户能力/资源范围内 | 与 `resources`、层级、周期匹配，无不可得数据/技术 | 无数据集/无技术却要做大型系统（黑名单不可落地） |
| C5 | ✅ 不是烂大街的方向 | 有新对象/新视角/新方法/新证据，且不在引擎 A 饱和清单 | 与 saturated_topics 同构、纯综述无增量 |
| C6 | ✅ 符合场景态度基调 | 符合 tone_rules；幽默只服务表达、不削弱证据 | 严肃场玩梗、轻松场端架子；幽默越合规红线 |

> **可证伪性 / 假问题**审查显式落在 C2（问题成立且可被证据推翻）与 C5（增量真实），并由黑名单「假问题型」一票否决兜底。

### 3.3 第三步：黑名单 5 类一票否决复核

无论清单表现如何，再对照 [`bad_topic_blacklist.md`](./bad_topic_blacklist.md) 逐类排查；命中任一即判**不通过**，并在 `fatal_flaw` 中标注类型：

1. **概念堆砌型**：热词拼接、抽掉热词问题不成立（C2/C5）；
2. **过度饱和型**：与饱和清单同构、无新角度新方法（C5）；
3. **无法落地型**：超出能力/资源/数据/技术（C4）；
4. **范围过大型**：边界模糊、规定篇幅装不下（C1/C2）；
5. **假问题型**：问题不成立、无法证伪、无研究价值（C2）。

### 3.4 第四步：据意见精修并迭代

对未通过但**有救**的候选，给出可直接替换的精修（`refined`）：缩小对象、补足限定、把主题改成问句、替换为可行方法、删除热词、调整语气。然后进入下一轮重判。

**迭代轮次**：`critique_settings.rounds`（默认 2，可配 1–3）。

- 每轮只针对上一轮 `issues` 复核；
- **无救候选**（命中假问题/概念堆砌且无法通过修改挽救）直接淘汰，不再占用轮次；
- 精修后重新走 3.2–3.3，防止「修了 A 又坏 B」。

### 3.5 第五步：质量闸门裁决

- `pass_all`（默认）：**6 条全部通过 + 无黑名单命中**才进入 `final_candidates`。
- `pass_majority`（仅宽松场景可配）：6 条中 ≥5 条通过且无致命黑名单命中即可；但 C2（假问题/可证伪）与 C4（可落地）**始终为必过项**。

### 3.6 第六步：数量不足则回灌引擎 B

- 若 `final_candidates` 数量 < `target_count`：把每个落选/淘汰候选的具体 `issues` 汇总成 `reloop_request`，**回灌引擎 B**（建议调整碰撞域、换算子、放宽/收紧关联、优先填缺口）后重新生成，再回到引擎 C。
- **外层总循环不超过 `max_outer_loops`（默认 3）**。
- 仍不足时：输出全部通过候选，并在报告中如实说明「合格候选仅 N 个，未凑数」，**绝不降闸门放水**。

---

## 4. 迭代终止条件

满足任一即终止本引擎：

1. **达标终止**：`final_candidates` 满足 `target_count` 且全部通过闸门；
2. **轮次上限终止**：达到 `rounds`（内层）与 `max_outer_loops`（外层）后，只保留通过者，其余淘汰；
3. **吹毛求疵终止（nitpick rule）**：某轮候选的所有 `issues` 都只是措辞/排版级润色、不影响问题成立性、可证伪性与可行性时，可提前判通过（源自 Anthropic adversarial-review 的停止准则「until only nitpicks remain」）。

> 禁止以「差不多行了」「应该可以」作为终止理由；终止必须能对应到上述三条之一。

---

## 5. 输出契约（交给 Step 5）

```json
{
  "engine": "self_critique",
  "finished_at": "2026-10-13T08:30:00+00:00",
  "rounds_run": 2,
  "outer_loops": 1,
  "verdicts": [
    {
      "candidate_id": "cand_1",
      "final_verdict": "pass",
      "fatal_flaw": null,
      "checklist": [
        { "item": "C1", "pass": true, "note": "对象明确：《文明》罗马设定 + 30名非历史专业学生" },
        { "item": "C2", "pass": true, "note": "问题可回答、可证伪，非假问题" },
        { "item": "C3", "pass": true, "note": "文本分析+问卷访谈，材料可得" },
        { "item": "C4", "pass": true, "note": "问卷样本与游戏文本在资源范围内" },
        { "item": "C5", "pass": true, "note": "游戏媒介视角有增量，非饱和方向" },
        { "item": "C6", "pass": true, "note": "符合公选课允许的趣味基调" }
      ],
      "refined": null
    },
    {
      "candidate_id": "cand_2",
      "final_verdict": "reject",
      "fatal_flaw": "concept_stack",
      "checklist": [
        { "item": "C2", "pass": false, "note": "抽掉热词后问题不成立" },
        { "item": "C5", "pass": false, "note": "无真实增量" }
      ],
      "refined": null
    }
  ],
  "final_candidates": [
    {
      "candidate_id": "cand_1",
      "title": "《从<文明>系列游戏看大众对罗马帝国的认知偏差——以某高校30名非历史专业本科生为例》",
      "question": "《文明》系列对罗马帝国的呈现使玩家形成了哪些认知偏差？",
      "object": "《文明》系列罗马文明设定 + 非历史专业玩家",
      "method_hint": "游戏文本分析 + 玩家问卷/访谈",
      "passed_checklist": ["C1", "C2", "C3", "C4", "C5", "C6"]
    }
  ],
  "reloop_request": {
    "needed": true,
    "shortfall": 4,
    "instructions": [
      "已用游戏媒介方向，请换碰撞域或算子（如机制类比/方法移植）",
      "优先填 gaps 中的方向，避免再次产出热词拼接"
    ]
  }
}
```

| 输出字段 | 类型 | 去向 |
|----------|------|------|
| `verdicts[]` | array | 审稿留痕，供 F 部断言与问题追溯 |
| `final_candidates[]` | array | **→ Step 5 formatter** 按四要素输出 |
| `reloop_request` | object | 数量不足时 **→ 引擎 B** 重新碰撞 |

---

## 6. 可直接执行的 Prompt

### 6.1 系统提示词（System Prompt）

```text
# 角色
你是「创意分身」的【引擎 C · 严苛审稿人】。你以拒稿为天职，只认硬标准；任何选题必须先过你这一关。你不照顾作者情绪，也不堆砌客套，但对事不对人，不得出现侮辱或歧视性表达。

# 你会收到的输入
- scene_config：tone_rules、constraint_list、exclusion_rules
- candidates：引擎 B 的候选（每个含 title、question、object、method_hint、why_link、fills_gap）
- profile_snapshot：用户 resources（用于可行性裁决）
- critique_settings：rounds、quality_gate、target_count、max_outer_loops

# 审稿流程（对每个候选执行）
1. 先问 5 个尖锐问题：题目太大吗？有真实增量吗？用户真做得出来吗？是假问题/能证伪吗？语气分寸对吗？
2. 按 6 条硬约束逐条判定 pass/fail 并写具体理由：
   C1 有具体研究对象；C2 有明确问题且可证伪、非假问题；C3 有可操作且匹配的方法；
   C4 在用户能力/资源/周期内；C5 非烂大街、有增量、不在饱和清单；C6 符合场景基调。
3. 黑名单复核：对照 5 类（概念堆砌/过度饱和/无法落地/范围过大/假问题），命中任一即 fatal_flaw 并 reject。
4. 精修：对有救候选给出可直接替换的 refined（缩小对象、补限定、主题改问句、换可行方法、删热词、调语气）；无救者直接淘汰。
5. 迭代：按 rounds（默认 2，最多 3）对 issues 复核，每轮重新走判定，防止改一处坏一处。
6. 闸门：
   - pass_all：6 条全过且无黑名单命中才进 final_candidates；
   - pass_majority：仅当配置允许时，≥5 条通过且 C2、C4 必过；
   - 不允许「差不多/应该可以」式放行。
7. 回灌：若通过者少于 target_count，生成 reloop_request（逐题具体问题 + 调整建议）回引擎 B，
   外层总循环不超过 max_outer_loops；仍不足则输出全部并说明「合格仅 N 个，未凑数」。

# 提前通过规则
某候选的剩余问题全部仅为措辞/排版级 nitpick，且不影响问题成立性、可证伪性、可行性时，可提前判通过，并注明 nitpick。

# 输出格式（只返回 JSON）
{
  "engine": "self_critique",
  "finished_at": "ISO8601",
  "rounds_run": 0,
  "outer_loops": 1,
  "verdicts": [
    {
      "candidate_id": "cand_1",
      "final_verdict": "pass|reject",
      "fatal_flaw": "concept_stack|over_saturated|infeasible|too_broad|false_question|null",
      "checklist": [{ "item": "C1", "pass": true, "note": "" }],
      "refined": { "title": "", "question": "", "method_hint": "" }
    }
  ],
  "final_candidates": [
    {
      "candidate_id": "cand_1",
      "title": "",
      "question": "",
      "object": "",
      "method_hint": "",
      "passed_checklist": ["C1", "C2", "C3", "C4", "C5", "C6"]
    }
  ],
  "reloop_request": { "needed": false, "shortfall": 0, "instructions": [] }
}
```

### 6.2 用户输入模板（User Message Template）

```text
请对候选选题执行自我批判审稿。

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[candidates]
{粘贴引擎 B 输出的 candidates JSON，或逐条列出 title/question/object/method_hint/why_link}

[profile_snapshot]
resources: {resources}

[critique_settings]
rounds: {默认 2，1–3}
quality_gate: {pass_all | pass_majority}
target_count: {如 5}
max_outer_loops: {默认 3}
```

---

## 7. 审稿示例（精修前后对比）

### 7.1 由「宽泛主题」精修为「具体问题」

- 初稿：《游戏对历史认知的影响研究》
- 审稿意见：
  - C1 不通过：对象无边界（什么游戏？谁的认知？）；
  - C2 不通过：是主题不是问题，无法证伪；
  - C5 待确认：需说明相对既有研究的增量。
- 精修后：

  《从〈文明〉系列游戏看大众对罗马帝国的认知偏差——以某高校 30 名非历史专业本科生为例》

  → 限定了游戏、对象帝国、人群与样本，问题变为可观测、可证伪；方法与资源匹配；二轮通过。

### 7.2 直接淘汰（命中黑名单）

- 候选：《元宇宙背景下大模型赋能罗马史教学的路径研究》
- 裁决：C2、C5 不通过；`fatal_flaw = concept_stack`，**reject**。
- 理由：抽掉「元宇宙/大模型/赋能/路径」后问题不成立，无共享对象/机制，无真实增量。

### 7.3 因不可落地淘汰

- 候选：《基于多模态大模型的敦煌壁画自动修复系统研究》（作者：本科生，无技术、无数据集）
- 裁决：C4 不通过；`fatal_flaw = infeasible`，**reject**。
- 若缩小为可行版本（如《敦煌壁画数字图像公开数据集的现状与教学可用性梳理》）可重新提交。

---

## 8. 验收对照

- [x] 引擎目标与终端闸门位置明确
- [x] 提供审稿人系统提示词 + 用户输入模板，可直接执行
- [x] **审稿标准 6 条硬约束齐全**（PRD 五条问题 + 六清单）
- [x] 黑名单 5 类一票否决复核
- [x] 迭代 2–3 轮，含三条明确终止条件（含 nitpick 规则）
- [x] 质量闸门 pass_all / pass_majority，C2/C4 始终必过
- [x] 数量不足回灌引擎 B，外层循环 ≤3，不凑数
- [x] 输出含 `verdicts / final_candidates / reloop_request`，与架构第 8.3 契约一致
