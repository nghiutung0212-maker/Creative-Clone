# 创意分身 Skill — 各部门交付规格书

> 本文档由架构部（A）产出，是所有后续部门的统一参考。
> 明确每个部门的产出文件放在哪、叫什么、格式要求是什么。

## 目录结构总览

```
creative-clone/
├── SKILL.md                              ← A 已建骨架，C/D/E 完善正文，上司最终整合
├── scripts/
│   ├── init_profile.py                   ← D 产出
│   └── update_profile.py                 ← D 产出
├── references/
│   ├── scene_format_spec.md              ← A 已交付（场景配置格式规范）
│   ├── scene_configs.md                  ← B 产出（场景库使用说明 + 扩展指南）
│   ├── engine_saturation_scan.md         ← C 产出（领域饱和扫描引擎）
│   ├── engine_cross_collision.md        ← C 产出（跨界知识碰撞引擎）
│   ├── engine_self_critique.md           ← C 产出（自我批判迭代引擎）
│   ├── bad_topic_blacklist.md           ← C 产出（五种烂选题黑名单）
│   ├── output_template.md                ← C 产出（选题输出四要素模板）
│   ├── profile_schema.md                 ← D 产出（画像 JSON Schema + 授权机制）
│   ├── privacy_policy.md                 ← E 产出（完整隐私政策）
│   ├── quality_standards.md             ← F 产出（选题质量评分卡）
│   ├── test_scenarios.md                ← F 产出（3 个场景测试用例）
│   └── acceptance_checklist.md          ← F 产出（PRD 验收清单）
├── assets/
│   ├── profile_template.json              ← D 产出（默认画像模板）
│   └── scene_profiles/
│       ├── academic_paper.json            ← B 产出
│       ├── ppt_presentation.json         ← B 产出
│       ├── short_video.json               ← B 产出
│       ├── wechat_article.json            ← B 产出
│       ├── startup_idea.json              ← B 产出
│       ├── event_planning.json            ← B 产出
│       ├── podcast.json                   ← B 产出
│       ├── course_design.json             ← B 产出
│       └── interview_outline.json         ← B 产出
├── README.md                              ← G 产出
├── LICENSE                                ← G 产出（MIT）
├── CONTRIBUTING.md                        ← G 产出
└── .gitignore                            ← G 产出
```

## 各部门交付规格

### B · 场景库部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 9 个场景配置 | `assets/scene_profiles/*.json` | JSON，严格遵守 `references/scene_format_spec.md` |
| 场景库说明 | `references/scene_configs.md` | Markdown |

### C · 引擎部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 饱和扫描引擎 | `references/engine_saturation_scan.md` | Markdown，含可直接执行的 Prompt |
| 跨界碰撞引擎 | `references/engine_cross_collision.md` | Markdown，含可直接执行的 Prompt |
| 自我批判引擎 | `references/engine_self_critique.md` | Markdown，含可直接执行的 Prompt |
| 烂选题黑名单 | `references/bad_topic_blacklist.md` | Markdown，5 种类型 + 定义 + 示例 |
| 输出模板 | `references/output_template.md` | Markdown，四要素 + ≥2 个完整示例 |

### D · 画像部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 画像 Schema | `references/profile_schema.md` | Markdown，含 JSON Schema 定义 + 授权机制 |
| 默认画像模板 | `assets/profile_template.json` | JSON，空值模板 |
| 初始化脚本 | `scripts/init_profile.py` | Python，可独立运行 |
| 更新脚本 | `scripts/update_profile.py` | Python，可独立运行 |

### E · 合规部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 隐私政策 | `references/privacy_policy.md` | Markdown |
| README 隐私草稿 | 交付时附在通知中 | Markdown 片段 |

### F · 验收部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 质量评分标准 | `references/quality_standards.md` | Markdown |
| 测试用例 | `references/test_scenarios.md` | Markdown |
| 验收清单 | `references/acceptance_checklist.md` | Markdown |

### G · 发布部

| 产出文件 | 路径 | 格式 |
|---------|------|------|
| 项目说明 | `README.md` | Markdown |
| 开源协议 | `LICENSE` | MIT 标准文本 |
| 贡献指南 | `CONTRIBUTING.md` | Markdown |
| Git 忽略 | `.gitignore` | 标准 gitignore |

## 命名规范

- 场景配置文件：`snake_case.json`（如 `academic_paper.json`）
- Reference 文件：`snake_case.md`（如 `engine_saturation_scan.md`）
- 脚本文件：`snake_case.py`
- 所有 JSON 文件必须通过 JSON 语法校验

## 交接方式

1. 每个部门完成后，将产出文件放到上述指定路径
2. 在交付时附一段简短说明：改了哪些文件、有没有偏离规格、有没有遗留 TODO
3. 交付给上司（整合阶段）做统一组装和打包验证
