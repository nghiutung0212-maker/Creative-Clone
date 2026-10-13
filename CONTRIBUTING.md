# Contributing

Thanks for your interest in Creative Avatar. This guide explains how to contribute.

---

## Code of conduct

- Respect all contributors; no personal attacks, no discrimination
- Focus discussion on the work, not the person
- If you find a security or privacy issue, contact the maintainer privately first; do not disclose it in a public issue

---

## How to add a scene profile

Adding a scenario is the most common contribution. It takes two steps:

1. Create `{scene_id}.json` under `assets/scene_profiles/` (snake_case naming)
2. Append one row to the scenario index table in `references/scene_configs.md`

**The file must contain these 7 top-level fields**:

```json
{
  "scene_id": "scene_identifier",
  "scene_name": "human-readable scenario name",
  "scene_description": "one-line description",
  "questionnaire_template": {
    "rounds": [],
    "skip_logic": { "rules": [] }
  },
  "tone_rules": {
    "base_tone": "academic|playful|formal",
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

**Self-check list**:
- [ ] File name is snake_case and exactly matches `scene_id`
- [ ] All 7 top-level fields are present
- [ ] Questionnaire runs in steps, 2-3 questions per round
- [ ] `skip_logic.rules` has at least 2 entries
- [ ] Passes `python3 -m json.tool` syntax check

See [scene profile format spec](references/scene_format_spec.md).

---

## How to improve engine prompts

The three engine prompts live in `references/engine_*.md`. Each file contains the system prompt and the user-input template.

Guidelines:
1. **Do not break the data contract**: the JSON input/output format between engines is the core contract; keep changes backwards-compatible
2. **Keep the no-fabrication rule**: Engine A's evidence requirements and fallback logic must not be weakened
3. **Keep the mandatory why_link**: Engine B's logical-link filter is the core anti-fabrication step; do not remove it
4. **Do not lower the gate**: Engine C's six hard constraints and the pass_all gate must not be relaxed
5. **Add tests**: verify your change with the cases in `references/test_scenarios.md`

---

## How to report a bug

1. Search GitHub Issues for an existing report
2. Open a new issue and include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Runtime environment (OS, Python version, scenario used)
   - Error message, if any

> **Do not paste your raw profile (`~/.creative-clone/profile.json`) or any sensitive content into an issue.**

---

## How to suggest a feature

1. Search Issues for a similar suggestion first
2. Open a new issue describing:
   - What problem it solves
   - The proposed solution
   - Whether it changes the existing flow

---

## Code style

### Python scripts

- Use only the Python standard library; no third-party dependencies
- Type hints: use `from __future__ import annotations` with built-in types
- Writes: always use temp file + atomic replace
- Naming: snake_case

### Markdown docs

- Use relative paths when linking to other files
- Prefer tables over prose
- Mark code blocks with a language tag

---

## Commit conventions

```
<type>: <description>

types:
  feat:     new feature (e.g. adding a scenario)
  fix:      bug fix
  docs:     documentation changes
  refactor: refactor (no behavior change)
  test:     test-related
  chore:    build / tooling / misc
```

Examples:
- `feat: add exhibition planning scene profile`
- `fix: fix update_profile.py crash when the profile does not exist`
- `docs: add examples of Engine B collision operators`

---

## Development workflow

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit your changes
4. Push to your fork: `git push origin feat/your-feature`
5. Open a pull request

The PR will be checked against:
- [ ] JSON syntax check passes
- [ ] Scripts run standalone
- [ ] No privacy leak (no raw profile content, no upload code)
- [ ] Documentation links resolve

---

## Privacy and security

If you find a privacy or security issue:
- **Do not** file it in a public issue
- Contact the repository maintainer directly
- We will respond within 48 hours

Any change to the privacy policy requires bumping `consent_version` and re-requesting consent from users who have already authorized.
