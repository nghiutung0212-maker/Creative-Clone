# Topic Output Template

> This document is produced by Team C (Engines). It is the **unified format standard** for Step 5 output in Creative Avatar.
> Every candidate that passes the Engine C gate must be rendered by the formatter as a **four-element topic card**. All four elements are required; a scene may only add fields, never remove them.
> The quality gate is in [`engine_self_critique.md`](./engine_self_critique.md). The avoidance standard is in [`bad_topic_blacklist.md`](./bad_topic_blacklist.md). Scene-specific tweak fields live in each scene profile under `output_format_adjustments`.

---

## 1. Standard four-element template (fill-in skeleton)

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Topic {number}
[Topic title]
"{concrete research question} (case study of {concrete object} / from {concrete angle})"

[Why it fits you]
This topic matches the following entries in your profile:
- {background / major entry} — how it is used
- {interest entry} — how it is used
- {preference / tone entry} — how it is used
(Each line must cite an entry that actually exists in the profile. Do not invent entries that are not there.)

[Three angles to approach it]
1. Angle A: {concrete, ready-to-use path}
2. Angle B: {concrete, ready-to-use path}
3. Angle C: {concrete, ready-to-use path}

[Risk notes]
- Feasibility risk: {whether data / channels / resources are available; fallback if not}
- Difficulty note: {the hardest step, method barrier, rough time needed}
- Ethics / compliance note: {if it involves human subjects, privacy, copyright, ad law, or platform rules; write "none" otherwise}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Hard requirements for the four elements**:

| Element | Must do | Common failures |
|------|----------|------------|
| (1) Topic title | A **concrete question** (with object + qualifier); the sentence can be answered and falsified | Vague theme, buzzword stacking, only a field name |
| (2) Why it fits you | Cite **specific profile entries** and explain how each is used | Only says "fits you well" with no basis; invents profile entries |
| (3) Three angles | Three **different, ready-to-use** paths, no repetition | Three lines saying the same thing; only direction, no how-to |
| (4) Risk notes | Covers feasibility / difficulty / ethics-compliance; concrete, not perfunctory | Only writes "not hard, watch the time"; dodges real issues |

---

## 2. How to fill in each element

### 2.1 Topic title

- Structure: `"{concrete question} — {qualifier structure}"`, usually "case study of X / from the X angle / using the X method".
- Must include: a **concrete object** (work / account / population / case) plus at least one qualifier (time / region / platform / population).
- Playful scenes may put the hook first. For short video: `"{hook copy}" "{title}"` (see the scene profile).

### 2.2 Why it fits you

- Use a paired "**profile entry → how it is used**" format; at least 2 lines.
- Prefer citing `base.backgrounds / interests / resources` and `preferences`.
- Follow "current request first, explicit first" (consistent with profile rules). Do **not** invent entries just to force a match.

### 2.3 Three angles to approach it

- The three paths must **not overlap**. Suggested split: "material / data angle", "theory / angle angle", "method / comparison angle".
- Each line says what to do first and what to look at, so the user can start immediately.
- Playful scenes may write one angle as a "viral / meme" angle, but it must still be executable.

### 2.4 Risk notes

- **Feasibility**: state clearly whether the key data / sample / channel is available; give a fallback.
- **Difficulty**: point out the hardest step and the method barrier; give a rough workload.
- **Ethics / compliance**: human subjects and informed consent, privacy and copyright, ad law and platform rules. If none apply, write "none". This row must not be omitted.

---

## 3. Scene tweak rules

- The four elements **cannot be omitted** in any scene. A scene profile may only add fields via `output_format_adjustments` (`extra_fields`) or adjust the title format (`title_format`).
- Added fields go after the four elements, under a "[Scene add-ons]" section.

| Scene | Title format example | Common added fields |
|------|--------------|--------------|
| Academic paper | `"{question} (case study of {object})"` | Suggested length, suggested method, keywords and databases to search, ethics review requirements |
| Short video | `"{hook copy}" "{title}"` | First-3-second hook, suggested duration, shooting format, tags and cover suggestions |
| Startup direction | `"{question} — validation based on {scenario}"` | MVP validation path, key assumptions, minimum-cost estimate |
| PPT presentation | `"{question} — {object}"` | Suggested duration, core argument, suggested slide count |
| WeChat article | `"{question}"` | Suggested word count, cover / title direction, target reader |

> Other scenes (event planning, podcast, course design, interview outline, etc.) follow the same "four elements + scene add-ons" rule.

---

## 4. Full example A (academic scene)

> Scene: `academic_paper`. User profile: history undergrad, interested in video games, general-education assignment, allows a little playfulness, method must be rigorous.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Topic 1
[Topic title]
"Public cognitive bias about the Roman Empire as seen in the Civilization series: a case study of 30 non-history undergraduates at one university"

