#!/usr/bin/env bash
# check_categorical_grounding.sh
#
# ADVISORY report (NOT a gate): lists DOMAIN-tier .agda modules that prove an
# algebraic structural law (-assoc / -comm / -idem / -identity) yet import
# NOTHING from Substrate.Category. Per categorical-name-first: such a module is
# almost always an *instance* of a named categorical primitive (CommutativeMonoid,
# Group, SymmetricMonoidal, Coequalizer, …) built by hand, off-spine. The fix is
# to ground it — build on / rename a Category primitive (the AsNamed thin-skin
# pattern), or relate to it via a proved equivalence ("better than refl") — so the
# domain term becomes a named leg of the categorical structure rather than a
# free-floating reimplementation.
#
# PROVENANCE: born from the 2026-06-12 retrospective on Logic/Evidence/* (the
# retrospective-ritual G9 ESCALATE gate). That whole tier was built as bare
# data+refl, floating free of Category/*; nothing in the build loop forced a
# categorical-name-first check. This script is the preventative measure for that
# CLASS, accumulated into the advisory machinery (not a passive memory note).
#
# WHY ADVISORY, NOT BLOCKING:
#   "Proves a structural law" is a HEURISTIC for "is an algebraic structure", and
#   a domain module may legitimately prove a one-off law without warranting a
#   Category dependency. A hard gate would breed suppression noise. So this ALWAYS
#   exits 0; it informs judgment, it does not enforce. Like check_file_sizes.sh it
#   is deliberately NOT in `make check` / the pre-commit hook.
#
# SCOPE: domain/application tiers only. The math-infra namespaces that Category is
# BUILT FROM (Foundation, Foundations, Category, Algebra, Groups, Axes,
# Cardinality) are excluded — flagging them would retroactively demand grounding
# in a layer that postdates them. The excluded count is reported for transparency.
#
# Usage:
#   scripts/check_categorical_grounding.sh           # ranked report
#   scripts/check_categorical_grounding.sh --count   # just the count
#
# Exit: always 0 (advisory).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/agda/Substrate"

# math-infra namespaces (Category is built from / part of these); excluded.
INFRA=" Foundation Foundations Category Algebra Groups Axes Cardinality "

mode=""
[ "${1:-}" = "--count" ] && mode="count"

# A module "defines a structural law" if some name at column 0 (Unicode-initial
# allowed; not a comment, not `-`-initial) ends in -assoc/-comm/-idem/-identity
# followed by a non-letter (so `-commutative` etc. do not false-match).
LAW_RE='^[^-[:space:]:(][^[:space:]:(]*-(assoc|comm|idem|identity)([^A-Za-z]|$)'

flagged=""
infra_hits=0
while IFS= read -r f; do
  if ! grep -qE "$LAW_RE" "$f"; then continue; fi              # proves a law?
  if grep -q 'import Substrate\.Category' "$f"; then continue; fi  # already grounded?
  rel="${f#"$SRC"/}"
  ns="${rel%%/*}"
  case "$INFRA" in
    *" $ns "*) infra_hits=$((infra_hits + 1)); continue ;;     # infra: excluded
  esac
  flagged+="${f#"$ROOT"/}"$'\n'
done < <(find "$SRC" -name '*.agda' -not -path '*/_build/*')

sorted="$(printf '%s' "$flagged" | sed '/^$/d' | sort)"
total="$(printf '%s' "$sorted" | grep -c . || true)"

if [ "$mode" = "count" ]; then
  echo "$total"
  exit 0
fi

if [ "$total" -eq 0 ]; then
  echo "categorical-grounding advisory: no ungrounded domain algebraic modules."
else
  echo "categorical-grounding advisory ($total domain module(s) prove an algebraic"
  echo "law but import no Substrate.Category.* — likely hand-rolled instances of a"
  echo "named categorical primitive):"
  echo "  ADVISORY ONLY — judgment required, not all are violations."
  printf '%s\n' "$sorted" | awk '{printf "  %s\n", $0}'
  echo "  ── Ground each in / rename a Category primitive (CommutativeMonoid, Group,"
  echo "     SymmetricMonoidal, Coequalizer, …) via the AsNamed thin-skin, or relate"
  echo "     via a proved equivalence. (categorical-name-first / domain-skin.)"
  echo "  ($infra_hits infra module(s) excluded: Foundation/Category/Algebra/Groups/"
  echo "   Axes/Cardinality — the layers Category is built from.)"
fi
exit 0
