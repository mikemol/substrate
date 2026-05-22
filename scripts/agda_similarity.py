#!/usr/bin/env python3
"""agda_similarity — pairwise multi-scale cosine similarity + template
extraction + parametric skeleton construction over Agda files.

This is a thin entry-point shim. The implementation lives in the
sibling package `agda_similarity/` (see its submodules: tokenize,
similarity, template, skeleton, cli). Each submodule is small enough
to one-pass rewrite per the file-size-one-pass-rewrite discipline.

Usage:
  Pairwise similarity:
    agda_similarity.py FILE1 FILE2
    agda_similarity.py --glob '.../Z*.agda' --top 20 --breakdown

  Template extraction (per-scale skeleton/holes):
    agda_similarity.py --glob '...' --template
    agda_similarity.py --glob '...' --template --scale line --no-holes

  Recursive template (coarse-to-fine drill-down into holes):
    agda_similarity.py --glob '...' --recursive --max-show 8

  Skeleton construction (parametric template via hole substitution):
    agda_similarity.py --glob '...' --skeleton
    agda_similarity.py --glob '...' --skeleton --hole-marker '<n>'
"""

from __future__ import annotations

import sys

# Python's import machinery prefers a package directory over a same-named
# .py module at the same path, so `from agda_similarity.cli import main`
# below resolves to scripts/agda_similarity/cli.py (the package), not
# back to this script. Ensure scripts/ is on sys.path when running
# this file directly.
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agda_similarity.cli import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main())
