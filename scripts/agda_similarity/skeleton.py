"""Parametric skeleton construction by hole-marker substitution.

Where template.py REPORTS shared structure level-by-level, this
module CONSTRUCTS a usable artefact: tokenize each file, find tokens
that vary across files (the residue), substitute them with a hole
marker. If all files reduce to identical text, that text IS the
parametric template; the per-file substitution map IS the parameter list.

For pure orbits (e.g. post-rename Z_n-x-FreeCyclic), all files
reduce to the same template. For partial orbits, the largest
aligned subset is shown with each shared-by-all line marked `*`.
"""

from __future__ import annotations

import re
from pathlib import Path

from .tokenize import TOKEN_RE, strip_comment_lines


def _substitute_tokens(text: str, replacements: dict[str, str]) -> str:
    """Replace each TOKEN_RE-matched occurrence in text via the
    replacements map (token → marker). Non-token chars (whitespace,
    punctuation outside the regex) pass through verbatim."""
    def repl(m: re.Match) -> str:
        return replacements.get(m.group(), m.group())
    return TOKEN_RE.sub(repl, text)


def construct_skeleton(
    paths: list[Path],
    *,
    hole_marker: str = "<HOLE>",
    line_width: int = 100,
    max_show: int = 30,
) -> None:
    """Construct a parametric skeleton from a set of files.

    1. Tokenize each file (comment-stripped) and compute the cross-file
       shared token set.
    2. Per file, the residue = tokens NOT in the shared set.
    3. Substitute each file's residue tokens with hole_marker.
    4. If all files produce identical post-substitution text → print
       the unified skeleton + per-file substitution maps.
    5. Else → print the first file's substituted view with shared-by-
       all lines marked, plus per-file residue counts.
    """
    raw_texts: dict[Path, str] = {
        p: p.read_text(errors="replace") for p in paths
    }
    bodies: dict[Path, str] = {
        p: strip_comment_lines(raw_texts[p]) for p in paths
    }
    per_file_tokens: dict[Path, set[str]] = {
        p: set(TOKEN_RE.findall(bodies[p])) for p in paths
    }

    sets = list(per_file_tokens.values())
    if not sets or not all(sets):
        print("Cannot construct skeleton: at least one file has no tokens.")
        return

    shared = set.intersection(*sets)
    residue_per_file: dict[Path, set[str]] = {
        p: per_file_tokens[p] - shared for p in paths
    }

    skeletons: dict[Path, str] = {
        p: _substitute_tokens(
            raw_texts[p],
            {t: hole_marker for t in residue_per_file[p]},
        )
        for p in paths
    }

    first_path = paths[0]
    first_skel = skeletons[first_path]
    all_match = all(skeletons[p] == first_skel for p in paths[1:])

    print(f"# Skeleton over {len(paths)} files (hole marker: {hole_marker})")
    print(f"#   shared tokens: {len(shared)}")
    print(f"#   per-file residue counts: " + ", ".join(
        f"{p.name}={len(residue_per_file[p])}" for p in paths
    ))

    if all_match:
        print(f"# Result: all files reduce to one template.\n")
        print(first_skel)
        print()
        print(f"# --- Substitution map (per file) ---")
        for p in paths:
            tokens_ = sorted(residue_per_file[p])
            print(f"# {p.name}:")
            for t in tokens_:
                print(f"#   {hole_marker}  ←  {t}")
        return

    # Partial alignment: some lines line up across substituted files.
    print(f"# Result: skeletons DIFFER. Showing largest aligned subset.\n")

    per_file_lines: dict[Path, list[str]] = {
        p: [
            line for line in strip_comment_lines(skeletons[p]).splitlines()
            if line.strip()
        ]
        for p in paths
    }
    line_sets = [set(ls) for ls in per_file_lines.values()]
    shared_lines = (
        set.intersection(*line_sets) if all(line_sets) else set()
    )

    print(f"# View from {first_path.name} "
          f"(* = line appears in every file after substitution):\n")
    first_substituted_lines = skeletons[first_path].splitlines()
    for line in first_substituted_lines:
        stripped = line.strip()
        if stripped and stripped in shared_lines:
            print(f"* {line}")
        else:
            print(f"  {line}")

    print()
    print(f"# {len(shared_lines)} lines shared across all {len(paths)} "
          f"substituted files (out of "
          f"{len(per_file_lines[first_path])} code-lines in {first_path.name}).")
    print()
    print(f"# --- Per-file residue (substitution targets) ---")
    for p in paths:
        tokens_ = sorted(residue_per_file[p])
        print(f"# {p.name} ({len(tokens_)} residue tokens):")
        for t in tokens_[:max_show]:
            print(f"#   {hole_marker}  ←  {t}")
        if len(tokens_) > max_show:
            print(f"#   ... ({len(tokens_) - max_show} more)")
