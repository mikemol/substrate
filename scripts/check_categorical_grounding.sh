#!/usr/bin/env bash
# check_categorical_grounding.sh
#
# ADVISORY report (NOT a gate): DOMAIN-tier .agda modules that prove an algebraic
# structural law (-assoc / -comm / -idem / -identityˡ / -identityʳ) yet are not
# grounded on the CATEGORICAL spine — usually an instance of a named primitive
# built by hand. The substrate's real bridge-index is
# Category.UniversalProperty.Registry: typechecked `BackedUP` bridges + a coverage
# / unification metric ("grow this list to unify the repo"). The proper fix is a
# registered / typechecked bridge — "better than refl" — not a grep, and never a
# passive memory note.
#
# TWO buckets (the re-mechanized judgments from the 2026-06-12 walk over the list):
#   * FLOATING — proves laws but bundles into NO structure record at all
#     (hand-rolled laws). The primary target: ground in a Category structure-
#     instance / register a bridge.
#   * GROUNDS-IN-ALGEBRA (off-spine) — bundles into an Algebra.* structure record
#     (Monoid / Group / …). NOT floating, but Algebra ∥ Category are PARALLEL
#     hierarchies (Algebra imports 0 Category; no delooping bridge), so this does
#     NOT reach the categorical spine. The Algebra↔Category convergence gap,
#     surfacing at a leaf — fix it once at the hierarchy level, not per module.
#
# PROVENANCE: the retrospective-ritual G9 ESCALATE gate (the Logic/Evidence tier
# built off-spine). Heuristic ("proves a law" ≈ "is a structure"), hence ADVISORY:
# always exits 0, never in `make check` / the pre-commit hook.
#
# SCOPE: domain/application tiers. Foundation/Category (the spine + its base) and
# Algebra/Groups/Axes/Cardinality (a PARALLEL structure hierarchy, NOT below
# Category — see the Algebra∥Category finding) are excluded as namespaces; the
# GROUNDS-IN-ALGEBRA bucket still catches DOMAIN modules that reach into Algebra.
#
# Usage:
#   scripts/check_categorical_grounding.sh           # bucketed report
#   scripts/check_categorical_grounding.sh --count   # just the total
#
# Exit: always 0 (advisory).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/agda/Substrate"

INFRA=" Foundation Foundations Category Algebra Groups Axes Cardinality "

# Structural laws. Directional unit laws only (-identityˡ/ʳ): bare `-identity`
# catches named theorems like `jacobi-identity` (the Jacobi *identity*) — a false
# positive found in the walk; the unambiguous forms are -assoc/-comm/-idem and the
# directional units.
LAW_RE='^[^-[:space:]:(][^[:space:]:(]*-(assoc|comm|idem|identityˡ|identityʳ)([^A-Za-z]|$)'
# Bundling into the PARALLEL Algebra structure-record hierarchy (not the spine).
ALG_RE='import Substrate\.Algebra\.(Magma|Semigroup|Monoid|Group|AbelianGroup|Ring|Semiring|Field|Module)([. ]|$)'

mode=""
[ "${1:-}" = "--count" ] && mode="count"

floating=""
offspine=""
infra_hits=0
while IFS= read -r f; do
  if ! grep -qE "$LAW_RE" "$f"; then continue; fi                  # proves a law?
  if grep -q 'import Substrate\.Category' "$f"; then continue; fi  # on the spine
  rel="${f#"$SRC"/}"; ns="${rel%%/*}"
  case "$INFRA" in
    *" $ns "*) infra_hits=$((infra_hits + 1)); continue ;;         # infra/parallel
  esac
  if grep -qE "$ALG_RE" "$f"; then
    offspine+="${f#"$ROOT"/}"$'\n'
  else
    floating+="${f#"$ROOT"/}"$'\n'
  fi
done < <(find "$SRC" -name '*.agda' -not -path '*/_build/*')

fl_sorted="$(printf '%s' "$floating" | sed '/^$/d' | sort)"
os_sorted="$(printf '%s' "$offspine" | sed '/^$/d' | sort)"
fl_n="$(printf '%s' "$fl_sorted" | grep -c . || true)"
os_n="$(printf '%s' "$os_sorted" | grep -c . || true)"
total=$((fl_n + os_n))

if [ "$mode" = "count" ]; then echo "$total"; exit 0; fi

if [ "$total" -eq 0 ]; then
  echo "categorical-grounding advisory: no ungrounded domain algebraic modules."
  exit 0
fi

echo "categorical-grounding advisory ($total domain module(s) off the categorical"
echo "spine — Category.UniversalProperty.Registry is the bridge-index to grow):"
echo "  ADVISORY ONLY — judgment required only where the buckets can't yet decide."
if [ "$fl_n" -gt 0 ]; then
  echo "  FLOATING ($fl_n) — prove laws, bundle into NO structure record (hand-rolled):"
  printf '%s\n' "$fl_sorted" | awk '{printf "    %s\n", $0}'
  echo "    → ground in a Category structure-instance / register a typechecked bridge."
fi
if [ "$os_n" -gt 0 ]; then
  echo "  GROUNDS-IN-ALGEBRA ($os_n) — bundle into Algebra.* (Monoid/Group/…), which is"
  echo "  PARALLEL to Category (no bridge) — the Algebra↔Category convergence gap:"
  printf '%s\n' "$os_sorted" | awk '{printf "    %s\n", $0}'
  echo "    → fix once at the hierarchy level (bridge Algebra→Category), not per module."
fi
echo "  ($infra_hits infra / parallel-hierarchy module(s) excluded by namespace.)"
exit 0
