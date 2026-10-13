# Bad-Topic Blacklist

> This document is produced by Team C (Engines). It is the **global blacklist** that Creative Avatar applies to all scenes.
> It defines five bad-topic types that must be actively avoided, and gives a **definition, examples, detection signals, and fix / rewrite methods** for each.
> Consumers: Engine A (detects over-saturated directions), Engine B (detects concept stacking), Engine C (one-vote veto review). It stacks with each scene's `exclusion_rules`.

---

## 0. How the blacklist is used

1. **Detection stage**: Engine A writes "over-saturated" directions into `saturated_topics` during its scan; Engine B writes "concept stacking" pseudo-combinations into `filtered_out` during collision.
2. **Adjudication stage**: Engine C runs a one-vote veto review on all five types. Any hit triggers `reject`, and the type is recorded in `fatal_flaw`.
3. **Stacking order** (later layers are stricter): global blacklist → scene `exclusion_rules` → user-stated `excludes / red_lines` → scene `constraint_list` (positive hard filter).
4. **Salvage principle**: except for the "false question" type, most bad topics can be salvaged by **narrowing the object, swapping the method, or deleting buzzwords**. Salvaged topics must go back through Engine C.

**Five types at a glance**:

| Type | One-line flaw | Fatal review item |
|------|------------|------------|
| 1. Concept stacking | Buzzwords forced together; remove the buzzwords and the question falls apart | C2 / C5 |
| 2. Over-saturated | Research volume has exploded; no new angle or method left | C5 |
| 3. Infeasible | Beyond the researcher's ability / resources / data / tech | C4 |
| 4. Too broad | Blurry boundaries; cannot fit in the assigned length | C1 / C2 |
| 5. False question | The question itself is invalid and cannot be falsified | C2 |

---

## 1. Concept Stacking

**Definition**: multiple trendy buzzwords (often "big words") are forced into a title with connectors such as "in the context of / empower / path / horizon". **There is no arguable mechanism between the words, and no real question behind the title.** It creates the illusion of being both trendy and grand, but cannot actually be answered.

**Typical examples**:

- "Ethical governance paths for large models empowering rural revitalization in the metaverse context" (original PRD example)
- "Ecosystem construction for ChatGPT empowering ideological and political education from the digital twin horizon"
- "Innovation paths for intangible cultural heritage communication driven by blockchain + metaverse + AIGC"
- "Mechanisms by which digital transformation empowers common prosperity under the dual-circulation development pattern" (no concrete object / industry)

**Detection signals**:

- You can swap in a different buzzword and the title still "reads fine" (replace "metaverse" with "blockchain" and it still looks plausible).
- Two or more "big words" appear, but there is no concrete research object or case.
- The verbs are all "empower / construct / path / couple / horizon"; no testable relationship is present.
- After removing the buzzwords, you cannot answer "who specifically, in what situation, what actually happened".

**Fix / rewrite**: keep one object you actually care about, delete the unconnected buzzwords, and land on a falsifiable question.

- Bad: "Ethical governance paths for large models empowering rural revitalization in the metaverse context"
- Fixed: "How do AI scripting tools change smallholder farmers' pitch language and deal closure in county-level livestream e-commerce? A case study of 20 farmers in one county"

---

## 2. Over-Saturated

**Definition**: research or content on a direction has exploded, and the frameworks are highly similar. **Without a new object, a new angle, a new method, or new evidence, the topic is destined to repeat existing conclusions.** It is not forbidden, but it cannot be touched **without adding an increment**.

**Typical examples**:

- "Marketing strategies of beauty influencers on Douyin" (original PRD example)
- "User behavior research on short videos" (roughly 1200+ papers on the same topic in the last three years; questionnaire + descriptive statistics)
- "Factors influencing consumer purchase intention in livestream e-commerce"
- "Self-presentation on WeChat Moments"; "Current state and countermeasures of the influencer economy"

**Detection signals**:

- Search results on the same topic / same framework are dense; titles can be batch-copied by swapping the platform or the population.
- The common ending is the templated three-part "current state → problems → countermeasures".
- Reviews explicitly state "research is already fairly mature" or "results are abundant".
- Methods cluster around questionnaire + descriptive statistics, and conclusions are highly homogeneous.

**Fix / rewrite**: stack a new variable. Pick a less-studied population, a new platform feature, new data, or a new method; or move to the `gaps` that Engine A points out.

- Bad: "Marketing strategies of beauty influencers on Douyin"
- Fixed: "How do middle-aged and elderly beauty influencers build trust through 'de-youngifying' narratives? A comment-text study of 10 silver-haired beauty accounts on Douyin"

---

## 3. Infeasible

**Definition**: the **technology, data, equipment, channels, permissions, or timeline** the topic needs clearly exceeds the researcher's current ability and resources. No matter how elegant the idea, it cannot be completed under the given conditions; it is a castle in the air.

**Typical examples**:

- "An automatic restoration system for Dunhuang murals based on multimodal large models" — no technology, no dataset (original PRD example)
- "Fairness of recommendation algorithms based on nationwide million-scale user behavior logs" — logs are unavailable, no compute
- "A ten-year longitudinal experiment on early screen exposure and children's brain development" (course paper; no team, no timeline)
- "Design of a low-power edge computing system based on self-developed chips" (undergraduate; no fabrication access)

**Detection signals**:

- Depends on non-public data, equipment, or compute that would cost a large purchase.
- Requires cross-institutional, long-cycle, or high ethical-barrier work that the author has no resources for.
- The method says "build a system" or "self-develop a model" but the author has no engineering ability.
- Clearly contradicts the profile `resources`, level, or timeline (check against Engine C's C4).

**Fix / rewrite**: narrow down to materials you can actually obtain, or downgrade "build a system" to "analyze an existing system / public data".

- Bad: "An automatic restoration system for Dunhuang murals based on multimodal large models"
- Fixed: "The current state and teaching usability of public digital-image resources for Dunhuang murals: a secondary analysis of public datasets and literature"

---

## 4. Too Broad

**Definition**: the topic has blurry boundaries, covers too many objects, and spans too much time / space. **It cannot be fully handled in the assigned length and timeline**, and ends up as an empty overview or vague generalities.

**Typical examples**:

- "A comparative study of Chinese and Western literature" (original PRD example)
- "The impact of AI on human society"
- "The contemporary value of traditional Chinese culture"
- "Urban development under globalization"

**Detection signals**:

- The title has no qualifiers at all (no specific work, person, region, period, or group).
- Any one item would fill a book, yet it is crammed into one paper / one video.
- The only way to hide the mismatch is with words like "brief discussion / overview / limited view".
- The research question can be split into a dozen unrelated sub-questions.

**Fix / rewrite**: keep narrowing with "concrete object + qualifier + case study" until the length can hold it.

- Bad: "A comparative study of Chinese and Western literature"
- Fixed: "How does the recluse imagery travel across languages? A close reading of Tao Yuanming's 'Drinking Wine No. 5' against three translations of Thoreau's Walden"

---

## 5. False Question

**Definition**: the **presupposition of the question itself is invalid**, or it cannot be answered or falsified by any evidence. It is essentially a value statement, a metaphysical proposition, or an undefined conceptual dispute, and has no research value. This is the type that is **hardest to salvage by editing**.

**Typical examples**:

- "Will AI replace writers?" (original PRD example)
- "Does the internet make people more free or less free?" (concept undefined, cannot be falsified)
- "Has short video ruined this generation?" (presupposes "ruined"; emotional, unmeasurable)
- "Is this world real?"; "Is human nature inherently good or evil?" (no shared definition, no empirical outlet)

**Detection signals**:

- The answer can only take sides; no verifiable criterion is possible.
- Core concepts ("free", "ruined", "replace", "real") have no operational definition.
- Whatever evidence appears can be explained by either side; **it cannot be falsified**.
- It reads more like an opinion / slogan than a researchable question.

**Fix / rewrite**: rewrite the unfalsifiable grand judgment into a study of an "observable mechanism". In most cases, reject the topic outright.

- Bad: "Will AI replace writers?"
- Fixed: "At which concrete stages do AI writing tools change web-novel authors' workflows? Interviews with 15 signed authors"
- Bad: "Has short video ruined this generation?"
- Fixed: "The relationship between pre-sleep short-video use and next-day self-rated attention: a two-week diary study of 60 students at one university"

---

## 6. Unified detection checklist (run after generation)

> For each candidate, run through these quickly. Any hit means flag it and send it to Engine C for adjudication:

1. **Remove the buzzwords**. Does the question still hold? (concept stacking)
2. **How much has already been done**? What new thing do I bring? (over-saturation)
3. **Do I actually have the data and technology**? (infeasible)
4. **Can one paper / one video hold it**? Where are the boundaries? (too broad)
5. **What evidence would overturn it**? (false question)

---

## 7. Field mapping to the three engines

| Blacklist type | `fatal_flaw` value | First detected by | Review item |
|------------|-------------------|----------------|------------|
| Concept stacking | `concept_stack` | Engine B (`filtered_out`) | C2 / C5 |
| Over-saturated | `over_saturated` | Engine A (`saturated_topics`) | C5 |
| Infeasible | `infeasible` | Engine C (C4) | C4 |
| Too broad | `too_broad` | Engine C (C1 / C2) | C1 / C2 |
| False question | `false_question` | Engine C (C2) | C2 |

---

## 8. Acceptance checklist

- [x] All five types present: concept stacking, over-saturation, infeasible, too broad, false question
- [x] Each type includes **a definition and multiple examples** (all original PRD examples retained)
- [x] Each type adds detection signals and a positive rewrite example
- [x] Mapping to the three-engine fields (`fatal_flaw` / review items) is explicit
- [x] Stacking order and salvage principle are explicit
- [x] A unified self-check mnemonic is provided
