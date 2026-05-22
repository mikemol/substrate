#!/usr/bin/env python3
"""
agda_similarity.py — pairwise multi-scale cosine similarity over Agda files.

Computes cosine similarity at four scales of "slicing":
  1. char 3-grams      — surface-level token reuse
  2. tokens            — identifier/keyword overlap
  3. lines (stripped)  — structural copy/paste
  4. blocks            — section-level shape (separated by blank lines
                         or "------" rule comments)

Per-pair similarity is the geometric mean of the four scales; each
scale's cosine is in [0, 1]. A pair gets a score in [0, 1] where 1 =
identical (after whitespace / comment normalization).

Usage:
  agda_similarity.py FILE1 FILE2                      # single pair
  agda_similarity.py --glob 'agda/Substrate/Groups/Z*.agda'  # all pairs
  agda_similarity.py --glob '...' --top 20            # top N pairs
  agda_similarity.py --glob '...' --threshold 0.7     # filter by min score
  agda_similarity.py --glob '...' --csv               # CSV output

Substrate use case: find orbits — clusters of files with same shape —
as candidates for genericization via a parametric module. After
genericization, scores in the cluster should DROP (shape moved into
the generic, instances are now thin).
"""

from __future__ import annotations

import argparse
import glob as glob_mod
import math
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Tokenizers — the "smaller and smaller ways of slicing text".
# ---------------------------------------------------------------------------

# Agda-aware token split: identifiers (letters/digits/unicode chars),
# operators, punctuation. We treat each as a token unit.
TOKEN_RE = re.compile(
    r"[A-Za-z_][\w'-]*"          # identifier
    r"|[ℕ-℧⁰-⁹₀-₉ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψω]+"  # unicode names
    r"|->|→|⇒|=>|≡|≈|≠|≢|≤|≥|<|>|::|\.\.|"
    r"|[(){}\[\]:;,.=|]"
)

# Block separator: blank line, OR a comment rule (---- or more), OR
# a section heading line that's all dashes.
BLOCK_SEP_RE = re.compile(r"^\s*(?:--+\s*)?$|^-+\s*$")


def strip_comment_lines(text: str) -> str:
    """Drop full-line Agda comments (-- and {- ... -}) so similarity
    isn't dominated by commentary boilerplate. Keeps code structure."""
    out_lines = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if in_block:
            if "-}" in stripped:
                in_block = False
            continue
        if stripped.startswith("{-"):
            if "-}" not in stripped:
                in_block = True
            continue
        if stripped.startswith("--"):
            continue
        # Drop inline -- comments
        if " --" in line:
            line = line[: line.index(" --")]
        out_lines.append(line)
    return "\n".join(out_lines)


def char_ngrams(text: str, n: int = 3) -> Counter[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return Counter(text[i : i + n] for i in range(len(text) - n + 1))


def tokens(text: str) -> Counter[str]:
    return Counter(TOKEN_RE.findall(text))


def lines(text: str) -> Counter[str]:
    return Counter(
        s for line in text.splitlines() if (s := line.strip())
    )


def blocks(text: str) -> Counter[str]:
    """Split on blank lines / ---- rules; normalize within each block."""
    out: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if BLOCK_SEP_RE.match(line):
            if cur:
                out.append(" ".join(cur).strip())
                cur = []
        else:
            stripped = line.strip()
            if stripped:
                cur.append(stripped)
    if cur:
        out.append(" ".join(cur).strip())
    # Canonicalize each block: collapse whitespace, sort tokens.
    canonical = [
        " ".join(sorted(TOKEN_RE.findall(b))) for b in out if b
    ]
    return Counter(canonical)


# ---------------------------------------------------------------------------
# Cosine similarity over a single Counter pair.
# ---------------------------------------------------------------------------


def cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Multi-scale similarity profile + aggregation.
# ---------------------------------------------------------------------------


SCALE_NAMES = ("char3", "token", "line", "block")


def profile(text: str) -> tuple[Counter, Counter, Counter, Counter]:
    body = strip_comment_lines(text)
    return char_ngrams(body, 3), tokens(body), lines(body), blocks(body)


def pair_similarity(
    p1: tuple[Counter, Counter, Counter, Counter],
    p2: tuple[Counter, Counter, Counter, Counter],
) -> tuple[float, tuple[float, float, float, float]]:
    scores = tuple(cosine(a, b) for a, b in zip(p1, p2))
    # Geometric mean of non-zero scores; if any score is 0 the
    # geometric mean is 0 (correct: missing one scale means they
    # differ in some fundamental way).
    if any(s == 0.0 for s in scores):
        return 0.0, scores
    geo = math.exp(sum(math.log(s) for s in scores) / len(scores))
    return geo, scores


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------


def expand_paths(args: argparse.Namespace) -> list[Path]:
    if args.glob:
        paths = []
        for pattern in args.glob:
            paths.extend(Path(p) for p in glob_mod.glob(pattern, recursive=True))
        return sorted(set(paths))
    if args.files:
        return [Path(f) for f in args.files]
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("files", nargs="*", help="Two files for single-pair mode")
    ap.add_argument(
        "--glob",
        action="append",
        help="Glob pattern; may be passed multiple times. All pairs are scored.",
    )
    ap.add_argument(
        "--top", type=int, default=None, help="Show only top N pairs"
    )
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Only show pairs with geometric mean >= threshold",
    )
    ap.add_argument("--csv", action="store_true", help="CSV output instead of table")
    ap.add_argument(
        "--breakdown",
        action="store_true",
        help="Show per-scale breakdown (char3 / token / line / block)",
    )
    args = ap.parse_args(argv)

    paths = expand_paths(args)
    if len(paths) < 2:
        ap.error("Need at least two files (use positional args or --glob)")

    profiles = {p: profile(p.read_text(errors="replace")) for p in paths}

    results: list[tuple[float, tuple[float, ...], Path, Path]] = []
    for a, b in combinations(paths, 2):
        geo, scales = pair_similarity(profiles[a], profiles[b])
        if geo >= args.threshold:
            results.append((geo, scales, a, b))

    results.sort(reverse=True)
    if args.top:
        results = results[: args.top]

    if args.csv:
        cols = ["score"]
        if args.breakdown:
            cols += list(SCALE_NAMES)
        cols += ["file_a", "file_b"]
        print(",".join(cols))
        for geo, scales, a, b in results:
            row = [f"{geo:.4f}"]
            if args.breakdown:
                row += [f"{s:.4f}" for s in scales]
            row += [str(a), str(b)]
            print(",".join(row))
        return 0

    # Pretty table
    header = ["score"]
    if args.breakdown:
        header += list(SCALE_NAMES)
    header += ["pair"]
    widths = [8] + ([7] * (len(SCALE_NAMES)) if args.breakdown else []) + [0]
    print(" ".join(h.ljust(w) if w else h for h, w in zip(header, widths)))
    for geo, scales, a, b in results:
        row_str = f"{geo:6.4f}".ljust(8)
        if args.breakdown:
            row_str += "  ".join(f"{s:5.3f}" for s in scales) + "  "
        row_str += f"{a}  <->  {b}"
        print(row_str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
