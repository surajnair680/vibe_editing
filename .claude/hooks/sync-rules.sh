#!/bin/bash
# Runs before every user message (UserPromptSubmit). Brings shared rule and tool changes from the default branch
# into this session's branch, so no session ever works from stale rules and the user never has to ask.
# Prints a note (added to Claude's context) only when something shared changed or the merge needs a hand.
set -u
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

DEF=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
[ -n "$DEF" ] || DEF=$(timeout 15 git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p')
[ -n "$DEF" ] || exit 0
timeout 20 git fetch -q origin "$DEF" 2>/dev/null || exit 0

CUR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ "$CUR" = "$DEF" ] && exit 0
git merge-base --is-ancestor "origin/$DEF" HEAD 2>/dev/null && exit 0          # nothing new

SHARED=$(git diff --name-only HEAD...origin/"$DEF" 2>/dev/null | grep -E '^(CLAUDE\.md|\.claude/|tools/|docs/|templates/)' | tr '\n' ' ')
if git merge --no-edit -q "origin/$DEF" >/dev/null 2>&1; then
  if [ -n "$SHARED" ]; then
    echo "[rules sync] The default branch ($DEF) had new shared changes and they were merged into $CUR: $SHARED"
    echo "Before doing anything else: re-read CLAUDE.md (and any changed skill, hook or tool listed) and follow the new version from now on. Tell the user in one line that the latest rules were loaded. Push this merge with your next push."
  fi
else
  git merge --abort >/dev/null 2>&1
  echo "[rules sync] origin/$DEF could not be merged into $CUR automatically (conflict or local changes in the way). Before continuing, merge it by hand as CLAUDE.md rule 5 says, then re-read CLAUDE.md."
fi
exit 0
