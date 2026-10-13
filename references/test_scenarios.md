# Creative Avatar Skill: Test Cases

> This document is produced by Team F (Acceptance). It gives complete test cases covering 3 different scenarios, plus a "live run" record of the 6-step loop.
> Grading basis: `quality_standards.md` (scoring rubric). Cross-checked against Team C's `bad_topic_blacklist.md` and `output_template.md`.

## 1. Case overview

| Case | Scenario scene_id | User setup | Key difficulty |
|------|-------------------|------------|----------------|
| Case 1 | academic_paper | History undergrad, interested in video games, wants to write a paper for an elective | Cross-domain collision + academic rigor with a fun touch |
| Case 2 | short_video | Beginner creator, wants to make educational content, no team | Cold start + sparse info + compliance |
| Case 3 | event_planning | Student club, limited budget, wants a creative event | Zero budget + safety/compliance + executability |

Each case includes: input (profile + questionnaire answers), expected output (four elements + scenario extras), acceptance checkpoints (against the rubric).

---

## 2. Case 1: paper topic idea (academic_paper)

### 2.1 User setup

History undergrad, interested in video games, wants to submit a course paper for an elective with some pop-culture appeal.

### 2.2 Input

**Profile snapshot (profile_snapshot)**

```json
{
  "base": {
    "language": "zh-CN",
    "backgrounds": ["History (BA)"],
    "interests": ["video games"],
    "resources": ["school library database", "about 12 hours per week"]
  },
  "preferences": [
    { "key": "tone_preference", "value": "can be a bit playful", "source": "explicit" }
  ]
}
```

**Questionnaire answers (answers)**

| Field | Answer |
|-------|--------|
| discipline | History (modern Chinese history track) |
| level | Course paper |
| research_type | Case/text analysis |
| length | 3000–5000 words |
| cycle | Within two weeks |
| tone | Can be a bit playful |
| interests | Video games (the Civilization series) |
| resources | School library database, about 12 hours per week |
| hard_constraints | Elective course assignment; must show a clear research question and literature support |
| excludes | Does not want a pure literature review |

### 2.3 Expected output

Output N candidates per the `academic_paper` config. Each candidate strictly contains the four elements, plus scenario extras (suggested length, suggested method, keywords and databases, ethics-review requirements):

1. **Topic title**: `"{concrete question} (case study of {research object})"`, with object and qualifiers complete and a falsifiable question;
2. **Why it fits you**: cite real profile entries (history background, video game interest, elective tone, resources). Do not invent.
3. **Three angles**: non-overlapping, ready to start;
4. **Risk notes**: cover feasibility / difficulty / ethics and compliance;
5. **Scenario extras**: suggested length, method, keywords and databases, ethics-review requirements.

### 2.4 Acceptance checkpoints

- [ ] Four elements complete; title is a falsifiable concrete question
- [ ] "Why it fits you" cites >= 3 profile entries and explains each use
- [ ] No bad-topic blacklist types appear (watch especially for "concept stacking" and "scope too broad")
- [ ] Method matches resources (library database + 12 hours; no large system needed)
- [ ] Tone fits "can be a bit playful" but argumentation is rigorous (D5)
- [ ] Score per `quality_standards.md`: total >= 18, each dimension >= 3, zero blacklist hits

---

## 3. Case 2: short-video topic idea (short_video)

### 3.1 User setup

Beginner creator, wants to make educational content, no team, one person with one phone.

### 3.2 Input

**Profile snapshot**

```json
{
  "base": {
    "language": "zh-CN",
    "backgrounds": ["college student"],
    "interests": ["study methods", "productivity tools"],
    "resources": ["one person, one phone", "zero budget"]
  },
  "preferences": [
    { "key": "hook_style", "value": "counterintuitive", "source": "explicit" }
  ]
}
```

**Questionnaire answers (answers)**

| Field | Answer |
|-------|--------|
| account_domain | College-student education channel |
| platform | Douyin |
| audience | College students |
| duration | 30–60 seconds |
| form | Talking-head presentation |
| account_stage | Zero-follower cold start |
| hook_style | Counterintuitive |
| goal | Grow followers |
| red_lines | No anxiety-bait, no controversy-bait |

### 3.3 Expected output

