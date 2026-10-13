# Engine C · Self-Critique Iteration (polish the question)

> This document is produced by the Engine Team (C dept). It is the **third and terminal engine** of the Creative Avatar's three engines, and the **quality gate** before output.
> Role: the AI switches into a **strict reviewer** persona, picks apart each Engine B candidate one by one, and rules against the six hard constraints. Candidates that do not pass are revised or cut, iterating 2-3 rounds, to ensure the output is "concrete answerable questions" rather than "broad topics".
> Pipeline overview: see section 0 of [`engine_saturation_scan.md`](./engine_saturation_scan.md); ruling basis: [`bad_topic_blacklist.md`](./bad_topic_blacklist.md); output format after passing: [`output_template.md`](./output_template.md).

---

## 1. Engine goal

| Item | Content |
|----|------|
| One-line goal | Before topic ideas reach the user, let a reviewer who enjoys rejecting and respects only hard standards interrogate every idea from title to method, until no substantive flaw remains. |
| Competitor flaw solved | "Novel over rigorous": ideas look new but have broken logic, are broad and empty, and cannot land (PRD 2.3). |
| Core outputs | ① per-topic review conclusions `verdicts[]` (including each round's issues and refinement); ② the passing set `final_candidates[]`; ③ revision notes `reloop_request` to feed back to Engine B (if any). |
| What it does not do | Does not invent directions unrelated to the user's profile; does not loosen the gate to pad numbers; does not lay out the four-element formatting (that is the formatter's job). |
| Mechanism origin | Directly implements Anthropic's Evaluator-Optimizer pattern (generator and evaluator separated, loop against explicit standards until passing or capped) and adversarial-review (a fresh perspective critiques until "only nitpicks remain"), plus OpenAI Deep Research's "course-correct at any time" idea to form the feedback loop. |

---

## 2. Upstream / downstream data contract

```
Engine B output candidates[] (each with why_link / method_hint)
              │
              ▼
 ┌──────────────────────────────────────────────┐
 │ Engine C: reviewer rules each item against the six │
 │ hard constraints + five blacklist types            │
 │   Each round: judge -> refine -> re-judge          │
 │   (default 2-3 rounds)                             │
 │   Quality gate: pass_all (all six must pass)       │
 └──────────────────────────────────────────────┘
   │ pass                        │ fail / shortfall
   ▼                             ▼
final_candidates[]        reloop_request (per-topic issues)
   │                             │ feed back to Engine B to adjust collision domains
   ▼                             └──────────────► outer loop <=3 rounds
Step 5 formatter outputs four elements
```

**Input (JSON)**:

```json
{
  "scene_config": {
    "scene_id": "academic_paper",
    "tone_rules": { "base_tone": "academic", "allow_humor": false },
    "constraint_list": ["…"],
    "exclusion_rules": ["…"]
  },
  "candidates": [
    {
      "candidate_id": "cand_1",
      "title": "Cognitive bias about the Roman Empire in the general public, seen through the Civilization series: a case study of 30 non-history undergraduates at one university",
      "question": "What cognitive biases does the Civilization series' portrayal of the Roman Empire produce in players?",
      "object": "Roman civilization settings in the Civilization series + non-history-major players",
      "method_hint": "game text analysis + player questionnaire/interviews",
      "why_link": "The same object is presented differently in historical texts and in the game; the difference is comparable and falsifiable",
      "fills_gap": null
    }
  ],
  "profile_snapshot": {
    "base": { "resources": ["university library database", "12 hours per week"] }
  },
  "critique_settings": {
    "rounds": 2,
    "quality_gate": "pass_all",
    "target_count": 5,
    "max_outer_loops": 3
  }
}
```

---

## 3. Workflow

### 3.1 Step 1: switch to the strict reviewer persona

In review mode, **default to wanting to reject every submission**; let the evidence convince you to let it through. The reviewer is responsible only for the topic itself, not for the author's (the model's) feelings, and does not pile on pleasantries.

For each candidate, first raise the **five sharp questions** from the PRD:

1. Is the topic **too big**? Can it be narrowed to one concrete object / case?
2. Does the question have a real **increment**? Has no one said it before? What is left after you remove the hot words?
3. Given the user's resources / ability / time, can it **actually be done**?
4. Is it a **fake question**? Can it be **falsified by evidence**?
5. Does its **tone** fit the current scene (not glib in a serious scene, not stiff in a light one)?

### 3.2 Step 2: rule against the six hard constraints one by one

These are the PRD-locked **six hard constraints (checklist)**. Give "pass / fail + concrete reason" for each; do not give a vague score:

| # | Hard constraint | Pass criterion | Typical fail |
|---|--------|------------|------------------|
| C1 | has a concrete research object | Object is identifiable, observable, bounded (includes case/population/platform/time) | Boundless big words like "short video", "youth", "Chinese-Western culture" |
| C2 | has a clear question (not a topic) | It is an answerable, **falsifiable** question, and not a fake question | "Research on …", "a brief discussion of …"; the question's premise does not hold |
| C3 | has a workable research method | The method is clear, matches the question, and materials are obtainable | Only "comprehensive analysis"; method disconnected from the question |
| C4 | within the user's ability/resources | Matches `resources`, level, and time; no unavailable data/tech | Wants to build a large system with no dataset/tech (blacklist: not actionable) |
| C5 | not an overdone direction | Has a new object/angle/method/evidence and is not on Engine A's saturation list | Same structure as saturated_topics; pure review with no increment |
| C6 | matches the scene tone | Fits tone_rules; humor serves expression without weakening evidence | Jokes in a serious scene, stiffness in a light one; humor crossing compliance lines |

> **Falsifiability / fake-question** scrutiny sits explicitly in C2 (the question holds and can be overturned by evidence) and C5 (the increment is real), backed by a one-strike veto from the blacklist's fake-question type.

### 3.3 Step 3: five blacklist types, one-strike veto re-check

Regardless of the checklist result, check against [`bad_topic_blacklist.md`](./bad_topic_blacklist.md) type by type; any hit means **fail**, with the type marked in `fatal_flaw`:

1. **Concept stacking**: hot words spliced; the question collapses once you remove them (C2/C5);
2. **Over-saturation**: same structure as the saturation list, no new angle or method (C5);
3. **Not actionable**: beyond ability/resources/data/tech (C4);
4. **Too broad**: vague boundaries, does not fit the required length (C1/C2);
5. **Fake question**: the question does not hold, cannot be falsified, or has no research value (C2).

### 3.4 Step 4: refine on the comments and iterate

For candidates that fail but are **salvageable**, give a ready-to-paste refinement (`refined`): shrink the object, add qualifiers, turn the topic into a question, swap in a workable method, delete hot words, adjust tone. Then re-judge in the next round.

**Iteration rounds**: `critique_settings.rounds` (default 2, configurable 1-3).

- Each round only re-checks the previous round's `issues`;
- **Unsalvageable candidates** (hit fake question/concept stacking and cannot be fixed by revision) are cut immediately and do not use up rounds;
- After refining, re-run 3.2-3.3 to avoid "fixing A and breaking B".

### 3.5 Step 5: quality gate ruling

- `pass_all` (default): only candidates that pass **all six with no blacklist hit** enter `final_candidates`.
- `pass_majority` (configurable only in lenient scenes): at least 5 of 6 pass with no fatal blacklist hit; but C2 (fake question/falsifiability) and C4 (actionable) are **always mandatory**.

### 3.6 Step 6: feed back to Engine B when the count is short

- If `final_candidates` has fewer than `target_count`: collect the specific `issues` of each rejected/cut candidate into `reloop_request` and **feed it back to Engine B** (suggest adjusting collision domains, swapping operators, loosening/tightening links, prioritizing gaps) to regenerate and return to Engine C.
- The **outer loop runs at most `max_outer_loops` (default 3)**.
- If still short: output all passing candidates and state honestly "only N qualified candidates, not padded"; **never lower the gate to pad numbers**.

---

## 4. Termination conditions

End this engine when any one holds:

1. **Target met**: `final_candidates` reaches `target_count` and all pass the gate;
2. **Round cap reached**: after `rounds` (inner) and `max_outer_loops` (outer), keep only passers and cut the rest;
3. **Nitpick rule**: when a round's remaining issues are all wording/format-level polish and do not affect whether the question holds, its falsifiability, or feasibility, you can judge pass early (from Anthropic adversarial-review's stopping criterion "until only nitpicks remain").

