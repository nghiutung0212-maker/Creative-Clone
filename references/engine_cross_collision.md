# 引擎 B · 跨界知识碰撞引擎（Cross-Domain Collision）——「找新角度」

> 本文档由 C·引擎部产出，是「创意分身」三引擎中的**第二引擎**。
> 定位：把用户的**核心领域 A**与画像里的**兴趣领域 B、C、D**（哪怕看似无关）做结构化交叉碰撞，产生用户自己想不到、但有真实逻辑关联的**反共识角度**，并提炼成具体问题。
> 流水线总览见 [`engine_saturation_scan.md`](./engine_saturation_scan.md) 第 0 节；下游审稿见 [`engine_self_critique.md`](./engine_self_critique.md)；鉴别硬拼接见 [`bad_topic_blacklist.md`](./bad_topic_blacklist.md)。

---

## 1. 引擎目标

| 项 | 内容 |
|----|------|
| 一句话目标 | 让「历史学 + 爱玩游戏」这类**本来八竿子打不着的两块知识**，在用户脑子里撞出一个既新鲜、又能落地的具体问题。 |
| 解决的竞品缺陷 | 「重共性，轻个性」——通用模板千人一面；以及「热门关键词拼接」式的伪创新（PRD 2.3 / 2.4）。 |
| 核心产出 | ① 碰撞点清单 `collision_points[]`（每个含逻辑关联说明）；② 候选研究问题 `candidates[]`；③ 被剔除的伪拼接 `filtered_out[]`。 |
| 不做什么 | 不做无逻辑的热词拼盘（一旦发现即剔除并记录）；不做最终质量裁决（交给引擎 C）；不重复扫描饱和方向。 |
| 机制溯源 | 借鉴 Arthur Koestler「双重联想（bisociation）」与类比迁移理论；工程上借鉴 OpenAI **双层个性化**——场景配置定边界、个人画像供碰撞源；借鉴 Anthropic 多智能体「用新鲜视角强行跳出本领域框架」。 |

---

## 2. 上下游数据契约

```
引擎 A 输出                          引擎 B 处理                        引擎 C 输入
───────────                          ───────────                        ─────────
saturated_topics[] ──► 禁止域 ──┐
blacklist_hits[]   ──► 禁止域 ──┤
gaps[]             ──► 优先靶区 ─┤   A×B / A×C / A×D
scene_config       ──► 约束/基调 ─┤   结构碰撞 → 逻辑关联筛选
profile_snapshot   ──► 兴趣域 B/C/D ┘   → 提炼具体问题
                                                              ──► candidates[]
                                                                  （每个带 why_link）
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
  "scan_output": {
    "saturated_topics": ["短视频用户行为研究"],
    "gaps": ["短视频对听障青年信息获取的影响"],
    "blacklist_hits": [{ "matched_type": "over_saturated", "topic": "短视频用户行为研究" }]
  },
  "profile_snapshot": {
    "base": {
      "backgrounds": ["历史学（本科）"],
      "interests": ["电子游戏", "罗马帝国", "乐队文化"],
      "resources": ["学校图书馆数据库", "每周 12 小时"]
    }
  },
  "collide_settings": {
    "min_logic_link": "strong",
    "max_candidates": 20,
    "target_count": 5
  }
}
```

| 输入字段 | 用途 |
|----------|------|
| `scan_output.saturated_topics / blacklist_hits` | **禁止域**：碰撞结果不得落在这些方向上，否则剔除。 |
| `scan_output.gaps` | **优先靶区**：碰撞结果若能填某个缺口，优先保留。 |
| `profile_snapshot.base.backgrounds` | 核心领域 A 的来源。 |
| `profile_snapshot.base.interests` | 碰撞域 B/C/D 的来源；兴趣越多，碰撞组合越丰富。 |
| `collide_settings.min_logic_link` | 关联强度门槛（`loose`/`medium`/`strong`，默认 `strong`）。 |
| `collide_settings.max_candidates` | 碰撞池上限（默认 20），防止发散失控。 |

---

## 3. 工作流程

### 3.1 第一步：提取核心领域 A

- 从 `profile_snapshot.base.backgrounds` 与问卷学科字段确定**核心领域 A**（如「历史学 / 罗马帝国史」）。
- 明确 A 的三要素：**研究对象**（罗马帝国）、**常用理论/视角**（史料考据、社会史）、**常用方法**（文献、史料分析）。

### 3.2 第二步：提取碰撞域 B、C、D

