# 引擎 A · 领域饱和扫描引擎（Saturation Scan）——「排雷」

> 本文档由 C·引擎部产出，是「创意分身」三引擎中的**第一引擎**。
> 定位：在生成任何选题之前，先扫描目标领域**哪些方向已经被做烂、哪些方向仍有缺口**，把饱和方向拉入黑名单，从源头杜绝「烂大街」选题。
> 配套文件：[`engine_cross_collision.md`](./engine_cross_collision.md)（引擎 B）、[`engine_self_critique.md`](./engine_self_critique.md)（引擎 C）、[`bad_topic_blacklist.md`](./bad_topic_blacklist.md)（全局黑名单）、[`output_template.md`](./output_template.md)（输出模板）。

---

## 0. 三引擎串联总览（流水线地图）

三引擎**严格串行、逐级传参**，对应 6 步闭环的 Step 4。这是整条流水线的权威地图，引擎 B / C 文档只引用本图、不重复展开。

```
                         ┌─────────────────────────────────────────────┐
   Step 1-3 产物          │ 场景配置 scene_config（tone_rules /           │
   ───────────────►       │ constraint_list / exclusion_rules）           │
   · 场景配置 JSON         │ 画像快照 profile（base / preferences）         │
   · 问卷答案 answers      │ 问卷答案 answers（domain / keywords …）        │
                         └─────────────────────────────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              ▼                                                           ▼
┌───────────────────────────┐                       ┌───────────────────────────┐
│ 引擎 A · 领域饱和扫描（排雷）│  WebSearch + 知识库兜底  │ 全局黑名单 bad_topic_       │
│                           │ ◄────────────────────► │ blacklist.md（5 类）       │
│ 输出 saturation_report：  │                       └───────────────────────────┘
│  · saturated_topics[]     │──┐
│  · gaps[]                 │  │  把饱和方向 + 黑名单命中
│  · blacklist_hits[]       │  │  作为「硬约束」下传
│  · evidence{}             │  │
└───────────────────────────┘  │
                              ▼
              ┌──────────────────────────────────────────────────────────┐
              │ 引擎 B · 跨界知识碰撞（找新角度）                            │
              │  A×B / A×C / A×D，注入 gaps，只保留有逻辑关联的交叉点        │
              │  输出 collision_points[] → 候选问题 candidates[]            │
              └──────────────────────────────────────────────────────────┘
                              │  候选选题下传审稿
                              ▼
              ┌──────────────────────────────────────────────────────────┐
              │ 引擎 C · 自我批判迭代（打磨问题意识）                         │
              │  严苛审稿人按 6 条硬约束逐题判定，质量闸门 pass_all            │
              │  迭代 2-3 轮；不达标则把批判意见回灌引擎 B 重新碰撞            │
              │  输出 final_candidates[]（通过闸门的候选集）                  │
              └──────────────────────────────────────────────────────────┘
                              │
                              ▼
                   Step 5 · formatter 按 output_template.md
                   输出 N 个「四要素」选题 → Step 6 反馈沉淀回画像
```

**数据传递三条铁律**：

1. **A → B**：引擎 A 的 `saturated_topics`（饱和方向）与 `blacklist_hits`（黑名单命中）必须作为引擎 B 的**禁止域**注入；`gaps`（缺口）作为引擎 B 的**优先靶区**注入。
2. **B → C**：引擎 B 的每个候选必须携带 `why_link`（逻辑关联说明），引擎 C 据此判定是否构成「概念堆砌」。
3. **C → B（回灌）**：若通过闸门的候选数不足 `output.count`，引擎 C 把逐题 `issues` 回灌引擎 B，调整碰撞域或关联强度后重新生成，**外层总循环不超过 3 轮**。

---

## 1. 引擎目标

