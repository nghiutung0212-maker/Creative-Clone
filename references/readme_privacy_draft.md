# README Privacy Draft (Team E · Compliance -> Team G · Release)

> **Handover team**: Team E (Compliance)
> **Document version**: v1.0 (matches `privacy_policy.md` v1.0 and `consent_version = "1.0"`)
> **Purpose**: this file is a Markdown snippet for Team G to integrate into `README.md`.
> **Placement (hard requirement, from PRD 7.3)**: first screen of the README, **after the project title / one-line intro and before the installation section**. It is the first formal section a reader sees after opening the README.
> **Writing requirement**: plain language for non-technical users; technical details are linked out to the full policy rather than expanded here.

---

## Snippet to integrate below (copy everything below this line into README.md)

---

## Privacy and security

**Creative Avatar does not collect any of your data.**

- **No account, no server, no tracking**: all data-processing logic is open source; you can review it line by line.
- **File reading is off by default**: it only turns on when you explicitly grant access and pick a folder yourself. Without access, every feature still works.
- **It reads only the folder you specify, not the whole disk**: it extracts four kinds of summary features (writing style, knowledge background, interests, depth of thinking), and does not copy or modify your files. The results are stored only in `~/.creative-clone/profile.json` on your machine.
- **You can change your mind at any time**: turn it off in one click in Settings and it falls back to questionnaire + dialogue mode. The profile can be viewed, edited, or deleted at any time.

> Note: when topic ideas are generated through a cloud model (GPT / Gemini / DeepSeek, etc.), your conversation, including the summary features extracted locally, is handled under that model service's privacy policy. The original file content never enters the conversation. To work fully offline, you can point the Skill at a local model backend.

| Data | Where it is stored | Uploaded? |
|------|--------------------|-----------|
| Questionnaire answers, dialogue, feedback, selected topic ideas | Your local profile file | No |
| Summary features extracted after authorization (style / background / interests / depth of thinking) | Your local profile file | No |
| Original document content | Not extracted, not stored | No |

**Common operations**:

- View the profile: open `~/.creative-clone/profile.json`
- Disable local file reading: Settings -> Privacy & Authorization -> turn off "Local file reading"
- Remove everything: delete the profile file; there is no cloud copy

Full details in the [privacy policy](references/privacy_policy.md).

---

## Integration notes (for Team G, do not copy into README)

1. **Position must not be moved down**: PRD 7.3 requires the privacy policy to sit in the most visible spot of the GitHub README. This snippet must appear before the installation instructions.
2. **Link path**: `references/privacy_policy.md` is the actual path in the repo. Confirm the link is clickable after integration.
3. **Keep the wording plain**: if layout requires small tweaks, only adjust formatting. Do not weaken the four promises ("off by default / opt-in / reads only the chosen folder / can be turned off at any time"), and do not remove the cloud-model note (to avoid misleading users).
4. **Echo at the end of the README**: before the "License" section at the end of the README, add one line: `Privacy policy: [references/privacy_policy.md](references/privacy_policy.md). AI-generated content is for reference only.`
5. **Version sync**: when the privacy policy is upgraded (for example, `consent_version` changes), this summary must be updated in lockstep and announced in the README / CHANGELOG.