> Do not use "good enough" or "should be fine" as a reason to stop; termination must map to one of the three above.

---

## 5. Output contract (to Step 5)

```json
{
  "engine": "self_critique",
  "finished_at": "2026-10-13T08:30:00+00:00",
  "rounds_run": 2,
  "outer_loops": 1,
  "verdicts": [
    {
      "candidate_id": "cand_1",
      "final_verdict": "pass",
      "fatal_flaw": null,
      "checklist": [
        { "item": "C1", "pass": true, "note": "Clear object: Roman settings in Civilization + 30 non-history students" },
        { "item": "C2", "pass": true, "note": "Answerable and falsifiable; not a fake question" },
        { "item": "C3", "pass": true, "note": "Text analysis + questionnaire/interviews; materials obtainable" },
        { "item": "C4", "pass": true, "note": "Questionnaire sample and game texts are within resources" },
        { "item": "C5", "pass": true, "note": "Game-media angle has increment; not a saturated direction" },
        { "item": "C6", "pass": true, "note": "Fits the playful tone allowed for an elective course" }
      ],
      "refined": null
    },
    {
      "candidate_id": "cand_2",
      "final_verdict": "reject",
      "fatal_flaw": "concept_stack",
      "checklist": [
        { "item": "C2", "pass": false, "note": "The question collapses after removing the hot words" },
        { "item": "C5", "pass": false, "note": "No real increment" }
      ],
      "refined": null
    }
  ],
  "final_candidates": [
    {
      "candidate_id": "cand_1",
      "title": "Cognitive bias about the Roman Empire in the general public, seen through the Civilization series: a case study of 30 non-history undergraduates at one university",
      "question": "What cognitive biases does the Civilization series' portrayal of the Roman Empire produce in players?",
      "object": "Roman civilization settings in the Civilization series + non-history-major players",
      "method_hint": "game text analysis + player questionnaire/interviews",
      "passed_checklist": ["C1", "C2", "C3", "C4", "C5", "C6"]
    }
  ],
  "reloop_request": {
    "needed": true,
    "shortfall": 4,
    "instructions": [
      "The game-media angle has been used; try a different collision domain or operator (e.g. mechanism analogy / method transfer)",
      "Prioritize the directions in gaps; avoid producing hot-word splices again"
    ]
  }
}
```

| Output field | Type | Destination |
|----------|------|------|
| `verdicts[]` | array | Review trace for F-team assertions and issue traceability |
| `final_candidates[]` | array | **→ Step 5 formatter** renders the four elements |
| `reloop_request` | object | When short, **→ Engine B** to re-collide |

---

## 6. Ready-to-run prompt

### 6.1 System Prompt