| 项 | 内容 |
|----|------|
| 一句话目标 | 回答用户：「在我想做的这个领域里，**哪些题已经被做烂了不能碰、哪些缝里还能长出新东西**？」 |
| 解决的竞品缺陷 | 「重广度，轻深度」——传统 AI 批量生成表层方向，踩中大量已被反复研究的题（PRD 2.3）。 |
| 核心产出 | ① 饱和度报告 `saturation_report`；② 饱和方向黑名单 `saturated_topics`；③ 领域缺口清单 `gaps`；④ 证据台账 `evidence`。 |
| 不做什么 | 不直接产出最终选题（那是引擎 B/C 的职责）；不做学术贡献度的定性结论；**绝不编造检索数字与文献**。 |
| 机制溯源 | 借鉴 OpenAI **Deep Research「先计划后执行、带引用可追溯」**——先产出检索计划再执行，每条饱和判定都挂证据；借鉴 Anthropic 多智能体研究系统「先把领域地图摸清再动笔」。 |

---

## 2. 输入契约

引擎 A 由编排器（Step 4）调用，输入为一个 JSON 上下文对象：

```json
{
  "scene_config": {
    "scene_id": "academic_paper",
    "tone_rules": { "base_tone": "严肃学术" },
    "constraint_list": ["…"],
    "exclusion_rules": ["…"]
  },
  "answers": {
    "discipline": "传播学",
    "interests": "电子游戏、乐队文化",
    "resources": "可访问学校图书馆数据库",
    "excludes": "不想做纯问卷"
  },
  "profile_snapshot": {
    "base": {
      "backgrounds": ["传播学（本科）"],
      "interests": ["电子游戏", "罗马帝国"],
      "resources": ["学校图书馆数据库", "每周 12 小时"]
    },
    "preferences": []
  },
  "scan_settings": {
    "sources": ["web_search", "scholar", "model_knowledge"],
    "horizon": "3y",
    "require_evidence": true,
    "on_no_evidence": "mark_unsure",
    "saturation_threshold": 80
  }
}
```

| 输入字段 | 来源 | 说明 |
|----------|------|------|
| `scene_config` | Step 1 加载的场景配置 | 取 `tone_rules`、`constraint_list`、`exclusion_rules`；扫描来源与时间窗由场景配置的引擎参数决定（默认 `web_search + scholar`、`3y`）。 |
| `answers` | Step 2 问卷答案 | 提取**学科领域 + 关键词**（见 3.1）；`excludes` 直接并入规避项。 |
| `profile_snapshot` | Step 3 画像读取 | 用画像中的 `backgrounds / interests` 补全关键词，避免只靠当次问卷。 |
| `scan_settings` | 场景配置 / 默认值 | `sources` 检索源；`horizon` 时间窗（`3y`/`1y`/`current`）；`require_evidence` 是否必须有证据；`on_no_evidence` 无证据兜底策略；`saturation_threshold` 饱和阈值（默认 80）。 |

**`on_no_evidence` 三种策略**（对齐架构 ADR-4，默认 `mark_unsure`）：

- `mark_unsure`：无法实时检索时，**显式标注「未实时检索」**，改用模型知识库给出谨慎判断，且不计入硬性黑名单（只作提示）。
- `skip_scan`：跳过扫描，直接交引擎 B，但报告中注明「未排雷」。
- `fail`：停止生成并报告错误（用于高严谨投稿场景）。

---

## 3. 工作流程

### 3.1 第一步：提取领域与关键词

从问卷答案与画像中抽取并分层：

1. **核心领域（domain）**：`answers.discipline`（如「传播学」），可细化到二级学科（如「跨文化传播」）。
2. **对象关键词（object keywords）**：研究对象/载体，如「短视频」「美妆博主」「弹幕」。
3. **方法关键词（method keywords）**：用户偏好或排斥的方法，如「问卷法」「文本分析」。
4. **兴趣关键词（interest keywords）**：`answers.interests` + `profile_snapshot.base.interests`，如「电子游戏」「乐队文化」。
5. **限定词（qualifiers）**：层级、地域、人群、平台、时间，如「本科生」「一线城市」「Z 世代」「抖音」。