Output per the `short_video` config. Title is "hook line + topic title", with four elements + scenario extras (first-3-second hook, suggested length, shooting format, tags and cover suggestions):

1. The topic explains a **single point** within 60 seconds;
2. The first 3 seconds have a counterintuitive hook;
3. Doable by one person with one phone (no team, no props, no outdoor shoot);
4. The point has common-sense basis; no exaggeration, no promise of results.

### 3.4 Acceptance checkpoints

- [ ] Four elements complete; title has a hook
- [ ] One video expresses one information point (per `constraint_list`)
- [ ] Shootable with no team/budget (D3 feasibility)
- [ ] Does not violate platform rules, controversy-bait, or false advertising (D5 + scenario `exclusion_rules`)
- [ ] Matches the "zero-follower cold start + college-student audience" profile (D4)
- [ ] Passes the rubric (total >= 18, each dimension >= 3, zero blacklist hits)

---

## 4. Case 3: event planning (event_planning)

### 4.1 User setup

Student club, limited budget, wants a creative event.

### 4.2 Input

**Profile snapshot**

```json
{
  "base": {
    "language": "zh-CN",
    "backgrounds": ["student club at a university"],
    "interests": ["board games", "creative markets"],
    "resources": ["free on-campus space", "8 club members", "budget under 500 RMB"]
  },
  "preferences": [
    { "key": "style_preference", "value": "playful", "source": "explicit" }
  ]
}
```

**Questionnaire answers (answers)**

| Field | Answer |
|-------|--------|
| organizer | University board-game club |
| event_type | Campus club event |
| audience | 30–50 enrolled students |
| budget | Under 500 RMB |
| cycle | About one week |
| goal | Recruit new members |
| venue | Free on-campus classroom (confirmed) |
| style | Playful |
| constraints_excludes | Needs school approval; no open flame; participants may have dietary restrictions |

### 4.3 Expected output

Output per the `event_planning` config. Title is "event theme + event type plan", with four elements + scenario extras (budget breakdown, key timeline, roles, supply list, contingency plan):

1. The plan is executable within budget (under 500 RMB), people (8), time (one week), and venue (on-campus classroom);
2. Has a clear event goal (recruitment) and a way to measure it;
3. Low participation barrier; accommodates different personalities and physical conditions;
4. Safe and compliant, with a contingency plan.

### 4.4 Acceptance checkpoints

- [ ] Four elements complete (for the event scenario, the four elements take the form of a plan)
- [ ] Executable on a low budget; no expensive supplies (D3)
- [ ] Covers recruitment goal and retention/conversion design (scenario `skip_logic`)
- [ ] No safety hazards, no open flame, dietary restrictions respected (D5 + `exclusion_rules`)
- [ ] Has a contingency plan (weather/equipment/headcount/incidents) (scenario `constraint_list`)
- [ ] Passes the rubric

---

## 5. Appendix: live run (Case 1 · full 6-step loop record)

> Live run date 2026-10-13; ran offline locally, no WebSearch mounted. The record below follows the SKILL.md main flow step by step, truthfully, including one measured **degradation path**.

### Step 1 Scenario selection

The user describes "elective course paper topic" -> matches the `academic_paper` trigger phrase -> loads the scene profile -> JSON syntax and 7-field validation pass -> enter Step 2.

### Step 2 Scenario questionnaire

Answered in 4 rounds (answers in section 2.2). "Course paper" triggers a jump: skips journal/grant-level questions, keeps length and cycle questions.

### Step 3 Follow-up dialogue

Three follow-up questions to fill profile gaps: (1) Do you want some pop-culture flair in the elective -> yes, but the argument must stay rigorous; (2) Tolerance for counterintuitive angles -> high; (3) Any available player sample channel -> yes, classmates at the same university. No local reading consent -> stay in light mode, skip local file reading.

### Step 4 Three engines

**Engine A · Saturation scan**: no WebSearch in this environment; follows `on_no_evidence = mark_unsure` with knowledge-base fallback, `evidence.real_time = false`, conclusions are advisory avoidance only:

- "Causes of the fall of the Roman Empire" -> classic topic, heavily saturated, `hot` (advisory avoidance; not written to the hard blacklist);
- "The effect of the game medium on public historical cognition (using Civilization as the object)" -> little empirical work at this intersection, `gap`;
- Saturation hits and blacklist hits: none (no real-time search, so nothing is written to the hard blacklist).

