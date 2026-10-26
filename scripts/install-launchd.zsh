#!/bin/zsh
# Install (or reinstall) the monthly backup LaunchAgent. The checked-in plist is
# a template, so this public repo holds no local paths; this fills it in.

set -eu

repo_root=${0:A:h:h}
label=com.benshaw.playlist-backup
template="$repo_root/launchd/$label.plist"
target="$HOME/Library/LaunchAgents/$label.plist"
user_domain="gui/$(id -u)"

mkdir -p "$HOME/Library/LaunchAgents" "$repo_root/logs"
temporary=$(mktemp "$repo_root/logs/$label.plist.XXXXXX")
sed -e "s|__REPO_ROOT__|$repo_root|g" -e "s|__HOME__|$HOME|g" "$template" > "$temporary"
/usr/bin/plutil -lint "$temporary" >/dev/null
/bin/launchctl bootout "$user_domain" "$target" >/dev/null 2>&1 || true
mv "$temporary" "$target"
/bin/launchctl bootstrap "$user_domain" "$target"
/bin/launchctl enable "$user_domain/$label"
print "installed $target"