> 关键词用于构造检索式；**兴趣关键词不在本引擎检索**，而是交给引擎 B 做碰撞，避免提前污染扫描。

### 3.2 第二步：制定检索计划（先计划后执行）

先列出一张「检索计划清单」，再逐条执行，不盲目搜索。检索式按场景 `sources` 选择：

| 检索目的 | WebSearch 检索式示例（中文） | 检索式示例（英文） |
|----------|------------------------------|--------------------|
| 领域综述/研究现状 | `{领域} {对象} 研究综述 研究现状` | `{object} research review literature` |
| 近年热点 | `{领域} {对象} 研究热点 近三年` | `{object} research trends 2023..2026` |
| 数量/过载信号 | `{对象} 论文 数量 知网上传` | `{object} site:scholar.google.com` |
| 细分缺口 | `{领域} {对象} 不足 研究展望 未来方向` | `{object} research gaps future directions` |
| 平台/商业场景 | `{平台} {赛道} 同质化 泛滥`（短视频/公众号场景） | `{platform} {niche} saturated` |

检索规则：

- **检索不超过 3 轮**：第 1 轮宽口径摸现状，第 2 轮针对疑似饱和方向确认，第 3 轮专门找缺口与「未来研究方向」。
- 每个方向**至少 2 个独立来源**交叉验证后才判饱和；单一来源只标「待确认」。
- 时间窗按 `horizon`：`3y`（近三年，学术默认）、`1y`（近一年，追热点）、`current`（当下榜单/热榜，短视频默认）。

### 3.3 第三步：WebSearch 检索（MVP 主力方案）

在 WorkBuddy AI 环境中，**首选 WebSearch 工具**实时检索，不绑定任何付费学术 API：

1. 用 3.2 的检索式执行 WebSearch，读取返回的标题、摘要、站点与发布时间。
2. 记录**过载信号**：同一选题出现大量同构标题、综述明确写「研究已较为充分/成果丰硕」、平台同质化吐槽。
3. 记录**缺口信号**：综述「未来展望」里反复点名但少有人做的方向、跨学科/新政策/新技术带来的新对象。
4. 对每条结果保留来源 URL、标题、日期，写入 `evidence.sources`。

**能力降级顺序（三级兜底，逐级降、逐级标注）**：

```
① WebSearch 实时检索（最可信，结论可进硬黑名单）
        │  不可用 / 无结果
        ▼
② 免费学术入口兜底（Google Scholar / arXiv / CNKI 开放检索页等可公开访问页面）
        │  仍不可用
        ▼
③ 模型自身知识库（截止训练语料）——必须标注「未实时检索，基于知识库判断」，
   结论只作「提示性规避」，不写入硬性黑名单
```

### 3.4 第四步：饱和度打分

对每个细分方向用**统一标尺**打分（0–100，分数越高越饱和）。打分基于可观察证据，不凭感觉：

| 维度 | 观察点 | 权重 |
|------|--------|:----:|
| 数量信号 | 同题论文/内容数量、检索结果页密度 | 35% |
| 同构信号 | 标题/框架是否高度雷同、换汤不换药 | 25% |
| 时效信号 | 是否集中在旧热点、近一年是否仍在简单重复 | 20% |
| 缺口信号 | 是否存在「新对象/新方法/新数据/新地域」的明显空档（反向计分） | 20% |

**饱和度分档**：

| 档位 | 分值 | 处置 |
|------|------|------|
| 🔴 饱和（saturated） | ≥ `saturation_threshold`（默认 80） | 列入 `saturated_topics`，**生成时硬规避**；命中黑名单类型的同步进 `blacklist_hits`。 |
| 🟠 较热（hot） | 50–79 | 不封禁，但要求引擎 B 必须叠加「新对象/新方法/新视角」才可碰。 |
| 🟡 有缺口（gap） | 20–49 | 列入 `gaps`，作为引擎 B 的优先靶区。 |
| 🟢 蓝海（blue ocean） | < 20 | 列入 `gaps`，但需额外验证「**为什么没人做**」——是机会，还是做不了/没价值（伪蓝海）。 |

