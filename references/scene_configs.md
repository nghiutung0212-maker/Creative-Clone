# 场景库说明文档（Scene Library）

> 本文档由 B·场景库部产出，是「创意分身」Skill 场景库的使用说明与扩展指南。
> 场景配置的**字段格式圣经**是 [`scene_format_spec.md`](./scene_format_spec.md)；本文档说明当前场景库包含什么、运行时如何读取、以及如何新增场景。

---

## 1. 场景库是什么

场景库是「创意分身」实现**场景自适应**（核心设计原则 1）与**场景维度可扩展**（核心设计原则 5）的配置层：

- 一个场景 = 一个独立的 JSON 配置文件；
- 配置文件声明该场景的：分步问卷、语气基调、硬约束、排斥项、输出格式微调；
- 三引擎与主流程**不感知具体场景**，所有场景差异都由配置注入。新增一个场景，只需新增一个 JSON 文件，不改任何核心逻辑。

---

## 2. 当前支持的场景索引（9 个）

配置文件统一位于 `assets/scene_profiles/`。

| # | scene_id | 场景名称 | 基础语气基调 | 允许幽默 | 允许非正式 | 一句话说明 |
|---|----------|----------|--------------|:--------:|:----------:|------------|
| 1 | `academic_paper` | 学术论文选题 | 严肃学术 | 否 | 否 | 课程论文、毕设、开题、期刊投稿与基金申请的选题，标杆配置 |
| 2 | `ppt_presentation` | PPT 汇报选题 | 商业正式 | 否 | 是 | 课程汇报、答辩、工作汇报、路演与会议分享的主题 |
| 3 | `short_video` | 短视频选题 | 轻松玩梗 | 是 | 是 | 三分钟以内短视频的选题、钩子与拍摄形式 |
| 4 | `wechat_article` | 公众号文章选题 | 商业正式 | 否 | 是 | 观点评论、干货、行业分析、情感故事与热点解读 |
| 5 | `startup_idea` | 创业方向选题 | 商业正式 | 否 | 是 | 创业点子、产品方向与商业机会，含 MVP 验证路径 |
| 6 | `event_planning` | 活动策划选题 | 轻松玩梗 | 是 | 是 | 校园社团、团建、商业活动、沙龙比赛与线上活动 |
| 7 | `podcast` | 播客选题 | 轻松玩梗 | 是 | 是 | 播客单集话题、讨论点与节目规划 |
| 8 | `course_design` | 课程设计选题 | 严肃学术 | 否 | 否 | 单节课、单元课与整门课的教学设计 |
| 9 | `interview_outline` | 人物采访提纲 | 商业正式 | 否 | 是 | 人物特稿、行业/事件/宣传采访的问题清单 |

> 三种语气基调全部覆盖：**严肃学术**（论文、课程设计）、**轻松玩梗**（短视频、活动、播客）、**商业正式**（PPT、公众号、创业、采访）。

---

## 3. 文件位置与命名

- 目录：`assets/scene_profiles/`
- 文件名：`{scene_id}.json`，蛇形命名（snake_case），且文件内 `scene_id` 字段必须与文件名（去掉 `.json`）完全一致。
- 示例：`academic_paper.json` ↔ `"scene_id": "academic_paper"`。

---

## 4. 运行时如何读取场景配置

### 4.1 加载时机（对应 6 步闭环）

```
Step 1 场景选择
  ├─ 用户在场景菜单中选择，或自由描述场景
  ├─ 加载 assets/scene_profiles/{scene_id}.json
  └─ 校验：JSON 语法合法 + 7 个顶层字段齐全 + scene_id 与文件名一致
        └─ 校验通过才进入 Step 2
Step 2 场景化问卷
  ├─ 按 questionnaire_template.rounds 逐轮提问（每轮 2-3 题）
  ├─ 渲染每题前先求值 condition，决定 show / skip
  └─ 每轮结束后对照 skip_logic.rules 判断是否追加或省略问题
Step 3 对话式补充
  └─ 结合问卷回答与本地画像，追问 3-5 个画像缺口（详见 profile_schema.md）
Step 4 选题生成（三引擎）
  ├─ constraint_list → 作为生成结果的硬性过滤条件
  ├─ exclusion_rules → 与全局黑名单叠加，作为规避方向
  └─ tone_rules      → 作为生成与审稿的语气/分寸依据
Step 5 输出选题
  └─ 按 output_format_adjustments 调整标题格式、追加/省略字段
Step 6 反馈迭代
  └─ 问卷回答与最终选中选题沉淀进用户画像（跨场景复用）
```

