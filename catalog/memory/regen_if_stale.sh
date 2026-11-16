#!/usr/bin/env bash
# Ⓜ.regen-hook — keep MEMORY.md (the loaded mesh index) fresh, correct-by-construction.
# Cheap mtime GATE: no-op unless a memory file (or the mechanizer) is newer than MEMORY.md.
# When stale, launch the regen DETACHED + single-instance (flock) so the hook returns
# instantly and never blocks a turn. Best-effort: always exits 0 (never breaks a session).
# Wired as a Stop + SessionStart hook in ~/.claude/settings.json.
set -u
MEM="/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory"
M="$MEM/MEMORY.md"; S="$MEM/synth_wire.py"   # MEMORY.md is the synth-apex root (synth-swap, 2026-06-24)
[ -f "$S" ] || exit 0

stale=0
if [ ! -f "$M" ]; then
  stale=1
else
  # any memory *.md newer than MEMORY.md (exclude MEMORY.md, ARCHIVE.md, the index/ tree)
  if find "$MEM" -name '*.md' -not -name 'MEMORY.md' -not -name 'ARCHIVE.md' -newer "$M" 2>/dev/null \
       | grep -vE '/index/|/synth/' | grep -q .; then stale=1; fi
  # the mechanizer itself changing also invalidates the index
  find "$S" -newer "$M" 2>/dev/null | grep -q . && stale=1
fi
[ "$stale" -eq 0 ] && exit 0

# detached, single-instance regen (flock -n: a second trigger while one runs just skips;
# the next Stop/SessionStart re-gates and catches any edit it missed). The synth root
# regen = re-scale apexes (synth_scale) then re-wire root (synth_wire → MEMORY.md); ~5min,
# detached so it never blocks. (Incremental per-cluster regen is a future optimization.)
setsid flock -n "$MEM/.regen.lock" -c \
  "cd '$MEM' && timeout 560 python3 synth_scale.py 4 && python3 synth_wire.py >>'$MEM/.regen.log' 2>&1" \
  >/dev/null 2>&1 &
exit 0
