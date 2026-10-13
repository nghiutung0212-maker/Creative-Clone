# Creative Avatar Skill: Topic Quality Scoring Standard

> This document is produced by Team F (Acceptance). It is the quantitative quality ruler for Step 5 topic output in Creative Avatar, and the basis for test cases and the acceptance checklist.
> Upstream inputs: Team C's `bad_topic_blacklist.md` (five bad-topic types), `engine_self_critique.md` (six hard review constraints), `output_template.md` (four elements); PRD section 8 "success criteria".

## 1. Scorecard overview

Each candidate topic idea is scored 1-5 (integer) on 5 dimensions, for a maximum of 25. **A blacklist hit is a one-vote veto and is not scored.**

| # | Dimension | Evaluation question | Maps to Engine C review item |
|---|---------|---------|-------------------|
| D1 | Concreteness | Is it a concrete question, or a vague theme? | C1 (concrete object), C2 (question that is falsifiable) |
| D2 | Novelty | Does it add something to the field? Is it overdone? | C5 (not saturated, adds increment) |
| D3 | Feasibility | Can it be done within the user's ability / resources? | C4 (within resources / timeline) |
| D4 | Fit | How well does it match the user profile? | Profile-citation accuracy (element 2 in output_template) |
| D5 | Register | Does it match the scene tone? | C6 (matches tone_rules) |

## 2. Scoring anchors per dimension

### D1 Concreteness (1-5)

| Score | Anchor |
|------|------|
| 5 | Identifiable concrete object (case / population / platform / time) + at least one qualifier, and the output is a **falsifiable question**, not a theme |
| 3 | Has an object but not enough qualifiers (for example, says only "short video" without landing on a group / platform), or the question is theme-like and falsification is blurry |
| 1 | Only an unbounded broad field ("Chinese vs Western culture", "youth", "impact of AI"); no object, no question |

### D2 Novelty (1-5)

| Score | Anchor |
|------|------|
| 5 | At least one of: new object / new angle / new method / new evidence, and not on Engine A's saturation list |
| 3 | Some increment, but the angle is common, or the increment needs more explanation (a "hot" direction with nothing added) |
| 1 | Repeats existing conclusions; hits "over-saturated"; or buzzwords forced together with no real question (hits "concept stacking") |

### D3 Feasibility (1-5)

| Score | Anchor |
|------|------|
| 5 | Data / sample / channel / method are all available; matches the user's `resources`, level, length, and timeline |
| 3 | A key step needs extra coordination (for example, cross-campus sampling), but a clear fallback exists |
| 1 | Clearly exceeds ability / resources / data / tech (no dataset, no tech, yet asked to build a large system); hits "infeasible" |

### D4 Fit (1-5)

| Score | Anchor |
|------|------|
| 5 | Cites **at least 3 specific profile entries** (background / interest / resources / preference), and each explains "how it is used" |
| 3 | Cites 1-2 entries, or citations are vague and weakly tied to the topic |
| 1 | Unrelated to the profile, or **invents entries that do not exist** just to force a match |

### D5 Register (1-5)

| Score | Anchor |
|------|------|
| 5 | Tone, format, and constraints fully match the scene `tone_rules`; humor (if allowed) serves expression and does not weaken evidence |
| 3 | Tone is mostly right, but one or two phrases are slightly off (for example, casual wording in an academic scene) |
| 1 | Wrong register: playful in a serious scene, stiff in a playful scene; or touches platform / legal / ethical lines |

## 3. Hard veto items (five blacklist types, one-vote veto)

A blacklist hit **is not scored and is marked fail directly (record 0)**, with the `fatal_flaw` type noted in the result. This table matches Team C's `bad_topic_blacklist.md`:

| Type | Fatal review item | Veto criterion |
|------|-----------|-------------|
| Concept stacking | C2 / C5 | Removing buzzwords breaks the question; buzzwords can be swapped arbitrarily while the title still "reads fine" |
| Over-saturated | C5 | Same topic / same framework is overloaded, with no new object / angle / method / evidence |
| Infeasible | C4 | Required data / tech / equipment / permissions / timeline clearly exceed the user's resources |
| Too broad | C1 / C2 | Blurry boundaries, no qualifiers, cannot fit the assigned length |
| False question | C2 | The presupposition is invalid, unfalsifiable, or has no research value |

## 4. Pass line and grades

| Condition | Result |
|------|------|
| Hits any blacklist type | Fail directly (0, with `fatal_flaw` noted) |
| Any dimension < 3 | Fail |
| Total < 18 | Fail |
| Total 18-20, and no dimension < 3 | Pass (publish; suggest improvement points) |
| Total 21-23 | Good |
| Total 24-25 | Excellent |

> Pass line = **total >= 18, every dimension >= 3, and zero blacklist hits**. This cross-checks Engine C's `pass_all` gate: the gate is a binary qualification, the scorecard is quality ranking.

## 5. Bad-topic detection checklist (run after generation)

For each candidate, ask these 5 questions in a row. Any hit means flag it and send it to Engine C for adjudication:

1. **Remove the buzzwords**. Does the question still hold? (concept stacking)
2. **How much has already been done**? What new thing do I bring? (over-saturated)
3. **Do I actually have the data and technology**? (infeasible)
4. **Can one paper / one video hold it**? Where are the boundaries? (too broad)
5. **What evidence would overturn it**? (false question)

## 6. Scoring flow and scorer

1. **Qualification**: Engine C first runs `pass_all` on the six hard constraints. Failures do not enter scoring.
2. **Scoring**: score each candidate that passes the gate on the 5 dimensions; re-check the blacklist, and veto on any hit.
3. **Ranking**: tie-breaking uses the scene profile `output.sort_by` (relevance / novelty / feasibility).
4. **Record**: write each scoring round down for traceability (template in section 7).

Scorer: dual track between Team F acceptance and an optional runtime script. In the MVP stage, acceptance rounds are scored by human / model using this scorecard.

## 7. Scoring record template

```text
candidate_id / title
D1 Concreteness __  D2 Novelty __  D3 Feasibility __  D4 Fit __  D5 Register __
Total __ / 25   Blacklist hit: none / [type]   Result: pass / good / excellent / fail
Improvement points: ___
```

## 8. Acceptance checklist (Team F itself)

- [x] Scoring standard is quantitative and operational (5 dimensions x 1-5 + pass line + grades)
- [x] Bad-topic detection checklist attached, mapped one-to-one to the five blacklist types
- [x] Mapping to Engine C's six hard review constraints is explicit
- [x] Scoring flow and record template provided, ready for acceptance rounds