### 4.2 每个字段如何被消费

| 顶层字段 | 类型 | 消费者 | 用途 |
|----------|------|--------|------|
| `scene_id` | string | 路由 / 主流程 | 场景唯一标识，须与文件名一致 |
| `scene_name` | string | 场景菜单 | 菜单中展示给用户的中文名 |
| `scene_description` | string | 场景菜单 / 路由 | 一句话说明，帮助用户判断与辅助匹配 |
| `questionnaire_template` | object | Step 2 问卷 | `rounds` 定义分步问题；`skip_logic` 定义跳转规则 |
| `tone_rules` | object | Step 4/5 | 基础基调、是否允许幽默/非正式、语气正例与反例 |
| `constraint_list` | array | 三引擎 | 选题**必须满足**的硬条件，作为过滤条件 |
| `exclusion_rules` | array | 三引擎 | 该场景**主动规避**的方向 |
| `output_format_adjustments` | object | Step 5 输出 | 标题模板、额外字段、可省略字段 |

---

## 5. 三种语气基调

| 基调 | allow_humor | allow_informal | 覆盖场景 |
|------|:-----------:|:--------------:|----------|
| 严肃学术 | false | false | 学术论文、课程设计 |
| 轻松玩梗 | true | true | 短视频、活动策划、播客 |
| 商业正式 | false | true | PPT 汇报、公众号、创业方向、采访提纲 |

补充规则：

- 基调是**默认值**，不是死规则。多数配置的 `tone_rules` 中含 `conditional_notes`，当用户在问卷中明确表达不同基调时（如课程汇报想玩梗、公众号想写深度长文），以**用户当前请求为准**，按条件说明切换。
- 任何基调节点都不可突破法律与平台合规底线；幽默不得用于侮辱、歧视、引战或削弱证据。

---

## 6. 分步问卷与跳转机制

### 6.1 分步追问

- 问卷按 `questionnaire_template.rounds` 中的 `round_id` 顺序逐轮进行；
- 每轮 2-3 个问题，用户作答后再进入下一轮，不一次性甩出全部问题；
- 每个问题声明 `field`（字段名）、`question`（提问文案）、`type`（`text` / `choice`）、`required`、`options`（选择题）等。

### 6.2 条件渲染（condition）

题目级别的显隐通过 `condition` 声明，统一结构：

```json
"condition": {
  "if": {"field": "level", "in": ["硕士论文", "博士论文"]},
  "then": "show",
  "else": "skip"
}
```

每次渲染该问题前，先根据已收集答案求值；未声明 `condition` 的问题始终展示。

### 6.3 跳转规则（skip_logic）

`questionnaire_template.skip_logic.rules` 以自然语言声明跨轮次的追加、省略与生成约束，每个场景均含 **不少于 2 条**跳转规则。典型模式：

- **层级跳转**：选「课程论文」→ 不问博士层级的理论贡献要求；
- **目标跳转**：选「带货」→ 追加商品信息、风险提醒增加广告合规；
- **资源跳转**：已有现成数据集 → 不再追问数据可得性，优先复用；
- **时长跳转**：时长极短 → 只保留单一观点、单一话题。

---

## 7. 约束与排斥的叠加关系

生成时，规避条件按以下顺序叠加，越靠后越严格：

1. **全局黑名单**：`bad_topic_blacklist.md` 中定义的五种烂选题（概念堆砌、过度饱和、无法落地、范围过大、假问题），对所有场景生效；
2. **场景排斥项**：当前场景 `exclusion_rules` 中的方向，在全局黑名单之上叠加；
3. **用户显式排除**：问卷中用户填写的排斥/禁忌（如 `excludes`、`red_lines`）；
4. **场景硬约束**：`constraint_list` 是正向过滤条件，不满足的选题直接淘汰，不进入输出。

---

