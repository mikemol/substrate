"""Argparse driver + mode dispatch.

Modes (in priority order):
  --skeleton   : construct parametric template (skeleton.construct_skeleton)
  --recursive  : recursive coarse-to-fine drill-down (template.recursive_template)
  --template   : per-scale skeleton/holes report (template.print_templates)
  default      : pairwise cosine similarity (similarity.pair_similarity)
"""

from __future__ import annotations

import argparse
import glob as glob_mod
from itertools import combinations
from pathlib import Path

from .score import print_score
from .similarity import SCALE_NAMES, pair_similarity, profile
from .skeleton import construct_skeleton
from .template import DEFAULT_RECURSIVE_ORDER, print_templates, recursive_template
from .tokenize import read_anonymized


def expand_paths(args: argparse.Namespace) -> list[Path]:
    if args.glob:
        paths = []
        for pattern in args.glob:
            paths.extend(Path(p) for p in glob_mod.glob(pattern, recursive=True))
        return sorted(set(paths))
    if args.files:
        return [Path(f) for f in args.files]
    return []


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Multi-scale cosine similarity + template extraction + "
            "skeleton construction over Agda files."
        )
    )
    ap.add_argument("files", nargs="*", help="Two files for single-pair mode")
    ap.add_argument(
        "--glob",
        action="append",
        help="Glob pattern; may be passed multiple times.",
    )

    # Similarity mode (default) options
    ap.add_argument(
        "--top", type=int, default=None, help="Show only top N pairs"
    )
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Only show pairs with geometric mean >= threshold",
    )
    ap.add_argument(
        "--csv", action="store_true", help="CSV output instead of table"
    )
    ap.add_argument(
        "--breakdown",
        action="store_true",
        help="Show per-scale breakdown (char3 / token / line / block)",
    )

    # Template mode options
    ap.add_argument(
        "--template",
        action="store_true",
        help=(
            "Template-extraction mode: across the file set, print the "
            "shared skeleton + per-file holes at each scale."
        ),
    )
    ap.add_argument(
        "--scale",
        action="append",
        choices=list(SCALE_NAMES),
        help=(
            "Restrict template/recursive extraction to one or more "
            "scales. May be passed multiple times. Default: all four."
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

    # Recursive template options
    ap.add_argument(
        "--recursive",
        action="store_true",
        help=(
            "Recursive template extraction: run scales coarse-to-fine "
            "(block → line → token → char3 by default), feeding each "
            "level's per-file holes forward as the next-level input. "
            "Implies --template; --scale (repeatable) overrides the order."
        ),
    )

    # Skeleton mode options
    ap.add_argument(
        "--skeleton",
        action="store_true",
        help=(
            "Construct a parametric skeleton: substitute per-file "
            "residue tokens with a hole marker; if all files reduce "
            "to identical text, print the unified skeleton + per-file "
            "substitution maps. Else print the largest aligned subset."
        ),
    )
    ap.add_argument(
        "--hole-marker",
        default="<HOLE>",
        help="Hole marker for skeleton mode (default: <HOLE>)",
    )
    ap.add_argument(
        "--typed-holes",
        action="store_true",
        help=(
            "In --skeleton mode, group residue tokens by first-"
            "appearance position across files and assign each group "
            "its own marker (derived from common prefix/suffix when "
            "meaningful, else <H1>, <H2>, ...). Requires all files "
            "have equal residue counts; falls back to single-hole "
            "mode if not."
        ),
    )

    # Score mode option
    ap.add_argument(
        "--score",
        action="store_true",
        help=(
            "Genericization-score mode: print per-scale shared/total "
            "ratios + a STRONG/PARTIAL/WEAK orbit verdict. Quick "
            "actionable summary without reading full template dumps."
        ),
    )

    # Preprocessing: pattern-based anonymization
    ap.add_argument(
        "--anonymize",
        action="append",
        nargs=2,
        metavar=("PATTERN", "REPLACEMENT"),
        help=(
            "Apply a regex-based substitution to each file's text "
            "BEFORE tokenization. Repeatable: each `--anonymize "
            "PATTERN REPLACEMENT` adds one substitution. Converts "
            "rename-orbits to structural orbits the analysis can see "
            "cleanly. Example: `--anonymize 'Z[2-9]' '<Zn>' "
            "--anonymize 'Z[₂-₉]' '<Zn>'`. Applies to similarity, "
            "template, recursive, skeleton, and score modes."
        ),
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    paths = expand_paths(args)
    if len(paths) < 2:
        ap.error("Need at least two files (use positional args or --glob)")

    # argparse gives args.anonymize as list[list[str]] (each nargs=2 pair);
    # convert to list of tuples for clean downstream typing.
    anonymize_patterns: list[tuple[str, str]] | None = (
        [(p, r) for p, r in args.anonymize] if args.anonymize else None
    )

    if args.score:
        print_score(paths, anonymize_patterns=anonymize_patterns)
        return 0

    if args.skeleton:
        construct_skeleton(
            paths,
            hole_marker=args.hole_marker,
            typed_holes=args.typed_holes,
            max_show=args.max_show,
            anonymize_patterns=anonymize_patterns,
        )
        return 0

    if args.recursive:
        scales = args.scale or list(DEFAULT_RECURSIVE_ORDER)
        recursive_template(
            paths,
            scales,
            max_show=args.max_show,
            anonymize_patterns=anonymize_patterns,
        )
        return 0

    if args.template:
        scales = args.scale or list(SCALE_NAMES)
        print_templates(
            paths,
            scales,
            max_show=args.max_show,
            show_holes=not args.no_holes,
            anonymize_patterns=anonymize_patterns,
        )
        return 0

    # ---- similarity mode (default) ----
    profiles = {
        p: profile(read_anonymized(p, anonymize_patterns)) for p in paths
    }

    results: list[tuple[float, tuple[float, ...], Path, Path]] = []
    for a, b in combinations(paths, 2):
        geo, scale_scores = pair_similarity(profiles[a], profiles[b])
        if geo >= args.threshold:
            results.append((geo, scale_scores, a, b))

    results.sort(reverse=True)
    if args.top:
        results = results[: args.top]

    if args.csv:
        cols = ["score"]
        if args.breakdown:
            cols += list(SCALE_NAMES)
        cols += ["file_a", "file_b"]
        print(",".join(cols))
        for geo, scale_scores, a, b in results:
            row = [f"{geo:.4f}"]
            if args.breakdown:
                row += [f"{s:.4f}" for s in scale_scores]
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
    for geo, scale_scores, a, b in results:
        row_str = f"{geo:6.4f}".ljust(8)
        if args.breakdown:
            row_str += "  ".join(f"{s:5.3f}" for s in scale_scores) + "  "
        row_str += f"{a}  <->  {b}"
        print(row_str)
    return 0
