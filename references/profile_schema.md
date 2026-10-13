# 创意分身 Skill — 用户画像 Schema 与授权机制

> 本文档由画像部（D）产出，是画像系统的唯一数据契约，也是合规部（E）编写隐私政策的输入。
> 配套交付物：`assets/profile_template.json`（默认画像模板）、`scripts/init_profile.py`（初始化脚本）、`scripts/update_profile.py`（更新脚本）。

## 1. 定位与职责

画像系统回答一个问题：**「创意分身」凭什么越来越懂你？**

它是产品的「长期记忆」，把用户跨场景的思维模式、知识背景、兴趣倾向、审美判断沉淀成一个本地 JSON 文件，供三引擎（饱和扫描、跨界碰撞、自我批判）读取，实现「越用越懂你」。它不参与任何网络传输，不上传任何服务器。

核心职责：

- 收集并合并三重信息来源（本地文件读取、问卷回答、对话交互）；
- 以可溯源、可置信的方式沉淀偏好，区分「显式偏好」与「推断偏好」；
- 支持跨场景复用，任何场景都能复用同一份画像；
- 承载授权状态，完整模式与轻量模式可随时切换；
- 全程本地化，用户可随时查看、编辑、删除。

## 2. 设计原则

对齐 PRD 设计原则 2（用户画像跨场景沉淀）与架构部第 7 章「用户画像数据契约」：

1. **跨场景复用**：偏好、风格、兴趣不绑定任何具体场景；场景级短期约束用 `scope` / `scenario` 字段区分，不污染全局画像。
2. **可溯源**：每条偏好都带 `source`（显式/推断）、`evidence`（证据）与 `confidence`（置信度），借鉴 OpenAI Memory 的来源可展示，避免「幻觉式偏好」。
3. **显式优先**：显式偏好优先于推断偏好；推断偏好只有在跨会话出现一致证据时才写入。
4. **当前请求优先**：用户本次明确表达与画像冲突时，以本次为准，并降低对应画像条目置信度。
5. **最小采集**：只采集生成选题必需的字段，不做全量原文累积（画像的 `history` 与 `signals` 均有上限）。
6. **本地与透明**：明文 JSON 存本地，进 `.gitignore`，开源可审计。

## 3. 画像文件与生命周期

| 项 | 说明 |
|----|------|
| 默认路径 | `~/.creative-clone/profile.json` |
| 编码 | UTF-8 |
| 格式 | JSON（顶层为对象，字段 snake_case） |
| 初始化 | 首次使用时由 `scripts/init_profile.py` 从模板复制创建 |
| 更新 | 每次反馈后由 `scripts/update_profile.py` 增量更新 |
| 隐私 | 全部本地，不进版本库（应写入 `.gitignore`） |

生命周期：`init_profile.py` 建文件 → 运行时读取画像快照 → 选题生成 → 用户反馈 → `update_profile.py` 沉淀 → 下一轮复用。删除文件即清空画像。

## 4. 顶层结构总览

| 顶层字段 | 类型 | 含义 |
|---------|------|------|
| `schema_version` | integer | 画像格式版本，当前恒为 1 |
| `profile_meta` | object | 画像元信息（用户标识、时间戳、模式） |
| `base` | object | 基础画像：知识背景、兴趣、资源、写作风格、思考深度 |
| `preferences` | array | 跨场景偏好清单（可溯源） |
| `history` | array | 交互历史（每次反馈一条，结构化摘要） |
| `signals` | object | 近期反馈信号聚合（供下一轮生成纠偏） |
| `stats` | object | 反馈统计计数 |
| `privacy` | object | 授权与隐私状态 |

## 5. 完整 JSON Schema（draft-07）