## 8. 输出格式微调

- 四要素（具体问题 / 为什么适合你 / 三个切入角度 / 风险提醒）**任何场景都不可省略**；
- `output_format_adjustments.title_format` 定义标题模板，如论文场景 `《{具体问题}——以{研究对象}为例》`；
- `extra_fields` 声明场景专属的追加字段（如短视频追加「前3秒钩子」，创业追加「MVP 验证路径」）；
- `suppress_fields` 声明可省略的标准字段；当前 9 个场景均保持为空，即完整保留四要素。

---

## 9. 如何新增一个场景

> 目标：新增场景 = 新增一个 JSON 文件 + 在本文件索引表追加一行，无需改动 SKILL.md 与任何引擎逻辑。

### 9.1 操作步骤

1. **新建文件**：在 `assets/scene_profiles/` 下新建 `{scene_id}.json`，`scene_id` 使用蛇形命名（如 `exhibition_curation.json`）。
2. **填写配置**：严格按 [`scene_format_spec.md`](./scene_format_spec.md) 填齐 7 个顶层字段：
   - `scene_id`、`scene_name`、`scene_description`；
   - `questionnaire_template`：分轮设计，每轮 2-3 题；
   - `tone_rules`：选择与场景匹配的基础基调；
   - `constraint_list`、`exclusion_rules`；
   - `output_format_adjustments`。
3. **设计跳转**：问卷至少包含 2 条 `skip_logic` 跳转规则；需要题目级显隐时使用 `condition`。
4. **校验语法**：运行 JSON 校验（见 9.3）。
5. **登记索引**：在本文档第 2 节的索引表中追加一行。
6. **完成**：无需改动 SKILL.md、引擎与画像代码；如确需当前配置无法表达的新能力，先提交架构评审，不得直接改核心逻辑。

### 9.2 新增场景 Checklist

- [ ] 文件名蛇形命名，且与 `scene_id` 完全一致
- [ ] 7 个顶层字段齐全，问卷题目字段（field/question/type/required）完整
- [ ] 问卷分步进行，每轮 2-3 题，不一次性提问
- [ ] `skip_logic.rules` 不少于 2 条，condition 结构正确
- [ ] 基础基调与场景匹配，`tone_examples` 含正例与反例
- [ ] `constraint_list` 可执行、可过滤；`exclusion_rules` 与全局黑名单无冲突
- [ ] 输出保留四要素，`extra_fields` 仅追加不删减
- [ ] 通过 JSON 语法校验
- [ ] 已在 `scene_configs.md` 索引表登记

### 9.3 校验命令

```bash
# 校验全部场景配置
python3 -m json.tool assets/scene_profiles/{scene_id}.json > /dev/null && echo OK

# 一次性校验整个场景库
for f in assets/scene_profiles/*.json; do python3 -m json.tool "$f" > /dev/null || echo "BAD: $f"; done
```

---

## 10. 与其他文件的关系

| 文件 | 关系 |
|------|------|
| `references/scene_format_spec.md` | 场景配置的字段格式规范（A 部门产出），本文件是其配套使用说明 |
| `references/bad_topic_blacklist.md` | 全局烂选题黑名单，与各场景 `exclusion_rules` 叠加 |
| `references/engine_*.md` | 三引擎，消费配置中的问卷答案、约束、排斥与语气规则 |
| `references/output_template.md` | 四要素输出模板，受 `output_format_adjustments` 微调 |
| `references/profile_schema.md` | 用户画像，问卷回答与选中选题跨场景沉淀其中 |
| `SKILL.md` | 入口文档，Step 1/2 引用本场景库 |

---

## 11. 交付说明（B·场景库部）

- **产出文件**：`assets/scene_profiles/` 下 9 个场景配置 JSON + 本文档 `references/scene_configs.md`。
- **规格符合情况**：全部配置严格遵循 `scene_format_spec.md` 的 7 个顶层字段；论文标杆配置覆盖 PRD 模块 1 全部 8 个问卷维度；每场景跳转规则均 ≥ 2 条；三种语气基调全覆盖。
- **遗留 TODO**：无。场景菜单的最终展示文案由整合阶段在 SKILL.md 中衔接，不影响配置本身。
