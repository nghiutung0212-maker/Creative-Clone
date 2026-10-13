---
name: creative-clone
description: >-
  Creative Avatar: a general topic-ideation skill for any scenario. Trigger when
  the user needs to come up with topic ideas from scratch, find angles, or find
  a direction. Covers academic papers, PPT presentations, short videos, WeChat
  articles, startup ideas, event planning, podcast topics, exhibition planning,
  course design, and interview outlines. Uses a scenario questionnaire, a local
  profile of the user's feedback, and three generation engines to produce
  original, actionable topic ideas: a saturation scan flags overdone directions,
  cross-domain collision finds new angles, and self-critique iteration polishes
  the results. The profile accumulates the user's feedback over time, so later
  topic ideas fit the user better.
agent_created: true
---

# Creative Avatar: General-Purpose Topic Ideation Skill

## What this is

Creative Avatar keeps a local profile of the user's feedback and uses it on every run, instead of answering from a generic prompt.

- **Matches how you think**: it does not output generic answers; it matches your thinking style, knowledge background, and interests
- **Finds real gaps**: no templates, no buzzword stacking; it looks for gaps in the field and counter-consensus angles
- **Keeps the right tone**: it switches between open brainstorming and grounded rigor depending on the scenario

---

## Core workflow (6-step loop)

### Step 1: Pick a scenario

The user picks or describes their scenario when they start. The Skill loads the matching scene profile.

**9 scenarios are supported** (profile files under `assets/scene_profiles/*.json`):

| Scenario | scene_id | Tone | What it covers |
|----------|----------|------|---------|
| Academic paper | `academic_paper` | Academic | Course papers, thesis, proposal, journal submission |
| PPT presentation | `ppt_presentation` | Formal | Course presentation, defense, work report, pitch |
| Short video | `short_video` | Playful | Topic ideas for Douyin / Kuaishou / Bilibili / Xiaohongshu |
| WeChat article | `wechat_article` | Formal | Opinion pieces, tutorials, industry analysis |
| Startup idea | `startup_idea` | Formal | Startup ideas, product direction, business opportunities |
| Event planning | `event_planning` | Playful | Campus clubs, team building, business events, salons |
| Podcast | `podcast` | Playful | Episode topics, discussion points |
| Course design | `course_design` | Academic | Single lesson, unit, or whole course design |
| Interview outline | `interview_outline` | Formal | Profiles, industry / event interviews |

**Selection flow**:

1. Show the menu above; the user picks an option or describes their scenario in free text
2. If the user describes the scenario in free text: match the closest scene_id by keywords. If no match, fall back to general mode and tune the questionnaire to the closest scenario
3. Load `assets/scene_profiles/{scene_id}.json`
4. Validate: valid JSON syntax, all 7 top-level fields present, scene_id matches the file name. Then move to Step 2.

> See `references/scene_format_spec.md` for the scene profile format spec.
> See `references/scene_configs.md` for the scene library guide and extension notes.
> **To add a scenario, add one JSON file and append one row to the scene library index; no core logic changes.**

### Step 2: Scenario questionnaire

The Skill asks the questions from the scenario's questionnaire template step by step (2-3 questions per round). Questions have conditional jumps between them.

**Questionnaire dimensions** (each scenario uses a subset; the academic paper scenario is the most complete):

| Dimension | What it means | Example |
|------|------|------|
| Discipline / field | Core direction | Communication studies, modern Chinese history |
| Level / stage | Academic level or account stage | Course paper / zero-follower cold start |
| Research type / format | Method or content form | Empirical / quantitative / talking-head video |
| Length / duration | Output size | 3000-5000 words / 30-60 seconds |
| Tone | Voice preference | Academic / playful |
| Interests | Inputs for cross-domain collision | Video games, cat ownership, band culture |
| Resources | Available data / channels / equipment | Library databases / one person with a phone |
| Hard constraints | Required conditions | Advisor-assigned direction / 500 RMB budget |
| Exclusions | Directions the user explicitly does not want | Pure literature review / flame-bait topics |