[Why it fits you]
- History (undergraduate) background — you can provide the baseline narrative from historical records and scholarship on the Roman Empire, as a reference for judging bias.
- Interest: video games (Civilization series) — you know the game mechanics and can break down how the Roman civilization is designed.
- General-education course + tone that allows a little playfulness — the title has a casual, web-native feel and reads well in class, while the argument can stay rigorous.
- Resources: university library databases, about 12 hours per week — enough for text analysis and a small-sample questionnaire.

[Three angles to approach it]
1. Material / design angle: extract the tech tree, government, leader, and wonder designs for Rome in Civilization VI one by one,
   and mark where they simplify or dramatize "Rome's rise and fall" (for example, compressing complex institutional change into a linear tech progression).
2. Cognition / audience angle: run a questionnaire plus 5 interviews with 30 non-history players,
   measure how their views on "causes of Rome's fall", "slavery and the legions", etc. change before and after playing, and classify the bias types.
3. Comparison / angle angle: read the game narrative alongside 2-3 authoritative Roman-history surveys,
   extract cognitive frames the game implants (manifest destiny, technological determinism, great-man history), and analyze where they come from.

[Risk notes]
- Feasibility risk: the player sample must control for "whether they have formally studied Roman history before", otherwise attribution is hard;
  you can run the questionnaire in a general-ed class at the same university and, if the sample is small, expand to two neighboring schools.
- Difficulty note: the hard part is operationalizing "cognitive bias" into codeable, comparable items;
  run a small pilot interview first and design a coding sheet. Estimated 4-6 weeks.
- Ethics / compliance note: the questionnaire involves human subjects; anonymize, get informed consent, and allow withdrawal at any time.
  Game screenshots and design references must respect copyright and be used only for teaching / academic commentary.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Full example B (playful scene)

> Scene: `short_video`. User profile: college student starting a knowledge channel cold, one person with one phone, under 60 seconds on Douyin, goal is follower growth, prefers counter-intuitive hooks.

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Topic 1
[Topic title]
"The 'dumb method' you think is actually the hidden cheat code of top students"
Why does harder rote memorization lead to slower recall?

[Why it fits you]
- College-student knowledge-channel positioning — study methods are the most needed, most relatable topic for your target audience (college students).
- Cold start + one person with one phone — a talking-head shoot is enough; no props, team, or location needed.
- Prefers counter-intuitive hooks — "the harder you try, the slower you get" creates immediate cognitive conflict and fits your hook style.
- 60 seconds, Douyin vertical screen — the whole video makes one counter-intuitive point, and the length fits.

[Three angles to approach it]
1. Counter-intuitive opening: lead with "copying 10 times by hand is worse than active recall twice", and name it in one line as the testing effect.
2. Live demo: act out two memorization methods on camera (re-reading vs closing the book and recalling),
   so viewers see the difference at once, and give a 3-step method they can use tonight.
3. Comment interaction: end with a question, "are you the silent-reading type or the writing-it-out type?",
   push viewers to take sides in the comments, and turn the top comment into next week's topic.

[Risk notes]
- Feasibility risk: the point needs backing (cite the common finding on the testing effect / retrieval practice);
  do not present personal experience as an absolute truth. State the preconditions in the talking head.
- Difficulty note: in 60 seconds, only one point can be made; the most common mistake is trying to pack in too many methods.
  Write down in one line "what viewers should remember after watching".
- Ethics / compliance note: do not manufacture anxiety, do not put down any study method, do not promise "guaranteed admission to a top school";
  avoid false advertising and fight-baiting. Do not use unlicensed material.

[Scene add-ons]
- First-3-second hook: "Stop! Still reading the same page over and over? You might be 'fake-working'."
- Suggested duration: 45-60 seconds
- Shooting format: talking head + one cutaway of a study scene
- Tags and cover suggestions: #study methods #college students #memorization; cover headline "slower the more you memorize?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Output organization (a batch of N topic ideas)

1. **Count**: follow the scene profile `output.count` (default 5). If fewer pass, output all of them and say so; do not pad.
2. **Order**: sort by `output.sort_by` (`relevance` / `novelty` / `feasibility`). Default is relevance.
3. **Numbering**: number the whole batch (Topic 1...N) and separate cards with a divider.
4. **Opening line**: one sentence on what this batch is about and how it differs from the last batch, at most 2 sentences.
5. **Feedback entry at the end**: tell the user they can reply "interesting / give me a new batch / off track", and can pick one topic to go deeper (maps to Step 6).
6. **AI label and disclaimer** (fixed at the end of every batch):

```text
—
The above topic ideas are AI-generated and for creative reference only. Verify research, ethics, and compliance judgments on your own before using them.
Your feedback is saved to your local profile so the next batch fits you better. All data stays on your machine and is never uploaded.
```

---

## 7. Acceptance checklist

- [x] Four-element template complete: topic title / why it fits you / three angles / risk notes
- [x] Fill-in rules and common failures for each element
- [x] Scene tweak rules (title format + added fields)
- [x] Two full examples attached: one academic (history x games), one playful (short video)
- [x] Batch-level rules for count, order, numbering, and feedback entry
- [x] AI label and disclaimer included
- [x] Four elements are only added to, never dropped; consistent with the scene format spec
