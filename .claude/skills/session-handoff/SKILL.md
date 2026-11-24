---
name: session-handoff
description: Write a complete, self-contained handoff summary of the current conversation so it can be pasted into a brand-new session with zero context loss. Use when the user says "session handoff", "handoff summary", "/session-handoff", or wants to clear or move the conversation without losing context.
---

## Vibe editing house rules (read first; they override the upstream text below)

Added 2026-11-24 from the user's upload (session-handoff.zip, one SKILL.md, no scripts). The upstream text is kept
unchanged below this section.

- **Save it in the repo, not only in the chat.** Memory and the container are wiped between sessions. Write the
  summary to `projects/<name>/HANDOFF.md` for a video session (or `docs/playbook/handoffs/<date>-<topic>.md` for a
  setup session), commit it and push it to the session branch, then also paste it in the reply. A new session
  only needs: "read projects/<name>/HANDOFF.md and carry on".
- **Never write secret values.** The upstream template asks for "secrets": list only their names and where they
  come from (the ElevenLabs key is injected by the environment's network secret; Codex signs in per session with
  the user's ChatGPT account). No tokens, keys, auth.json contents or the user's email.
- **Video sessions: cover the vibe editing state.** Video name and branch; which raw files are needed again (raw
  footage is not in git, list each file with length and what it is); the approved cut and look; the current
  version (v1, v2...) and what the user said about it, word for word where it matters; every open question with the
  default; the exact rebuild steps (point to `RENDER.md`); paid audio already generated (never regenerate); lessons
  not yet written to `docs/playbook/lessons-learned.md` (write them there too).
- Plain human language, no em dashes. End by reminding the user the summary is also saved at the path above.

---

# Upstream skill text

Write a complete, self-contained handoff summary of the current conversation so it can be pasted into a brand-new session with zero context loss.

The summary must cover everything a future Claude instance needs to continue without asking follow-up questions. Do not be lazy. Do not omit anything important. Structure it as follows:

---

## Project Overview
What the project is, what it does, who it's for. Include all key URLs, repo paths, account names, and identifiers.

## Full Architecture
Every component in the system: what it does, how it connects to other components, key file paths, environment variables, secrets, and any non-obvious wiring. Be exhaustive.

## Key File Paths
All important files and their purpose.

## Current State
What is working, what is broken, what has been attempted. Include test results, known edge cases, and open questions.

## Bugs Fixed (this session)
For each bug fixed: what the symptom was, what the root cause was, what the fix was, which commit it landed in.

## What Was Done This Session
Chronological summary of every meaningful action taken: code changes, config changes, infrastructure changes, decisions made.

## What to Do Next
Prioritised list of next steps with enough context that the next session can begin immediately without re-investigation.

## Important Constraints and Gotchas
Non-obvious rules, anti-patterns to avoid, things that were tried and failed, architectural decisions that must not be undone.

---

After writing the summary, remind the user to copy it before clearing the conversation.
