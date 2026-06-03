#!/usr/bin/env bash
# check_up_nonvacuity.sh — the universal-property non-vacuity census.
#
# A universal property backed by the substrate's center must be NON-VACUOUS:
# its Witness must discriminate (Category.UniversalProperty.Vacuity.Contentful),
# not collapse to ⊤ (the false-positive shape — see [[project_center_free_
# universal_property]]). This scans for the vacuous ⊤-Witness pattern
#   Witness = λ _ _ → ⊤
# and reports every occurrence OUTSIDE the two sanctioned ⊤-UPs:
#   * trivial-UP  (Category/UniversalProperty.agda) — the genuine terminal.
#   * PlaceholderUP (Category/HC/PlaceholderUP.agda) — the named placeholder.
# Everything else is UNIFICATION DEBT: a universal property claimed but not
# backed by a non-vacuous bridge (BackedUP). Advisory (always exit 0): it is
# a checklist to drive conversion, not a hard gate.

set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)/agda/Substrate"

# the sanctioned ⊤-UPs (legitimately terminal / explicitly placeholder).
whitelist='Category/UniversalProperty.agda|Category/HC/PlaceholderUP.agda'

hits="$(grep -rnE 'Witness *= *λ _ _ → ⊤' "$root" 2>/dev/null || true)"
debt="$(printf '%s\n' "$hits" | grep -vE "$whitelist" | grep -vE '^\s*$' || true)"

n_total=$(printf '%s\n' "$hits" | grep -cE 'Witness' || true)
n_debt=$(printf '%s\n' "$debt" | grep -cE 'Witness' || true)

echo "up-nonvacuity: ${n_total} ⊤-Witness UP(s); 2 sanctioned (trivial-UP, PlaceholderUP)."
if [ -n "$debt" ]; then
  echo "up-nonvacuity: ${n_debt} VACUOUS universal-property instance(s) = unification debt"
  echo "  (a real UP stubbed as ⊤ — should be backed by a Contentful BackedUP):"
  printf '%s\n' "$debt" | sed -E 's|.*/agda/Substrate/|    |'
  echo "  Fix: replace the ⊤-Witness with the real relation + a BackedUP"
  echo "       (Category.UniversalProperty.Backed). See scratch/up_nonvacuity_policy.md"
else
  echo "up-nonvacuity: no vacuous universal-property debt. ✓"
fi
exit 0
