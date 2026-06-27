#!/usr/bin/env bash
set -u

pid=790292
echo "--- ps ---"
ps -p "$pid" -o pid,ppid,stat,etime,time,%cpu,%mem,cmd || true

echo "--- children ---"
pgrep -P "$pid" -af || true

echo "--- cwd/fds count ---"
readlink "/proc/${pid}/cwd" 2>/dev/null || true
ls "/proc/${pid}/fd" 2>/dev/null | wc -l || true

echo "--- recent fd targets ---"
for fd in /proc/${pid}/fd/*; do
  target=$(readlink "$fd" 2>/dev/null || true)
  case "$target" in
    *socket*|*pipe*|*/outputs/*|*/cache/*) echo "$fd -> $target" ;;
  esac
done | head -n 80

echo "--- tcp sockets summary ---"
ss -tpn 2>/dev/null | grep "$pid" || true
