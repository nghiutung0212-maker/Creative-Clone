# Creative Avatar Skill: User Profile Schema and Consent Mechanism

> This document is produced by Team D (Profile). It is the single data contract for the profile system and the input Team E (Compliance) used to write the privacy policy.
> Related deliverables: `assets/profile_template.json` (default profile template), `scripts/init_profile.py` (init script), `scripts/update_profile.py` (update script).

## 1. Purpose and responsibilities

The profile system answers one question: **what lets Creative Avatar fit you better over time?**

It is the product's long-term memory. It accumulates your cross-scenario thinking patterns, knowledge background, interest tendencies, and aesthetic judgments into one local JSON file that the three engines (saturation scan, cross-domain collision, self-critique iteration) read, so later topic ideas fit you better. It does not participate in any network transfer and does not upload to any server.

Core responsibilities:

- Collect and merge three information sources (local file reading, questionnaire answers, dialogue interaction);
- Accumulate preferences in a traceable, confidence-rated way, separating explicit preferences from inferred preferences;
- Support cross-scenario reuse: any scenario can reuse the same profile;
- Hold consent state; full and light mode can switch at any time;
- Fully local; viewable, editable, and deletable by the user at any time.

## 2. Design principles

Aligned with PRD design principle 2 (cross-scenario accumulation of the user profile) and architecture team chapter 7 "User profile data contract":

1. **Cross-scenario reuse**: preferences, style, and interests are not tied to any specific scenario. Short-term, scenario-level constraints use the `scope` / `scenario` fields and do not pollute the global profile.
2. **Traceable**: every preference carries `source` (explicit/inferred), `evidence`, and `confidence`. This borrows the traceable-source idea from OpenAI Memory and avoids "hallucinated preferences".
3. **Explicit first**: explicit preferences outrank inferred ones. Inferred preferences are written only when consistent evidence appears across sessions.
4. **Current request first**: when what the user says now conflicts with the stored profile, the current statement wins, and the confidence of the matching profile entry is lowered.
5. **Data minimization**: only fields needed to generate topic ideas are collected. There is no bulk accumulation of original text (`history` and `signals` are both capped).
6. **Local and transparent**: plain JSON stored locally, in `.gitignore`, open source and auditable.

## 3. Profile file and lifecycle

| Item | Description |
|------|-------------|
| Default path | `~/.creative-clone/profile.json` |
| Encoding | UTF-8 |
| Format | JSON (top level is an object; snake_case fields) |
| Initialize | On first use, copied from the template by `scripts/init_profile.py` |
| Update | After each feedback event, incrementally by `scripts/update_profile.py` |
| Privacy | All local, not committed to version control (must be in `.gitignore`) |

Lifecycle: `init_profile.py` creates the file -> the runtime reads a profile snapshot -> topic generation -> user feedback -> `update_profile.py` accumulates it -> reuse in the next round. Deleting the file clears the profile.

## 4. Top-level structure