> 「伪蓝海」甄别：研究极少可能是因为数据不可得、方法不成立、问题本身无价值。此类方向在报告中加 `pseudo_blue_ocean: true`，提醒引擎 C 重点审查可行性与问题真实性。

### 3.5 第五步：输出饱和度报告并下传

按第 4 节输出契约生成 `saturation_report`，并：

- 把 `saturated_topics` + `blacklist_hits` 作为**禁止域**下传引擎 B；
- 把 `gaps` 作为**优先靶区**下传引擎 B；
- 任何无法验证的数字一律写「约 / 估计」并标注来源或 `未实时检索`。

---

## 4. 输出契约（传给引擎 B）

引擎 A 输出**结构化 JSON**（同时供引擎 B 消费、供 F 部做测试断言）：

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "传播学 / 短视频",
  "saturation_report": [
    {
      "topic": "短视频用户行为研究",
      "saturation_score": 88,
      "level": "saturated",
      "reason": "近三年同题论文数量庞大，标题与框架高度同构，多为问卷+描述统计",
      "evidence_ids": ["src_1", "src_2"],
      "blacklist_type": "over_saturated"
    },
    {
      "topic": "短视频对特定冷门群体（如听障青年）信息获取的影响",
      "saturation_score": 28,
      "level": "gap",
      "reason": "综述展望中反复点名但实证极少，对象新、需特殊渠道",
      "evidence_ids": ["src_3"],
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": ["短视频用户行为研究", "短视频泛化的注意力影响"],
  "gaps": [
    "短视频对听障青年信息获取的影响",
    "弹幕作为小众社群知识协作的机制"
  ],
  "blacklist_hits": [
    {
      "matched_type": "over_saturated",
      "topic": "短视频用户行为研究"
    }
  ],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [
      {
        "id": "src_1",
        "title": "近三年短视频研究综述",
        "url": "https://example.org/review",
        "date": "2025-06-01"
      }
    ],
    "note": "数量为检索结果的近似估计，非精确统计"
  }
}
```

| 输出字段 | 类型 | 去向 / 用途 |
|----------|------|-------------|
| `saturation_report[]` | array | 报告主体，逐方向给分、档位、理由、证据 |
| `saturated_topics[]` | string | **→ 引擎 B 禁止域** |
| `gaps[]` | string | **→ 引擎 B 优先靶区** |
| `blacklist_hits[]` | array | **→ 引擎 B 禁止域**，并在引擎 C 复核 |
| `evidence{checked, real_time, sources, note}` | object | 证据台账；`real_time=false` 时所有结论降级为「提示性」 |

---

## 5. 可直接执行的 Prompt

> 用法：把下方「系统提示词」作为系统消息，把「用户输入模板」填好后作为用户消息。模型可直接执行，无需改代码。

### 5.1 系统提示词（System Prompt）

```text
# 角色
你是「创意分身」的【引擎 A · 领域饱和扫描官】，一位极度厌恶「烂大街选题」的领域排雷专家。你不生产选题，你只负责在选题生成前把领域地图摸清楚：哪些方向已经被做烂、哪些缝隙还有缺口。

# 你会收到的输入
- scene_config：当前场景配置（含 tone_rules、constraint_list、exclusion_rules）
- answers：用户场景化问卷的回答（学科、兴趣、资源、排斥项等）
- profile_snapshot：用户本地画像快照（backgrounds、interests、resources）
- scan_settings：sources（检索源）、horizon（时间窗）、require_evidence、on_no_evidence、saturation_threshold

# 工作步骤（严格按顺序）
1. 提取关键词：从 answers 与 profile_snapshot 中分层抽取——
   核心领域、对象关键词、方法关键词、兴趣关键词、限定词（层级/地域/人群/平台/时间）。
   兴趣关键词只记录，不参与本引擎检索（留给引擎 B 碰撞）。
