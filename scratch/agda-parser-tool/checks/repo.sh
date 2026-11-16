#!/usr/bin/env bash
# repo.sh — discriminating witnesses for the plan's factual claims. Each key
# greps the CURRENT substrate tree and exits 0 iff the asserted fact holds, so a
# claim that has drifted from the code fails its gate. Design-intent claims do
# NOT route here — they carry `premise:` and are surfaced as not-machine-checked.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"   # scratch/agda-parser-tool/checks -> substrate root
cd "$ROOT" || exit 2

case "${1:-}" in
  strip-comment-stripper)
    grep -q 'def strip' scripts/_agdatext.py \
      && [ "$(grep -c 're\.sub' scripts/_agdatext.py)" -ge 2 ] ;;
  strip-many-importers)
    [ "$(grep -rl 'from _agdatext import strip' scripts scratch jea 2>/dev/null | wc -l)" -ge 8 ] ;;
  vacuity-greps-raw)
    grep -q 'Witness' scripts/check_up_nonvacuity.sh \
      && ! grep -q '_agdatext' scripts/check_up_nonvacuity.sh ;;
  import-permutation-guard)
    grep -qi 'permutation' scratch/agda_imports.py ;;
  deletion-scar)
    grep -q '2094' scratch/agda_imports.py ;;
  set1-why-not-grep)
    grep -qiE 'elaborated information|WHY NOT GREP' scripts/set1_ratchet_cores.py ;;
  shim-links-agda)
    grep -q 'package Agda' jea/metalanguage/agdai_shim.hs ;;
  shim-jsonl)
    grep -qiE 'JSON-lines|jsonl' jea/metalanguage/agdai_shim.hs ;;
  filesize-advisory)
    grep -qiE 'advisory|always exits 0' scripts/check_file_sizes.sh ;;
  public-source-regex)
    grep -qi 'open' scripts/check_public_ratchet.py \
      && ! grep -qE 'decode_core|jea_agdai|catalog\.db' scripts/check_public_ratchet.py ;;
  gate-suite)
    grep -q 'check: check-defproof' agda/Makefile ;;
  migrate-line-prefix)
    grep -q 'startswith' scripts/migrate_to_foundation.py ;;
  *)
    echo "repo.sh: unknown check key: ${1:-<none>}" >&2; exit 2 ;;
esac
