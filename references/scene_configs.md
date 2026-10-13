# Scene Library Guide

> This document is produced by Team B (Scene Library). It is the usage and extension guide for the Creative Avatar scene library.
> The field format bible for scene profiles is [`scene_format_spec.md`](./scene_format_spec.md). This document explains what the current scene library contains, how it is loaded at runtime, and how to add a new scene.

---

## 1. What the scene library is

The scene library is the configuration layer that lets Creative Avatar do **scene adaptation** (core design principle 1) and **extensible scene dimensions** (core design principle 5):

- One scene = one standalone JSON configuration file.
- Each file declares the step-by-step questionnaire, tone, hard constraints, exclusions, and output format tweaks for that scene.
- The three engines and the main flow are **not aware of any specific scene**. All scene differences are injected by configuration. Adding a scene means adding one JSON file; no core logic changes.

---

## 2. Index of currently supported scenes (9)

Configuration files live in `assets/scene_profiles/`.

| # | scene_id | Scene name | Base tone | Allow humor | Allow informal | One-line description |
|---|----------|------------|--------------|:--------:|:----------:|------------|
| 1 | `academic_paper` | Academic paper topic ideas | Academic | No | No | Topic ideas for course papers, thesis, proposal, journal submission, and grant applications. Reference configuration. |
| 2 | `ppt_presentation` | PPT presentation topic ideas | Formal | No | Yes | Topics for course presentations, defense, work reports, pitches, and conference sharing. |
| 3 | `short_video` | Short video topic ideas | Playful | Yes | Yes | Topic ideas, hooks, and shooting formats for videos under three minutes. |
| 4 | `wechat_article` | WeChat article topic ideas | Formal | No | Yes | Opinion pieces, tutorials, industry analysis, stories, and hot-topic takes. |
| 5 | `startup_idea` | Startup direction topic ideas | Formal | No | Yes | Startup ideas, product direction, and business opportunities, with an MVP validation path. |
| 6 | `event_planning` | Event planning topic ideas | Playful | Yes | Yes | Campus clubs, team building, business events, salons, competitions, and online events. |
| 7 | `podcast` | Podcast topic ideas | Playful | Yes | Yes | Episode topics, discussion points, and show planning. |
| 8 | `course_design` | Course design topic ideas | Academic | No | No | Teaching design for a single lesson, a unit, or a whole course. |
| 9 | `interview_outline` | Interview outline | Formal | No | Yes | Question lists for profiles, industry / event / promotion interviews. |

> All three tones are covered: **academic** (papers, course design), **playful** (short videos, events, podcasts), and **formal** (PPT, WeChat articles, startups, interviews).

---

## 3. File location and naming

- Directory: `assets/scene_profiles/`
- File name: `{scene_id}.json`, snake_case. The `scene_id` field inside the file must match the file name without `.json`.
- Example: `academic_paper.json` matches `"scene_id": "academic_paper"`.

---

## 4. How scene profiles are loaded at runtime

### 4.1 Loading points (mapped to the 6-step loop)

```
Step 1 Pick a scenario
  ├─ User picks from the scene menu, or describes the scene in free text
  ├─ Load assets/scene_profiles/{scene_id}.json
  └─ Validate: valid JSON syntax + all 7 top-level fields present + scene_id matches file name
        └─ Only after validation passes, enter Step 2
Step 2 Scenario questionnaire
  ├─ Ask questions round by round per questionnaire_template.rounds (2-3 per round)
  ├─ Before rendering each question, evaluate condition to decide show / skip
  └─ After each round, check skip_logic.rules to decide whether to add or drop questions
Step 3 Follow-up dialogue
  └─ Use the questionnaire answers and local profile to ask 3-5 follow-up questions for profile gaps (see profile_schema.md)
Step 4 Topic generation (three engines)
  ├─ constraint_list → used as hard filters on generated results
  ├─ exclusion_rules → combined with the global blacklist to form avoid directions
  └─ tone_rules      → used as the tone / register basis for generation and review
Step 5 Output topic ideas
  └─ Adjust title format and add / drop fields per output_format_adjustments
Step 6 Feedback loop
  └─ Questionnaire answers and the selected topic idea are saved into the user profile (reused across scenes)
```

