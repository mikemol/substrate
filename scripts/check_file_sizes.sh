#!/usr/bin/env bash
# check_file_sizes.sh
#
# ADVISORY report (NOT a gate) for theorem-per-file pressure: lists .agda
# files carrying many top-level signatures, ranked. Surfaces candidates for
# decomposition per the theorem/lemma-per-file policy
# (scratch/def_proof_separation_policy.md sibling discipline; see also
# feedback_targeted_edit_means_too_large).
#
# WHY ADVISORY, NOT BLOCKING:
#   Unlike def/proof separation (name-based, exact, zero false positives),
#   signature-counting has REAL false positives — a cohesive primitives
#   module (e.g. Foundation/Nat) legitimately has many signatures. A hard
#   threshold would block reasonable files and breed suppression noise. So
#   this ALWAYS exits 0; it informs human judgment, it does not enforce a
#   number. Do not add it to the blocking `make check` / pre-commit gate.
#
# Usage:
#   scripts/check_file_sizes.sh              # ranked report (threshold 8)
#   scripts/check_file_sizes.sh 12           # custom threshold
#   scripts/check_file_sizes.sh --count [N]  # just the count over threshold
#
# Exit: always 0 (advisory).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/agda/Substrate"

threshold=8
mode=""
for a in "$@"; do
  case "$a" in
    --count) mode="count" ;;
    ''|*[!0-9]*) ;;          # ignore non-numeric
    *) threshold="$a" ;;
  esac
done

# Count top-level type signatures: a line starting at column 0 with an
# identifier and a top-level `:` (not a comment / module / open / import /
# pragma). Heuristic — see the false-positive note above. `grep -c` always
# prints exactly one integer; force it to 0 on no-match without spawning a
# second token.
rows=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  n="$(grep -cE '^[A-Za-z_].*[[:space:]]:[[:space:]]' "$f" || true)"
  : "${n:=0}"
  if [ "$n" -ge "$threshold" ]; then
    rows+="$n	${f#"$ROOT"/}"$'\n'
  fi
done < <(find "$SRC" -name '*.agda' -not -path '*/_build/*')

sorted="$(printf '%s' "$rows" | sed '/^$/d' | sort -rn)"
total="$(printf '%s' "$sorted" | grep -c . || true)"

if [ "$mode" = "count" ]; then
  echo "$total"
  exit 0
fi

if [ "$total" -eq 0 ]; then
  echo "file-size advisory: no files with >= $threshold top-level signatures."
else
  echo "file-size advisory (theorem-per-file pressure; >= $threshold signatures):"
  echo "  ADVISORY ONLY — judgment required, not all are violations"
  echo "  (a cohesive primitives module may legitimately exceed the threshold)."
  printf '%s\n' "$sorted" | awk -F'\t' '{printf "  %4d  %s\n",$1,$2}'
  echo "  ── $total file(s) over threshold. Decompose where they bundle"
  echo "     independent theorems; leave cohesive modules alone."
fi
exit 0