| Top-level field | Type | Meaning |
|-----------------|------|---------|
| `schema_version` | integer | Profile format version; currently always 1 |
| `profile_meta` | object | Profile metadata (user id, timestamps, mode) |
| `base` | object | Base profile: knowledge background, interests, resources, writing style, thinking depth |
| `preferences` | array | Cross-scenario preference list (traceable) |
| `history` | array | Interaction history (one entry per feedback event, structured summary) |
| `signals` | object | Aggregated recent feedback signals (for correcting the next round's generation) |
| `stats` | object | Feedback counters |
| `privacy` | object | Consent and privacy state |

## 5. Full JSON Schema (draft-07)

This Schema is the machine-readable contract for the profile file. It is also the validation basis when the three engines produce profile patches in structured-output mode (see section 13, cross-model compatibility).

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://creative-clone.local/schemas/profile-schema.json",
  "title": "Creative Avatar User Profile Schema",
  "description": "Local user profile data contract, reused across scenarios, not uploaded to any server.",
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

## 6. Field details

### 6.1 profile_meta (metadata)

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Local anonymous id, fixed at `local-anon` (no account system) |
| `created_at` | string/null | Profile creation time (ISO 8601, UTC) |
| `updated_at` | string/null | Last update time |
| `mode` | enum | `full` (full mode) / `light` (light mode) |

### 6.2 base (base profile)

`base` is the static "who you are" face, reused across scenarios.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `language` | string | Default | Preferred language, default `zh-CN` |
| `backgrounds` | string[] | Questionnaire + local reading | Knowledge background / academic discipline / professional identity |
| `interests` | string[] | Questionnaire + feedback + local reading | Interest areas, focus areas (input for cross-domain collision) |
| `resources` | string[] | Questionnaire | Available resources, data, corpora (input for feasibility checks) |
| `writing_style` | string/null | Local reading (requires consent) | Writing style summary feature |
| `thinking_depth` | string/null | Local reading (requires consent) | Depth of thinking (suggested values: `shallow` / `medium` / `deep`) |

### 6.3 preferences (preference list)

An array of traceable preferences; this is the core of fitting you. Each preference:

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Preference key, e.g. `tone_preference`, `angle_style`, `selected_topic` |
| `value` | string | Preference value |
| `confidence` | number 0–1 | Confidence, default 0.5 |
| `source` | enum | `explicit` (user stated) / `inferred` |
| `scope` | string | `cross_scenario` (cross-scenario) / a specific scenario id |
| `scenario` | string/null | When `scope` is scenario-level, records the scenario id |
| `evidence` | string[] | Evidence supporting the preference (e.g. `academic_paper:2026-10-13T08:00:00+00:00`) |
| `updated_at` | string/null | Last update time |

### 6.4 history (interaction history)

One structured record per feedback event. No full original-text accumulation (capped at 500 entries; older ones deleted).

| Field | Type | Description |
|-------|------|-------------|
| `scenario` | string | Scenario id, e.g. `academic_paper` |
| `query` | string | Summary of the user's original request (may be empty) |
| `topic` | string | This round's topic idea |
| `chosen_topics` | string[] | Finally selected topics (non-empty only when `select`) |
| `feedback` | enum | `like` / `dislike` / `redirect` / `select` |
| `timestamp` | string/null | Timestamp (ISO 8601, UTC) |

### 6.5 signals (feedback signal aggregation)

A lightweight aggregation window of recent feedback (50 entries per category, keeping only recent signals), used at Step 6 to adjust the next round:

| Field | Description |
|-------|-------------|
| `liked_topics` | Recent topics marked "interesting" |
| `disliked_topics` | Recent topics with "show another batch" |
| `redirected_topics` | Recent topics with "wrong direction" |
| `selected_topics` | Recent finally selected topics |

### 6.6 stats (counters)

`total_sessions`, `like_count`, `dislike_count`, `redirect_count`, `select_count`, all non-negative integers, used for the profile panel and trend display.

### 6.7 privacy (consent and privacy)

| Field | Type | Description |
|-------|------|-------------|
| `local_reading_enabled` | boolean | Whether local file reading is on |
| `authorized_dirs` | string[] | Directories the user explicitly authorized (least privilege) |
| `consented_at` | string/null | Last consent confirmation time |
| `consent_version` | string/null | Consent notice version |
| `last_reviewed_at` | string/null | Last time the user viewed consent settings |

## 7. Three information-source mapping

Aligned with PRD section 5 module 2. How the three profile sources map to written fields:

| Source | How collected | What collected | Fields written | Consent required? |
|--------|---------------|----------------|----------------|-------------------|
| Local file reading | Reads documents/notes/code in user-authorized directories | Writing style, knowledge background, interests, depth of thinking | `base.backgrounds`, `base.interests`, `base.writing_style`, `base.thinking_depth` | Explicit check required |
| Questionnaire answers | Scenario questionnaire at each ideation | Current scenario preferences, constraints, interests | `preferences` (`source=explicit`, may carry `scenario`), `base.*` | No consent |
| Dialogue interaction | Feedback and follow-up questions during ideation | Aesthetic tendencies, criteria for "good topic ideas", historical topic records | `history`, `signals`, `stats`, `preferences` (`source=inferred`) | No consent |

## 8. Cross-scenario reuse design

Cross-scenario reuse hinges on separating "global fields" from "scenario fields":

- **Global fields**: `base`, `preferences` (`scope=cross_scenario`), `signals`, `stats` — shared by every scenario. For example, an interest accumulated in the paper scenario ("interests: video games") can feed cross-domain collision in the short-video scenario.
- **Scenario fields**: `preferences` entries whose `scope` is a specific scenario id, plus `history.scenario` — they apply only to that scenario, so scenario preferences do not leak across.
- **Upgrade path**: if a scenario-level preference gets consistent evidence across multiple scenarios, it can be upgraded to a cross-scenario preference (R2 in section 9).

## 9. Read/write and priority rules

Profile reads and writes follow six rules (aligned with architecture team chapter 7):

| # | Rule | Meaning |
|---|------|---------|
| R1 | Explicit over inferred | `source=explicit` preferences outrank `inferred` ones |
| R2 | Inferred needs consistent evidence | An inferred preference is written only after at least two independent supports across sessions; a single feedback goes only to `history` |
| R3 | Current request over stored | When the current statement conflicts with the profile, the current one wins and the matching entry's confidence drops |
| R4 | Locally manageable | Plain JSON; viewable/editable/deletable. Deletion is irreversible and requires confirmation. |
| R5 | Batch writes | Updates happen at the end of each round; no writes mid-generation to avoid interference |
| R6 | Minimized collection | Write only fields declared in the scene profile's `profile.capture` and feedback signals |

## 10. Feedback types and update logic

`scripts/update_profile.py` updates fields by feedback type. The feedback enum matches both UI labels and script parameters:

| Parameter | UI label | Update action |
|-----------|----------|---------------|
| `like` | This is interesting | Append to `history`, `signals.liked_topics`; `stats.like_count + 1` |
| `dislike` | Show another batch | Append to `history`, `signals.disliked_topics`; `stats.dislike_count + 1` |
| `redirect` | Wrong direction | Append to `history`, `signals.redirected_topics`; `stats.redirect_count + 1` |
| `select` | Final pick | Append to `history` (with `chosen_topics`), `signals.selected_topics`, `stats.select_count + 1`; accumulate the selected topic into `base.interests` and `preferences` (`selected_topic`, `source=explicit`, `confidence=0.9`) |

All feedback refreshes `profile_meta.updated_at` to the current time. Writes use temp file + atomic replace to avoid a half-written corrupted profile.

## 11. Consent mechanism design

### 11.1 Two modes

| Mode | Data sources | Profile richness |
|------|--------------|------------------|
| Full mode (`full`) | Local file reading + questionnaire + dialogue | High |
| Light mode (`light`) | Questionnaire + dialogue only | Basic |

Light mode is the default. After consent is revoked, it falls back to light mode automatically. The core flow is unaffected; only profile richness drops.

### 11.2 Consent interaction (first run)

1. When entering Step 3 (follow-up dialogue), detect `privacy.local_reading_enabled == false` and no prior consent -> show the consent popup.
2. The popup says in plain language: "I will read documents in the folders you authorize to learn your writing style and interests. All data stays on your machine and is never uploaded."
3. The user chooses one of two:
   - "Not now" -> stay in light mode, continue questionnaire + dialogue;
   - "Turn on and pick a folder" -> show the system folder picker; the user picks a directory.
4. After the user picks a directory, write `authorized_dirs`, `consented_at`, `consent_version`, set `local_reading_enabled = true`, switch to full mode.
5. From then on, local reading is limited to `authorized_dirs`, extracting only the "writing style / knowledge background / interests / depth of thinking" summary features. No original text is copied and nothing is sent back.

### 11.3 Least privilege

- Read only directories the user explicitly picks; never auto-scan the whole disk;
- Do not recursively follow symlinks; do not read hidden system directories;
- Read-only: do not modify, move, or delete the user's original files;
- Extract summary features only; do not copy document original text into the profile.

### 11.4 Revoke anytime and degrade

- Settings offers a one-click "turn off local reading": set `local_reading_enabled = false`, mode drops to `light`;
- After turn-off, `authorized_dirs` is kept but no longer read; the user can clear it. Extracted features are kept by default and the user can delete them manually;
- Turning back on requires re-confirmation and (optionally) re-picking a directory.

### 11.5 Consent state machine

```
unauthorized(light) --user checks and picks a directory--> authorized(full)
authorized(full)  --one-click off-->                       closed(light, directory kept)
closed(light)     --re-confirm consent-->                   authorized(full)
```

## 12. Data governance

- **View/edit**: open `~/.creative-clone/profile.json` directly;
- **Delete**: deleting the file clears the profile. Deletion is irreversible; scripts should prompt for confirmation before deleting;
- **Backups**: before `init_profile.py --force` re-initializes, the old file is backed up to `.bak`;
- **Write safety**: all writes use temp file + atomic replace, so an interrupted process cannot corrupt the profile;
- **Bounded growth**: `history` capped at 500 entries, `signals` at 50 per category; older entries are deleted;
- **Versioning**: `schema_version` is fixed at 1. Future field changes require a version bump and a migration script;
- **Concurrency**: the MVP is single-machine, single-process. Scripts run read-modify-atomic-write in order, which is enough. Add file locks later if multi-process concurrency is needed.

## 13. Cross-model compatibility (GPT / Gemini / DeepSeek)

The profile Schema is both a "data contract" and a "structured output contract". To let Creative Avatar mount onto any major model backend in the future, the Schema follows these rules:

| Design point | Approach | Rationale |
|--------------|----------|-----------|
| Field naming | All snake_case | Matches the OpenAI-compatible ecosystem of GPT/DeepSeek and Gemini's official function-calling naming conventions |
| Schema standard | JSON Schema draft-07 | The common denominator across all three structured-output modes |
| Strict mode | Top-level `additionalProperties:false` + full `required` list | Meets OpenAI GPT `response_format=json_schema` strict mode |
| Enums first | Feedback, source, mode, etc. use `enum`, not free strings | Reduces model drift; all three support `enum` |
| Traceable preferences | `source` + `evidence` + `confidence` | Borrows the traceable-source idea from OpenAI Memory; prevents the model from inventing preferences |
| Deterministic scripts | Profile reads/writes go through Python scripts, not the LLM | Model uncertainty does not leak into the data layer (architecture team ADR-3) |
| Null policy | The template uses `null` placeholders; when engines produce patches, "omitted fields" are preferred over "explicit null" | Avoids strict union/null limits in some backends |

Backend mounting notes:

- **OpenAI GPT**: `response_format: {"type":"json_schema","json_schema":{"name":"profile_patch","strict":true,"schema":{...}}}`;
- **Google Gemini**: `responseMimeType: "application/json"` + `responseSchema` (OpenAPI 3.0 subset, covering the `type/properties/required/enum/items` used by this Schema);
- **DeepSeek**: `response_format: {"type":"json_object"}` (OpenAI-compatible); newer versions can pass `json_schema` directly.

## 14. Data-scope alignment with Team E (Compliance)

To help Team E write the privacy policy, the profile system's collected data scope is defined as follows:

| Data category | Specific content | Uploaded? |
|---------------|------------------|-----------|
| Provided by the user | Questionnaire answers, follow-up dialogue, feedback, selected topic ideas | No |
| Extracted after consent | "Summary features" from documents/notes/code in `authorized_dirs` (writing style, knowledge background, interests, depth of thinking) | No |
| Technical metadata | File paths, ISO 8601 timestamps, `schema_version` | No |

**Explicitly not collected**: account/identity information (local anonymous `local-anon`), original document content, network request logs, any telemetry.

## 15. Full examples

### 15.1 Full-mode profile example (consented, with history)

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
    "backgrounds": ["History (BA)"],
    "interests": ["video games", "Roman Empire", "Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university"],
    "resources": ["school library database access", "12 hours per week available"],
    "writing_style": "restrained, prefers long sentences",
    "thinking_depth": "medium"
  },
  "preferences": [
    {
      "key": "tone_preference",
      "value": "serious and rigorous",
      "confidence": 0.9,
      "source": "explicit",
      "scope": "cross_scenario",
      "scenario": null,
      "evidence": ["academic_paper:2026-10-13T08:05:00+00:00"],
      "updated_at": "2026-10-13T08:05:00+00:00"
    },
    {
      "key": "selected_topic",
      "value": "Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university",
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
      "query": "History undergrad, wants a course paper with some pop-culture appeal for an elective",
      "topic": "Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university",
      "chosen_topics": ["Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university"],
      "feedback": "select",
      "timestamp": "2026-10-13T09:30:00+00:00"
    }
  ],
  "signals": {
    "liked_topics": [],
    "disliked_topics": [],
    "redirected_topics": [],
    "selected_topics": ["Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university"]
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

### 15.2 Light-mode profile example (default template)

See `assets/profile_template.json`. All fields are pre-defined with empty values (`[]` / `null` / defaults).

## 16. Acceptance checklist (Team D criteria)

| Acceptance criterion | Status |
|----------------------|--------|
| JSON Schema is complete and covers the three information sources | See sections 5, 6, 7 |
| Cross-scenario reuse fields are well designed | See sections 2, 8 (`base` + `preferences.scope`) |
| profile_template.json passes JSON syntax validation | Passed (`python3 -m json.tool`) |
| init_profile.py runs standalone and prints the correct path | See `scripts/init_profile.py` |
| update_profile.py runs standalone and updates JSON correctly | See `scripts/update_profile.py` |
| Consent mechanism meets PRD section 7 | See section 11 |
| Scripts use only the Python standard library | `argparse`/`json`/`pathlib`/`datetime`, etc.; no third-party dependencies |
