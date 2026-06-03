#!/usr/bin/env bash
# check_up_nonvacuity.sh — the universal-property non-vacuity GATE.
#
# A universal property backed by the substrate's center must be NON-VACUOUS:
# its Witness must discriminate (Category.UniversalProperty.Vacuity.Contentful),
# not collapse to ⊤ (the false-positive shape — see [[project_center_free_
# universal_property]]). This scans for the vacuous ⊤-Witness pattern
#   Witness = λ _ _ → ⊤
# and reports every occurrence OUTSIDE the two sanctioned ⊤-UPs:
#   * trivial-UP  (Category/UniversalProperty.agda) — the genuine terminal.
#   * PlaceholderUP (Category/HC/PlaceholderUP.agda) — the named placeholder.
# Everything else is a VACUOUS universal property (a real UP stubbed as ⊤).
#
# HARD GATE: exits non-zero if any vacuous UP is found (the tree is at 0 as of
# the 2026-06-03 audit/fix; this keeps it from regressing). Pass --quiet to
# suppress success output (used by the pre-commit hook). Bypass: --no-verify.

set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)/agda/Substrate"

quiet=0
[ "${1:-}" = "--quiet" ] && quiet=1

# the sanctioned ⊤-UPs (legitimately terminal / explicitly placeholder).
whitelist='Category/UniversalProperty.agda|Category/HC/PlaceholderUP.agda'

hits="$(grep -rnE 'Witness *= *λ _ _ → ⊤' "$root" 2>/dev/null || true)"
debt="$(printf '%s\n' "$hits" | grep -vE "$whitelist" | grep -vE '^\s*$' || true)"

n_total=$(printf '%s\n' "$hits" | grep -cE 'Witness' || true)
n_debt=$(printf '%s\n' "$debt" | grep -cE 'Witness' || true)

if [ -n "$debt" ]; then
  echo "up-nonvacuity: ${n_debt} VACUOUS universal-property instance(s) — GATE FAILED" >&2
  echo "  (a real UP stubbed as ⊤ — must be a Contentful UPArrow / BackedUP):" >&2
  printf '%s\n' "$debt" | sed -E 's|.*/agda/Substrate/|    |' >&2
  echo "  Fix: replace the ⊤-Witness with the real relation + a Contentful" >&2
  echo "       certificate. See scratch/up_nonvacuity_policy.md" >&2
elif [ "$quiet" -eq 0 ]; then
  echo "up-nonvacuity: ${n_total} ⊤-Witness UP(s), all sanctioned (trivial-UP, PlaceholderUP); no vacuous debt. ✓"
fi

[ -z "$debt" ]   # exit 0 iff no vacuous debt