- 从 `base.interests`、问卷兴趣字段提取**所有非本专业领域**（如「电子游戏（《文明》系列）」「乐队文化」）。
- 每个碰撞域同样拆出：**载体/对象**、**内在机制**、**可借用的方法或视角**。
- 兴趣域不足时（轻量模式画像稀疏），补充两类「近邻域」：
  - **方法论近邻**：与 A 方法可互通的领域（如历史学 ↔ 考古学、人类学）；
  - **对象近邻**：与 A 共享对象的当代载体（如历史 ↔ 影视/游戏/教科书等大众叙事媒介）。

### 3.3 第三步：结构化碰撞（A×B / A×C / A×D）

不是把两个词并排写在一起，而是用**五种碰撞算子**让两域产生真实反应。对每一对 (A, X) 依次尝试：

| 算子 | 做法 | 典型产物 |
|------|------|----------|
| ① 视角借用 | 用 X 的理论透镜重新审视 A 的对象 | 用游戏设计中的「叙事选择」机制看史书如何塑造历史宿命感 |
| ② 方法移植 | 把 X 的分析方法搬到 A | 用游戏玩家行为日志方法分析历史人物决策的「路径依赖」 |
| ③ 对象互证 | 同一对象同时出现在 A 与 X 中，比较二者呈现差异 | 罗马帝国（史书）vs 罗马帝国（《文明》游戏）→ 认知偏差 |
| ④ 机制类比 | 论证 A 与 X 存在同构机制 | 军团补给线 与 游戏资源经济 的同构（需可证伪） |
| ⑤ 媒介/受众反身 | 把 X 当作大众接触 A 的媒介来研究 | 《文明》作为大众学习罗马史的「隐性教材」 |

> 每种算子至少产出 1 个候选角度；全部组合数量受 `max_candidates` 约束。

### 3.4 第四步：逻辑关联筛选（核心防伪步骤）

对每个碰撞点，**强制写出 `why_link`（为什么二者真的有关）**，并评定关联强度：

| 强度 | 判据 | 处置 |
|------|------|------|
| `strong` | 存在可论证的**因果/同构/可验证**关系，两域共享明确对象或机制，且用户资源可支撑 | 保留（默认门槛） |
| `medium` | 有合理类比，但需要额外论证或桥接概念 | 仅当 `min_logic_link=medium/loose` 或能填补缺口时保留 |
| `loose` | 仅表面/字眼相似，无机制连接 | **剔除并写入 `filtered_out`，原因标「概念堆砌」** |

**一票否决（出现即剔除）**：

- 无法回答「为什么 A 和 X 放在一起是合理的」；
- 只是把「元宇宙 / 大模型 / 赋能 / 路径」等热词贴在 A 前面（见黑名单概念堆砌型）；
- 碰撞结果落在 `saturated_topics` / `blacklist_hits` 内且未带来新对象/新方法；
- 超出用户资源、明显不可行（留给引擎 C 复核，但明显者提前剔除）。

### 3.5 第五步：从碰撞点提炼具体研究问题

对通过筛选的碰撞点，把「角度」落成**可回答、可证伪的具体问题**：

1. **锚定具体对象**：不是「游戏与历史」，而是「《文明 VI》中罗马文明的科技树设定」。
2. **加限定词**：人群/地域/平台/时间/个案，如「中山大学 20 名历史专业本科生」。
3. **给出问题句式**：优先用「X 如何影响 Y」「A 与 B 在 Z 上有何差异」「什么因素导致 Z」等可检验句式，避免「浅谈/试论/关于…的研究」这类空壳。
4. **配方法暗示**：该问题可用什么方法回答（文本比较、问卷、实验、个案），并与 `resources` 对照。
5. **对齐缺口**：能填 `gaps` 中某条的，标注 `fills_gap`。

> 提炼结果必须是「问题」而不是「主题」；这一条由引擎 C 的审稿清单二次强制。

---

## 4. 输出契约（传给引擎 C）

```json
{
  "engine": "cross_collision",
  "generated_at": "2026-10-13T08:20:00+00:00",
  "base_domain": "历史学 / 罗马帝国史",
  "collision_points": [
    {
      "id": "cp_1",
      "a": "历史学（罗马帝国史）",
      "b": "电子游戏（《文明》系列）",
      "operator": "对象互证 / 媒介反身",
      "logic_link": "strong",
      "why_link": "《文明》系列以可交互的方式重构了罗马帝国的兴衰，是大众接触罗马史的高频媒介；同一对象在史书与游戏中的呈现差异可直接比较、可证伪。",
      "candidate_angle": "游戏作为大众历史认知的隐性教材",
      "candidate_question": "《文明》系列对罗马帝国的呈现，使非历史专业玩家形成了哪些关于罗马帝国的认知偏差？",
      "fills_gap": null,
      "resource_check": "可获取游戏文本与玩家问卷，资源可支撑"
    }
  ],
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
  "filtered_out": [
    {
      "raw": "元宇宙背景下大模型赋能罗马史教学",
      "reason": "概念堆砌：热词拼接，无机制连接，why_link 不成立"
    }
  ]
}
```

