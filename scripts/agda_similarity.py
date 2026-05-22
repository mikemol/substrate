#!/usr/bin/env python3
"""
agda_similarity.py — pairwise multi-scale cosine similarity + template
extraction over Agda files.

Computes cosine similarity at four scales of "slicing":
  1. char 3-grams      — surface-level token reuse
  2. tokens            — identifier/keyword overlap
  3. lines (stripped)  — structural copy/paste
  4. blocks            — section-level shape (separated by blank lines
                         or "------" rule comments)

Per-pair similarity is the geometric mean of the four scales; each
scale's cosine is in [0, 1]. A pair gets a score in [0, 1] where 1 =
identical (after whitespace / comment normalization).

Two modes:

  similarity (default): pairwise cosine similarity, top-N or threshold.
    agda_similarity.py FILE1 FILE2
    agda_similarity.py --glob 'agda/Substrate/Groups/Z*.agda' --top 20
    agda_similarity.py --glob '...' --threshold 0.7
    agda_similarity.py --glob '...' --breakdown      # show per-scale
    agda_similarity.py --glob '...' --csv

  template extraction: across a *set* of files, find the shared
    skeleton (units appearing in every file) vs the per-file holes
    (units unique to one file). Useful for spotting genericization
    targets — when the skeleton dominates, the set is an orbit.
      agda_similarity.py --glob '...' --template
      agda_similarity.py --glob '...' --template --scale line
      agda_similarity.py --glob '...' --template --max-show 30

Substrate use case: find orbits — clusters of files with same shape —
as candidates for genericization via a parametric module. After
genericization, similarity scores in the cluster should DROP (shape
moved into the generic, instances are now thin); the template's
skeleton should shrink toward "the open-import line + the per-Zₙ data".
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
# Template extraction — multi-file co-occurrence at each scale.
#
# For a set of files, partition each scale's units by how many files
# contain them. Units appearing in ALL files are the shared SKELETON
# (the genericizable template); units appearing in ONE file are the
# per-file HOLES (the parametric data). The breakdown shows how much
# of the structure is shared vs. per-Zₙ.
# ---------------------------------------------------------------------------


def units_at_scale(text: str, scale: str) -> list[str]:
    """Extract a flat list of units at the given scale. Same
    tokenization/normalization as the cosine code uses, but returns
    a list (not Counter) so we can compute per-unit file membership."""
    body = strip_comment_lines(text)
    if scale == "char3":
        clean = re.sub(r"\s+", " ", body).strip()
        return [clean[i : i + 3] for i in range(len(clean) - 2)]
    if scale == "token":
        return TOKEN_RE.findall(body)
    if scale == "line":
        return [s for line in body.splitlines() if (s := line.strip())]
    if scale == "block":
        out: list[str] = []
        cur: list[str] = []
        for line in body.splitlines():
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
        return [" ".join(sorted(TOKEN_RE.findall(b))) for b in out if b]
    raise ValueError(f"unknown scale: {scale!r}")


def template_at_scale(
    paths: list[Path], scale: str
) -> dict[str, set[Path]]:
    """Map each unit at this scale to the set of files containing it.
    Uses set-presence (a unit appearing 3× in one file still counts
    as "in 1 file") since orbit analysis cares about file-membership
    not within-file frequency."""
    unit_files: dict[str, set[Path]] = {}
    for path in paths:
        text = path.read_text(errors="replace")
        for unit in set(units_at_scale(text, scale)):
            unit_files.setdefault(unit, set()).add(path)
    return unit_files


def _bucket_by_count(
    unit_files: dict[str, set[Path]],
) -> dict[int, list[str]]:
    by_count: dict[int, list[str]] = {}
    for unit, fs in unit_files.items():
        by_count.setdefault(len(fs), []).append(unit)
    return by_count


def _truncate(s: str, limit: int) -> str:
    return s if len(s) <= limit else s[: limit - 3] + "..."


def print_template_for_scale(
    paths: list[Path],
    scale: str,
    *,
    max_show: int,
    show_holes: bool,
    line_width: int = 100,
) -> None:
    """Print the template at one scale: skeleton + intermediate
    counts + per-file holes."""
    n = len(paths)
    unit_files = template_at_scale(paths, scale)
    by_count = _bucket_by_count(unit_files)

    total_units = sum(len(v) for v in by_count.values())
    shared = len(by_count.get(n, []))
    unique = len(by_count.get(1, []))

    print(f"\n=== Template at scale: {scale} ({n} files) ===")
    print(
        f"    {total_units} distinct units total — "
        f"{shared} shared by ALL ({100*shared/total_units:.1f}%), "
        f"{unique} unique to one file ({100*unique/total_units:.1f}%)"
    )

    # Skeleton: appears in every file.
    skel = sorted(by_count.get(n, []))
    if skel:
        print(f"\n-- SKELETON (in all {n} files; {len(skel)} units) --")
        for u in skel[:max_show]:
            print(f"  {_truncate(u, line_width)}")
        if len(skel) > max_show:
            print(f"  ... ({len(skel) - max_show} more)")

    # Intermediate buckets — useful for spotting near-orbits.
    for count in sorted(by_count.keys(), reverse=True):
        if count == n or count == 1:
            continue
        bucket = sorted(by_count[count])
        print(f"\n-- shared by {count}/{n} ({len(bucket)} units) --")
        for u in bucket[:max_show]:
            print(f"  {_truncate(u, line_width)}")
        if len(bucket) > max_show:
            print(f"  ... ({len(bucket) - max_show} more)")

    # Per-file holes: each file's unique-to-itself units.
    if show_holes and unique > 0:
        print(f"\n-- HOLES (unique to one file; {unique} units total) --")
        by_file: dict[Path, list[str]] = {}
        for unit in by_count.get(1, []):
            (only_file,) = unit_files[unit]
            by_file.setdefault(only_file, []).append(unit)
        for path in sorted(by_file.keys()):
            us = sorted(by_file[path])
            print(f"\n  {path}  ({len(us)} unique)")
            for u in us[:max_show]:
                print(f"    {_truncate(u, line_width)}")
            if len(us) > max_show:
                print(f"    ... ({len(us) - max_show} more)")


def print_templates(
    paths: list[Path],
    scales: list[str],
    *,
    max_show: int,
    show_holes: bool,
) -> None:
    """Print templates at each requested scale."""
    print(f"Template analysis over {len(paths)} files:")
    for p in paths:
        print(f"  {p}")
    for scale in scales:
        print_template_for_scale(
            paths, scale, max_show=max_show, show_holes=show_holes
        )


# ---------------------------------------------------------------------------
# Recursive skeleton extraction.
#
# The independent-scale template (above) reveals shared structure AT each
# scale separately. But the per-file holes at LINE scale are themselves
# token-similar across files (only Zₙ differs after rename pass), so a
# second-order skeleton lives WITHIN the holes. The recursive form
# captures this by feeding the previous level's per-file holes back in as
# the input text for the next-finer level.
#
# Coarse-to-fine ordering: block → line → token → char3. At each level
# we absorb the shared skeleton and pass each file's residue forward.
# After all four levels, the remaining residue is the genuinely
# per-file content (typically just the Zₙ digit difference).
# ---------------------------------------------------------------------------


DEFAULT_RECURSIVE_ORDER: tuple[str, ...] = ("block", "line", "token", "char3")


def recursive_template(
    paths: list[Path],
    scale_order: list[str],
    *,
    max_show: int,
    line_width: int = 100,
) -> None:
    """Apply skeleton extraction recursively at coarse-to-fine scales.

    At each level: extract per-file units, compute the shared skeleton
    (units in every file), report it; then re-pack each file's holes
    (set difference vs. skeleton) as text for the next level. The
    coarser-scale skeleton absorbs structure first; finer scales then
    surface shared content that lives WITHIN the per-file holes.
    """
    n = len(paths)
    print(f"Recursive template over {n} files, scales: {' → '.join(scale_order)}")
    for p in paths:
        print(f"  {p}")

    current: dict[Path, str] = {
        p: p.read_text(errors="replace") for p in paths
    }

    for level, scale in enumerate(scale_order):
        per_file_units: dict[Path, set[str]] = {
            p: set(units_at_scale(current[p], scale)) for p in paths
        }
        sets = list(per_file_units.values())
        if sets and all(sets):
            shared = set.intersection(*sets)
        else:
            shared = set()

        total = sum(len(u) for u in sets)
        holes_total = sum(len(per_file_units[p] - shared) for p in paths)

        print(
            f"\n--- LEVEL {level} ({scale}) ---"
            f"\n  {total} unit-presences over all files; "
            f"{len(shared)} in shared skeleton; "
            f"{holes_total} hole presences across {n} files"
        )

        if shared:
            print(f"\n  SKELETON @ {scale} ({len(shared)} units):")
            for u in sorted(shared)[:max_show]:
                print(f"    {_truncate(u, line_width)}")
            if len(shared) > max_show:
                print(f"    ... ({len(shared) - max_show} more)")

        # Re-pack per-file holes as text for the next level.
        current = {
            p: "\n".join(sorted(per_file_units[p] - shared)) for p in paths
        }

    # After all levels: per-file residue (genuinely irreducible content).
    print(f"\n=== Per-file residue (after all {len(scale_order)} levels) ===")
    for p in paths:
        residue = [r for r in current[p].splitlines() if r.strip()]
        print(f"\n  {p}: {len(residue)} residue units")
        for r in sorted(residue)[:max_show]:
            print(f"    {_truncate(r, line_width)}")
        if len(residue) > max_show:
            print(f"    ... ({len(residue) - max_show} more)")


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
        help="Glob pattern; may be passed multiple times.",
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
    ap.add_argument(
        "--template",
        action="store_true",
        help=(
            "Template-extraction mode: across the file set, print the "
            "shared skeleton + per-file holes at each scale. Useful for "
            "spotting genericization targets."
        ),
    )
    ap.add_argument(
        "--scale",
        action="append",
        choices=list(SCALE_NAMES),
        help=(
            "Restrict template extraction to one or more scales. "
            "May be passed multiple times. Default: all four."
        ),
    )
    ap.add_argument(
        "--max-show",
        type=int,
        default=20,
        help="Cap units printed per bucket in template mode (default: 20)",
    )
    ap.add_argument(
        "--no-holes",
        action="store_true",
        help="In template mode, suppress per-file holes (count=1 units)",
    )
    ap.add_argument(
        "--recursive",
        action="store_true",
        help=(
            "Recursive template extraction: run scales coarse-to-fine "
            "(block → line → token → char3 by default), feeding each "
            "level's per-file holes forward as the next-level input. "
            "Surfaces shared structure WITHIN per-file unique content "
            "(e.g., shared tokens within Zₙ-varying lines). Implies "
            "--template; --scale (repeatable) overrides the order."
        ),
    )
    args = ap.parse_args(argv)

    paths = expand_paths(args)
    if len(paths) < 2:
        ap.error("Need at least two files (use positional args or --glob)")

    if args.recursive:
        scales = args.scale or list(DEFAULT_RECURSIVE_ORDER)
        recursive_template(paths, scales, max_show=args.max_show)
        return 0

    if args.template:
        scales = args.scale or list(SCALE_NAMES)
        print_templates(
            paths,
            scales,
            max_show=args.max_show,
            show_holes=not args.no_holes,
        )
        return 0

    # ---- similarity mode (default) ----
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
