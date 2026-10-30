---
name: vibe-wrap-up
description: End-of-session learning for the Vibe editing project. Use when the user calls /vibe-wrap-up, or says the editing session is done and asks what was learned, to "save the lessons", "remember this for next time", "wrap up", "debrief", or to carry knowledge into future sessions. Reviews the whole session, explains in detail every lesson, skill and piece of knowledge gained, and writes all of it permanently into docs/playbook/lessons-learned.md and CLAUDE.md (pushed to the default branch) so every future session starts better. Run once at the end of each video session; it is safe to run more than once.
---

# Vibe wrap-up: learn from this session, permanently

The user makes one video per session and wants to get better every session, with **no lesson ever lost**. Memory does
not survive between sessions; only the repo does. This skill turns everything this session taught into durable
knowledge, then tells the user what was learned. The user calls it once when a session is done; do the whole job
without asking for anything, apart from the final-merge question in step 7.

Write in plain, human language, never em dashes (the user's rule).

## 1. Sync first
- `git fetch origin`, merge the default branch (find it with `git remote show origin`, HEAD branch) into the session
  branch, so you build on the latest `docs/playbook/lessons-learned.md` and `CLAUDE.md`.
- Read `docs/playbook/lessons-learned.md` in full and the "Learning loop" and "Lessons from past edits" sections of
  `CLAUDE.md`, so you know what is already recorded.

## 2. Gather the evidence (the whole session, not just the end)
Go through, in order:
- **The conversation from its first message:** every note, correction, complaint, question and preference the user
  gave, every "why did you...", every request that changed course. Note what you proposed and what they chose.
- **The project folder** (`projects/<name>/`): `brief.md` (decisions, beat sheet), `work/revisions.md` (each round and
  why), `RENDER.md`, the code (`scene.py`, `work/build/`, `work/matte/`...), `git log -- projects/<name>`.
- **Anything already added to the lessons file during this session** (learning loop step 2), so you only add what is
  missing and improve what is there.

## 3. Extract the lessons
Look for every kind, and be concrete (numbers, times, file paths, the exact note in the user's words when it helps):
- **The user's taste and working style:** what they liked, disliked, asked to change, how they like to be asked, how
  they send footage, what they care about (quality, physique time, face, accuracy).
- **Revisions:** every note that cost a round. What was wrong, why it happened, the rule that prevents it next time.
- **Techniques that worked**, with the code location to copy (`projects/<name>/...`, function names) and the key
  parameters. Effects, grades, mattes, captions, transitions, timing methods.
- **Things that failed or were tried and dropped**, and why (a model that gave a lumpy edge, a crop that showed a logo).
- **Tools and models:** which worked for what, versions, quirks, install issues, speed (render time per second).
- **Numbers worth keeping:** file sizes per crf and length, loudness, durations, sizes and positions of text, fps.
- **Process lessons:** what made approvals faster, what checks caught problems, what you should have asked earlier.
- **Environment facts:** limits hit (30 MiB send, memory, disk), workarounds, anything blocked.
- **Mistakes you made**, plainly, so they never repeat.
Skip anything already recorded unless this session adds new detail; then update the existing entry instead of
writing a duplicate.

## 4. Write them down
- **`docs/playbook/lessons-learned.md`:** put each lesson in the right section (1 the user, 2 reference remakes,
  3 footage, 4 cut-outs, 5 effects, 6 text and captions, 7 audio, 8 workflow, 9 delivery, 10 mistakes). Add a new
  section when a topic doesn't fit (for example a new video type). Tag every entry with the video name, like `[r04]`,
  and add the tag to the legend at the top. Keep entries short and actionable: the rule first, then the evidence.
  Merge with existing entries when they are about the same thing.
- **`CLAUDE.md`, "Lessons from past edits":** add a short "Learned on <video> (<date>)" block with only the lessons
  that cost a revision or apply to every video (CLAUDE.md is always loaded, so keep it tight). Point to the lessons
  file for detail.
- **Reusable code:** make sure every effect or recipe the lessons point to is committed in its project folder
  (`git add -f` for files under the ignored `work/`). Never move it out of the project; the lessons give the path.
- **A new type of video or a big new technique** (several lessons that form a playbook): suggest a new skill or an
  update to the matching skill in `.claude/skills/`, and do it if the user agrees.
- **A new doc:** put it in `docs/system/`, `docs/playbook/` or `docs/library/` and add one line to `docs/README.md`.

## 5. Save it for every future session
These are shared-file changes (CLAUDE.md rule 4 of "Working in several sessions at once"; standing permission):
1. Commit only the shared files (`CLAUDE.md`, `docs/`, `.claude/`) in their own commit, message like
   `Lessons: <video> wrap-up (<n> lessons)`. Video work stays in separate commits.
2. Push them to the default branch at once: cherry-pick that commit onto `origin/<default>` in a temporary worktree
   (so an unfinished video does not reach the default branch) and `git push origin HEAD:<default>`; then fetch and
   merge the default branch back into the session branch and push the session branch. Retry pushes on rejection
   (fetch, merge, 2/4/8/16 s), never force-push.
3. Notify the user's other open sessions on this repo (claude-code-remote `list_sessions` with `mine: true`, then
   `send_message` to the ones working on this repo) that new lessons are on the default branch. Skip sessions that
   are not about this repo.

## 6. Tell the user what was learned
Reply in detail, grouped, plain language, like this:
- **What I learned about you** (taste, preferences, how you work)
- **Techniques and effects** that worked, with where they live
- **Tools and numbers** worth keeping
- **What went wrong and the rule that now prevents it**
- **What changed in the rules:** the new lines in CLAUDE.md, the count of entries added or updated in the lessons file,
  and that it is already on the default branch, so the next session uses it automatically.
If nothing new was learned (for example the skill already ran), say so in one line and list what is recorded.

## 7. Close the video if needed
If the user approved the video as final and the project is not on the default branch yet, ask in one line whether to
merge it now (CLAUDE.md rule 6). If they already said it is final in this session, merge it without asking.
