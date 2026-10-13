# Creative Avatar Skill: Per-Team Delivery Spec

> This document is produced by Team A (Architecture). It is the shared reference for all downstream teams.
> It specifies where each team's deliverables go, what they are named, and the format requirements.

## Directory layout

```
creative-clone/
├── SKILL.md                              ← A built the skeleton; C/D/E fill the body; the lead integrates at the end
├── scripts/
│   ├── init_profile.py                   ← D deliverable
│   └── update_profile.py                 ← D deliverable
├── references/
│   ├── scene_format_spec.md              ← A delivered (scene profile format spec)
│   ├── scene_configs.md                  ← B deliverable (scene library usage guide + extension guide)
│   ├── engine_saturation_scan.md         ← C deliverable (saturation scan engine)
│   ├── engine_cross_collision.md        ← C deliverable (cross-domain collision engine)
│   ├── engine_self_critique.md           ← C deliverable (self-critique iteration engine)
│   ├── bad_topic_blacklist.md           ← C deliverable (five bad-topic types blacklist)
│   ├── output_template.md                ← C deliverable (four-element output template)
│   ├── profile_schema.md                 ← D deliverable (profile JSON schema + authorization)
│   ├── privacy_policy.md                 ← E deliverable (full privacy policy)
│   ├── quality_standards.md              ← F deliverable (topic quality scorecard)
│   ├── test_scenarios.md                ← F deliverable (3 scene test cases)
│   └── acceptance_checklist.md          ← F deliverable (PRD acceptance checklist)
├── assets/
│   ├── profile_template.json              ← D deliverable (default profile template)
│   └── scene_profiles/
│       ├── academic_paper.json            ← B deliverable
│       ├── ppt_presentation.json         ← B deliverable
│       ├── short_video.json              ← B deliverable
│       ├── wechat_article.json           ← B deliverable
│       ├── startup_idea.json              ← B deliverable
│       ├── event_planning.json           ← B deliverable
│       ├── podcast.json                  ← B deliverable
│       ├── course_design.json            ← B deliverable
│       └── interview_outline.json        ← B deliverable
├── README.md                              ← G deliverable
├── LICENSE                                ← G deliverable (MIT)
├── CONTRIBUTING.md                        ← G deliverable
└── .gitignore                            ← G deliverable
```

## Per-team delivery spec

### B · Scene Library

| Deliverable | Path | Format |
|---------|------|------|
| 9 scene profiles | `assets/scene_profiles/*.json` | JSON, strictly per `references/scene_format_spec.md` |
| Scene library guide | `references/scene_configs.md` | Markdown |

### C · Engines

| Deliverable | Path | Format |
|---------|------|------|
| Saturation scan engine | `references/engine_saturation_scan.md` | Markdown, with a directly runnable prompt |
| Cross-domain collision engine | `references/engine_cross_collision.md` | Markdown, with a directly runnable prompt |
| Self-critique engine | `references/engine_self_critique.md` | Markdown, with a directly runnable prompt |
| Bad-topic blacklist | `references/bad_topic_blacklist.md` | Markdown, 5 types + definition + examples |
| Output template | `references/output_template.md` | Markdown, four elements + at least 2 full examples |

### D · Profile

| Deliverable | Path | Format |
|---------|------|------|
| Profile schema | `references/profile_schema.md` | Markdown, with JSON schema definition + authorization mechanism |
| Default profile template | `assets/profile_template.json` | JSON, empty-value template |
| Init script | `scripts/init_profile.py` | Python, runs standalone |
| Update script | `scripts/update_profile.py` | Python, runs standalone |

### E · Compliance

| Deliverable | Path | Format |
|---------|------|------|
| Privacy policy | `references/privacy_policy.md` | Markdown |
| README privacy draft | Attached to the handover notice | Markdown snippet |

### F · Acceptance

| Deliverable | Path | Format |
|---------|------|------|
| Quality scoring standard | `references/quality_standards.md` | Markdown |
| Test cases | `references/test_scenarios.md` | Markdown |
| Acceptance checklist | `references/acceptance_checklist.md` | Markdown |

### G · Release

| Deliverable | Path | Format |
|---------|------|------|
| Project readme | `README.md` | Markdown |
| Open-source license | `LICENSE` | Standard MIT text |
| Contribution guide | `CONTRIBUTING.md` | Markdown |
| Git ignore | `.gitignore` | Standard gitignore |

## Naming rules

- Scene profile files: `snake_case.json` (for example, `academic_paper.json`)
- Reference files: `snake_case.md` (for example, `engine_saturation_scan.md`)
- Script files: `snake_case.py`
- All JSON files must pass JSON syntax validation.

## Handover

1. After each team finishes, place deliverables at the paths above.
2. Attach a short handover note: which files changed, any deviation from the spec, any outstanding TODO.
3. Hand over to the lead (integration stage) for unified assembly and packaging verification.