**Skip logic** (declared in each scenario's `skip_logic.rules`, at least 2 rules):

- **Level jump**: if "course paper" is picked, do not ask about PhD-level theoretical contribution
- **Goal jump**: if "product sales" is picked, ask for product details and add an advertising-law compliance reminder
- **Resource jump**: if the user already states they have a dataset, do not ask about data availability
- **Duration jump**: if "under 30 seconds" is picked, give one single point per topic idea
- **Platform jump**: if "Xiaohongshu" is picked, prefer photo or image-text formats and add hashtag suggestions

**Execution**: ask rounds in the order of `round_id` in `questionnaire_template.rounds`; evaluate each question's `condition` before rendering it to decide show/skip; after each round, check `skip_logic.rules` to decide whether to add or drop questions.

### Step 3: Follow-up dialogue

After the questionnaire, the Skill asks 3-5 follow-up questions about preferences the user has not stated. If local file reading is authorized, it also reads local files to fill in the profile.

**Profile loading**:

1. Run `scripts/init_profile.py` to check whether a profile file already exists locally (default path `~/.creative-clone/profile.json`)
2. If not, create an empty profile from `assets/profile_template.json` (schema_version 2, light mode, `mode=light`)
3. If the user has authorized local file reading (`privacy.local_reading_enabled == true`):
   - Read documents under the directories listed in `privacy.authorized_dirs`
   - Extract only four summary features: writing style, knowledge background, areas of interest, depth of thinking
   - Does not copy the original text, does not modify the files, does not scan outside the authorized directories
4. Inject the profile snapshot (`base` + `preferences` + `signals` + top-weighted topics from `weighted_topics`) into the three engines

> Profiles created under v1 are automatically migrated to schema_version 2 on the next `update_profile.py` run (adds `weighted_topics` and `feedback_log`; existing data is preserved).

**Follow-up questions** (3-5, targeting profile gaps):

- How open are you to counter-consensus angles? (sets the collision strength of Engine B)
- Do you prefer more theoretical or more hands-on topic ideas? (sets the method hints)
- Do you have sample / data sources available? (sets the feasibility boundary)
- What makes a good topic idea in your judgment? (stored into `preferences`)
- What topic ideas have you worked on before? Were you satisfied? (reused across scenarios)

**Profile read/write rules** (see `references/profile_schema.md` for details):

- R1 Explicit beats inferred: preferences stated by the user override inferences
- R2 Inferences need consistent evidence: write an inferred preference only after at least two supporting signals across sessions
- R3 Current request beats stored data: if the current request conflicts with the profile, use the current request
- R4 Locally manageable: plain-text JSON; view, edit, or delete at any time
- R5 Batch writes: update once at the end of each round; do not write mid-generation
- R6 Minimal collection: store only the fields needed to generate topic ideas

> See `references/profile_schema.md` for the profile system, `scripts/init_profile.py` for the init script, and `scripts/update_profile.py` for the update script.

### Step 4: Topic generation (three engines in sequence)

The three engines run strictly in sequence, passing outputs to the next engine, so the results are not overdone, are original, and are actionable:

#### Engine A · Saturation scan (find overdone directions)

First check which directions are already overdone, then find the gaps.

**Workflow**:
1. Extract keywords from the questionnaire answers and the profile (core domain, object keywords, method keywords, interest keywords, qualifiers)
2. Make a search plan first, then execute it (at most 3 search rounds)
3. Run real-time WebSearch (the main MVP path), recording over-saturation signals and gap signals
4. Score on four dimensions (volume 35% + homogeneity 25% + recency 20% + inverse-gap 20%), then tier the results
5. Output a saturation report; pass saturated directions as forbidden areas and gaps as priority targets to Engine B

**Fallback tiers** (three levels):
- Real-time WebSearch (most reliable; its conclusions may enter the hard blacklist)
- Free academic sources (Google Scholar / arXiv / open CNKI pages)
- The model's own knowledge base (marked "not searched in real time"; conclusions are only advisory)

**No-fabrication rule**: do not invent precise numbers, references, journals, or search results. Always mark quantities as "about" or "estimated".

> Engine prompt: `references/engine_saturation_scan.md`.

#### Engine B · Cross-domain collision (find new angles)

Extract the user's multi-domain profile and combine domains.

**Five collision operators**:
1. Perspective borrowing: re-examine the object of A through the theoretical lens of X
2. Method transfer: apply X's analytical method to A
3. Mutual evidence: compare how the same object appears in A and in X
4. Mechanism analogy: argue that A and X share an isomorphic mechanism (must be falsifiable)
5. Media / audience reflexivity: study X as the medium through which the public encounters A

**Anti-fabrication step**: every collision point must include a `why_link` (why the two domains are genuinely related). Filter into `strong / medium / loose`; drop `loose` points and record them as "concept stacking".

**From collision point to concrete question**: anchor to a concrete object → add qualifiers (population / region / platform / time) → use a testable sentence pattern ("How does X affect Y") → add a method hint → mark points that fill a gap as `fills_gap`.

> Engine prompt: `references/engine_cross_collision.md`.

#### Engine C · Self-critique iteration (polish the research question)

The model switches to a strict reviewer role: it picks flaws in each candidate, judges each against the six hard constraints, and revises or drops candidates that fail.

**Six hard constraints** (the `pass_all` gate):
- C1 Has a concrete research object (identifiable, observable, bounded)
- C2 Has a clear, falsifiable question (not a topic, not a fake problem)
- C3 Has an actionable research method (matches the question, materials available)
- C4 Within the user's ability / resources (matches `resources`, level, and time frame)
- C5 Not an overdone direction (new object / new perspective / new method / new evidence)
- C6 Matches the scenario tone (no glibness in academic settings, no stiffness in playful settings)

**Five blacklist types, one-strike review**: concept stacking / over-saturation / not actionable / scope too broad / fake problem.

**Iteration**: 2 rounds by default (at most 3); for salvageable candidates, give a direct revised replacement. If candidates that pass the gate are fewer than `target_count`, feed the per-candidate issues back to Engine B for another collision round; the outer loop runs at most 3 rounds. **The gate is never lowered to fill the quota.**

**Three stopping conditions**: pass / round limit reached / nitpicking only (remaining issues are all wording-level nits).

> Engine prompt: `references/engine_self_critique.md`; bad-topic blacklist: `references/bad_topic_blacklist.md`.

#### Data flow across the three engines

```
Step 1-3 outputs (scene profile + profile snapshot + questionnaire answers)
    |
    v
Engine A saturation scan -> saturated_topics[] (forbidden areas) + gaps[] (priority targets) + blacklist_hits[]
    |
    v
Engine B cross-domain collision -> gaps injected, keep only logically linked intersections -> candidates[] (each with why_link)
    |
    v
Engine C self-critique -> judge each against the six hard constraints -> final_candidates[] (those that pass the gate)
    |                 if too few, feed back to Engine B (outer loop <= 3 rounds)
    v
Step 5 formatter outputs the four-element template
```

### Step 5: Output topic ideas

Every candidate topic idea must include all four elements; none may be missing:

| Element | Must | Common failures |
|------|----------|------------|
| Title | A concrete question (object + qualifiers), answerable and falsifiable | Broad theme, buzzword stacking |
| Why it fits you | Cites specific profile entries and explains how they are used | "Fits you well" with no evidence; fabricated profile |
| Three angles to approach it | Non-overlapping, actionable paths | Three near-duplicates; direction only, no how-to |
| Risk notes | Covers feasibility / difficulty / ethics and compliance, practical | Avoids real issues; "not very difficult" only |

**Scenario tweaks**: the four elements may not be omitted. A scene profile can use `output_format_adjustments` to add fields (e.g. short video adds "first-3-second hook"; startup adds "MVP validation path") and adjust the title format.

**Batch output rules**:
- Output `output.count` ideas (default 5); if fewer qualify, say so honestly, do not pad
- Sort by relevance, number them, separate cards with dividers
- Open with one sentence about what this batch covers
- End by telling the user they can reply "this is interesting / give me another batch / off track"
- Always close with the AI-generated notice and disclaimer

> Output template: `references/output_template.md` (includes 2 full examples: academic + playful).

### Step 6: Feedback loop

The user marks feedback → the Skill adjusts the next generation → the finally selected topic idea is saved into the user's profile.

**Four feedback types and profile updates** (executed by `scripts/update_profile.py`):

| Feedback | Parameter value | Weight delta | Update action |
|------|--------|------|---------|
| "Selected" | `select` | +0.30 | Save to `base.interests` + `preferences` (`source=explicit`, `confidence=0.9`); `weighted_topics` weight +0.30 |
| "This is interesting" | `like` | +0.10 | Append to `history` + `signals.liked_topics`; `weighted_topics` weight +0.10 |
| "Give me another batch" | `dislike` | -0.20 | Append to `history` + `signals.disliked_topics`; `weighted_topics` weight -0.20 |
| "Off track" | `redirect` | -0.40 | Append to `history` + `signals.redirected_topics`; `weighted_topics` weight -0.40 |

**Profile weight system** (v2):

Every topic the user gives feedback on gets a weight in `weighted_topics` (range 0.0–1.0). The weight reflects how well the topic aligns with the user's interests, and accumulates across sessions. When generating new ideas, the top-weighted topics are injected into the engines as priority directions — so topics the user repeatedly likes or selects steer future generation, while topics the user redirects away from are deprioritized.

- **Weights accumulate**: multiple feedbacks on the same topic add up (clamped to [0.0, 1.0])
- **Time decay**: topics not touched in 90 days have their weight halved (×0.5). Decay is applied lazily — only when the profile is updated or when `update_profile.py --decay` is run. Recent interests stay more influential than stale ones.
- **Idempotency**: each (topic, feedback) pair is tracked in `feedback_log`. If the same topic receives the same feedback type again, the weight is not updated a second time — preventing accidental double-counting from retries or replays.

**Profile update logic**:
- All writes use a temp file + atomic replace, so an interrupted process cannot corrupt the profile
- `weighted_topics` is capped at 200 entries; lowest-weight entries are dropped first
- `history` is capped at 500 entries; each `signals` category at 50; oldest entries are dropped first
- After each feedback, `profile_meta.updated_at` is set to the current time and `stats` are recalculated
- Selected topic ideas are stored across scenarios and reused automatically in later sessions

**Cross-scenario design**:
- Global fields (`base`, `preferences` entries with `scope=cross_scenario`, `signals`, `stats`) are shared across all scenarios
- Scenario-specific fields (`preferences` entries whose `scope` is a specific scenario id, `history.scenario`) apply only within that scenario
- A scenario-level preference can be promoted to a cross-scenario preference if consistent evidence appears in multiple scenarios

> Profile schema: `references/profile_schema.md`; update script: `scripts/update_profile.py`.

---

## Authorization and privacy

> Full privacy policy: `references/privacy_policy.md`.

- **Light mode by default, local reading off by default**: the 6-step flow works without any authorization on first use
- **Two-step authorization**: at Step 3, an info dialog appears → the user actively checks "I have read and agree" → the user picks a directory themselves in the system folder picker. No pre-checked boxes, no nudging
- **Least privilege**: read only the authorized directories, do not follow symlinks, do not scan the whole disk, extract only the four summary features (writing style / knowledge background / areas of interest / depth of thinking), do not modify the original files
- **Revoke any time**: one toggle in Settings drops back to light mode; the 6-step flow and output standards do not degrade
- **Zero upload**: the Skill contains no server address, no upload endpoint, no analytics SDK; the profile is plain-text JSON stored only locally
- **No user data collected**: no account, no telemetry, no crash reporting

**Note on the model runtime**: when topic ideas are generated through a cloud model, the conversation (including the locally extracted summary features) is handled under that model service's privacy policy. The original file content never enters the conversation. To work fully offline, point the Skill at a local model backend.

> Authorization interaction details, state machine, dialog copy, and the cross-model authorization prompt contract are in `references/privacy_policy.md` section 6 and appendix A.

---

## Quality assurance

> Scoring rubric: `references/quality_standards.md`; test cases: `references/test_scenarios.md`; acceptance checklist: `references/acceptance_checklist.md`.

**Topic quality scorecard** (5 dimensions × 1-5 points, max 25):

| Dimension | Question reviewed | Review criterion |
|------|---------|-----------|
| D1 Concreteness | Is it a concrete question or a broad theme? | C1 / C2 |
| D2 Novelty | Does it add something to the field? Is it overdone? | C5 |
| D3 Feasibility | Can it be done with the user's ability and resources? | C4 |
| D4 Fit | How well does it match the user's profile? | Accuracy of profile references |
| D5 Tone control | Does it match the scenario tone? | C6 |

**Pass line**: total >= 18, each dimension >= 3, zero blacklist hits.

**QA flow**:
1. Engine C first admits candidates via the six hard constraints (`pass_all`) (eligibility check)
2. Score gate-passing candidates on the 5 dimensions (quality ranking)
3. Rank ties by the scenario profile's `output.sort_by`
4. Log every round's scores for later review

**Test-run result** (section F, case 1, full 6-step loop): the three engines chain correctly, the offline fallback path works, the concept-stacking counter-example is dropped as expected, the final candidate scores 24/25, and the blacklist has zero hits.

---

## Technical architecture

### File layout

```
creative-clone/
├── SKILL.md                          # This file: 6-step flow + three engines + scenario adaptation + profile read/write
├── scripts/
│   ├── init_profile.py               # Profile init (stdlib only, atomic write)
│   ├── update_profile.py             # Profile update: weighted feedback + decay + idempotency (stdlib only)
│   └── validate_output.py            # Validate engine outputs, scene profiles, and profile (stdlib only)
├── schemas/
│   ├── engine_a_output.json          # JSON Schema: Engine A saturation scan output
│   ├── engine_b_output.json          # JSON Schema: Engine B cross-domain collision output
│   ├── engine_c_output.json          # JSON Schema: Engine C self-critique output
│   ├── scene_profile.json            # JSON Schema: scene profile files
│   └── profile_v2.json               # JSON Schema: user profile (schema_version 2)
├── references/
│   ├── scene_format_spec.md          # Scene profile format spec
│   ├── scene_configs.md              # Scene library guide + extension notes
│   ├── engine_saturation_scan.md     # Engine A: saturation scan prompt
│   ├── engine_cross_collision.md     # Engine B: cross-domain collision prompt
│   ├── engine_self_critique.md       # Engine C: self-critique iteration prompt
│   ├── bad_topic_blacklist.md        # Five bad-topic types
│   ├── output_template.md            # Four-element output template
│   ├── profile_schema.md             # Profile JSON schema + authorization mechanism
│   ├── privacy_policy.md             # Full privacy policy
│   ├── quality_standards.md          # Topic quality scorecard
│   ├── test_scenarios.md             # 3 scenario test cases
│   └── acceptance_checklist.md       # PRD acceptance checklist
├── assets/
│   ├── profile_template.json         # Default profile template (schema_version 2, empty values)
│   └── scene_profiles/
│       ├── academic_paper.json        # Academic paper scenario
│       ├── ppt_presentation.json      # PPT presentation scenario
│       ├── short_video.json           # Short video scenario
│       ├── wechat_article.json       # WeChat article scenario
│       ├── startup_idea.json         # Startup idea scenario
│       ├── event_planning.json       # Event planning scenario
│       ├── podcast.json              # Podcast scenario
│       ├── course_design.json        # Course design scenario
│       └── interview_outline.json     # Interview outline scenario
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

### Design principles

1. **Scenario adaptation**: questionnaire questions, tone, hard-constraint list, and output format all switch with the scene profile
2. **Profile accumulates across scenarios**: feedback and preferences from any scenario are saved into the same profile
3. **Weighted profile**: every feedback adjusts a topic's weight (0.0–1.0); time decay keeps recent interests dominant; top-weighted topics steer the engines
4. **General engines**: saturation scan + cross-domain collision + self-critique iteration, not tied to any discipline or scenario
5. **Unified output standard**: every candidate includes the four elements (concrete question / why it fits you / three angles / risk notes)
6. **Extensible scenarios**: adding a scenario requires only one JSON file; no core logic changes
7. **Schema-validated**: engine outputs, scene profiles, and the user profile are all validated against JSON Schema files in `schemas/`

### Cross-model compatibility

The profile schema follows JSON Schema draft-07 and can be mounted on mainstream model backends such as GPT / Gemini / DeepSeek. Profile reads and writes go through Python scripts (deterministic), not through the LLM, so model uncertainty does not affect the data layer.