### 4.2 How each top-level field is consumed

| Top-level field | Type | Consumer | Purpose |
|----------|------|--------|------|
| `scene_id` | string | Routing / main flow | Unique scene identifier; must match file name. |
| `scene_name` | string | Scene menu | Name shown to users in the menu. |
| `scene_description` | string | Scene menu / routing | One-line description; helps users judge and assists matching. |
| `questionnaire_template` | object | Step 2 questionnaire | `rounds` defines step-by-step questions; `skip_logic` defines jump rules. |
| `tone_rules` | object | Step 4 / 5 | Base tone, whether humor / informal is allowed, positive and negative tone examples. |
| `constraint_list` | array | Three engines | Hard conditions topic ideas **must satisfy**; used as filters. |
| `exclusion_rules` | array | Three engines | Directions this scene **actively avoids**. |
| `output_format_adjustments` | object | Step 5 output | Title template, extra fields, droppable fields. |

---

## 5. The three tones

| Tone | allow_humor | allow_informal | Scenarios covered |
|------|:-----------:|:--------------:|----------|
| Academic | false | false | Academic papers, course design |
| Playful | true | true | Short videos, event planning, podcasts |
| Formal | false | true | PPT presentations, WeChat articles, startup directions, interview outlines |

Additional rules:

- Tone is a **default**, not a hard rule. Most `tone_rules` include `conditional_notes`. When the user's questionnaire answers express a different tone (for example, a course presentation that wants to be playful, or a WeChat article that wants deep long-form prose), the **user's current request wins** and the tone switches per the conditional notes.
- No tone may break legal or platform compliance. Humor must not be used to insult, discriminate, start a fight, or weaken evidence.

---

## 6. Step-by-step questionnaire and skip logic

### 6.1 Step-by-step follow-up

- The questionnaire proceeds round by round, in the `round_id` order in `questionnaire_template.rounds`.
- Each round has 2-3 questions. The user answers one round before the next starts; all questions are not dumped at once.
- Each question declares `field` (field name), `question` (prompt text), `type` (`text` / `choice`), `required`, and `options` (for choice questions).

### 6.2 Conditional rendering (condition)

Per-question show / hide is declared with `condition`, in a fixed shape:

```json
"condition": {
  "if": {"field": "level", "in": ["master's thesis", "PhD thesis"]},
  "then": "show",
  "else": "skip"
}
```

Before each render, the condition is evaluated against collected answers. Questions with no `condition` are always shown.

### 6.3 Skip rules (skip_logic)

`questionnaire_template.skip_logic.rules` declares cross-round additions, drops, and generation constraints in natural language. Each scene has **at least 2** skip rules. Typical patterns:

- **Level jump**: user picks "course paper" → do not ask PhD-level theoretical-contribution requirements.
- **Goal jump**: user picks "e-commerce" → add product information and ad-compliance risk notes.
- **Resource jump**: user already has a dataset → do not ask about data availability; prefer reuse.
- **Duration jump**: duration is very short → keep only a single point and a single topic.

---

## 7. How constraints and exclusions stack

At generation time, exclusion conditions stack in the following order; later layers are stricter:

1. **Global blacklist**: the five bad-topic types defined in `bad_topic_blacklist.md` (concept stacking, over-saturation, infeasible, too broad, false question), applied to all scenes.
2. **Scene exclusions**: directions in the current scene's `exclusion_rules`, stacked on top of the global blacklist.
3. **User-stated exclusions**: exclusions / taboos the user writes in the questionnaire (such as `excludes`, `red_lines`).
4. **Scene hard constraints**: `constraint_list` is a positive filter. Topic ideas that fail are rejected outright and do not enter the output.

---

## 8. Output format tweaks

