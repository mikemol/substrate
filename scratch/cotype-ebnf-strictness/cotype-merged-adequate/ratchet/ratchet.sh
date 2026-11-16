#!/bin/sh
# AI-MINSTRENGTH ratchet — CONFORMS to paperkit (does not wrap it).
# The only domain content is build_findings_subpaper.py (the scoping judgement).
# Everything resumable/incremental is paperkit's own: project, gate, and discriminate
# --min-strength behavioral --state/--budget (whose loop IS driver.py driving
# discriminate's pump witness — exit 2 = resume, not failure).
#
#   ratchet/ratchet.sh [ENGINE_DIR]
set -e
ENGINE="${1:-/tmp/paperkit/paperkit}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
# isolated parent in $HOME (Δ-LIMITATION #1: never a discriminate target directly under /tmp)
WORK="$(mktemp -d "${HOME}/ratchet-XXXXXX")"
PROJ="$WORK/proj"; mkdir -p "$PROJ"
trap 'rm -rf "$WORK"' EXIT

python3 "$HERE/ratchet/build_findings_subpaper.py" "$PROJ"

# conform: paperkit projects and gates its own paper
python3 "$ENGINE/project.py" "$PROJ" >/dev/null
python3 "$ENGINE/gate.py" "$PROJ"            # emits its own reified judgements

# conform: paperkit's driver-backed resumable grading. rc 2 = "resume me" (the pump
# contract), rc 0 = done, rc 1 = a finding fell below behavioral. Loop honors the
# budget exactly as driver.drive() does: run, persist, repeat while rc==2.
STATE="$WORK/grade.state"
while : ; do
  set +e
  python3 "$ENGINE/discriminate.py" --min-strength behavioral --state "$STATE" --budget 120 "$PROJ"
  rc=$?
  set -e
  [ "$rc" = "2" ] || break      # 2 = not done → resume; anything else is the verdict
done
exit "$rc"
