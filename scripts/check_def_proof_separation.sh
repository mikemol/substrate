#!/usr/bin/env bash
# check_def_proof_separation.sh
#
# Enforces the def/proof separation policy (the "Costco" invariant) from
# scratch/def_proof_separation_policy.md:
#
#   A DEFINITION-PROVIDER module must not import a PROOF module.
#
#   DEFINITION-PROVIDER = a module that declares a `data` or `record`
#                         (i.e. exports a datatype/structure that other
#                         modules import in order to USE it).
#   PROOF module         = filename ends in .Properties / .Laws / .Proofs.
#
# WHY this exact shape:
#   * Importing deserializes the full transitive closure INCLUDING proof
#     terms (~40x in-memory inflation) — the dominant driver of the
#     All.agda OOM (see project_oom_load_bound_finding_2026_06).
#   * The load cost is paid by CONSUMERS OF DEFINITIONS. The module a
#     def-consumer imports is the one that exports the datatype/record, so
#     THAT module's closure is what gets needlessly deserialized. Keep it
#     proof-free and def-consumers stop paying for proofs they never use.
#     (Measured: def-only import +1 MB vs def+proof +23 MB —
#     feedback_def_proof_separation_lever.)
#   * A pure-lemma file (no data/record) is ALREADY on the proof side: it
#     has no datatype to offer a def-only consumer, so importing
#     .Properties from it is fine. This is why the rule is scoped to
#     definition-providers, not "every module" — otherwise it would fire
#     on the one-theorem-per-file lemma modules, which is wrong.
#
# Color is NAME-based for proof modules on purpose: content classification
# mislabels record-with-laws definitions (Group/Monoid) as proofs. The
# suffix is unambiguous and needs no judgment.
#
# Usage:
#   scripts/check_def_proof_separation.sh           # check, print violations
#   scripts/check_def_proof_separation.sh --quiet   # exit code only
#   scripts/check_def_proof_separation.sh --count    # print count only
#
# Exit: 0 if clean, 1 if any violation. Suitable for pre-commit / CI.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/agda/Substrate"

mode="${1:-}"

# Candidate files: import a proof module, are not themselves proof modules,
# excluding _build.
candidates="$(
  grep -rlE 'import[[:space:]]+Substrate\.[A-Za-z0-9.]*\.(Properties|Laws|Proofs)' \
       --include='*.agda' "$SRC" 2>/dev/null \
    | grep -v '/_build/' \
    | grep -vE '\.(Properties|Laws|Proofs)\.agda$' \
    || true
)"

# Keep only DEFINITION-PROVIDERS: files declaring a top-level data/record.
violations=""
if [ -n "$candidates" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if grep -qE '^(data|record)[[:space:]]' "$f"; then
      violations+="${f#"$ROOT"/}"$'\n'
    fi
  done <<< "$candidates"
fi
violations="$(printf '%s' "$violations" | grep -c . >/dev/null 2>&1 && printf '%s' "$violations" | sed '/^$/d' | sort || true)"

n=0
[ -n "$violations" ] && n="$(printf '%s\n' "$violations" | grep -c .)"

case "$mode" in
  --count)
    echo "$n"
    ;;
  --quiet)
    ;;
  *)
    if [ "$n" -eq 0 ]; then
      echo "def/proof separation: OK (0 violations)"
    else
      echo "def/proof separation: $n violation(s) — definition-provider modules importing proof modules:"
      printf '%s\n' "$violations" | sed 's/^/  /'
      echo
      echo "Fix: move the proof-dependent code into a *.Properties sibling so the"
      echo "     data/record-exporting module's closure stays proof-free."
      echo "See scratch/def_proof_separation_policy.md"
    fi
    ;;
esac

[ "$n" -eq 0 ]
