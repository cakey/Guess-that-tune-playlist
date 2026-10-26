#!/bin/zsh
# Monthly LaunchAgent entry point: refresh the backups, then commit them
# locally so each month is a diff in git. It never pushes.

set -eu
setopt pipefail

export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

repo_root=${0:A:h:h}
cd "$repo_root"

print "$(date '+%Y-%m-%d %H:%M:%S') backup started"
python3 backup.py

backups=('*-backup-readable.txt' '*-backup-track-urls.txt')
git add -- $backups
if git diff --cached --quiet -- $backups; then
  print "no backup changes to commit"
  exit 0
fi
# Pathspecs keep anything else that happens to be staged out of this commit.
git commit -q -m "Backup $(date '+%Y-%m-%d')" -- $backups
print "committed $(git log --oneline -1)"
