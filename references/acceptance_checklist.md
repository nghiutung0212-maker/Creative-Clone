# Creative Avatar Skill: Acceptance Checklist

> This document is produced by Team F (Acceptance). It accepts item by item against the five dimensions of "success criteria" in PRD section 8, and adds Team F's own meta-level acceptance and live-run conclusions.
> Status legend: ✅ Passed (with evidence) | 🟡 Pending external verification (needs real users / release environment) | ❌ Not met.

## 1. Dimension 1: High quality

| # | Acceptance item | Status | Evidence |
|---|--------|------|------|
| 1.1 | Generated topic ideas hit none of the five blacklist types | ✅ | Engine C one-vote veto + `bad_topic_blacklist.md`. In live runs, a "concept stacking" counter-example was correctly rejected. |
| 1.2 | Every topic idea passes the self-critique review (six hard constraints) | ✅ | `engine_self_critique.md` 6-item list + `quality_gate=pass_all`. Live-run candidate 1 passed all six. |
| 1.3 | Output strictly contains the four elements, no omissions | ✅ | `output_template.md`. Live-run candidate 1 had all four elements plus scene add-ons. |
| 1.4 | Saturation scan has evidence or is explicitly marked "not searched live"; no fabrication | ✅ | `engine_saturation_scan.md` anti-fabrication line. Live runs used `mark_unsure` and labeled accordingly. |

## 2. Dimension 2: Legal

| # | Acceptance item | Status | Evidence |
|---|--------|------|------|
| 2.1 | Open-source compliance (MIT license) | 🟡 | LICENSE is delivered by Team G (not yet delivered). |
| 2.2 | Privacy compliance, covering the 5 design points in PRD section 7 | ✅ | `privacy_policy.md` section 12, item-by-item. |
| 2.3 | Does not collect user data (zero upload, zero telemetry, no account) | ✅ | Team E section 2. Team D scripts read / write locally only; auditable via `grep`. |
| 2.4 | Local reading requires explicit consent + least privilege + can be turned off at any time | ✅ | `privacy_policy.md` section 6 + Team D `profile_schema.md` section 11. |
| 2.5 | AI-generated content is labeled | ✅ | `privacy_policy.md` section 10, README privacy draft. |
| 2.6 | Profile file is in `.gitignore`, not in the public repo | 🟡 | Requirement is stated in Team E 4.1 / Team D; pending Team G's `.gitignore` to land. |

## 3. Dimension 3: Usable

| # | Acceptance item | Status | Evidence |
|---|--------|------|------|
| 3.1 | Install and use (scripts run standalone, stdlib only) | ✅ | `init_profile.py` / `update_profile.py` tested (idempotent, atomic write, `--force` backup). |
| 3.2 | 6-step loop runs smoothly | ✅ | One full live run (see appendix in `test_scenarios.md`). |
| 3.3 | Few bugs (profile read/write, JSON validation) | ✅ | All JSON passes `json.tool`; four feedback-update paths tested correct. |
| 3.4 | Docs are clear enough to follow and install | 🟡 | A/B/C/D/E docs are complete and cross-reference consistently; README pending Team G integration. |

## 4. Dimension 4: High practical value

| # | Acceptance item | Status | Evidence |
|---|--------|------|------|
| 4.1 | Real-user test: at least 6 of 10 say "I could actually use this topic" | 🟡 | Needs real-user testing after Team G release; test cases and scorecard are ready. |
| 4.2 | Test cases cover at least 3 different scenes | ✅ | `test_scenarios.md` covers paper / short video / event planning. |

## 5. Dimension 5: User retention

| # | Acceptance item | Status | Evidence |
|---|--------|------|------|
| 5.1 | Users come back after one use (profile accumulation creates positive feedback) | 🟡 | Cross-scene profile accumulation is implemented; retention needs real-use verification. |
| 5.2 | Users are willing to recommend (it gets better over time, and has good judgment) | 🟡 | Differentiating capability is in place; needs word-of-mouth verification. |

## 6. Team F self-acceptance (meta level)

| # | Acceptance item | Status |
|---|--------|------|
| 6.1 | Quality scoring standard is quantitative and operational | ✅ `quality_standards.md` |
| 6.2 | Test cases cover at least 3 different scenes | ✅ `test_scenarios.md` |
| 6.3 | Acceptance checklist maps one-to-one to PRD success criteria | ✅ Dimensions 1-5 in this checklist |
| 6.4 | Live-ran one 6-step loop using test cases and attached results | ✅ `test_scenarios.md` appendix |

## 7. Live-run summary

- Test case 1 (paper topic) passed: the three engines chained correctly, data passed through correctly, the offline fallback path is correct, and the counter-example was correctly rejected.
- Final candidate scored 24/25 (excellent), zero blacklist hits.
- Step 6 feedback accumulation was verified with the real script (`select` -> `history / signals / base.interests / preferences / stats` all updated correctly).

## 8. TODO and risks (handed to lead for integration)

1. The 🟡 items in dimensions 2 / 3 / 4 / 5 depend on Team G (README, LICENSE, `.gitignore`, GitHub release) and real-user testing; Team F cannot close them alone.
2. In test case 1, "within two weeks" and "4-6 weeks" are in tension; this is stated honestly in the risk / difficulty note. If two weeks must be strictly met, inject `cycle` as a hard constraint into Engine C at the questionnaire stage.
3. Engine A in an offline environment can only fall back to its knowledge base (`real_time=false`); conclusions are suggestive. After release, re-run a live-search round in a networked environment.