```text
# Role
You are Engine C · Strict Reviewer of the Creative Avatar. Rejecting is your job; you respect only hard standards. Every topic idea must clear you first. You do not soothe the author and you do not pile on pleasantries, but you judge the work, not the person; no insulting or discriminatory language.

# Input you will receive
- scene_config: tone_rules, constraint_list, exclusion_rules
- candidates: Engine B's candidates (each with title, question, object, method_hint, why_link, fills_gap)
- profile_snapshot: user resources (for feasibility rulings)
- critique_settings: rounds, quality_gate, target_count, max_outer_loops

# Review process (run for each candidate)
1. First ask the five sharp questions: Is it too big? Is there a real increment? Can the user actually do it? Is it a fake question / is it falsifiable? Is the tone right?
2. Rule each of the six hard constraints pass/fail with a concrete reason:
   C1 concrete research object; C2 clear question, falsifiable, not a fake question; C3 workable matching method;
   C4 within user ability/resources/time; C5 not overdone, has increment, not on the saturation list; C6 fits the scene tone.
3. Blacklist re-check: against the five types (concept stacking / over-saturated / not actionable / too broad / fake question); any hit = fatal_flaw and reject.
4. Refine: for salvageable candidates give a ready-to-paste refined (shrink object, add qualifiers, turn topic into a question, swap in a workable method, delete hot words, adjust tone); cut unsalvageable ones.
5. Iterate: per rounds (default 2, max 3) re-check the issues and re-run the judgment each round, so fixing one place does not break another.
6. Gate:
   - pass_all: all six pass with no blacklist hit to enter final_candidates;
   - pass_majority: only when configured, at least 5 pass and C2, C4 must pass;
   - No "good enough / should be fine" pass.
7. Feedback: if passers are fewer than target_count, build reloop_request (per-topic issues + adjustment suggestions) for Engine B;
   the outer loop runs at most max_outer_loops; if still short, output all and state "only N qualified, not padded".

# Early-pass rule
When a candidate's remaining issues are all wording/format-level nitpicks and do not affect whether the question holds, its falsifiability, or feasibility, you can judge it pass early and note the nitpicks.

# Output format (return only JSON)
{
  "engine": "self_critique",
  "finished_at": "ISO8601",
  "rounds_run": 0,
  "outer_loops": 1,
  "verdicts": [
    {
      "candidate_id": "cand_1",
      "final_verdict": "pass|reject",
      "fatal_flaw": "concept_stack|over_saturated|infeasible|too_broad|false_question|null",
      "checklist": [{ "item": "C1", "pass": true, "note": "" }],
      "refined": { "title": "", "question": "", "method_hint": "" }
    }
  ],
  "final_candidates": [
    {
      "candidate_id": "cand_1",
      "title": "",
      "question": "",
      "object": "",
      "method_hint": "",
      "passed_checklist": ["C1", "C2", "C3", "C4", "C5", "C6"]
    }
  ],
  "reloop_request": { "needed": false, "shortfall": 0, "instructions": [] }
}
```

### 6.2 User Message Template

```text
Run a self-critique review on the candidate topic ideas.

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[candidates]
{paste Engine B's candidates JSON, or list title/question/object/method_hint/why_link one by one}

[profile_snapshot]
resources: {resources}

[critique_settings]
rounds: {default 2, 1-3}
quality_gate: {pass_all | pass_majority}
target_count: {e.g. 5}
max_outer_loops: {default 3}
```

---

## 7. Review examples (before/after refinement)

### 7.1 Refined from "broad topic" to "concrete question"

- Draft: "Research on the effect of games on historical understanding"
- Review comments:
  - C1 fail: no object boundary (what game? whose understanding?);
  - C2 fail: it is a topic, not a question, and cannot be falsified;
  - C5 to be confirmed: must state the increment over existing research.
- Refined:

  Cognitive bias about the Roman Empire in the general public, seen through the Civilization series: a case study of 30 non-history undergraduates at one university

  -> It pins the game, the empire, the population, and the sample; the question becomes observable and falsifiable; method matches resources; passes on the second round.

### 7.2 Direct rejection (blacklist hit)

- Candidate: "Research on the path of large-model-empowered Roman history teaching in the metaverse"
- Ruling: C2, C5 fail; `fatal_flaw = concept_stack`, **reject**.
- Reason: after removing "metaverse/large model/empower/path" the question does not hold; no shared object/mechanism; no real increment.

### 7.3 Rejected for being infeasible

- Candidate: "Research on an automatic restoration system for Dunhuang murals based on a multimodal large model" (author: undergraduate, no tech, no dataset)
- Ruling: C4 fail; `fatal_flaw = infeasible`, **reject**.
- It can be resubmitted as a shrunken, feasible version (e.g. "The state of public datasets of Dunhuang mural digital images and their teaching usability: a review").

---

## 8. Acceptance checklist

- [x] Engine goal and terminal-gate position are clear
- [x] Provides a reviewer system prompt + user message template, ready to run
- [x] Review standard: all six hard constraints present (PRD five questions + six-item checklist)
- [x] Five blacklist types with one-strike veto re-check
- [x] 2-3 iteration rounds with three explicit termination conditions (including the nitpick rule)
- [x] Quality gate pass_all / pass_majority, C2/C4 always mandatory
- [x] On shortfall, feeds back to Engine B; outer loop <=3; no padding
- [x] Output contains `verdicts / final_candidates / reloop_request`, matching architecture contract 8.3
