# Creative Avatar: Topic Ideation Skill for Any Scenario

> A Skill for generating creative topic ideas from scratch, for scenarios such as academic papers, PPT presentations, short videos, WeChat articles, startup ideas, event planning, podcasts, course design, and interviews. It runs three engines together: a saturation scan to flag overdone directions, cross-domain collision to find new angles, and self-critique iteration to polish the results. It keeps a local profile of your feedback, so later topic ideas fit you better.

---

## Privacy and security

**Creative Avatar does not collect any of your data.**

- **No account, no server, no tracking**: all data-processing logic is open source; you can review it line by line.
- **File reading is off by default**: it only turns on when you explicitly grant access and pick a folder yourself. Without access, every feature still works.
- **It reads only the folder you specify, not the whole disk**: it extracts four kinds of summary features (writing style, knowledge background, interests, depth of thinking), and does not copy or modify your files. The results are stored only in `~/.creative-clone/profile.json` on your machine.
- **You can change your mind at any time**: turn it off in one click in Settings and it falls back to questionnaire + dialogue mode. The profile can be viewed, edited, or deleted at any time.

> Note: when topic ideas are generated through a cloud model (GPT / Gemini / DeepSeek, etc.), your conversation — including the summary features extracted locally — is handled under that model service's privacy policy. The original file content never enters the conversation. To work fully offline, you can point the Skill at a local model backend.

| Data | Where it is stored | Uploaded? |
|------|--------------------|-----------|
| Questionnaire answers, dialogue, feedback, selected topic ideas | Your local profile file | No |
| Summary features extracted after authorization (style / background / interests / depth of thinking) | Your local profile file | No |
| Original document content | Not extracted, not stored | No |

**Common operations**:

- View the profile: open `~/.creative-clone/profile.json`
- Disable local file reading: Settings → Privacy & Authorization → turn off "Local file reading"
- Remove everything: delete the profile file; there is no cloud copy

Full details in the [privacy policy](references/privacy_policy.md).

---

## Installation

### Install as a Skill

1. Clone or download this repository
2. Put the `creative-clone/` directory into your AI assistant's Skill directory
3. Type a trigger phrase such as "help me come up with topic ideas" or "I'm looking for a paper topic" to load the Skill automatically

### Manual use

For standalone use, you can still:

1. Read `SKILL.md` for the full workflow
2. Run the three engines manually with the engine prompts under `references/`
3. Run the profile scripts:

```bash
# Initialize the profile
python3 scripts/init_profile.py

# Update the profile after ideation (four feedback types)
python3 scripts/update_profile.py --feedback select --topic "your topic title" --scenario academic_paper
python3 scripts/update_profile.py --feedback like --topic "your topic title"
python3 scripts/update_profile.py --feedback dislike --topic "your topic title"
python3 scripts/update_profile.py --feedback redirect --topic "your topic title" --query "a more actionable direction"

# Apply time decay to stale topic weights
python3 scripts/update_profile.py --decay

# Print the user's top-N interests by weight
python3 scripts/update_profile.py --top-interests 10

# Validate outputs and configs
python3 scripts/validate_output.py --scenes                    # validate all scene profiles
python3 scripts/validate_output.py --engine a <file>           # validate Engine A output
python3 scripts/validate_output.py --engine b <file>           # validate Engine B output
python3 scripts/validate_output.py --engine c <file>           # validate Engine C output
python3 scripts/validate_output.py --profile ~/.creative-clone/profile.json  # validate profile
```

> The scripts use only the Python standard library; no third-party dependencies are needed.

---

## Usage (6-step interactive loop)

This is a **multi-turn interactive flow**. The AI pauses at each step and waits for your input before proceeding. It does not generate topics until the questionnaire and profile loading are complete. Each engine's intermediate output (saturation report, collision candidates, critique verdicts) is shown to you as a visible section before the final results.

```
Step 1 Pick a scenario ──STOP──► Step 2 Questionnaire (round by round) ──STOP──►
Step 3 Profile + follow-up ──STOP──►
Step 4 Engine A (visible report) → Engine B (visible report) → Engine C (visible report)
  ↓
Step 5 Topic ideas (four-element cards) ──► Step 6 Feedback → profile update
```