| 输出字段 | 类型 | 去向 |
|----------|------|------|
| `collision_points[]` | array | 碰撞过程留痕，供引擎 C 与 F 部核查 |
| `candidates[]` | array | **→ 引擎 C 审稿**；每个必须含 `why_link` 与 `method_hint` |
| `filtered_out[]` | array | 记录被剔除的伪拼接，供追溯与测试 |

---

## 5. 可直接执行的 Prompt

### 5.1 系统提示词（System Prompt）

```text
# 角色
你是「创意分身」的【引擎 B · 跨界知识碰撞师】，擅长把两个看似无关的知识领域焊接在一起，产生反共识但逻辑成立的新角度。你只做「有真实关联的碰撞」，极端厌恶热词拼盘。

# 你会收到的输入
- scene_config：当前场景（tone_rules、constraint_list、exclusion_rules）
- scan_output：引擎 A 的 saturated_topics、blacklist_hits（禁止域）与 gaps（优先靶区）
- profile_snapshot：用户 backgrounds（核心域）、interests（碰撞域）、resources
- collide_settings：min_logic_link、max_candidates、target_count

# 工作步骤（严格按顺序）
1. 定核心域 A：从 backgrounds 与学科字段确定 A，拆出其对象、常用视角、常用方法。
2. 定碰撞域：从 interests 提取所有非本专业领域 B/C/D；兴趣稀疏时补方法论近邻与对象近邻（如历史 ↔ 影视/游戏/教科书等大众媒介）。
3. 结构化碰撞：对每对 (A, X) 依次尝试五种算子——
   ①视角借用 ②方法移植 ③对象互证 ④机制类比 ⑤媒介/受众反身；每算子尽量产出 1 个角度，总数不超过 max_candidates。
4. 逻辑关联筛选：为每个碰撞点强制写 why_link（为什么二者真有关），并评 logic_link：
   - strong：有可论证的因果/同构/可验证关系，共享明确对象或机制；
   - medium：合理类比但需桥接；
   - loose：仅表面相似 → 剔除，写入 filtered_out，原因标「概念堆砌」。
   按 min_logic_link 门槛过滤；命中禁止域（saturated_topics/blacklist_hits）且无新对象/新方法的，剔除。
5. 提炼具体问题：把通过的角度落成可回答、可证伪的问题——
   锚定具体对象 → 加限定词（人群/地域/平台/时间/个案）→ 用「X如何影响Y/A与B在Z上有何差异」等可检验句式 → 配方法暗示并与 resources 对照 → 能填 gaps 的标 fills_gap。

# 质量红线
- 每个保留的碰撞点必须有 why_link；写不出 why_link 就是概念堆砌，一律剔除。
- 禁止把「元宇宙/大模型/赋能/路径/生态」等热词直接贴在 A 前面充当创新。
- 产出单位是「问题」不是「主题」；标题中必须出现具体对象与限定词。
- 不得伪造用户资源、数据可得性或方法可行性；不确定的标「待验证」，交引擎 C。
- 严格遵守场景基调（tone_rules）：严肃场景不玩梗，轻松场景不端架子；但任何场景都不得突破法律与平台合规。

# 输出格式（只返回 JSON）
{
  "engine": "cross_collision",
  "generated_at": "ISO8601",
  "base_domain": "",
  "collision_points": [
    {
      "id": "cp_1",
      "a": "",
      "b": "",
      "operator": "视角借用|方法移植|对象互证|机制类比|媒介反身",
      "logic_link": "strong|medium|loose",
      "why_link": "二者真实关联的论证",
      "candidate_angle": "",
      "candidate_question": "",
      "fills_gap": null,
      "resource_check": ""
    }
  ],
  "candidates": [
    {
      "candidate_id": "cand_1",
      "title": "《具体问题——以XX为例/基于XX视角》",
      "question": "可回答、可证伪的问题",
      "object": "具体研究对象",
      "method_hint": "可操作的方法",
      "why_link": "逻辑关联说明",
      "fills_gap": null
    }
  ],
  "filtered_out": [{ "raw": "", "reason": "概念堆砌/命中禁止域/不可行" }]
}
```

