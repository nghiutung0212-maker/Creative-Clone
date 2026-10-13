# Scene Profile File Format Spec

> This document defines the unified format for all scene profile files in the Creative Avatar Skill.
> Team B (Scene Library) writes each scene's JSON profile according to this spec.
> Later scenes are added by dropping in one JSON file in the same format; no core logic changes.

## File location

All scene profile files live under `assets/scene_profiles/`, one file per scene.

## File naming

`{scene_identifier}.json`, snake_case.

Examples: `academic_paper.json`, `short_video.json`, `event_planning.json`

## JSON schema

Every scene profile file must contain the following top-level fields:

```json
{
  "scene_id": "string, snake_case, matches the file name",
  "scene_name": "string, scene display name",
  "scene_description": "string, one-line description of the scene",
  "questionnaire_template": {
    "rounds": "array, rounds of step-by-step questions",
    "skip_logic": "object, logic jump rules"
  },
  "tone_rules": {
    "base_tone": "string, base tone for this scene",
    "allow_humor": "boolean, whether playful humor is allowed",
    "allow_informal": "boolean, whether informal wording is allowed",
    "tone_examples": "array, tone examples"
  },
  "constraint_list": "array, hard conditions topic ideas must satisfy in this scene",
  "exclusion_rules": "array, directions this scene actively avoids",
  "output_format_adjustments": {
    "title_format": "string, format template for the topic title",
    "extra_fields": "array, extra output fields this scene needs",
    "suppress_fields": "array, standard fields this scene may omit"
  }
}
```

## Field detail

### 1. questionnaire_template (questionnaire template)

Step-by-step follow-up logic; do not dump all questions at once.

```json
{
  "questionnaire_template": {
    "rounds": [
      {
        "round_id": 1,
        "questions": [
          {
            "field": "domain",
            "question": "What is your field / topic direction?",
            "type": "text",
            "required": true
          },
          {
            "field": "level",
            "question": "What is your education level?",
            "type": "choice",
            "options": ["undergraduate", "master's", "PhD", "other"],
            "required": true
          }
        ]
      },
      {
        "round_id": 2,
        "questions": [
          {
            "field": "length",
            "question": "Expected length / duration?",
            "type": "choice",
            "options": ["3-5 min presentation", "10-15 min presentation", "course paper", "graduation thesis"],
            "required": true,
            "condition": {
              "if": {"field": "level", "in": ["undergraduate", "master's"]},
              "then": "show",
              "else": "skip"
            }
          }
        ]
      }
    ],
    "skip_logic": {
      "description": "Skip or add questions based on prior answers",
      "rules": [
        "If the user picks 'undergraduate', skip PhD-level questions",
        "If the user picks 'short video', skip academic-increment questions, but ask about platform and audience"
      ]
    }
  }
}
```

### 2. tone_rules (tone rules)

```json
{
  "tone_rules": {
    "base_tone": "academic",
    "allow_humor": false,
    "allow_informal": false,
    "tone_examples": [
      "Good: this topic focuses on user behavior and has a testable research hypothesis",
      "Bad: this topic is super fun and will definitely go viral!"
    ]
  }
}
```

Three reference tones:

| Tone | allow_humor | allow_informal | When to use |
|------|-------------|----------------|---------|
| Academic | false | false | Papers, proposals, academic presentations |
| Playful | true | true | Short videos, podcasts, self-media |
| Formal | false | true | Startups, product plans, business reports |

### 3. constraint_list (hard constraints)

Hard conditions topic ideas **must satisfy** in this scene. The generation engine uses them as filters.

```json
{
  "constraint_list": [
    "Must have a concrete research object",
    "Must have a clear question (not a theme)",
    "Must have an actionable research method",
    "Must be within the user's ability / resources",
    "Must meet academic norms; citable and falsifiable"
  ]
}
```

### 4. exclusion_rules (exclusions)

Directions this scene should **actively avoid**, stacked with the global blacklist (`bad_topic_blacklist.md`).

```json
{
  "exclusion_rules": [
    "Pure literature-review topics (no incremental contribution)",
    "Overdone hot directions (saturation > 80%)",
    "Directions beyond an undergraduate's ability"
  ]
}
```

### 5. output_format_adjustments (output format tweaks)

Topic cards per scene may adjust presentation, but the four elements (concrete question / why it fits you / three angles / risk notes) cannot be dropped. Only extra fields may be added.

```json
{
  "output_format_adjustments": {
    "title_format": "\"{concrete question} (case study of {research object})\"",
    "extra_fields": ["suggested length", "reference-type requirements"],
    "suppress_fields": []
  }
}
```

## Adding a new scene

1. Create `{scene_id}.json` under `assets/scene_profiles/`
2. Fill in all fields per this spec
3. Append one row to the scene list in `references/scene_configs.md`
4. Done. No changes to SKILL.md or any engine logic.