1. **Pick a scenario**: choose or describe your scenario (paper / short video / event planning, etc.); the matching scene profile loads
2. **Scenario questionnaire**: step-by-step questions (2-3 per round) with conditional jumps — the AI asks round by round and waits for your answers before proceeding
3. **Follow-up dialogue + profile**: 3-5 follow-up questions to fill profile gaps, plus `init_profile.py` loads or creates your local profile
4. **Three-engine generation** (each engine's output is shown to you as a visible report):
   - Engine A: saturation scan — searches for overdone directions and gaps
   - Engine B: cross-domain collision — crosses your interest domains to find new angles (each with a `why_link` explaining the connection)
   - Engine C: self-critique — checks each candidate against 6 hard constraints, rejects or revises failures
5. **Topic ideas**: each idea has four elements — the concrete question / why it fits you / three angles to approach it / risk notes
6. **Feedback loop**: mark "interesting / show others / off track / selected" → `update_profile.py` records the feedback with weight deltas (select +0.30, like +0.10, dislike -0.20, redirect -0.40); weights decay over time so recent interests stay dominant → later suggestions fit you better

---

## Supported scenarios

| Scenario | Tone | What it covers |
|----------|------|----------------|
| Academic paper | Academic | Course papers, thesis, proposal, journal submission, grant applications |
| PPT presentation | Formal | Course presentation, defense, work report, pitch, conference sharing |
| Short video | Playful | Topic ideas, hooks, and shooting formats for videos under three minutes |
| WeChat article | Formal | Opinion pieces, tutorials, industry analysis, stories, hot-topic takes |
| Startup idea | Formal | Startup ideas, product direction, business opportunities, with an MVP validation path |
| Event planning | Playful | Campus clubs, team building, business events, salons, competitions, online events |
| Podcast | Playful | Episode topics, discussion points, show planning |
| Course design | Academic | Teaching design for a single lesson, a unit, or a whole course |
| Interview | Formal | Question lists for profiles, industry / event / promotion interviews |

**Adding a scenario**: add a JSON file under `assets/scene_profiles/` and append one row to the index in `references/scene_configs.md`. See [scene profile format spec](references/scene_format_spec.md) and [scene library guide](references/scene_configs.md).

---

## Three-engine logic

| Engine | Job | Output |
|--------|-----|--------|
| A · Saturation scan | Detect which directions are overdone and which have gaps | saturated_topics (avoid list) + gaps (priority targets) |
| B · Cross-domain collision | Cross the core domain with interest domains to find counter-consensus angles | candidates[] (each with why_link) |
| C · Self-critique iteration | Judge each topic against the six hard constraints like a strict reviewer | final_candidates[] (those that pass) |

**Six hard constraints**: has a concrete subject / has a clear, falsifiable question / has an actionable method / fits the user's resources / not overdone / matches the scenario tone

**Five bad-topic types (blacklist)**: concept stacking / over-saturation / not actionable / scope too broad / fake problem

---

## Project structure

```
creative-clone/
├── SKILL.md                    # Main file: 6-step flow + three engines + scenario adaptation
├── scripts/
│   ├── init_profile.py         # Profile init (standard library only)
│   ├── update_profile.py       # Weighted feedback + time decay + idempotency
│   └── validate_output.py      # Validate engine outputs, scene profiles, and profile
├── schemas/                    # JSON Schema files for validation
│   ├── engine_a_output.json    # Engine A saturation scan output schema
│   ├── engine_b_output.json    # Engine B cross-domain collision output schema
│   ├── engine_c_output.json    # Engine C self-critique output schema
│   ├── scene_profile.json      # Scene profile JSON schema
│   └── profile_v2.json         # User profile schema (v2, weighted topics)
├── references/                 # Engine prompts + blacklist + output template + privacy policy + quality standards
├── assets/
│   ├── profile_template.json   # Default profile template (schema_version 2)
│   └── scene_profiles/         # 9 scene profile JSONs
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

---

## Contributing

Contributions are welcome. See the [contribution guide](CONTRIBUTING.md).

You can:
- Add a scene profile (add one JSON file)
- Improve the engine prompts
- Report bugs or suggest improvements (do not paste profile content into issues)

---

## License

MIT License — free to use, modify, and distribute.

Privacy policy: [references/privacy_policy.md](references/privacy_policy.md). AI-generated content is for reference only.
