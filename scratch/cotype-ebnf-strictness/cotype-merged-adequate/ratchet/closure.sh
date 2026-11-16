#!/bin/sh
# AI-CLOSURE (sig 111, triadic-full) — the self-verifying run that closes the shadow-architecture.
# Conforms to paperkit (does not wrap); surfaces every reified judgement (does not collapse to a bit);
# embeds the read-gate (the 13/14 findings checks read warrants.bib prose before asserting — claim: form;
# f091_2 is honestly un-bindable, behavioral-by-crash, and SAID so).
#
# Composes paperkit's OWN commands; each step run ONCE (its output AND its rc both consumed — the
# demechanization law: a run delivers both, do not re-run to recover what you discarded):
#   1. project   2. gate ×3   3. rhetoric --check (opt-in)   4. findings behavioral ratchet (resumable)
# Exit 0 iff every step's judgement holds. Every judgement printed; none silently ANDed away.
#
#   ratchet/closure.sh [ENGINE_DIR]
ENGINE="${1:-/tmp/paperkit/paperkit}"
COTYPE="$(cd "$(dirname "$0")/.." && pwd)"
rc=0
step() {  # step <label> <cmd...> : run once, surface paperkit judgements, fold rc
  label="$1"; shift
  echo "── $label ──"
  out="$("$@" 2>&1)"; src=$?
  echo "$out" | grep -E '^(paperkit-|rhetoric:)' || echo "$out" | tail -2
  [ "$src" = "0" ] || rc=1
}

step "1. project (prose is a build artifact)" python3 "$ENGINE/project.py" "$COTYPE"
for mode in "" "--without-K" "--safe"; do
  step "2. gate ${mode:-plain}" python3 "$ENGINE/gate.py" "$COTYPE" $mode
done
step "3. rhetoric --check (opt-in)" python3 "$ENGINE/rhetoric.py" --check "$COTYPE"
step "4. findings behavioral ratchet" sh "$COTYPE/ratchet/ratchet.sh" "$ENGINE"

echo "── CLOSURE VERDICT ──"
[ "$rc" = "0" ] && echo "paperkit-closure: PASS — cotype self-verifies (gates ×3, rhetoric, behavioral ratchet)" \
                || echo "paperkit-closure: FAIL — a judgement above did not hold"
exit "$rc"
