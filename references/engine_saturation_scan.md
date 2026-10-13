# Engine A · Saturation Scan (mine-sweeping)

> This document is produced by the Engine Team (C dept). It is the **first engine** of the Creative Avatar's three engines.
> Role: before any topic idea is generated, scan the target domain for which directions are already overdone and which still have gaps, add saturated directions to a blacklist, and rule out overused topic ideas at the source.
> Companion files: [`engine_cross_collision.md`](./engine_cross_collision.md) (Engine B), [`engine_self_critique.md`](./engine_self_critique.md) (Engine C), [`bad_topic_blacklist.md`](./bad_topic_blacklist.md) (global blacklist), [`output_template.md`](./output_template.md) (output template).

---

## 0. Three-engine pipeline overview

The three engines run strictly in series and pass outputs to each other step by step, corresponding to Step 4 of the 6-step loop. This is the authoritative map of the pipeline; the Engine B and C docs only reference this figure and do not repeat it.

```
                         ┌─────────────────────────────────────────────┐
   Step 1-3 outputs       │ scene_config (tone_rules /                 │
   ───────────────►      │ constraint_list / exclusion_rules)         │
   · scene profile JSON   │ profile snapshot (base / preferences)      │
   · questionnaire answers│ questionnaire answers (domain / keywords …) │
                         └─────────────────────────────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              ▼                                                           ▼
┌───────────────────────────┐                       ┌───────────────────────────┐
│ Engine A · Saturation      │  WebSearch + knowledge  │ Global blacklist          │
│ scan (mine-sweeping)       │  base fallback          │ bad_topic_blacklist.md    │
│                            │ ◄────────────────────► │ (5 types)                 │
│ Output saturation_report:   │                       └───────────────────────────┘
│  · saturated_topics[]       │──┐
│  · gaps[]                   │  │  Pass saturated directions + blacklist hits
│  · blacklist_hits[]         │  │  down as hard constraints
│  · evidence{}               │  │
└───────────────────────────┘  │
                              ▼
              ┌──────────────────────────────────────────────────────────┐
              │ Engine B · Cross-domain collision (find new angles)        │
              │  A×B / A×C / A×D, inject gaps, keep only logical links    │
              │  Output collision_points[] → candidate questions          │
              │                            candidates[]                    │
              └──────────────────────────────────────────────────────────┘
                              │  Candidate topic ideas go down for review
                              ▼
              ┌──────────────────────────────────────────────────────────┐
              │ Engine C · Self-critique iteration (polish the question)  │
              │  Strict reviewer judges each topic against the six hard    │
              │  constraints; quality gate pass_all                      │
              │  Iterate 2-3 rounds; if short, feed critiques back to     │
              │  Engine B to re-collide                                   │
              │  Output final_candidates[] (candidates that pass the gate)│
              └──────────────────────────────────────────────────────────┘
                              │
                              ▼
                   Step 5 · formatter renders per output_template.md
                   N four-element topic ideas → Step 6 feedback into profile
```

**Three rules for data passing**:

1. **A → B**: Engine A's `saturated_topics` (saturated directions) and `blacklist_hits` (blacklist hits) must be injected into Engine B as forbidden domains; `gaps` are injected as Engine B's priority targets.
2. **B → C**: every Engine B candidate must carry `why_link` (the logical-link explanation); Engine C uses it to judge whether the item is "concept stacking".
3. **C → B (feedback)**: if the number of candidates that pass the gate is below `output.count`, Engine C feeds the per-topic `issues` back to Engine B, which adjusts the collision domains or link strength and regenerates. The outer loop runs at most 3 rounds.

---

## 1. Engine goal