- The four elements (concrete question / why it fits you / three angles to approach it / risk notes) **cannot be dropped in any scene**.
- `output_format_adjustments.title_format` defines the title template. For example, the paper scene uses `"{concrete question} (case study of {research object})"`.
- `extra_fields` declares scene-specific added fields (for example, short video adds "first-3-second hook"; startup adds "MVP validation path").
- `suppress_fields` declares standard fields that may be omitted. All 9 current scenes keep this empty, so the four elements are fully retained.

---

## 9. How to add a new scene

> Goal: adding a scene = adding one JSON file + appending one row to the index in this file. No changes to SKILL.md or any engine logic.

### 9.1 Steps

1. **Create the file**: add `{scene_id}.json` under `assets/scene_profiles/`. Use snake_case for `scene_id` (for example, `exhibition_curation.json`).
2. **Fill in the configuration**: follow [`scene_format_spec.md`](./scene_format_spec.md) strictly and fill all 7 top-level fields:
   - `scene_id`, `scene_name`, `scene_description`;
   - `questionnaire_template`: design by rounds, 2-3 questions per round;
   - `tone_rules`: pick a base tone that fits the scene;
   - `constraint_list`, `exclusion_rules`;
   - `output_format_adjustments`.
3. **Design skip logic**: the questionnaire must include at least 2 `skip_logic` rules. Use `condition` when per-question show / hide is needed.
4. **Validate syntax**: run JSON validation (see 9.3).
5. **Register in the index**: append one row to the index table in section 2 of this file.
6. **Done**: no changes to SKILL.md, engines, or profile code. If a new capability cannot be expressed by the current configuration, submit it for architecture review first; do not change core logic directly.

### 9.2 New-scene checklist

- [ ] File name is snake_case and exactly matches `scene_id`
- [ ] All 7 top-level fields present; question fields (field / question / type / required) complete
- [ ] Questionnaire proceeds by rounds, 2-3 questions per round, not all at once
- [ ] `skip_logic.rules` has at least 2 entries; condition structure is correct
- [ ] Base tone fits the scene; `tone_examples` includes both positive and negative examples
- [ ] `constraint_list` is executable and filterable; `exclusion_rules` does not conflict with the global blacklist
- [ ] Output keeps the four elements; `extra_fields` only adds, never drops
- [ ] Passes JSON syntax validation
- [ ] Registered in the `scene_configs.md` index table

### 9.3 Validation commands

```bash
# Validate a single scene profile
python3 -m json.tool assets/scene_profiles/{scene_id}.json > /dev/null && echo OK

# Validate the whole scene library in one pass
for f in assets/scene_profiles/*.json; do python3 -m json.tool "$f" > /dev/null || echo "BAD: $f"; done
```

---

## 10. Relationship with other files

| File | Relationship |
|------|------|
| `references/scene_format_spec.md` | Field format spec for scene profiles (produced by Team A). This file is its companion usage guide. |
| `references/bad_topic_blacklist.md` | Global bad-topic blacklist; stacked with each scene's `exclusion_rules`. |
| `references/engine_*.md` | The three engines; consume the questionnaire answers, constraints, exclusions, and tone rules from the configuration. |
| `references/output_template.md` | Four-element output template; adjusted by `output_format_adjustments`. |
| `references/profile_schema.md` | User profile; questionnaire answers and selected topic ideas are saved here across scenes. |
| `SKILL.md` | Entry document; Steps 1 / 2 reference this scene library. |

---

## 11. Delivery notes (Team B, Scene Library)

- **Deliverables**: 9 scene profile JSON files under `assets/scene_profiles/` plus this document `references/scene_configs.md`.
- **Spec compliance**: all configurations strictly follow the 7 top-level fields in `scene_format_spec.md`. The paper reference configuration covers all 8 questionnaire dimensions in PRD module 1. Each scene has at least 2 skip rules. All three tones are covered.
- **Outstanding TODO**: none. The final menu copy is wired into SKILL.md during integration; it does not affect the configuration itself.