本 Schema 是画像文件的机器可读契约，同时也是三引擎在「结构化输出」模式下产出画像补丁时的校验依据（详见第 13 节跨模型兼容性）。

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://creative-clone.local/schemas/profile-schema.json",
  "title": "创意分身 用户画像 Schema",
  "description": "本地存储的用户画像数据契约，跨场景复用，不上传任何服务器。",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "profile_meta",
    "base",
    "preferences",
    "history",
    "signals",
    "stats",
    "privacy"
  ],
  "properties": {
    "schema_version": {
      "type": "integer",
      "const": 1
    },
    "profile_meta": {
      "type": "object",
      "additionalProperties": false,
      "required": ["user_id", "created_at", "updated_at", "mode"],
      "properties": {
        "user_id": { "type": "string", "default": "local-anon" },
        "created_at": { "type": ["string", "null"], "format": "date-time" },
        "updated_at": { "type": ["string", "null"], "format": "date-time" },
        "mode": { "type": "string", "enum": ["full", "light"], "default": "light" }
      }
    },
    "base": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "language": { "type": "string", "default": "zh-CN" },
        "backgrounds": { "type": "array", "items": { "type": "string" } },
        "interests": { "type": "array", "items": { "type": "string" } },
        "resources": { "type": "array", "items": { "type": "string" } },
        "writing_style": { "type": ["string", "null"] },
        "thinking_depth": { "type": ["string", "null"] }
      }
    },
    "preferences": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["key", "value", "source", "updated_at"],
        "properties": {
          "key": { "type": "string" },
          "value": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.5 },
          "source": { "type": "string", "enum": ["explicit", "inferred"] },
          "scope": { "type": "string", "default": "cross_scenario" },
          "scenario": { "type": ["string", "null"], "default": null },
          "evidence": { "type": "array", "items": { "type": "string" } },
          "updated_at": { "type": ["string", "null"], "format": "date-time" }
        }
      }
    },
    "history": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["scenario", "topic", "feedback", "timestamp"],
        "properties": {
          "scenario": { "type": "string" },
          "query": { "type": "string" },
          "topic": { "type": "string" },
          "chosen_topics": { "type": "array", "items": { "type": "string" } },
          "feedback": { "type": "string", "enum": ["like", "dislike", "redirect", "select"] },
          "timestamp": { "type": ["string", "null"], "format": "date-time" }
        }
      }
    },
    "signals": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "liked_topics": { "type": "array", "items": { "type": "string" } },
        "disliked_topics": { "type": "array", "items": { "type": "string" } },
        "redirected_topics": { "type": "array", "items": { "type": "string" } },
        "selected_topics": { "type": "array", "items": { "type": "string" } }
      }
    },
    "stats": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "total_sessions": { "type": "integer", "minimum": 0 },
        "like_count": { "type": "integer", "minimum": 0 },
        "dislike_count": { "type": "integer", "minimum": 0 },
        "redirect_count": { "type": "integer", "minimum": 0 },
        "select_count": { "type": "integer", "minimum": 0 }
      }
    },
    "privacy": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "local_reading_enabled": { "type": "boolean", "default": false },
        "authorized_dirs": { "type": "array", "items": { "type": "string" } },
        "consented_at": { "type": ["string", "null"], "format": "date-time" },
        "consent_version": { "type": ["string", "null"] },
        "last_reviewed_at": { "type": ["string", "null"], "format": "date-time" }
      }
    }
  }
}
```

## 6. 字段详解

### 6.1 profile_meta（元信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 本地匿名标识，固定 `local-anon`（无账号体系） |
| `created_at` | string/null | 画像创建时间（ISO 8601，UTC） |
| `updated_at` | string/null | 最近一次更新时间 |
| `mode` | enum | `full`（完整模式）/ `light`（轻量模式） |

### 6.2 base（基础画像）

`base` 是「你是谁」的静态面，跨场景复用。

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `language` | string | 默认 | 首选语言，默认 `zh-CN` |
| `backgrounds` | string[] | 问卷 + 本地读取 | 知识背景 / 学科专业 / 职业身份 |
| `interests` | string[] | 问卷 + 反馈 + 本地读取 | 兴趣领域、关注领域（跨界碰撞的输入源） |
| `resources` | string[] | 问卷 | 可用资源、数据、语料（可行性校验输入） |
| `writing_style` | string/null | 本地读取（需授权） | 写作风格摘要特征 |
| `thinking_depth` | string/null | 本地读取（需授权） | 思考深度（建议值：`shallow` / `medium` / `deep`） |

### 6.3 preferences（偏好清单）

数组化的可溯源偏好，是「懂你」的核心。每条偏好：

| 字段 | 类型 | 说明 |
|------|------|------|
| `key` | string | 偏好键，如 `tone_preference`、`angle_style`、`selected_topic` |
| `value` | string | 偏好值 |
| `confidence` | number 0–1 | 置信度，默认 0.5 |
| `source` | enum | `explicit`（用户明说）/ `inferred`（推断） |
| `scope` | string | `cross_scenario`（跨场景）/ 具体场景标识 |
| `scenario` | string/null | 当 `scope` 为场景级时，记录场景标识 |
| `evidence` | string[] | 支持该偏好的证据（如 `academic_paper:2026-10-13T08:00:00+00:00`） |
| `updated_at` | string/null | 最近更新时间 |

### 6.4 history（交互历史）

每次反馈一条结构化记录，不做全文原文累积（上限 500 条，超出删除最旧）。

| 字段 | 类型 | 说明 |
|------|------|------|
| `scenario` | string | 场景标识，如 `academic_paper` |
| `query` | string | 用户原始诉求摘要（可为空） |
| `topic` | string | 本次选题内容 |
| `chosen_topics` | string[] | 最终选中的选题（仅 `select` 时非空） |
| `feedback` | enum | `like` / `dislike` / `redirect` / `select` |
| `timestamp` | string/null | 时间戳（ISO 8601，UTC） |

### 6.5 signals（反馈信号聚合）

近期反馈的轻量聚合窗口（每类上限 50 条，只保留最近信号），供 Step 6 调整下一轮生成：

| 字段 | 说明 |
|------|------|
| `liked_topics` | 最近表示「有意思」的选题 |
| `disliked_topics` | 最近「换一批」的选题 |
| `redirected_topics` | 最近「方向偏了」的选题 |
| `selected_topics` | 最近最终选中的选题 |

### 6.6 stats（统计计数）

`total_sessions`、`like_count`、`dislike_count`、`redirect_count`、`select_count`，均为非负整数，供画像面板与趋势展示。

### 6.7 privacy（授权与隐私）

| 字段 | 类型 | 说明 |
|------|------|------|
| `local_reading_enabled` | boolean | 是否开启本地文件读取 |
| `authorized_dirs` | string[] | 用户主动授权的目录列表（最小权限） |
| `consented_at` | string/null | 最近一次授权确认时间 |
| `consent_version` | string/null | 授权告知文案版本号 |
| `last_reviewed_at` | string/null | 用户最近一次查看授权设置的时间 |

## 7. 三信息来源映射

对齐 PRD 第五节模块 2，画像三重信息来源与写入字段的对应关系：

| 来源 | 采集方式 | 采集内容 | 写入字段 | 授权要求 |
|------|---------|---------|---------|---------|
| 本地文件读取 | 读取用户授权目录下的文档/笔记/代码 | 写作风格、知识背景、关注领域、思考深度 | `base.backgrounds`、`base.interests`、`base.writing_style`、`base.thinking_depth` | 必须主动勾选 |
| 问卷回答 | 每次选题的场景化问卷 | 当前场景偏好、约束、兴趣 | `preferences`（`source=explicit`，可带 `scenario`）、`base.*` | 无需授权 |
| 对话交互 | 选题过程中的反馈与追问 | 审美倾向、对「好选题」的判断标准、历史选题记录 | `history`、`signals`、`stats`、`preferences`（`source=inferred`） | 无需授权 |

## 8. 跨场景复用设计

跨场景复用的核心是「全局字段」与「场景字段」分离：

- **全局字段**：`base`、`preferences`（`scope=cross_scenario`）、`signals`、`stats`——任何场景都共享，例如用户在论文场景沉淀的「兴趣：电子游戏」，在短视频场景同样可用作跨界碰撞输入。
- **场景字段**：`preferences` 中 `scope` 为具体场景标识的条目，以及 `history.scenario`——只在对应场景生效，避免场景偏好串味。
- **升级路径**：场景级偏好若在多场景出现一致证据，可升级为跨场景偏好（对应第 9 节 R2）。

## 9. 读写与优先级规则

画像读写遵循六条规则（对齐架构部第 7 章）：

| 编号 | 规则 | 含义 |
|------|------|------|
| R1 | 显式大于推断 | `source=explicit` 的偏好优先于 `inferred` |
| R2 | 推断需一致证据 | 跨会话至少两次独立支持才写入推断偏好；单次反馈只进 `history` |
| R3 | 当前请求大于存储 | 用户本次表达与画像冲突时以本次为准，并降低对应条目置信度 |
| R4 | 本地可管理 | 明文 JSON，可查看/编辑/删除，删除不可恢复需确认 |
| R5 | 批量写入 | 每轮结束后统一更新，不在生成中途写入干扰 |
| R6 | 最小采集 | 只写场景配置 `profile.capture` 声明的字段与反馈信号 |

## 10. 反馈类型与更新逻辑

`scripts/update_profile.py` 按反馈类型更新对应字段。反馈枚举同时兼容 UI 文案与脚本参数：

| 参数值 | UI 文案 | 更新动作 |
|--------|---------|---------|
| `like` | 这个有意思 | 追加 `history`、`signals.liked_topics`，`stats.like_count + 1` |
| `dislike` | 换一批 | 追加 `history`、`signals.disliked_topics`，`stats.dislike_count + 1` |
| `redirect` | 方向偏了 | 追加 `history`、`signals.redirected_topics`，`stats.redirect_count + 1` |
| `select` | 最终选中 | 追加 `history`（含 `chosen_topics`）、`signals.selected_topics`、`stats.select_count + 1`，并把选中选题沉淀进 `base.interests` 与 `preferences`（`selected_topic`，`source=explicit`，`confidence=0.9`） |

所有反馈都会把 `profile_meta.updated_at` 刷新为当前时间。写入采用「临时文件 + 原子替换」，避免写一半损坏画像。

## 11. 授权机制设计

### 11.1 两种模式

| 模式 | 数据来源 | 画像丰富度 |
|------|---------|-----------|
| 完整模式（full） | 本地文件读取 + 问卷 + 对话 | 高 |
| 轻量模式（light） | 仅问卷 + 对话 | 基础 |

默认轻量模式。关闭授权后自动降级为轻量模式，核心流程不受影响，只是画像丰富度下降。

### 11.2 授权交互流程（首次使用）

1. 进入 Step 3（对话式补充）时，检测到 `privacy.local_reading_enabled == false` 且从未询问过 → 展示授权弹窗。
2. 弹窗用通俗语言说明：「我会读取你授权文件夹里的文档来了解你的写作风格和兴趣，所有数据只存在你本地，不会上传。」
3. 用户二选一：
   - 「暂不开启」→ 保持轻量模式，继续问卷 + 对话流程；
   - 「开启并选择文件夹」→ 弹出系统文件夹选择器，用户主动指定目录。
4. 用户选定目录后，写入 `authorized_dirs`、`consented_at`、`consent_version`，置 `local_reading_enabled = true`，切换到完整模式。
5. 此后所有本地读取仅限 `authorized_dirs` 内，且只提取「写作风格 / 知识背景 / 关注领域 / 思考深度」的摘要特征，不复制原文、不回传。

### 11.3 最小权限原则

- 只读取用户主动指定的目录，绝不自动扫描全盘；
- 不递归跟随符号链接、不读取隐藏的系统目录；
- 只读不改：不修改、不移动、不删除用户原始文件；
- 只提取摘要特征，不复制文档原文到画像。

### 11.4 随时关闭与降级

- 设置中提供「一键关闭本地读取」：置 `local_reading_enabled = false`，模式降为 `light`；
- 关闭后 `authorized_dirs` 保留但不再读取，用户可清空；已提取的特征默认保留，用户可手动删除；
- 再次开启需重新确认并（可选）重新选择目录。

### 11.5 授权状态机

```
未授权(light) --用户主动勾选并选择目录--> 已授权(full)
已授权(full)  --一键关闭-->              已关闭(light，目录保留)
已关闭(light) --重新确认授权-->          已授权(full)
```

## 12. 数据治理

- **查看/编辑**：直接打开 `~/.creative-clone/profile.json` 即可；
- **删除**：删除该文件即清空画像；删除不可恢复，脚本应在删除前提示确认；
- **备份**：`init_profile.py --force` 重初始化前会把旧文件备份为 `.bak`；
- **写入安全**：所有写回均为「临时文件 + 原子替换」，避免进程中断导致画像损坏；
- **有界增长**：`history` 上限 500 条、`signals` 每类上限 50 条，超出删除最旧；
- **版本控制**：`schema_version` 固定为 1，未来字段变更需升版本并提供迁移脚本；
- **并发**：MVP 为单机单进程使用，脚本按「读-改-原子写」顺序执行，已足够；若未来多进程并发，再加文件锁。

## 13. 跨模型兼容性设计（GPT / Gemini / DeepSeek）

画像 Schema 同时是「数据契约」和「结构化输出契约」。为让「创意分身」在未来可以挂载到任一主流模型后端，Schema 按下述规则设计：

| 设计点 | 做法 | 依据 |
|--------|------|------|
| 字段命名 | 全部 snake_case | 与 GPT/DeepSeek 的 OpenAI 兼容生态一致，也符合 Gemini function calling 官方命名约定 |
| Schema 标准 | JSON Schema draft-07 | 三家结构化输出的最大公约数 |
| 严格模式 | 顶层 `additionalProperties:false` + `required` 齐全 | 满足 OpenAI GPT `response_format=json_schema` 严格模式要求 |
| 枚举优先 | 反馈、来源、模式等用 `enum`，不写自由字符串 | 减少模型漂移，三家均支持 `enum` |
| 可溯源偏好 | `source` + `evidence` + `confidence` | 借鉴 OpenAI Memory 的来源可展示，防止模型编造偏好 |
| 确定性脚本 | 画像读写走 Python 脚本，不交给 LLM | 模型不确定性不污染数据层（架构部 ADR-3） |
| 空值策略 | 模板用 `null` 占位；引擎产出补丁时「缺省字段」优于「显式 null」 | 规避部分后端对 union/null 的严格限制 |

后端挂载建议：

- **OpenAI GPT**：`response_format: {"type":"json_schema","json_schema":{"name":"profile_patch","strict":true,"schema":{...}}}`；
- **Google Gemini**：`responseMimeType: "application/json"` + `responseSchema`（OpenAPI 3.0 子集，已覆盖本 Schema 用到的 `type/properties/required/enum/items`）；
- **DeepSeek**：`response_format: {"type":"json_object"}`（OpenAI 兼容），新版可直接传 `json_schema`。

## 14. 与合规部（E）的数据范围对齐

为方便 E 部编写隐私政策，画像系统收集的数据范围明确如下：

| 数据类别 | 具体内容 | 是否上传 |
|---------|---------|---------|
| 用户主动提供 | 问卷回答、对话补充、反馈、选中的选题 | 否 |
| 授权后提取 | `authorized_dirs` 内文档/笔记/代码的「摘要特征」（写作风格、知识背景、关注领域、思考深度） | 否 |
| 技术元数据 | 文件路径、ISO 8601 时间戳、`schema_version` | 否 |

**明确不收集**：账号/身份信息（本地匿名 `local-anon`）、原始文档内容、网络请求日志、任何遥测。

## 15. 完整示例

### 15.1 完整模式画像示例（已授权、有历史）

```json
{
  "schema_version": 1,
  "profile_meta": {
    "user_id": "local-anon",
    "created_at": "2026-10-13T08:00:00+00:00",
    "updated_at": "2026-10-13T09:30:00+00:00",
    "mode": "full"
  },
  "base": {
    "language": "zh-CN",
    "backgrounds": ["历史学（本科）"],
    "interests": ["电子游戏", "罗马帝国", "《从<文明>系列游戏看大众对罗马帝国的认知偏差》"],
    "resources": ["可访问学校图书馆数据库", "一周可投入 12 小时"],
    "writing_style": "克制、偏好长句",
    "thinking_depth": "medium"
  },
  "preferences": [
    {
      "key": "tone_preference",
      "value": "严肃严谨",
      "confidence": 0.9,
      "source": "explicit",
      "scope": "cross_scenario",
      "scenario": null,
      "evidence": ["academic_paper:2026-10-13T08:05:00+00:00"],
      "updated_at": "2026-10-13T08:05:00+00:00"
    },
    {
      "key": "selected_topic",
      "value": "《从<文明>系列游戏看大众对罗马帝国的认知偏差》",
      "confidence": 0.9,
      "source": "explicit",
      "scope": "cross_scenario",
      "scenario": null,
      "evidence": ["academic_paper:2026-10-13T09:30:00+00:00"],
      "updated_at": "2026-10-13T09:30:00+00:00"
    }
  ],
  "history": [
    {
      "scenario": "academic_paper",
      "query": "历史学本科生，想在公选课交一份有网感的论文",
      "topic": "《从<文明>系列游戏看大众对罗马帝国的认知偏差》",
      "chosen_topics": ["《从<文明>系列游戏看大众对罗马帝国的认知偏差》"],
      "feedback": "select",
      "timestamp": "2026-10-13T09:30:00+00:00"
    }
  ],
  "signals": {
    "liked_topics": [],
    "disliked_topics": [],
    "redirected_topics": [],
    "selected_topics": ["《从<文明>系列游戏看大众对罗马帝国的认知偏差》"]
  },
  "stats": {
    "total_sessions": 0,
    "like_count": 0,
    "dislike_count": 0,
    "redirect_count": 0,
    "select_count": 1
  },
  "privacy": {
    "local_reading_enabled": true,
    "authorized_dirs": ["/Users/me/Documents/notes"],
    "consented_at": "2026-10-13T08:00:00+00:00",
    "consent_version": "1.0",
    "last_reviewed_at": null
  }
}
```

### 15.2 轻量模式画像示例（默认模板）

见 `assets/profile_template.json`，所有字段预定义、值为空（`[]` / `null` / 默认值）。

## 16. 验收对照（D 部验收标准）

| 验收标准 | 落地情况 |
|---------|---------|
| JSON Schema 字段完整，覆盖三重信息来源 | 见第 5、6、7 节 |
| 跨场景复用字段设计合理 | 见第 2、8 节（`base` + `preferences.scope`） |
| profile_template.json 通过 JSON 语法校验 | 已通过（`python3 -m json.tool` 校验） |
| init_profile.py 可独立运行，输出正确路径 | 见 `scripts/init_profile.py` |
| update_profile.py 可独立运行，正确更新 JSON | 见 `scripts/update_profile.py` |
| 授权机制符合 PRD 第七节 | 见第 11 节 |
| 脚本仅使用 Python 标准库 | `argparse`/`json`/`pathlib`/`datetime` 等，无第三方依赖 |
