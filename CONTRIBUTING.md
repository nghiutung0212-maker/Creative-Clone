# 贡献指南

感谢你对「创意分身」项目的关注！本文档说明如何参与贡献。

---

## 行为准则

- 尊重所有贡献者，不人身攻击、不歧视
- 讨论聚焦内容本身，对事不对人
- 发现安全或隐私问题请先私信维护者，不要在公开 Issue 中暴露

---

## 如何新增场景配置

新增场景是最高频的贡献方式，只需两步：

1. 在 `assets/scene_profiles/` 下新建 `{scene_id}.json`（蛇形命名）
2. 在 `references/scene_configs.md` 的场景索引表中追加一行

**配置文件必须包含 7 个顶层字段**：

```json
{
  "scene_id": "scene_identifier",
  "scene_name": "场景中文名",
  "scene_description": "一句话描述",
  "questionnaire_template": {
    "rounds": [],
    "skip_logic": { "rules": [] }
  },
  "tone_rules": {
    "base_tone": "严肃学术|轻松玩梗|商业正式",
    "allow_humor": false,
    "allow_informal": false,
    "tone_examples": []
  },
  "constraint_list": [],
  "exclusion_rules": [],
  "output_format_adjustments": {
    "title_format": "",
    "extra_fields": [],
    "suppress_fields": []
  }
}
```

**自检清单**：
- [ ] 文件名蛇形命名，且与 `scene_id` 完全一致
- [ ] 7 个顶层字段齐全
- [ ] 问卷分步进行，每轮 2-3 题
- [ ] `skip_logic.rules` 不少于 2 条
- [ ] 通过 `python3 -m json.tool` 语法校验

详见 [场景配置格式规范](references/scene_format_spec.md)。

---

## 如何改进引擎 Prompt

三引擎 Prompt 位于 `references/engine_*.md`，每个文件含系统提示词和用户输入模板。

改进原则：
1. **不破坏数据契约**：引擎间的 JSON 输入输出格式是核心契约，修改时确保上下游兼容
2. **保留反编造红线**：引擎 A 的证据要求与降级逻辑不可弱化
3. **保留 why_link 强制**：引擎 B 的逻辑关联筛选是防伪核心，不可省略
4. **不降闸门**：引擎 C 的 6 条硬约束与 pass_all 闸门不可放宽
5. **附测试**：改动后请用 `references/test_scenarios.md` 中的用例验证

---

## 如何报 Bug

1. 在 GitHub Issues 中搜索是否已有相同问题
2. 新建 Issue，请包含：
   - 复现步骤
   - 期望行为 vs 实际行为
   - 运行环境（操作系统、Python 版本、使用场景）
   - （如有）报错信息

> **请勿在 Issue 中粘贴你的画像原文（`~/.creative-clone/profile.json`）或任何敏感内容。**

---

## 如何提功能建议

1. 先在 Issues 中搜索是否已有类似建议
2. 新建 Issue，说明：
   - 解决什么问题
   - 建议的方案
   - 是否影响现有流程

---

## 代码风格

### Python 脚本

- 仅使用 Python 标准库，不引入第三方依赖
- 类型标注：使用 `from __future__ import annotations` + 内置类型
- 写入操作：始终使用「临时文件 + 原子替换」
- 命名：snake_case

### Markdown 文档

- 引用其他文件时使用相对路径
- 表格优先于纯文字描述
- 代码块标注语言

---

## 提交规范

```
<type>: <description>

types:
  feat:     新功能（如新增场景）
  fix:      修复 Bug
  docs:     文档改进
  refactor:  重构（不改变行为）
  test:     测试相关
  chore:    构建/工具/杂项
```

示例：
- `feat: 新增展览策划场景配置`
- `fix: 修复 update_profile.py 在画像不存在时的崩溃`
- `docs: 补充引擎 B 的碰撞算子示例`

---

## 开发流程

1. Fork 仓库
2. 创建分支：`git checkout -b feat/your-feature`
3. 提交改动
4. 推送到你的 Fork：`git push origin feat/your-feature`
5. 创建 Pull Request

PR 会经过以下检查：
- [ ] JSON 语法校验通过
- [ ] 脚本可独立运行
- [ ] 无隐私泄露（不包含画像原文、不引入上传代码）
- [ ] 文档引用路径正确

---

## 隐私与安全

如果你发现了隐私或安全相关问题：
- **不要**在公开 Issue 中提交
- 请直接私信仓库维护者
- 我们会在 48 小时内响应

关于隐私政策的任何修改，都需要升版 `consent_version` 并重新征求已授权用户的同意。
