"""Parametric skeleton construction by hole-marker substitution.

Where template.py REPORTS shared structure level-by-level, this
module CONSTRUCTS a usable artefact: tokenize each file, find tokens
that vary across files (the residue), substitute them with a hole
marker. If all files reduce to identical text, that text IS the
parametric template; the per-file substitution map IS the parameter list.

Two substitution modes:

  Single-hole (default): every residue token in every file gets
    replaced with the same marker (--hole-marker). Simple.

  Typed-holes (--typed-holes): order each file's residue tokens by
    first appearance in source, group by ordered position across
    files, assign each group its own marker. Marker names are
    derived from the group's common prefix/suffix when meaningful
    (e.g., a group of values {Z2-Coxeter, Z3-Coxeter, ...} becomes
    <Z?-Coxeter>); else <H1>, <H2>, ... numbered fallback.

For pure orbits (e.g. post-rename Z_n-x-FreeCyclic), all files
reduce to the same template under either mode. For partial orbits,
the largest aligned subset is shown with each shared-by-all line
marked `*`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .tokenize import TOKEN_RE, read_anonymized, strip_comment_lines


# ---------------------------------------------------------------------------
# Substitution helpers.
# ---------------------------------------------------------------------------


def _substitute_tokens(text: str, replacements: dict[str, str]) -> str:
    """Replace each TOKEN_RE-matched occurrence in text via the
    replacements map (token → marker). Non-token chars (whitespace,
    punctuation outside the regex) pass through verbatim."""
    def repl(m: re.Match) -> str:
        return replacements.get(m.group(), m.group())
    return TOKEN_RE.sub(repl, text)


def _order_residues_by_first_appearance(
    text: str, residues: set[str]
) -> list[str]:
    """Return residue tokens ordered by first occurrence in text.
    Single pass over TOKEN_RE matches; O(text)."""
    first_offsets: dict[str, int] = {}
    for m in TOKEN_RE.finditer(text):
        tok = m.group()
        if tok in residues and tok not in first_offsets:
            first_offsets[tok] = m.start()
        if len(first_offsets) == len(residues):
            break
    return sorted(residues, key=lambda t: first_offsets.get(t, len(text) + 1))


def _common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def _common_suffix(strs: list[str]) -> str:
    if not strs:
        return ""
    suffix = strs[0]
    for s in strs[1:]:
        while not s.endswith(suffix):
            suffix = suffix[1:]
            if not suffix:
                return ""
    return suffix


def _derive_marker(values: list[str], index: int) -> str:
    """Derive a descriptive marker for a hole group from its values'
    common prefix/suffix. Falls back to <H{index+1}> when there's no
    meaningful shared pattern."""
    if not values:
        return f"<H{index+1}>"
    pref = _common_prefix(values)
    suff = _common_suffix(values)
    shortest = min(len(v) for v in values)
    # Require pref+suff to leave at least one varying char.
    if pref and suff and len(pref) + len(suff) < shortest:
        return f"<{pref}?{suff}>"
    if pref and len(pref) < shortest:
        return f"<{pref}?>"
    if suff and len(suff) < shortest:
        return f"<?{suff}>"
    return f"<H{index+1}>"


# ---------------------------------------------------------------------------
# Artifact emission helpers (for downstream tooling).
# ---------------------------------------------------------------------------


def _build_substitution_map(
    paths: list[Path],
    use_typed: bool,
    markers: list[str],
    groups: list[dict[Path, str]],
    residue_per_file: dict[Path, set[str]],
    hole_marker: str,
    template_text: str,
) -> dict:
    """Build a JSON-serializable substitution map from a successful
    skeleton construction. Format:
      {
        "mode": "typed-holes" | "single-hole",
        "template": "<unified template text>",
        "files": [<path>, ...],
        "groups": [
          {"marker": "<H1>", "values": {"file_a": "val_a", ...}},
          ...
        ]  # in typed-holes mode
        | "substitutions": {
          "<file>": {"<marker>": "<value>", ...}, ...
        }  # in single-hole mode
      }
    """
    base = {
        "mode": "typed-holes" if use_typed else "single-hole",
        "template": template_text,
        "files": [str(p) for p in paths],
    }
    if use_typed:
        base["groups"] = [
            {
                "marker": marker,
                "values": {str(p): groups[i][p] for p in paths},
            }
            for i, marker in enumerate(markers)
        ]
    else:
        base["marker"] = hole_marker
        base["substitutions"] = {
            str(p): {hole_marker: sorted(residue_per_file[p])} for p in paths
        }
    return base


# ---------------------------------------------------------------------------
# Skeleton construction.
# ---------------------------------------------------------------------------


def construct_skeleton(
    paths: list[Path],
    *,
    hole_marker: str = "<HOLE>",
    typed_holes: bool = False,
    line_width: int = 100,
    max_show: int = 30,
    anonymize_patterns: list[tuple[str, str]] | None = None,
    emit_template: Path | None = None,
    emit_map: Path | None = None,
) -> None:
    """Construct a parametric skeleton from a set of files.

    Pipeline:
      1. Tokenize each file (comment-stripped) and compute the cross-file
         shared token set.
      2. Per file, residue = tokens NOT in the shared set.
      3. Substitute each file's residue with marker(s).
         - typed_holes=False: every residue → hole_marker (single).
         - typed_holes=True: order each file's residues by first
           appearance; group by ordered position; assign each group
           its own marker (derived from common prefix/suffix or
           numbered). Requires all files have equal residue counts;
           falls back to single-mode if not.
      4. If all files produce identical post-substitution text →
         print the unified skeleton + per-group/per-file substitution
         maps.
      5. Else → print the first file's substituted view with shared-by-
         all lines marked, plus per-file residue counts.
    """
    raw_texts: dict[Path, str] = {
        p: read_anonymized(p, anonymize_patterns) for p in paths
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

    # Decide between single-hole and typed-holes modes.
    counts = [len(residue_per_file[p]) for p in paths]
    use_typed = typed_holes and counts and len(set(counts)) == 1 and counts[0] > 0

    if use_typed:
        n_holes = counts[0]
        ordered: dict[Path, list[str]] = {
            p: _order_residues_by_first_appearance(
                raw_texts[p], residue_per_file[p]
            )
            for p in paths
        }
        groups: list[dict[Path, str]] = [
            {p: ordered[p][i] for p in paths} for i in range(n_holes)
        ]
        markers: list[str] = [
            _derive_marker([groups[i][p] for p in paths], i)
            for i in range(n_holes)
        ]
        # Per-file substitution map.
        per_file_subs: dict[Path, dict[str, str]] = {
            p: {ordered[p][i]: markers[i] for i in range(n_holes)}
            for p in paths
        }
    else:
        per_file_subs = {
            p: {t: hole_marker for t in residue_per_file[p]} for p in paths
        }
        markers = []
        groups = []

    skeletons: dict[Path, str] = {
        p: _substitute_tokens(raw_texts[p], per_file_subs[p]) for p in paths
    }

    first_path = paths[0]
    first_skel = skeletons[first_path]
    all_match = all(skeletons[p] == first_skel for p in paths[1:])

    mode_label = (
        f"typed-holes ({len(markers)} groups)" if use_typed
        else f"single-hole ({hole_marker})"
    )
    print(f"# Skeleton over {len(paths)} files [{mode_label}]")
    print(f"#   shared tokens: {len(shared)}")
    print(f"#   per-file residue counts: " + ", ".join(
        f"{p.name}={len(residue_per_file[p])}" for p in paths
    ))
    if typed_holes and not use_typed:
        print(f"#   (--typed-holes requested but residue counts differ; "
              f"fell back to single-hole)")

    if all_match:
        print(f"# Result: all files reduce to one template.\n")
        print(first_skel)
        print()
        if use_typed:
            print(f"# --- Hole groups (per-marker values across files) ---")
            for i, marker in enumerate(markers):
                print(f"# {marker}:")
                for p in paths:
                    print(f"#   {p.name}  ←  {groups[i][p]}")
        else:
            print(f"# --- Substitution map (per file) ---")
            for p in paths:
                tokens_ = sorted(residue_per_file[p])
                print(f"# {p.name}:")
                for t in tokens_:
                    print(f"#   {hole_marker}  ←  {t}")

        # Optional artifact emission for downstream tooling.
        if emit_template is not None:
            emit_template.write_text(first_skel)
            print(f"\n# Template written to: {emit_template}")
        if emit_map is not None:
            payload = _build_substitution_map(
                paths, use_typed, markers, groups, residue_per_file,
                hole_marker, first_skel,
            )
            emit_map.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
            print(f"# Substitution map written to: {emit_map}")
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
            print(f"#   {t}")
        if len(tokens_) > max_show:
            print(f"#   ... ({len(tokens_) - max_show} more)")