**Engine B · Cross-domain collision**: core domain "history (Roman Empire)" x interest domain "video games (Civilization)" ->

- Candidate 1 (valid): "Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university". `why_link` = how the same object is presented differently in historical texts vs. games is comparable and falsifiable;
- Candidate 2 (counter-example, rejected): "Pathways of large-model-empowered Roman history teaching under the metaverse" -> fails once buzzwords are stripped; `filtered_out`.

**Engine C · Self-critique review** (`quality_gate = pass_all`):

- Candidate 1: C1–C6 all pass (clear object / falsifiable question / text-analysis + survey-interview method fits / within resources and timeline / game-medium angle adds value / fits the "a bit playful" tone) -> `pass`;
- Candidate 2: C2, C5 fail; `fatal_flaw = concept_stack` -> `reject`.

### Step 5 Output (candidates that passed the gate, four elements)

```text
Topic 1
[Topic title]
Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university
[Why it fits you]
· History (BA) background: provides the baseline narrative of Roman history as a reference for bias;
· Interest: video games (Civilization): knows the game mechanics and can break down its Roman setting;
· Elective + a bit playful: the title has pop-culture appeal and plays well in class, while the argument can stay rigorous;
· Resources: library database + 12 hours/week: supports text analysis and a small-sample survey.
[Three angles]
1. Setting angle: extract Civilization VI's Roman tech tree / government / leaders / wonders; mark how they simplify Rome's rise and fall;
2. Audience angle: survey 30 non-history players + 5 interviews; measure cognition before vs. after playing;
3. Comparison angle: read the game narrative alongside 2-3 authoritative Roman general histories; extract the cognitive framework implanted.
[Risk notes]
· Feasibility risk: control for "has formally studied Roman history"; if the sample is too small, expand to two nearby universities;
· Difficulty: the hard part is operationalizing "cognitive bias" into codable items; needs pilot interviews + a coding sheet; about 4-6 weeks;
· Ethics/compliance: involves human subjects; anonymize, informed consent, right to withdraw; game screenshots are used only for teaching/academic commentary.
[Scenario extras]
· Suggested length: 3000-5000 words
· Suggested method: text/setting analysis + small-sample survey and interviews
· Keywords and databases: Roman Empire; Civilization VI; historical cognitive bias / CNKI, JSTOR, Google Scholar
· Ethics review: course-paper level; anonymous survey + informed consent is enough; no formal IRB approval needed
```

### Step 6 Feedback iteration (real script run)

The user marks candidate 1 as "final pick" -> run the real desktop script:

```text
python3 scripts/update_profile.py --feedback select \
  --topic "Cognitive bias toward the Roman Empire as seen through the Civilization series: a case study of 30 non-history undergraduates at one university" \
  --scenario academic_paper --query "History undergrad, wants a course paper with some pop-culture appeal for an elective"
```

Result (real output, excerpt): `history` gains one `feedback=select` entry with `chosen_topics`; `signals.selected_topics` and `base.interests` write this topic; `preferences` gains `selected_topic` (`source=explicit`, `confidence=0.9`); `stats.select_count = 1`.

### Live-run scoring and conclusion

| Dimension | Candidate 1 | Candidate 2 (counter-example) |
|-----------|-------------|-------------------------------|
| D1 Concreteness | 5 | 1 |
| D2 Originality | 5 | 1 |
| D3 Feasibility | 4 | 2 |
| D4 Fit | 5 | 1 |
| D5 Restraint | 5 | 2 |
| Blacklist | None | concept_stack (veto) |
| Conclusion | 24/25 excellent | 0, fails |

**Live-run conclusion**: Case 1 passes. The 6-step loop runs end to end; the three engines chain and pass data correctly. The saturation scan correctly took the `mark_unsure` degradation path offline and explicitly marked "not searched in real time". Self-critique correctly rejected the concept-stacking counter-example. The final candidate scored 24/25 with no blacklist hits.

> Note: candidate 1's "within two weeks" and "4-6 weeks" are in tension. This is stated honestly in the risk/difficulty notes rather than hidden; it reflects the "no fake feasibility" principle. If "within two weeks" is a hard constraint, shrink the sample further (e.g., 10 people + text analysis only), and feasibility could rise to 5.
