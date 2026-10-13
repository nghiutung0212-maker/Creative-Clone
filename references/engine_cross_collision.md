# Engine B · Cross-Domain Collision (find new angles)

> This document is produced by the Engine Team (C dept). It is the **second engine** of the Creative Avatar's three engines.
> Role: structurally collide the user's **core domain A** with the interest domains B, C, D from the profile (even if they look unrelated), to produce counter-consensus angles the user would not think of but that have a real logical link, and distill them into concrete questions.
> Pipeline overview: see section 0 of [`engine_saturation_scan.md`](./engine_saturation_scan.md); downstream review: [`engine_self_critique.md`](./engine_self_critique.md); hard-paste detection: [`bad_topic_blacklist.md`](./bad_topic_blacklist.md).

---

## 1. Engine goal

| Item | Content |
|----|------|
| One-line goal | Make two knowledge areas that normally have nothing to do with each other, such as "history" and "being into games", collide in the user's mind into one concrete question that is fresh and actionable. |
| Competitor flaw solved | "Common over individual": generic templates look the same for everyone; plus the fake novelty of "hot-keyword splicing" (PRD 2.3 / 2.4). |
| Core outputs | ① collision point list `collision_points[]` (each with a logical-link explanation); ② candidate research questions `candidates[]`; ③ removed fake pastes `filtered_out[]`. |
| What it does not do | Does not build illogical hot-word mashups (removed and logged when found); does not make the final quality ruling (that is Engine C's job); does not re-scan saturated directions. |
| Mechanism origin | Borrows Arthur Koestler's "bisociation" and analogy-transfer theory; on the engineering side, OpenAI's two-layer personalization, where the scene profile sets boundaries and the personal profile supplies collision sources; and Anthropic's multi-agent idea of "force a fresh angle to break out of the home domain's frame". |

---

## 2. Upstream / downstream data contract

```
Engine A output                   Engine B work                        Engine C input
─────────────                     ───────────                        ─────────
saturated_topics[] ──► forbidden ──┐
blacklist_hits[]   ──► forbidden ──┤
gaps[]             ──► priority ───┤   A×B / A×C / A×D
scene_config       ──► constraints/tone ┤  structured collision -> logical-link filter
profile_snapshot   ──► interest domains B/C/D ┘ -> distill concrete questions
                                                              ──► candidates[]
                                                                  (each with why_link)
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
  "scan_output": {
    "saturated_topics": ["research on short-video user behavior"],
    "gaps": ["the effect of short video on information access for deaf young people"],
    "blacklist_hits": [{ "matched_type": "over_saturated", "topic": "research on short-video user behavior" }]
  },
  "profile_snapshot": {
    "base": {
      "backgrounds": ["history (B.A.)"],
      "interests": ["video games", "Roman Empire", "band culture"],
      "resources": ["university library database", "12 hours per week"]
    }
  },
  "collide_settings": {
    "min_logic_link": "strong",
    "max_candidates": 20,
    "target_count": 5
  }
}
```

| Input field | Use |
|----------|------|
| `scan_output.saturated_topics / blacklist_hits` | **Forbidden domains**: collision results must not land on these directions, or they are removed. |
| `scan_output.gaps` | **Priority targets**: a collision result that fills a gap is kept first. |
| `profile_snapshot.base.backgrounds` | Source for core domain A. |
| `profile_snapshot.base.interests` | Source for collision domains B/C/D; the more interests, the richer the collision set. |
| `collide_settings.min_logic_link` | Link-strength threshold (`loose`/`medium`/`strong`, default `strong`). |
| `collide_settings.max_candidates` | Cap on the collision pool (default 20), to prevent runaway divergence. |

---

## 3. Workflow

### 3.1 Step 1: extract core domain A

- Determine **core domain A** from `profile_snapshot.base.backgrounds` and the questionnaire discipline field (e.g. "history / Roman imperial history").
- State A's three elements: **research object** (Roman Empire), **common theories/angles** (source criticism, social history), **common methods** (archival work, source analysis).

### 3.2 Step 2: extract collision domains B, C, D

- Pull **all non-home-domain areas** from `base.interests` and the questionnaire interest field (e.g. "video games (Civilization series)", "band culture").
- For each collision domain, split out the same three parts: **carrier/object**, **internal mechanism**, **transferable method or angle**.
- When interest domains are thin (light-mode sparse profile), add two kinds of "near domains":
  - **Methodological neighbors**: domains whose methods transfer to A (e.g. history ↔ archaeology, anthropology);
  - **Object neighbors**: contemporary carriers that share A's object (e.g. history ↔ popular narrative media such as film, games, textbooks).

### 3.3 Step 3: structured collision (A×B / A×C / A×D)

This is not writing two words side by side. Use **five collision operators** to make the two domains actually react. Try each pair (A, X) in turn:

| Operator | How | Typical output |
|------|------|----------|
| ① Angle borrowing | Re-examine A's object through X's theoretical lens | Use the "narrative choice" mechanic in game design to see how historical texts shape a sense of historical fate |
| ② Method transfer | Move X's analysis method into A | Use game player behavior-log methods to analyze "path dependence" in historical figures' decisions |
| ③ Object cross-check | The same object appears in both A and X; compare how the two present it | Roman Empire (historical texts) vs Roman Empire (Civilization game) -> cognitive bias |
| ④ Mechanism analogy | Argue that A and X share an isomorphic mechanism | Legion supply lines vs game resource economy (must be falsifiable) |
| ⑤ Medium/audience reflexivity | Study X as the medium through which the public encounters A | Civilization as an "implicit textbook" for the public learning Roman history |

> Each operator produces at least 1 candidate angle; the total number is capped by `max_candidates`.

### 3.4 Step 4: logical-link filter (core anti-fake step)

For each collision point, **force a `why_link` (why the two are genuinely related)** and rate the link strength:

| Strength | Criterion | Action |
|------|------|------|
| `strong` | A defensible causal / isomorphic / verifiable relationship; the two domains share a clear object or mechanism; and the user's resources support it | Keep (default threshold) |
| `medium` | A reasonable analogy but needs extra argument or a bridging concept | Keep only when `min_logic_link=medium/loose` or it fills a gap |
| `loose` | Only surface / wording similarity, no mechanism connection | **Remove and write into `filtered_out`, reason "concept stacking"** |

**One-strike veto** (remove on sight):

- Cannot answer "why are A and X put together reasonably?";
- Merely sticking hot words like "metaverse / large model / empower / path" in front of A (see the blacklist concept-stacking type);
- The collision lands inside `saturated_topics` / `blacklist_hits` without bringing a new object or method;
- Beyond the user's resources and clearly infeasible (left for Engine C, but obvious cases are removed early).

### 3.5 Step 5: distill concrete research questions from collision points

For collision points that pass, turn the "angle" into an **answerable, falsifiable concrete question**:

1. **Anchor a concrete object**: not "games and history", but "the technology-tree design for Roman civilization in Civilization VI".
2. **Add qualifiers**: population/region/platform/time/case, e.g. "20 history majors at Sun Yat-sen University".
3. **Use a question form**: prefer testable forms such as "how does X affect Y", "how do A and B differ on Z", "what factors cause Z"; avoid empty shells like "a brief discussion of / a tentative study of / research on …".
4. **Attach a method hint**: what method could answer the question (text comparison, questionnaire, experiment, case study), and check it against `resources`.
5. **Align with gaps**: if it fills a gap in `gaps`, mark `fills_gap`.

> The result must be a "question", not a "topic". Engine C's review checklist enforces this a second time.

---

## 4. Output contract (to Engine C)

```json
{
  "engine": "cross_collision",
  "generated_at": "2026-10-13T08:20:00+00:00",
  "base_domain": "history / Roman imperial history",
  "collision_points": [
    {
      "id": "cp_1",
      "a": "history (Roman imperial history)",
      "b": "video games (Civilization series)",
      "operator": "object cross-check / medium reflexivity",
      "logic_link": "strong",
      "why_link": "The Civilization series reconstructs the rise and fall of the Roman Empire interactively and is a high-frequency medium through which the public encounters Roman history; the difference between how the same object is presented in historical texts and in the game can be directly compared and falsified.",
      "candidate_angle": "games as an implicit textbook for public historical understanding",
      "candidate_question": "What cognitive biases about the Roman Empire does the Civilization series produce in non-history-major players?",
      "fills_gap": null,
      "resource_check": "Game texts and a player questionnaire are obtainable; resources support it"
    }
  ],
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
  "filtered_out": [
    {
      "raw": "Large-model-empowered Roman history teaching in the metaverse",
      "reason": "Concept stacking: hot words spliced, no mechanism link; why_link does not hold"
    }
  ]
}
```

| Output field | Type | Destination |
|----------|------|------|
| `collision_points[]` | array | Collision trace for Engine C and the F team to audit |
| `candidates[]` | array | **→ Engine C for review**; each must carry `why_link` and `method_hint` |
| `filtered_out[]` | array | Logs removed fake pastes, for traceability and testing |

---

## 5. Ready-to-run prompt

### 5.1 System Prompt

```text
# Role
You are Engine B · Cross-Domain Collisionist of the Creative Avatar. You weld two knowledge areas that look unrelated into counter-consensus angles that still hold up logically. You only build collisions with a real link; you strongly dislike hot-word mashups.

# Input you will receive
- scene_config: current scene (tone_rules, constraint_list, exclusion_rules)
- scan_output: Engine A's saturated_topics, blacklist_hits (forbidden domains) and gaps (priority targets)
- profile_snapshot: user backgrounds (core domain), interests (collision domains), resources
- collide_settings: min_logic_link, max_candidates, target_count

# Steps (strictly in order)
1. Fix core domain A: determine A from backgrounds and the discipline field; split out its object, common angles, and common methods.
2. Fix collision domains: pull all non-home areas B/C/D from interests; when interests are thin, add methodological and object neighbors (e.g. history ↔ popular media such as film, games, textbooks).
3. Structured collision: for each pair (A, X), try the five operators in turn -
   ① angle borrowing ② method transfer ③ object cross-check ④ mechanism analogy ⑤ medium/audience reflexivity; each operator should yield about 1 angle, capped by max_candidates.
4. Logical-link filter: force a why_link for every collision point (why the two are genuinely related) and rate logic_link:
   - strong: a defensible causal / isomorphic / verifiable relationship, sharing a clear object or mechanism;
   - medium: a reasonable analogy but needs a bridge;
   - loose: surface similarity only -> remove, write into filtered_out, reason "concept stacking".
   Filter by the min_logic_link threshold; remove any result that hits a forbidden domain (saturated_topics/blacklist_hits) without a new object or method.
5. Distill concrete questions: turn passing angles into answerable, falsifiable questions -
   anchor a concrete object -> add qualifiers (population/region/platform/time/case) -> use a testable form such as "how does X affect Y / how do A and B differ on Z" -> attach a method hint and check against resources -> mark fills_gap if it fills a gap.

# Quality red lines
- Every kept collision point must have a why_link; if you cannot write one, it is concept stacking and must be removed.
- Do not stick hot words such as "metaverse / large model / empower / path / ecosystem" in front of A and call it innovation.
- The unit of output is a "question", not a "topic"; the title must contain a concrete object and qualifiers.
- Do not fake the user's resources, data availability, or method feasibility; mark the uncertain ones "to be verified" and leave them for Engine C.
- Follow the scene tone strictly (tone_rules): no jokes in a serious scene, no stiffness in a light scene; but no scene may break the law or platform compliance.

# Output format (return only JSON)
{
  "engine": "cross_collision",
  "generated_at": "ISO8601",
  "base_domain": "",
  "collision_points": [
    {
      "id": "cp_1",
      "a": "",
      "b": "",
      "operator": "angle_borrowing|method_transfer|object_cross_check|mechanism_analogy|medium_reflexivity",
      "logic_link": "strong|medium|loose",
      "why_link": "argument for the real link between the two",
      "candidate_angle": "",
      "candidate_question": "",
      "fills_gap": null,
      "resource_check": ""
    }
  ],
  "candidates": [
    {
      "candidate_id": "cand_1",
      "title": "Concrete question: case of X / through the lens of Y",
      "question": "answerable, falsifiable question",
      "object": "concrete research object",
      "method_hint": "workable method",
      "why_link": "logical-link explanation",
      "fills_gap": null
    }
  ],
  "filtered_out": [{ "raw": "", "reason": "concept stacking / hits forbidden domain / infeasible" }]
}
```

### 5.2 User Message Template

```text
Run a cross-domain collision.

[scene_config]
scene_id: {scene_id}
base_tone: {base_tone}
allow_humor: {true|false}
constraint_list: {constraint_list}
exclusion_rules: {exclusion_rules}

[scan_output]
saturated_topics: {saturated_topics}
blacklist_hits: {blacklist_hits}
gaps: {gaps}

[profile_snapshot]
backgrounds: {backgrounds}        # core domain A
interests: {interests}            # collision domains B/C/D
resources: {resources}

[collide_settings]
min_logic_link: {strong|medium|loose}
max_candidates: {default 20}
target_count: {number of candidates needed, e.g. 5}
```

---

## 6. Collision examples (benchmark)

### 6.1 History × video games (PRD classic case)

- **Core domain A**: history (Roman imperial history)
- **Collision domain B**: video games (Civilization series)
- **Operators**: ③ object cross-check + ⑤ medium reflexivity
- **why_link**: Civilization reconstructs the rise and fall of Rome interactively and is a high-frequency medium for the public to encounter Roman history; the difference between how the same object is presented in texts and in the game is directly comparable and falsifiable.
- **Result**:

  Cognitive bias about the Roman Empire in the general public, seen through the Civilization series: a case study of 30 non-history undergraduates at one university

  - **Question**: What cognitive biases about the Roman Empire does the Civilization series' portrayal produce in non-history-major players?
  - **Method**: game text/settings analysis + player questionnaire and small-sample interviews
  - **Why it holds**: shared object "Roman Empire"; the difference is observable and measurable; materials and sample are easy to obtain -> fresh, on-interest, and actionable.

### 6.2 More collision demos (showing the generalizability)

| Core domain A | Collision domain B | Operator | Concrete question produced (illustrative) |
|----------|----------|------|--------------------------|
| biology (apoptosis) | game design | mechanism analogy | To what extent can the "attack-defense resource scheduling" of a tower-defense game be analogous to the signaling pathways of apoptosis? Where does the analogy break? (boundaries must be argued) |
| marketing | band culture | angle borrowing | How do indie bands convert the subcultural capital of being "non-commercial" into fan monetization? A case study of one livehouse venue |
| CS (algorithms) | cooking | method transfer | Can the "step-by-step optimization" logic of a recipe be used to explain the state transitions of dynamic programming? A case study of one general-education course |
| communication studies | cat ownership | medium reflexivity | How does "cloud petting cats" content become an emotional compensation mechanism for young people? A case study of the comments under cat-ownership topics on Xiaohongshu |

> Counter-example (**must be removed**): "Research on the path of large-model-empowered Roman history teaching in the metaverse". Hot words spliced, no mechanism link, `why_link` does not hold; it goes into `filtered_out`.

---

## 7. Concept stacking vs real collision: three quick self-check questions

For each candidate, ask in sequence; any "no" sends it back or removes it:

1. **"If you take out the hot words, does the question still hold?"** - no = concept stacking.
2. **"What object/mechanism do A and B share? Can you state the causal or isomorphic link in one sentence?"** - cannot = fake paste.
3. **"Can the answer to this question be overturned by evidence? Does the user have the materials to produce that answer?"** - not falsifiable / no materials = send to Engine C to judge as a fake question or infeasible.

---

## 8. Exceptions and degradation

| Situation | Handling |
|------|------|
| Profile has no interest domain (light mode) | Use methodological + object neighbors to fill collision domains, and note "no personal interests used; lower personalization". |
| All collisions are loose | Loosen to `medium` and require a bridging argument; if still nothing, send back to Engine A to re-confirm gaps. |
| Fewer candidates than `target_count` | Output all honestly and let Engine C trigger feedback (see Engine C 3.4). |
| Suspected pseudo blue ocean collision | Keep but label it, and tell Engine C to scrutinize feasibility. |

---

## 9. Acceptance checklist

- [x] Engine goal and upstream/downstream position are clear
- [x] Provides a ready-to-run system prompt + user message template
- [x] Five collision operators + three-level logical-link filter + forced `why_link`
- [x] Includes the history×game benchmark case and several cross-domain demos
- [x] Output contains `collision_points / candidates / filtered_out`, matching architecture contract 8.2
- [x] States concept-stacking detection and data passing (A->B, B->C)
- [x] Count is capped by `max_candidates` to prevent divergence