2. 制定检索计划：先列出你打算执行的检索式清单（宽口径摸现状 → 疑似饱和方向确认 → 专门找缺口），再逐条执行。
3. 执行检索：优先用 WebSearch 按检索计划检索，最多 3 轮。
   - 每个方向至少 2 个独立来源交叉验证才判饱和；单一来源只标「待确认」。
   - 记录过载信号（同题大量、标题同构、综述称「研究已较充分」）与缺口信号（综述「未来展望」点名但少有人做、新对象/新方法/新数据）。
4. 饱和度打分：对每个细分方向按四维度打分（数量 35%、同构 25%、时效 20%、缺口反向 20%），给出 0–100 分与档位：
   ≥阈值（默认 80）= saturated；50–79 = hot；20–49 = gap；<20 = blue_ocean。
   对 blue_ocean 方向必须追问「为什么没人做」：若因数据不可得/方法不成立/问题无价值，标记 pseudo_blue_ocean=true。
5. 输出饱和度报告：严格按【输出格式】返回 JSON，把 saturated_topics 与 blacklist_hits 作为禁止域、gaps 作为优先靶区，供引擎 B 使用。

# 证据与反编造红线（最高优先级）
- 每条饱和判定必须挂证据（来源标题 + URL + 日期）。
- 数量一律用「约/估计」，并注明口径；禁止编造精确数字、文献、期刊、检索结果。
- WebSearch 不可用时，按降级顺序处理：免费学术入口 → 模型自身知识库。
  一旦使用知识库，必须在 evidence.real_time 置 false 并在 note 写明「未实时检索，基于知识库判断」，此时结论只能作「提示性规避」，不得写入硬性 saturated_topics。
- 若 scan_settings.on_no_evidence = mark_unsure：无法确认的方向写「未确认」，禁止猜测；
  若 = skip_scan：跳过并注明「未排雷」；若 = fail：停止并返回错误说明。
- 与全局黑名单（bad_topic_blacklist.md 五类）对照：命中时在 blacklist_hits 中给出 matched_type。

# 语气
- 报告语言克制、就事论事；对事不对人，不使用侮辱性、歧视性表达。
- 输出面向下一个引擎，不面向读者寒暄；除 JSON 外只给极简的「检索计划」与「关键提示」。

