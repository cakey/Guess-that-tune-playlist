#!/bin/zsh
# Monthly LaunchAgent entry point: refresh the backups, then commit them
# and push them so each month is a diff in git.

set -eu
setopt pipefail

export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

repo_root=${0:A:h:h}
cd "$repo_root"

print "$(date '+%Y-%m-%d %H:%M:%S') backup started"
python3 backup.py

branch=$(git symbolic-ref --short HEAD 2>/dev/null || true)
if [[ $branch != master ]]; then
  print "on ${branch:-a detached HEAD}, not master; backups written but not committed"
  exit 0
fi

backups=('*-backup-readable.txt' '*-backup-track-urls.txt')
git add -- $backups
if git diff --cached --quiet -- $backups; then
  print "no backup changes to commit"
else
  # Pathspecs keep anything else that happens to be staged out of this commit.
  git commit -q -m "Backup $(date '+%Y-%m-%d')" -- $backups
  print "committed $(git log --oneline -1)"
fi

# Also catches up a push that failed on an earlier run.
if [[ -n $(git rev-list origin/master..master) ]]; then
  git push -q origin master
  print "pushed to origin/master"
fi
