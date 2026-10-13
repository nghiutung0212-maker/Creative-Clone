# 场景配置文件格式规范

> 本文档定义「创意分身」Skill 中所有场景配置文件的统一格式。
> B 部门（场景库部）按此规范编写每个场景的 JSON 配置文件。
> 后续新增场景也只需按此格式添加一个 JSON 文件，无需改动核心逻辑。

## 文件位置

所有场景配置文件放在 `assets/scene_profiles/` 目录下，一个场景一个文件。

## 文件命名

`{scene_identifier}.json`，使用蛇形命名法（snake_case）。

示例：`academic_paper.json`、`short_video.json`、`event_planning.json`

## JSON Schema

每个场景配置文件必须包含以下顶层字段：

```json
{
  "scene_id": "字符串，蛇形命名，与文件名一致",
  "scene_name": "字符串，场景中文名",
  "scene_description": "字符串，一句话描述该场景",
  "questionnaire_template": {
    "rounds": "数组，分步追问的轮次",
    "skip_logic": "对象，逻辑跳转规则"
  },
  "tone_rules": {
    "base_tone": "字符串，该场景的基础语气基调",
    "allow_humor": "布尔值，是否允许幽默玩梗",
    "allow_informal": "布尔值，是否允许非正式表达",
    "tone_examples": "数组，语气示例"
  },
  "constraint_list": "数组，该场景下选题必须满足的硬性条件",
  "exclusion_rules": "数组，该场景下应主动规避的方向",
  "output_format_adjustments": {
    "title_format": "字符串，选题标题的格式模板",
    "extra_fields": "数组，该场景额外需要的输出字段",
    "suppress_fields": "数组，该场景可以省略的标准字段"
  }
}
```

## 字段详细说明

### 1. questionnaire_template（问卷模板）

分步追问逻辑，不是一次性甩给用户所有问题。

```json
{
  "questionnaire_template": {
    "rounds": [
      {
        "round_id": 1,
        "questions": [
          {
            "field": "domain",
            "question": "你的学科领域 / 主题方向是什么？",
            "type": "text",
            "required": true
          },
          {
            "field": "level",
            "question": "你的学历层级是？",
            "type": "choice",
            "options": ["本科", "硕士", "博士", "其他"],
            "required": true
          }
        ]
      },
      {
        "round_id": 2,
        "questions": [
          {
            "field": "length",
            "question": "预期的篇幅 / 时长是？",
            "type": "choice",
            "options": ["3-5分钟汇报", "10-15分钟汇报", "课程论文", "毕业论文"],
            "required": true,
            "condition": {
              "if": {"field": "level", "in": ["本科", "硕士"]},
              "then": "show",
              "else": "skip"
            }
          }
        ]
      }
    ],
    "skip_logic": {
      "description": "根据前序回答跳过或追加问题",
      "rules": [
        "用户选「本科」→ 不问博士层级相关问题",
        "用户选「短视频」→ 不问学术增量要求，但问平台和受众"
      ]
    }
  }
}
```

### 2. tone_rules（语气规则）

```json
{
  "tone_rules": {
    "base_tone": "严肃学术",
    "allow_humor": false,
    "allow_informal": false,
    "tone_examples": [
      "正确示例：该选题聚焦于用户行为层面，具有可验证的研究假设",
      "错误示例：这个选题超有趣，绝对能火！"
    ]
  }
}
```

三种基调参考：
| 基调 | allow_humor | allow_informal | 适用场景 |
|------|-------------|----------------|---------|
| 严肃学术 | false | false | 论文、开题、学术汇报 |
| 轻松玩梗 | true | true | 短视频、播客、自媒体 |
| 商业正式 | false | true | 创业、产品方案、商业汇报 |

### 3. constraint_list（硬约束清单）

该场景下选题**必须满足**的硬性条件，生成引擎会将其作为过滤条件。

```json
{
  "constraint_list": [
    "必须有具体研究对象",
    "必须有明确的问题（不是主题）",
    "必须有可操作的研究方法",
    "必须在用户能力 / 资源范围内",
    "符合学术规范，可引用可证伪"
  ]
}
```

### 4. exclusion_rules（排斥项）

该场景下应**主动规避**的方向，与全局黑名单（`bad_topic_blacklist.md`）叠加生效。

```json
{
  "exclusion_rules": [
    "纯综述性选题（无增量贡献）",
    "已被做烂的热门方向（饱和度 > 80%）",
    "超出本科生能力范围的方向"
  ]
}
```

### 5. output_format_adjustments（输出格式微调）

不同场景的选题卡片可调整呈现方式，但四要素（具体问题 / 为什么适合你 / 三个切入角度 / 风险提醒）不可省略，只能追加额外字段。

```json
{
  "output_format_adjustments": {
    "title_format": "《{具体问题}——以{研究对象}为例》",
    "extra_fields": ["建议篇幅", "参考文献类型要求"],
    "suppress_fields": []
  }
}
```

## 新增场景流程

1. 在 `assets/scene_profiles/` 下新建 `{scene_id}.json`
2. 按本规范填写所有字段
3. 在 `references/scene_configs.md` 的场景列表中追加一行
4. 完成 — 无需改动 SKILL.md 或任何引擎逻辑