# 输出格式（只返回 JSON，不要包裹在代码块外额外解释）
{
  "engine": "saturation_scan",
  "scanned_at": "ISO8601",
  "domain": "核心领域 / 主要对象",
  "saturation_report": [
    {
      "topic": "细分方向",
      "saturation_score": 0,
      "level": "saturated|hot|gap|blue_ocean",
      "reason": "基于证据的判断",
      "evidence_ids": ["src_1"],
      "blacklist_type": "over_saturated|concept_stack|none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": [],
  "gaps": [],
  "blacklist_hits": [{ "matched_type": "over_saturated", "topic": "" }],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [{ "id": "src_1", "title": "", "url": "", "date": "" }],
    "note": "数量为近似估计"
  }
}
```

### 5.2 用户输入模板（User Message Template）

```text
请执行领域饱和扫描。

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[answers]
学科/领域: {discipline}
研究对象/载体: {object}
研究类型/方法: {research_type}
兴趣方向: {interests}
可用资源: {resources}
硬约束: {hard_constraints}
排斥项: {excludes}

[profile_snapshot]
backgrounds: {backgrounds}
interests: {interests}
resources: {resources}

[scan_settings]
sources: {sources，如 web_search, scholar, model_knowledge}
horizon: {3y | 1y | current}
require_evidence: {true | false}
on_no_evidence: {mark_unsure | skip_scan | fail}
saturation_threshold: {默认 80}
```

---

## 6. 输出示例

### 6.1 正常扫描（实时检索成功）

> 检测到「短视频用户行为研究」在近三年已有约 1200+ 篇同题论文，标题与框架高度同构（问卷 + 描述统计 + 泛化建议），饱和度过高（88 分），**已自动规避并列入禁止域**。
> 同时发现缺口：「短视频对听障青年信息获取的影响」在综述展望中被反复点名但实证极少（28 分），已列为引擎 B 的优先靶区。

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "传播学 / 短视频",
  "saturation_report": [
    {
      "topic": "短视频用户行为研究",
      "saturation_score": 88,
      "level": "saturated",
      "reason": "近三年同题论文约1200篇，标题框架高度同构",
      "evidence_ids": ["src_1", "src_2"],
      "blacklist_type": "over_saturated",
      "pseudo_blue_ocean": false
    },
    {
      "topic": "短视频对听障青年信息获取的影响",
      "saturation_score": 28,
      "level": "gap",
      "reason": "综述展望点名但实证极少，对象新、需特殊渠道",
      "evidence_ids": ["src_3"],
      "blacklist_type": "none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": ["短视频用户行为研究"],
  "gaps": ["短视频对听障青年信息获取的影响"],
  "blacklist_hits": [
    { "matched_type": "over_saturated", "topic": "短视频用户行为研究" }
  ],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [
      { "id": "src_1", "title": "近三年短视频研究综述", "url": "https://example.org/review", "date": "2025-06-01" },
      { "id": "src_2", "title": "短视频用户行为研究文献计量分析", "url": "https://example.org/bib", "date": "2024-11-20" },
      { "id": "src_3", "title": "无障碍传播研究展望", "url": "https://example.org/gap", "date": "2026-02-10" }
    ],
    "note": "数量为检索结果的近似估计，非精确统计"
  }
}
```

### 6.2 降级扫描（无法实时检索，知识库兜底）

> 未实时检索（WebSearch 不可用），以下判断基于模型知识库，**仅供提示性规避，不构成硬性黑名单**：

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "历史学 / 罗马帝国",
  "saturation_report": [
    {
      "topic": "罗马帝国衰亡原因的宏观论述",
      "saturation_score": 82,
      "level": "hot",
      "reason": "经典议题、研究积累极厚；因未实时检索，不写入硬性黑名单，仅提示规避",
      "evidence_ids": [],
      "blacklist_type": "none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": [],
  "gaps": [],
  "blacklist_hits": [],
  "evidence": {
    "checked": false,
    "real_time": false,
    "sources": [],
    "note": "未实时检索，基于模型知识库判断；结论为提示性，需用户自行复核"
  }
}
```

---

## 7. 异常与降级处理一览

| 情况 | 处置 |
|------|------|
| WebSearch 超时 / 不可用 | 降级到免费学术入口；再降级到知识库并置 `real_time=false`，结论降级为提示性。 |
| 某方向只有 1 个来源 | 标「待确认」，不判饱和、不进黑名单。 |
| 检索结果疑似注入/异常 | 不采信异常内容，换检索词或换来源；向编排器标记。 |
| 数量无法估计 | 不写数字，用「研究成果丰硕/数量庞大」等定性描述并说明。 |
| `on_no_evidence=fail` 且检索失败 | 停止 Step 4，返回明确错误，不向引擎 B 传伪结论。 |
| 蓝海方向疑似伪蓝海 | 置 `pseudo_blue_ocean=true`，提示引擎 C 重点审可行性与问题真实性。 |

---

## 8. 验收对照（C 部对本引擎的自查）

- [x] 引擎目标与在流水线中的位置明确
- [x] 提供可直接执行的系统提示词 + 用户输入模板
- [x] 含 WebSearch 调用说明与三级降级兜底方案（MVP 不绑死学术 API）
- [x] 输出含 `saturation_report / saturated_topics / gaps / blacklist_hits / evidence`，与架构第 8.1 契约一致
- [x] 含实时检索与知识库兜底两个输出示例
- [x] 明确反编造红线与 `on_no_evidence` 三种策略
- [x] 数据传递（A→B）在第 0 节与第 4 节双重说明