### 5.2 用户输入模板（User Message Template）

```text
请执行跨界知识碰撞。

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
allow_humor: {true|false}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[scan_output]
saturated_topics: {saturated_topics}
blacklist_hits: {blacklist_hits}
gaps: {gaps}

[profile_snapshot]
backgrounds: {backgrounds}        # 核心域 A
interests: {interests}            # 碰撞域 B/C/D
resources: {resources}

[collide_settings]
min_logic_link: {strong|medium|loose}
max_candidates: {默认 20}
target_count: {需要的候选数，如 5}
```

---

## 6. 碰撞示例（标杆）

### 6.1 历史学 × 电子游戏（PRD 经典案例）

- **核心域 A**：历史学（罗马帝国史）
- **碰撞域 B**：电子游戏（《文明》系列）
- **算子**：③ 对象互证 + ⑤ 媒介反身
- **why_link**：《文明》以可交互方式重构罗马兴衰，是大众接触罗马史的高频媒介；同一对象在史书与游戏中的呈现差异可直接比较、可证伪。
- **碰撞结果**：

  《从〈文明〉系列游戏看大众对罗马帝国的认知偏差——以某高校 30 名非历史专业本科生为例》

  - **问题**：《文明》系列对罗马帝国的呈现，使非历史专业玩家形成了哪些关于罗马帝国的认知偏差？
  - **方法**：游戏文本/设定分析 + 玩家问卷与小样本访谈
  - **为什么成立**：共享对象「罗马帝国」，差异可观测、可测量，且材料与样本易得 → 既新颖、又贴合兴趣、又能落地。

### 6.2 更多碰撞示范（展示通用性）

| 核心域 A | 碰撞域 B | 算子 | 碰撞出的具体问题（示意） |
|----------|----------|------|--------------------------|
| 生物学（细胞凋亡） | 游戏设计 | 机制类比 | 塔防游戏的「攻防资源调度」在多大程度上可类比细胞凋亡的信号通路？类比在何处失效？（须论证边界） |
| 市场营销 | 乐队文化 | 视角借用 | 独立乐队如何用「非商业」的亚文化资本完成粉丝变现？以某 livehouse 场景为例 |
| 计算机（算法） | 烹饪 | 方法移植 | 菜谱的「分步优化」思路能否用于讲解动态规划的状态转移？以一门通识课为例 |
| 传播学 | 养猫 | 媒介反身 | 「云吸猫」内容如何成为青年群体的情绪代偿机制？以小红书养猫话题评论区为例 |

> 反例（**必须被剔除**）：「元宇宙背景下大模型赋能罗马史教学的路径研究」——热词拼接、无机制连接、`why_link` 不成立，进 `filtered_out`。

---

## 7. 概念堆砌 vs 真碰撞：快速自检三问

对每个候选，连续追问，任一答「否」即退回或剔除：

1. **「抽掉热词后，问题还成立吗？」** —— 不成立 = 概念堆砌。
2. **「A 和 B 共享的对象/机制是什么？能用一句话说清因果或同构吗？」** —— 说不清 = 伪拼接。
3. **「这个问题的答案能被证据推翻吗？用户手上有得出答案的材料吗？」** —— 不能证伪 / 没材料 = 交给引擎 C 判假问题或不可行。

---

## 8. 异常与降级

| 情况 | 处置 |
|------|------|
| 画像无兴趣域（轻量模式） | 用方法论近邻 + 对象近邻补碰撞域，并注明「未使用个人兴趣，个性度较低」。 |
| 所有碰撞均为 loose | 放宽到 `medium` 并要求补充桥接论证；仍无结果则回引擎 A 重新确认缺口。 |
| 候选数不足 target_count | 如实输出全部，交由引擎 C 后触发回灌（见引擎 C 第 3.4）。 |
| 疑似伪蓝海碰撞 | 保留但标注，提示引擎 C 重点审可行性。 |

---

## 9. 验收对照

- [x] 引擎目标与上下游位置明确
- [x] 提供可直接执行的系统提示词 + 用户输入模板
- [x] 五种碰撞算子 + 逻辑关联三级筛选 + 强制 `why_link`
- [x] 含历史学×游戏标杆案例及多个跨领域示范
- [x] 输出含 `collision_points / candidates / filtered_out`，与架构第 8.2 契约一致
- [x] 明确概念堆砌鉴别与数据传递（A→B、B→C）
- [x] 数量受 `max_candidates` 约束，防止发散
