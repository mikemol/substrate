"""Template extraction: per-scale skeleton/holes + recursive drill-down.

Where similarity.py REPORTS a number, this module REPORTS structured
buckets: which units (at each scale) are shared by all files (= the
skeleton) vs unique to one file (= the holes). The recursive variant
feeds each level's per-file holes forward as the next-finer level's
input, surfacing shared structure WITHIN per-file unique content.
"""

from __future__ import annotations

from pathlib import Path

from .tokenize import units_at_scale


DEFAULT_RECURSIVE_ORDER: tuple[str, ...] = ("block", "line", "token", "char3")


# ---------------------------------------------------------------------------
# Independent-scale templates.
# ---------------------------------------------------------------------------


def template_at_scale(
    paths: list[Path], scale: str
) -> dict[str, set[Path]]:
    """Map each unit at this scale to the set of files containing it.
    Set-presence (a unit appearing 3× in one file counts as "in 1
    file") since orbit analysis cares about file-membership, not
    within-file frequency."""
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
# Recursive skeleton extraction (coarse-to-fine, drill into holes).
# ---------------------------------------------------------------------------


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