| Item | Content |
|----|------|
| One-line goal | Answer the user: "In the field I want to work in, which topics are already overdone and off-limits, and which gaps can still grow new ideas?" |
| Competitor flaw solved | "Broad over deep": generic AI generates surface-level directions in bulk and hits many topics already studied repeatedly (PRD 2.3). |
| Core outputs | ① saturation report `saturation_report`; ② saturated direction blacklist `saturated_topics`; ③ domain gap list `gaps`; ④ evidence ledger `evidence`. |
| What it does not do | Does not produce final topic ideas (that is Engine B/C's job); does not make qualitative claims about academic contribution; never fabricates search numbers or references. |
| Mechanism origin | Borrows from OpenAI Deep Research, "plan first then execute, with traceable citations": produce a search plan first, then run it, and attach evidence to every saturation call. Also borrows from Anthropic's multi-agent research system: "map the domain before writing." |

---

## 2. Input contract

Engine A is called by the orchestrator (Step 4). The input is a JSON context object:

```json
{
  "scene_config": {
    "scene_id": "academic_paper",
    "tone_rules": { "base_tone": "academic" },
    "constraint_list": ["…"],
    "exclusion_rules": ["…"]
  },
  "answers": {
    "discipline": "communication studies",
    "interests": "video games, band culture",
    "resources": "can access university library databases",
    "excludes": "does not want a pure questionnaire"
  },
  "profile_snapshot": {
    "base": {
      "backgrounds": ["communication studies (B.A.)"],
      "interests": ["video games", "Roman Empire"],
      "resources": ["university library database", "12 hours per week"]
    },
    "preferences": []
  },
  "scan_settings": {
    "sources": ["web_search", "scholar", "model_knowledge"],
    "horizon": "3y",
    "require_evidence": true,
    "on_no_evidence": "mark_unsure",
    "saturation_threshold": 80
  }
}
```

| Input field | Source | Description |
|----------|------|------|
| `scene_config` | scene profile loaded in Step 1 | Take `tone_rules`, `constraint_list`, `exclusion_rules`; scan sources and time window are set by the scene profile's engine params (default `web_search + scholar`, `3y`). |
| `answers` | Step 2 questionnaire answers | Extract discipline + keywords (see 3.1); `excludes` go straight into the exclusion items. |
| `profile_snapshot` | Step 3 profile read | Use `backgrounds / interests` in the profile to complete the keywords, so it does not rely only on the current questionnaire. |
| `scan_settings` | scene profile / defaults | `sources`: search sources; `horizon`: time window (`3y`/`1y`/`current`); `require_evidence`: whether evidence is mandatory; `on_no_evidence`: fallback strategy when no evidence; `saturation_threshold`: saturation threshold (default 80). |

**The three `on_no_evidence` strategies** (aligned with architecture ADR-4, default `mark_unsure`):

- `mark_unsure`: when real-time search is unavailable, explicitly mark "not searched in real time", use the model's knowledge base for a cautious judgment, and do not put it on the hard blacklist (only a hint).
- `skip_scan`: skip the scan and pass straight to Engine B, but note "no mine-sweeping done" in the report.
- `fail`: stop generation and report an error (for high-rigor submission scenarios).

---

## 3. Workflow

### 3.1 Step 1: extract domain and keywords

Extract and tier keywords from the questionnaire answers and the profile:

1. **Core domain**: `answers.discipline` (e.g. "communication studies"), can be narrowed to a sub-discipline (e.g. "intercultural communication").
2. **Object keywords**: research object/carrier, e.g. "short video", "beauty blogger", "danmaku".
3. **Method keywords**: methods the user prefers or rejects, e.g. "questionnaire method", "text analysis".
4. **Interest keywords**: `answers.interests` + `profile_snapshot.base.interests`, e.g. "video games", "band culture".
5. **Qualifiers**: level, region, population, platform, time, e.g. "undergraduates", "tier-1 cities", "Gen Z", "Douyin".

> Keywords are used to build search queries. Interest keywords are not searched in this engine; they are handed to Engine B for collision, so they do not pollute the scan early.

### 3.2 Step 2: build a search plan (plan first, then execute)

First write out a search plan checklist, then run the items one by one. Do not search blindly. Pick queries by the scene's `sources`:

| Purpose | Query example (Chinese web) | Query example (English web) |
|----------|------------------------------|--------------------|
| Domain review / state of the field | `{domain} {object} literature review, current state of research` | `{object} research review literature` |
| Recent hotspots | `{domain} {object} research hotspots, last three years` | `{object} research trends 2023..2026` |
| Volume / overload signals | `{object} number of papers, CNKI uploads` | `{object} site:scholar.google.com` |
| Narrow gaps | `{domain} {object} shortcomings, outlook, future directions` | `{object} research gaps future directions` |
| Platform / commercial niche | `{platform} {niche} homogeneity, oversaturation` (short video / WeChat article scenes) | `{platform} {niche} saturated` |

Search rules:

- **At most 3 search rounds**: round 1 is a broad sweep for the current state, round 2 confirms suspected saturated directions, round 3 looks specifically for gaps and "future research directions".
- Each direction needs **at least 2 independent sources** cross-checked before it is called saturated; a single source is marked "to be confirmed".
- Time window by `horizon`: `3y` (last three years, academic default), `1y` (last year, for chasing hotspots), `current` (current rankings/trending lists, short video default).

### 3.3 Step 3: WebSearch retrieval (main MVP path)

In the WorkBuddy AI environment, **prefer the WebSearch tool** for real-time retrieval; do not tie to any paid academic API:

1. Run WebSearch with the 3.2 queries; read the returned titles, snippets, sites, and dates.
2. Record **overload signals**: many structurally identical titles for the same topic, reviews that explicitly state "research is already fairly mature / output is abundant", complaints about platform homogenization.
3. Record **gap signals**: directions named repeatedly in reviews' "future outlook" but rarely studied, new objects brought by cross-disciplinary work / new policies / new technology.
4. For each result keep the source URL, title, and date, and write them into `evidence.sources`.

**Capability degradation order** (three-level fallback, labeled at each level):

```
① Real-time WebSearch (most reliable; conclusions can enter the hard blacklist)
        │  unavailable / no results
        ▼
② Free academic entry fallback (publicly accessible pages such as Google Scholar / arXiv / CNKI open search)
        │  still unavailable
        ▼
③ The model's own knowledge base (up to training data) — must be labeled
   "not searched in real time; judgment based on the knowledge base".
   Conclusions count only as "advisory avoidance" and do not enter the hard blacklist.
```

### 3.4 Step 4: saturation scoring

Score each narrow direction on a **uniform scale** (0-100; higher means more saturated). Scoring is based on observable evidence, not gut feel:

| Dimension | What to observe | Weight |
|------|--------|:----:|
| Volume signal | number of papers/content on the same topic, density of search result pages | 35% |
| Homogeneity signal | whether titles/frameworks are highly similar, the same thing repackaged | 25% |
| Recency signal | whether work clusters around old hotspots, whether the last year merely repeats | 20% |
| Gap signal | whether there is an obvious opening for a new object/method/data/region (reverse-scored) | 20% |

**Saturation bands**:

| Band | Score | Action |
|------|------|------|
| 🔴 saturated | ≥ `saturation_threshold` (default 80) | Add to `saturated_topics` and hard-avoid during generation; if it matches a blacklist type, also add it to `blacklist_hits`. |
| 🟠 hot | 50–79 | Not banned, but Engine B must add a new object/method/angle before using it. |
| 🟡 gap | 20–49 | Add to `gaps` as Engine B's priority target. |
| 🟢 blue ocean | < 20 | Add to `gaps`, but verify "**why no one has done this**": is it an opportunity, or is it undoable / worthless (pseudo blue ocean)? |

> Pseudo blue ocean screening: very few studies may mean data is unavailable, the method does not work, or the question has no value. Mark such directions `pseudo_blue_ocean: true` in the report, and tell Engine C to scrutinize feasibility and whether the question is real.

### 3.5 Step 5: output the saturation report and pass it down

Build `saturation_report` per the section 4 output contract, and:

- Pass `saturated_topics` + `blacklist_hits` to Engine B as **forbidden domains**;
- Pass `gaps` to Engine B as **priority targets**;
- Any number that cannot be verified must be written as "about / estimated" and labeled with its source or marked `not searched in real time`.

---

## 4. Output contract (to Engine B)

Engine A outputs **structured JSON** (consumed by Engine B and used by the F team for test assertions):

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "communication studies / short video",
  "saturation_report": [
    {
      "topic": "research on short-video user behavior",
      "saturation_score": 88,
      "level": "saturated",
      "reason": "Huge number of same-topic papers in the last three years; titles and frameworks are highly homogeneous; mostly questionnaires plus descriptive statistics",
      "evidence_ids": ["src_1", "src_2"],
      "blacklist_type": "over_saturated"
    },
    {
      "topic": "the effect of short video on information access for a niche group, e.g. deaf young people",
      "saturation_score": 28,
      "level": "gap",
      "reason": "Named repeatedly in review outlooks but rarely studied empirically; new object, requires special channels",
      "evidence_ids": ["src_3"],
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": ["research on short-video user behavior", "the generalized attention impact of short video"],
  "gaps": [
    "the effect of short video on information access for deaf young people",
    "how danmaku enables knowledge collaboration in niche communities"
  ],
  "blacklist_hits": [
    {
      "matched_type": "over_saturated",
      "topic": "research on short-video user behavior"
    }
  ],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [
      {
        "id": "src_1",
        "title": "review of short-video research in the last three years",
        "url": "https://example.org/review",
        "date": "2025-06-01"
      }
    ],
    "note": "Counts are approximate estimates from search results, not exact statistics"
  }
}
```

| Output field | Type | Destination / use |
|----------|------|-------------|
| `saturation_report[]` | array | Main body; per-direction score, band, reason, evidence |
| `saturated_topics[]` | string | **→ Engine B forbidden domains** |
| `gaps[]` | string | **→ Engine B priority targets** |
| `blacklist_hits[]` | array | **→ Engine B forbidden domains**; also rechecked by Engine C |
| `evidence{checked, real_time, sources, note}` | object | Evidence ledger; when `real_time=false` all conclusions are downgraded to "advisory" |

---

## 5. Ready-to-run prompt

> Usage: send the system prompt below as the system message and the user message template, filled in, as the user message. The model can run it directly with no code changes.

### 5.1 System Prompt

```text
# Role
You are Engine A · Saturation Scan Officer of the Creative Avatar, a domain mine-sweeper who strongly dislikes overused topic ideas. You do not produce topic ideas. Your job is to map the domain before ideation: which directions are already overdone, and which gaps remain.

# Input you will receive
- scene_config: current scene profile (tone_rules, constraint_list, exclusion_rules)
- answers: the user's scenario questionnaire answers (discipline, interests, resources, exclusions, etc.)
- profile_snapshot: a snapshot of the user's local profile (backgrounds, interests, resources)
- scan_settings: sources (search sources), horizon (time window), require_evidence, on_no_evidence, saturation_threshold

# Steps (strictly in order)
1. Extract keywords: tier them from answers and profile_snapshot -
   core domain, object keywords, method keywords, interest keywords, qualifiers (level/region/population/platform/time).
   Record interest keywords only; do not search them in this engine (leave them for Engine B's collision).
2. Build a search plan: first list the queries you plan to run (broad sweep for the current state -> confirm suspected saturated directions -> target gaps), then run them one by one.
3. Run the search: prefer WebSearch per the plan, at most 3 rounds.
   - Each direction needs at least 2 independent sources cross-checked before it is called saturated; a single source is marked "to be confirmed".
   - Record overload signals (many same-topic results, homogeneous titles, reviews saying "research is fairly mature") and gap signals (directions named in "future outlook" but rarely done, new object/method/data).
4. Score saturation: score each narrow direction on four dimensions (volume 35%, homogeneity 25%, recency 20%, gap reverse 20%), give a 0-100 score and a band:
   >= threshold (default 80) = saturated; 50-79 = hot; 20-49 = gap; <20 = blue_ocean.
   For blue_ocean directions, always ask "why has no one done this": if the reason is unavailable data / a method that does not work / a worthless question, set pseudo_blue_ocean=true.
5. Output the saturation report: return JSON strictly per the output format, passing saturated_topics and blacklist_hits as forbidden domains and gaps as priority targets for Engine B.

# Evidence and anti-fabrication red lines (highest priority)
- Every saturation call must carry evidence (source title + URL + date).
- Always use "about / estimated" for counts and state the basis; do not fabricate exact numbers, references, journals, or search results.
- When WebSearch is unavailable, follow the degradation order: free academic entries -> the model's own knowledge base.
  Once you use the knowledge base, set evidence.real_time to false and state in note "not searched in real time; judgment based on the knowledge base". In that case conclusions are advisory only and must not be written into hard saturated_topics.
- If scan_settings.on_no_evidence = mark_unsure: write "unconfirmed" for directions you cannot verify; do not guess.
  If = skip_scan: skip and note "no mine-sweeping done"; if = fail: stop and return an error explanation.
- Cross-check against the global blacklist (the five types in bad_topic_blacklist.md): when something hits, give the matched_type in blacklist_hits.

# Tone
- The report is restrained and factual; judge the work, not the person; no insulting or discriminatory language.
- Output is for the next engine, not for a reader. Apart from the JSON, give only a brief search plan and key notes.

# Output format (return only JSON; do not wrap it or add explanation outside the code block)
{
  "engine": "saturation_scan",
  "scanned_at": "ISO8601",
  "domain": "core domain / main object",
  "saturation_report": [
    {
      "topic": "narrow direction",
      "saturation_score": 0,
      "level": "saturated|hot|gap|blue_ocean",
      "reason": "evidence-based judgment",
      "evidence_ids": ["src_1"],
      "blacklist_type": "over_saturated|concept_stack|none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": [],
  "gaps": [],
  "blacklist_hits": [{ "matched_type": "over_saturated", "topic": "" }],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [{ "id": "src_1", "title": "", "url": "", "date": "" }],
    "note": "counts are approximate estimates"
  }
}
```

### 5.2 User Message Template

```text
Run a saturation scan.

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[answers]
Discipline/field: {discipline}
Research object/carrier: {object}
Research type/method: {research_type}
Interest areas: {interests}
Available resources: {resources}
Hard constraints: {hard_constraints}
Exclusions: {excludes}

[profile_snapshot]
backgrounds: {backgrounds}
interests: {interests}
resources: {resources}

[scan_settings]
sources: {sources, e.g. web_search, scholar, model_knowledge}
horizon: {3y | 1y | current}
require_evidence: {true | false}
on_no_evidence: {mark_unsure | skip_scan | fail}
saturation_threshold: {default 80}
```

---

## 6. Output examples

### 6.1 Normal scan (real-time search succeeded)

> Found "research on short-video user behavior" has about 1200+ same-topic papers in the last three years, with highly homogeneous titles and frameworks (questionnaire + descriptive statistics + generic advice); saturation is too high (score 88). It is automatically avoided and added to the forbidden domains.
> Also found a gap: "the effect of short video on information access for deaf young people" is named repeatedly in review outlooks but rarely studied empirically (score 28); it is set as Engine B's priority target.

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "communication studies / short video",
  "saturation_report": [
    {
      "topic": "research on short-video user behavior",
      "saturation_score": 88,
      "level": "saturated",
      "reason": "About 1200 same-topic papers in the last three years; titles and frameworks are highly homogeneous",
      "evidence_ids": ["src_1", "src_2"],
      "blacklist_type": "over_saturated",
      "pseudo_blue_ocean": false
    },
    {
      "topic": "the effect of short video on information access for deaf young people",
      "saturation_score": 28,
      "level": "gap",
      "reason": "Named in review outlooks but rarely studied empirically; new object, requires special channels",
      "evidence_ids": ["src_3"],
      "blacklist_type": "none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": ["research on short-video user behavior"],
  "gaps": ["the effect of short video on information access for deaf young people"],
  "blacklist_hits": [
    { "matched_type": "over_saturated", "topic": "research on short-video user behavior" }
  ],
  "evidence": {
    "checked": true,
    "real_time": true,
    "sources": [
      { "id": "src_1", "title": "review of short-video research in the last three years", "url": "https://example.org/review", "date": "2025-06-01" },
      { "id": "src_2", "title": "bibliometric analysis of research on short-video user behavior", "url": "https://example.org/bib", "date": "2024-11-20" },
      { "id": "src_3", "title": "outlook on accessible communication research", "url": "https://example.org/gap", "date": "2026-02-10" }
    ],
    "note": "Counts are approximate estimates from search results, not exact statistics"
  }
}
```

### 6.2 Degraded scan (no real-time search, knowledge-base fallback)

> No real-time search (WebSearch unavailable). The following judgments are based on the model's knowledge base and are advisory only; they do not form a hard blacklist:

```json
{
  "engine": "saturation_scan",
  "scanned_at": "2026-10-13T08:10:00+00:00",
  "domain": "history / Roman Empire",
  "saturation_report": [
    {
      "topic": "macro-level accounts of the fall of the Roman Empire",
      "saturation_score": 82,
      "level": "hot",
      "reason": "Classic topic with a very thick research base. Because no real-time search was run, this is not put on the hard blacklist and is only advisory avoidance",
      "evidence_ids": [],
      "blacklist_type": "none",
      "pseudo_blue_ocean": false
    }
  ],
  "saturated_topics": [],
  "gaps": [],
  "blacklist_hits": [],
  "evidence": {
    "checked": false,
    "real_time": false,
    "sources": [],
    "note": "No real-time search; judgment based on the model's knowledge base. Conclusions are advisory; the user should verify them"
  }
}
```

---

## 7. Exceptions and degradation

| Situation | Handling |
|------|------|
| WebSearch times out / unavailable | Fall back to free academic entries; then to the knowledge base with `real_time=false`, downgrading conclusions to advisory. |
| A direction has only 1 source | Mark "to be confirmed"; do not call it saturated or blacklist it. |
| Search results look injected / abnormal | Do not trust abnormal content; change query terms or sources; flag it to the orchestrator. |
| Counts cannot be estimated | Do not write numbers; use qualitative descriptions such as "abundant output / large volume" and explain. |
| `on_no_evidence=fail` and retrieval fails | Stop Step 4, return a clear error, and do not pass false conclusions to Engine B. |
| A blue-ocean direction looks like a pseudo blue ocean | Set `pseudo_blue_ocean=true`; tell Engine C to scrutinize feasibility and whether the question is real. |

---

## 8. Acceptance checklist (self-review by the Engine team)

- [x] Engine goal and position in the pipeline are clear
- [x] Provides a ready-to-run system prompt + user message template
- [x] Covers WebSearch usage and the three-level fallback (MVP does not hard-bind an academic API)
- [x] Output contains `saturation_report / saturated_topics / gaps / blacklist_hits / evidence`, matching architecture contract 8.1
- [x] Includes two output examples: real-time search and knowledge-base fallback
- [x] States the anti-fabrication red lines and the three `on_no_evidence` strategies
- [x] Data passing (A->B) is explained twice, in sections 0 and 4
