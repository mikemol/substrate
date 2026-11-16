#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""split_pipeline - the one-lemma-per-file DRIVER, now a shim of adaptors over the package.

THIS FILE IS ADAPTORS (W4 file 4 step 13, tick 55). Every mechanism the origin held has a home
in `substrate/` and is witnessed there: the failure attribution is `agda_blame`; the readiness
verdict is `rewire_ready`; the build argv and captured run are `agda_build_cmd`; the collision
cure's PLAN is `agda_rename_plan`; the retire DECISION is `barrel_retire`; the read side (DAG,
freshness, classifier, census, stamp) is `split_census`, itself a shim over seven package modules;
the blocker chase is `split_unblock`. What stays here is the SEQUENCE - the stages are only
correct in order, and this is the one file that spells that order - plus the shape fifteen bare
consumer sites reach through `import split_pipeline as SP`:

- `main(argv)`, `DEFAULT_MB` (enforce_ban); `log_is_fresh`, `_classify`, `CLASS_REMEDY`
  (figures, stale_error_logs, wg_dispatch); `unblock` (wg_dispatch); `leverage`,
  `_blast_radius`, `tree_stamp` (figures); `blame` (fix_notinscope, bound as `_blame`);
  `isolate_check`, `rewire_only` (split_unblock's late-imported driver thunks).

THE MODES ARE A ROSTER, NOT A LADDER OF `if "--x" in sys.argv`. The origin dispatched ten modes
across `main` and a 430-line `__main__` block, in an order a reader could only learn by reading
both; `toolmodes --divergence` once reported all seventeen undocumented. `_MODES` names each flag
beside its handler, and `usage()` renders from it, so the roster and the help cannot drift.

TWO ORIGIN FACTS ARE KEPT AS RULES AND NAMED HERE RATHER THAN IN A STAGE COMMENT. `--census`
IMPLIES `--verify --from-build --build-log=<its own log>`: the census is a build followed by
exactly the read the artifacts get anyway, so there is one reader. And ONLY A FULL-POPULATION
run may write `.leaf-verify.tsv` - a scoped `--verify <file>` once overwrote a 1322-row census
with one row and destroyed a forty-minute worklist.

`DEFAULT_MB = 384` RESTATES THE MEMBUDGET LEASE CEILING (authority: `scripts/membudget`,
`AGDA_MB_MAX`), which the package deliberately did not carry (`agda_build_cmd`'s docstring).
It stays here because `enforce_ban` and `split_unblock` read it by this name; a reader of that
authority would retire it. Recorded as residue, not hidden.

The origin's stage comments were the record of why each stage exists; the package modules
carry those now and this file does not repeat them.

MODES (the `_MODES` roster below is the dispatch; `usage()` renders it; a selftest case holds
this block to it, because `toolmodes` reads THIS text as the tool's self-description):

    split_pipeline.py <file.agda> [--apply] [--mb=N]   split into one-lemma leaves, run the chain
    split_pipeline.py --last                            re-read the persisted census
    split_pipeline.py --leverage [--applied-open|--failed|<paths>]   what a set blocks
    split_pipeline.py --unblock <file.agda> [--apply]   chase the blocker chain to a fixpoint
    split_pipeline.py --diagnose [<paths>] [--blockers] [--trace] [--ready]   classify failures
    split_pipeline.py --why <file.agda>                 the compiler's own output
    split_pipeline.py --census [--jobs=N]               BUILD then READ, one command
    split_pipeline.py --verify [<paths>|--leaves] [--jobs=N]   isolate-check a population
    split_pipeline.py --verify --from-build [--build-log=FILE]   read the build's own logs
    split_pipeline.py --stale-why                       why each unmeasured module is unmeasured
    split_pipeline.py <Module> --retire [--apply]       delete a consumed barrel once it is dead
    split_pipeline.py <Module> --rewire-only [--apply]  stages 5-6b for an already-split parent
    split_pipeline.py --selftest
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import agda_defs
import check_indented_imports
import collapse_carrier_nesting
import edit_snapshot
import fix_stale_using
import rename_at_source
import split_census
import split_lemmas
from agda_lex import module_path
from split_census import (
    CLASS_REMEDY,
    _blast_radius,
    _classify,
    census_from_build,
    is_other,
    leaves,
    leverage,
    log_is_fresh,
    other_kind,
    run_census,
    tree_stamp,
)
from split_unblock import _under, diagnose, leaves_ready, unblock, verify

from substrate import (
    agda_blame,
    agda_build_cmd,
    agda_rename_plan,
    barrel_retire,
    leaf_ledger,
    rewire_ready,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

__all__ = [
    "CLASS_REMEDY",
    "DEFAULT_MB",
    "_blast_radius",
    "_classify",
    "_under",
    "blame",
    "census_from_build",
    "diagnose",
    "is_other",
    "isolate_check",
    "leaves",
    "leaves_ready",
    "leverage",
    "log_is_fresh",
    "main",
    "other_kind",
    "rewire_only",
    "run_census",
    "tree_stamp",
    "unblock",
    "verify",
]

ROOT = Path(__file__).resolve().parent.parent
AG = "agda"
# The membudget lease ceiling, RESTATED - see the module docstring.
DEFAULT_MB = 384
# The persisted census, relative to the repo root.
LEDGER = Path(AG) / ".leaf-verify.tsv"
# How many ranked rows the reports print.
TOP = 10
# The cure loop's bound: how many clashes one build may cure before it stops.
CURE_ROUNDS = 4
# `ready_verdict` compile-checks at most this many leaves; over it, it says so.
COMPILE_CAP = 24
# How many `ready` rows the diagnose report shows.
READY_ROWS = 5
# How much of a failing tool's tail `die` shows.
TAIL = 4000
# The consumed-parent kind the diagnose report gates `--ready` on.
FILE_NOT_FOUND = "file-not-found"

Row = tuple[str, str, str]

_SNAPPED: list[bool] = []


def _say(msg: str = "") -> None:
    """Print one line."""
    sys.stdout.write(msg + "\n")


def die(msg: str, out: str | None = None) -> NoReturn:
    """Print the failure (and the tail of the tool's output) and exit 1."""
    _say(f"\n✗ {msg}")
    if out:
        _say(out[-TAIL:])
    sys.exit(1)


def run(cmd: Sequence[str], cwd: str | None = None, label: str | None = None) -> tuple[int, str]:
    """Run `cmd` from the repo root unless told otherwise; return (rc, out) - the command's own."""
    return agda_build_cmd.run(cmd, cwd or str(ROOT), label)


def make_cmd(*extra: str) -> list[str]:
    """Return the full-build argv over the ONE `-j` authority."""
    return agda_build_cmd.make_cmd(split_census.agda_build_cmd_jobs(), *extra, agda_dir=AG)


def module_of(rel_agda_path: str) -> str:
    """Return `Substrate.Foo.Bar` for `agda/Substrate/Foo/Bar.agda`."""
    p = rel_agda_path.removeprefix(AG + "/")
    if not p.endswith(".agda"):
        msg = f"not an agda source: {rel_agda_path}"
        raise ValueError(msg)
    return module_path(p, "")


def _module_of(path: str) -> str:
    """Return the module an absolute or relative source path names."""
    rel = Path(path).resolve().relative_to(Path(AG).resolve())
    return module_path(str(rel), "")


def _snapshot_once(path: str) -> None:
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter."""
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        edit_snapshot.guard("split_pipeline", [path])
    except edit_snapshot.MutationContractError as e:
        _say(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


def isolate_check(leaf_path: str, mb: int = DEFAULT_MB) -> tuple[int, str]:
    """Compile one leaf alone under a membudget lease; return (rc, out)."""
    rel = leaf_path.removeprefix(AG + "/")
    label = rel.replace("/", "-")
    return run([str(ROOT / "scripts" / "membudget"), "run", str(mb), label,
                "--", "agda", "--safe", "-i.", rel], cwd=str(ROOT / AG))


def blame(leaf_path: str, out: str) -> tuple[str, str | None]:
    """Return ('clean'|'own'|'dependency', cited_file) for an isolate_check result."""
    return agda_blame.blame(leaf_path, out)


def why(path: str) -> tuple[int, str]:
    """Return the compiler's own output for one file - the diagnosis behind a verdict."""
    return isolate_check(path)


def sweep_orphan_agdai() -> list[str]:
    """Remove every `.agdai` under `agda/_build/*/agda` whose source is gone; return the paths."""
    removed: list[str] = []
    for agdai in (ROOT / AG / "_build").glob(f"*/{AG}/**/*.agdai"):
        # .../_build/<ver>/agda/Substrate/X.agdai -> agda/Substrate/X.agda: split at the LAST `agda`
        parts = agdai.parts
        idx = max(i for i, part in enumerate(parts) if part == AG)
        src = (ROOT / AG).joinpath(*parts[idx + 1:]).with_suffix(".agda")
        if not src.exists():
            agdai.unlink()
            removed.append(str(agdai))
    return removed


# ── the collision cure ──────────────────────────────────────────────────────────


def _parse_clash(out: str) -> tuple[str, str, str] | None:
    """Return (consumer_file, name, previous_def_file) from a [ClashingDefinition], or None."""
    return agda_blame.parse_clash(out)


def cure_collisions(out: str, leaves: Sequence[str] = (),
                    max_rounds: int = CURE_ROUNDS) -> tuple[int, str]:
    """Cure split-induced clashes by renaming at source; return (cured, note)."""
    leafset = {str(Path(x).resolve()) for x in leaves}
    cured = 0
    for _ in range(max_rounds):
        hit = _parse_clash(out)
        if not hit:
            break
        decision = agda_rename_plan.plan(hit, leafset, _module_of)
        if isinstance(decision, agda_rename_plan.Skip):
            _say(f"  collision {decision.name} ({hit[0]} vs {hit[2]}) {decision.reason}.")
            break
        _say(f"  collision: {decision.name} in {hit[0]} vs {hit[2]}")
        _say(f"    rename at source: {decision.home}.{decision.name} -> {decision.new}")
        home, name, new = decision.home, decision.name, decision.new
        _renamed, ambiguous = rename_at_source.rename(home, name, new, apply=True)
        for amb in ambiguous:
            rename_at_source.rename(home, name, new, apply=True, site=amb)
        cured += 1
        rc, out = run(make_cmd())
        if rc == 0:
            return cured, "build green after cure"
    if "AmbiguousOverloadedProjection" in out:
        return cured, ("AmbiguousOverloadedProjection remains — cure by QUALIFYING "
                       "AT THE VALUE (`Record.field value`), never a `using` filter "
                       "(banned). 403 applied-open sites tree-wide.")
    return cured, ""


# ── readiness ───────────────────────────────────────────────────────────────────


def ready_verdict(modname: str, compile_cap: int = COMPILE_CAP) -> list[str]:
    """Return the lines classifying whether `modname`'s rewire remedy is safe to run."""
    leaf_mods = _under(modname)
    manifest = ""
    if leaf_mods:
        _rc, manifest = run(["python3", "scratch/rewire_to_leaves.py", modname,
                             "--manifest", "--dry-run"])
    reex = tuple(r for r in agda_defs.reexport_index()
                 if r[2] == modname or r[2].startswith(modname + "."))
    inputs = rewire_ready.Inputs(leaf_count=len(leaf_mods),
                                 manifest=rewire_ready.parse_manifest(manifest),
                                 reexports=reex, compile_cap=compile_cap, root=str(ROOT))
    if rewire_ready.needs_compile(inputs):
        ok, rows = leaves_ready(modname)
        inputs = rewire_ready.Inputs(leaf_count=len(leaf_mods), manifest=inputs.manifest,
                                     reexports=reex, compiled=(ok, tuple(rows)),
                                     compile_cap=compile_cap, root=str(ROOT))
    return rewire_ready.verdict(inputs)


# ── the write stages ────────────────────────────────────────────────────────────


def _rewire(modname: str, *, apply: bool, manifest: bool) -> str:
    """Stage 5: rewire importers onto the leaves; die on failure; return the tool's output."""
    cmd = ["python3", "scratch/rewire_to_leaves.py", modname]
    if manifest:
        cmd.append("--manifest")
    cmd.append("--apply" if apply else "--dry-run")
    rc, out = run(cmd)
    _say(out.strip() or "(no output)")
    if rc != 0:
        die("rewire_to_leaves.py failed", out)
    if "⚠ UNMAPPED" in out:
        _say("   ⚠ some names were UNMAPPED — those importers were left untouched.")
    return out


def _sweep(modname: str, remedy: str) -> None:
    """Stage 6: die on any surviving reference the column-0 rewire could not see."""
    _say("\n-- sweeping for indented/nested `open import` misses --")
    hits = check_indented_imports.sweep(modname)
    if hits:
        _say(f"✗ {len(hits)} surviving reference(s) to {modname}:")
        for p, i, kind, line in hits:
            _say(f"   [{kind}] {p}:{i}: {line.strip()}")
        die(remedy)
    _say("✓ no surviving references.")


def _prune(paths: Sequence[str], *extra: str) -> None:
    """Run prune_imports over `paths`; die on failure."""
    rc, out = run(["python3", "scratch/prune_imports.py", *extra, *paths])
    _say(out.strip() or "(no output)")
    if rc != 0:
        die("prune_imports.py failed", out)


def rewire_only(modname: str, apply: bool = False) -> int:  # noqa: FBT001, FBT002 - the origin's contract
    """Stages 5-6b for a parent that was ALREADY split: rewire, sweep, prune."""
    _say(f"-- rewiring importers of {modname} --")
    out = _rewire(modname, apply=apply, manifest=True)
    widened = [ln.strip() for ln in out.split("\n")
               if ln.strip().endswith(".agda") and Path(ln.strip()).exists()]
    if not apply:
        _say("\nDry run only — pass --apply to execute.")
        return 0
    _sweep(modname, "fix the above by hand (bare-import at the right leaf), then re-run.")
    _say("\n-- pruning the rewired consumers --")
    if not widened:
        _say("   (the rewire touched nothing — nothing to prune)")
        return 0
    _prune(widened, "--apply")
    _say(f"✓ pruned {len(widened)} rewired consumer(s).")
    return 0


DERIVED: tuple[tuple[str, list[str]], ...] = (
    ("build makefiles", ["python3", "scripts/gen_build_makefiles.py"]),
    ("shape-node index", ["python3", "scripts/sppf_node_index.py"]),
)


def refresh_derived(*, apply: bool = False) -> int:
    """Regenerate every artifact derived from the module set and verify each; return 0."""
    if not apply:
        for label, cmd in DERIVED:
            _say(f"   would refresh: {label}  ({' '.join(cmd)})")
        return 0
    for label, cmd in DERIVED:
        rc, out = run(cmd)
        if rc != 0:
            die(f"{label}: regeneration failed", out)
        crc, cout = run([*cmd, "--check"])
        if crc != 0:
            die(f"{label}: still STALE after regeneration", cout)
        _say(f"   ✓ {label} refreshed and verified current")
    return 0


def retire(modname: str, *, apply: bool = False) -> int:
    """Stage 7 for a CONSUMED BARREL: verify it is dead, then delete it."""
    rel = f"{AG}/" + modname.replace(".", "/") + ".agda"
    leafdir = Path(rel[:-len(".agda")])
    exists = Path(rel).exists()
    if not exists:
        v = barrel_retire.verdict(modname, rel, barrel_retire.Inputs(exists=False))
        _say(v.lines[0])
        _say("-- checking artifacts derived from the module set --")
        return refresh_derived(apply=apply)
    _say(f"-- retiring the consumed barrel {modname} --")
    hits = tuple(check_indented_imports.sweep(modname))
    leaf_files = sorted(f.name for f in leafdir.glob("*.agda")) if leafdir.is_dir() else []
    occupied: tuple[str, tuple[str, ...]] | None = None
    if not hits and leaf_files:
        kind, uncovered = collapse_carrier_nesting.classify_occupied(
            modname + "." + leaf_files[0][:-5], modname)
        occupied = (kind, tuple(uncovered))
    inp = barrel_retire.Inputs(exists=True, hits=hits, has_leaf_dir=leafdir.is_dir(),
                               leaves=tuple(leaf_files), occupied=occupied)
    v = barrel_retire.verdict(modname, rel, inp)
    if v.action == barrel_retire.REFUSE:
        if hits:
            _say("\n".join(v.lines))
            die(v.remedy or "")
        die("\n".join(v.lines))
    _say("✓ zero live references.")
    _say(v.lines[1])
    if not apply:
        _say(f"\nWould DELETE {rel}")
        refresh_derived(apply=False)
        _say("Dry run only — pass --apply to execute.")
        return 0
    edit_snapshot.guard(f"retire {modname}", [rel])
    Path(rel).unlink()
    _say(f"✓ DELETED {rel}")
    _say("\n-- refreshing artifacts derived from the module set --")
    return refresh_derived(apply=True)


# ── the split path (stages 1-12) ────────────────────────────────────────────────


def _split_apply(path: str) -> tuple[list[str], list[tuple[str, list[str] | None]]]:
    """Stage 1: split for real, capturing the destroyed conduits; return (leaves, conduits)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        files, _named = split_lemmas.split(path, apply=True)
    text = buf.getvalue()
    sys.stdout.write(text)
    conduits: list[tuple[str, list[str] | None]] = []
    for ln in text.split("\n"):
        if ln.startswith("# CONDUIT:"):
            parts = ln[len("# CONDUIT:"):].split()
            if parts:
                conduits.append((parts[0], parts[1:] if parts[1:] != ["*"] else None))
    leaves = sorted(files)
    _say(f"\n✓ split: {len(leaves)} leaf file(s) written, {path} deleted.")
    return leaves, conduits


def _prune_leaves(path: str, leaves: Sequence[str]) -> None:
    """Stage 2: prune every leaf's inherited import block, demand-guided from HEAD when present."""
    _say("\n-- pruning imports --")
    demand_ref = f"HEAD:{path}"
    rc, _ = run(["git", "cat-file", "-e", demand_ref])
    if rc != 0:
        _say(f"  ⚠ {path} is not at HEAD — no demand map available;"
             " pruning on the provision index alone.")
        _prune(leaves)
    else:
        _prune(leaves, "--demand-from", demand_ref)


def _isolate_leaves(leaves: Sequence[str], mb: int) -> None:
    """Stage 3: isolate-check every leaf; die on the first failure."""
    _say("\n-- isolate-checking leaves --")
    for leaf in leaves:
        rc, out = isolate_check(leaf, mb)
        if rc != 0:
            die(f"isolate-check FAILED for {leaf} (exit {rc}) — fix it (or restore\n"
                f"  the specific missing import) before re-running the pipeline.\n"
                f"  The split itself is DONE; do not revert (stash if you must).", out)
    _say(f"✓ {len(leaves)} leaf(s) isolate-clean.")


def _regen_makefiles(label: str) -> None:
    """Stages 4 and 9: regenerate the build makefiles and verify them current."""
    _say(f"\n-- regenerating makefiles{label} --")
    rc, out = run(["python3", "scripts/gen_build_makefiles.py"])
    if rc != 0:
        die("gen_build_makefiles.py failed", out)
    rc, out = run(["python3", "scripts/gen_build_makefiles.py", "--check"])
    if rc != 0:
        die(f"gen_build_makefiles.py --check failed after regen{label}", out)


def _prune_consumers(modname: str) -> None:
    """Stage 6b: prune the consumers the wide rewire just handed every leaf."""
    leafpat = f"import {modname}."
    consumers: list[str] = []
    for p in Path(AG).glob("Substrate/**/*.agda"):
        try:
            if leafpat in p.read_text(encoding="utf-8"):
                consumers.append(str(p))
        except OSError:
            continue
    _say(f"\n-- pruning {len(consumers)} rewired consumer(s) --")
    if consumers:
        rc, out = run(["python3", "scratch/prune_imports.py", *consumers])
        _say(out.strip()[-1500:] or "(no output)")
        if rc != 0:
            die("prune_imports.py failed on the rewired consumers", out)


def _rebind_one(modname: str, owner: str, names: list[str]) -> int:
    """Rebind every consumer reaching `names` through `modname` at `owner`; return the count."""
    pat = re.compile(r"^([ \t]*)open import " + re.escape(modname)
                     + r"[ \t]*(?:\n[ \t]+)?[ \t]*using[ \t]*\(([^)]*)\)[ \t]*$", re.MULTILINE)

    def rebind(mo: re.Match[str]) -> str:
        want = [t for t in re.split(r"[;\s]+", mo.group(2)) if t]
        if not any(t in names for t in want):
            return mo.group(0)
        rest = [t for t in want if t not in names]
        ind = mo.group(1)
        lines = [f"{ind}open import {owner}"]
        if rest:
            lines.append(f"{ind}open import {modname} using ({'; '.join(rest)})")
        return "\n".join(lines)

    hit = 0
    for p in (ROOT / AG / "Substrate").glob("**/*.agda"):
        try:
            o = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if modname not in o:
            continue
        s = pat.sub(rebind, o)
        if s != o:
            _snapshot_once(str(p))
            p.write_text(s, encoding="utf-8")
            hit += 1
    return hit


def _rebind_conduits(modname: str, conduits: Sequence[tuple[str, list[str] | None]]) -> None:
    """Stage 6b (P3): rebind the consumers of every `public` conduit the split destroyed."""
    if conduits:
        _say(f"\n-- rebinding {len(conduits)} destroyed conduit(s) at the owner --")
    for owner, names in conduits:
        if not names:
            _say(f"   ⚠ {modname} re-exported ALL of {owner}; consumers reaching it\n"
                 f"     through {modname} need binding at {owner} by hand "
                 f"(whole-surface conduit, no name list to match).")
            continue
        hit = _rebind_one(modname, owner, names)
        if hit:
            _say(f"   {owner}: {hit} consumer(s) rebound ({', '.join(names)})")


def _cycle_guard() -> None:
    """Stage 7: die on any import cycle a rewire introduced."""
    _say("\n-- import-cycle guard (tree-wide) --")
    if fix_stale_using.check_cycles():
        die("import cycle(s) introduced — remove the leaf→parent/self edges "
            "listed above (parent→leaf barrel edges are legitimate), then re-run:\n"
            "  python3 scratch/fix_stale_using.py --check-cycles")
    _say("✓ no import cycles.")


def _orphan_sweep() -> None:
    """Stage 8: remove the cores whose sources the split deleted."""
    _say("\n-- sweeping orphan .agdai cores --")
    removed = sweep_orphan_agdai()
    for r in removed:
        _say(f"   rm {r}")
    _say(f"✓ {len(removed)} orphan core(s) removed." if removed else "✓ no orphans.")


def _errors_and_caps(out: str) -> tuple[list[str], int]:
    """Return (the Agda error lines, the count of heap kills) in a build's output."""
    return [ln for ln in out.split("\n") if "error:" in ln], out.count("Error 251")


def _full_build(leaves: Sequence[str]) -> None:
    """Stage 10: build the tree; cure split-induced clashes; tolerate pre-existing cap debt."""
    _say("\n-- full build (make -C agda -j) --")
    rc, out = run(make_cmd())
    if rc == 0:
        _say("✓ full build green.")
        return
    agda_errs, caps = _errors_and_caps(out)
    note = ""
    if agda_errs:
        n_cured, note = cure_collisions(out, leaves=leaves)
        if n_cured:
            _say(f"✓ cured {n_cured} split-induced collision(s) by rename-at-source.")
            rc, out = run(make_cmd())
            agda_errs, caps = _errors_and_caps(out)
        if agda_errs:
            die(f"full build FAILED with {len(agda_errs)} Agda error(s) — "
                f"first: {agda_errs[0].strip()[:200]}" + (f"\n  {note}" if note else ""), out)
    if caps:
        _say(f"⚠ build exit {rc}: {caps} module(s) over the memory cap "
             f"(Error 251), 0 Agda errors.\n"
             f"  PRE-EXISTING cap debt, not this split — continuing. "
             f"(Splitting is the paydown for it.)")
    else:
        die(f"full build FAILED (exit {rc}) with no Agda error and no cap "
            f"kill — inspect the output.", out)


def _stale_using_sweep() -> None:
    """Stage 11: die on any stale `using` the per-module logs report."""
    _say("\n-- stale `using` sweep (per-module logs) --")
    stale = fix_stale_using.sites(str(Path(AG) / "_build"))
    if stale:
        for f, ln, mod, names in stale:
            _say(f"   {f}:{ln}  {mod}  -{len(names)} name(s)")
        die(f"{len(stale)} stale `using` site(s) — the split moved these names to "
            f"sibling leaves.\n"
            f"  These are a PIPELINE STAGE's work.  Repair and rebuild AS A PAIR — "
            f"the repair drops\n"
            f"  `public` conduits on the promise that the rebuild re-binds their "
            f"consumers:\n"
            f"    python3 scratch/fix_stale_using.py {AG}/_build --apply && "
            f"{' '.join(make_cmd())}\n"
            f"  Then re-run this pipeline to a fixpoint.")
    _say("✓ no stale `using` lists.")


GATE_CMD: dict[str, list[str]] = {
    "public ratchet": ["python3", "scripts/check_public_ratchet.py", "--quiet"],
    "carrier locality": ["python3", "scripts/check_carrier_locality.py", "--quiet"],
    "import-shape ratchet": ["python3", "scripts/check_import_shape.py", "--quiet"],
    "sumtype ratchet": ["python3", "scripts/check_sumtype_ratchet.py", "--quiet"],
    "build makefiles in sync": ["python3", "scripts/gen_build_makefiles.py", "--check"],
    "shape-node index current": ["python3", "scripts/sppf_node_index.py", "--check"],
    "decl-site shape tags": ["python3", "scripts/decl_shape_tag.py"],
    "def/proof separation": ["./scripts/check_def_proof_separation.sh", "--quiet"],
    "UP non-vacuity": ["./scripts/check_up_nonvacuity.sh", "--quiet"],
    "query cache in sync": ["python3", "jea/metalanguage/query_defs.py", "--check"],
    "apex gate": ["python3", "scripts/law_motif_apex.py", "--check"],
    "worklist tracker integrity": ["python3", "scripts/worklist.py", "--check"],
}


def _gate_battery() -> None:
    """Stage 12: run the pre-commit gates in measured fail-fast order; die on the first red."""
    _say("\n-- pre-commit gate battery (fail-fast order) --")
    rc, ordered = run(["python3", "scripts/gate_ledger.py", "--order"])
    ranked = [g for g in ordered.split("\n") if g in GATE_CMD] if rc == 0 else []
    ranked += [g for g in GATE_CMD if g not in ranked]
    for gate in ranked:
        t0 = time.time()
        grc, gout = run(GATE_CMD[gate])
        el = int(time.time() - t0)
        run(["python3", "scripts/gate_ledger.py", "--record", gate,
             "pass" if grc == 0 else "fail", str(el)])
        if grc != 0:
            die(f"gate FAILED — {gate}  ({el}s)\n"
                f"This split cannot be committed until it passes. The gate's own "
                f"output names the offending sites:", gout)
        _say(f"   ✓ {gate} ({el}s)")
    _say("✓ gate battery green — this split is committable.")


def _mb_of(argv: Sequence[str]) -> int:
    """Return the `--mb=N` lease, or the default."""
    for a in argv:
        if a.startswith("--mb="):
            return int(a.split("=", 1)[1])
    return DEFAULT_MB


def split_path(path: str, argv: Sequence[str]) -> int:
    """Run the twelve-stage split, dry by default; return the exit code."""
    apply = "--apply" in argv
    if not Path(path).exists():
        die(f"{path} does not exist")
    files, named = split_lemmas.split(path, apply=False)
    if len(files) <= 1:
        _say(f"{path}: already atomic ({len(named)} unit) — nothing to split.")
        return 0
    modname = module_of(path)
    _say(f"{path} ({modname}): {len(files)} leaf unit(s) planned:")
    for p in sorted(files):
        _say(f"   {p}")
    if not apply:
        _say("\nDry run only — pass --apply to execute.")
        return 0
    leaves, conduits = _split_apply(path)
    _prune_leaves(path, leaves)
    _isolate_leaves(leaves, _mb_of(argv))
    _regen_makefiles("")
    _say("\n-- rewiring importers --")
    _rewire(modname, apply=True, manifest=False)
    _sweep(modname, f"fix the above by hand (qualify or bare-import at the right leaf), "
                    f"then re-run:\n  python3 scratch/check_indented_imports.py {modname}\n"
                    f"before regenerating makefiles / building. Stopping here to avoid a "
                    f"slow failing build.")
    _prune_consumers(modname)
    _rebind_conduits(modname, conduits)
    _cycle_guard()
    _orphan_sweep()
    _regen_makefiles(" (post-rewire)")
    _full_build(leaves)
    _stale_using_sweep()
    _gate_battery()
    _say(f"\n{modname}: DONE — {len(leaves)} leaves, importers rewired, build green.")
    return 0


# ── the persisted census ────────────────────────────────────────────────────────


def _read_ledger() -> tuple[str, list[Row]]:
    """Return (stamp, rows) from the persisted census through `leaf_ledger`, the one reader.

    The origin's `--last` printed the stamp line with its `#stamp` keyword still attached
    (`stamp: stamp<TAB>3640:...`); the reader returns the VALUE, so that line now reads
    `stamp: 3640:...` - a display defect retired with the second spelling (W4 tick 58).
    """
    stamp, rows = leaf_ledger.read(LEDGER)
    return stamp or "", rows


def _write_ledger(stamp: str, rows: Sequence[tuple[str, str, str | None]]) -> None:
    """Persist the census under its stamp; a write failure is not a verdict."""
    leaf_ledger.write(LEDGER, stamp, rows)


def _need_ledger(hint: str) -> None:
    """Die with exit 2 when no census has been recorded."""
    if not LEDGER.exists():
        _say(f"no census recorded; run {hint}")
        sys.exit(2)


def _tally(rows: Sequence[tuple[str, str, str | None]]) -> tuple[dict[str, int], dict[str, int]]:
    """Return (verdict -> count, cited dependency -> count) over census rows."""
    tally: dict[str, int] = {}
    deps: dict[str, int] = {}
    for _p, v, c in rows:
        tally[v] = tally.get(v, 0) + 1
        if v == "dependency" and c:
            deps[c] = deps.get(c, 0) + 1
    return tally, deps


def _by_count(d: dict[str, int]) -> list[tuple[str, int]]:
    """Return the items of `d`, commonest first."""
    return sorted(d.items(), key=_neg_count)


def _neg_count(kv: tuple[str, int]) -> int:
    """Sort key: descending count."""
    return -kv[1]


def _operands(argv: Sequence[str]) -> list[str]:
    """Return every non-flag argument after the program name."""
    return [a for a in argv[1:] if not a.startswith("-")]


def _flag_value(argv: Sequence[str], flag: str) -> str | None:
    """Return the value of `--flag=value`, or None."""
    return next((a.split("=", 1)[1] for a in argv if a.startswith(flag + "=")), None)


# ── the modes ───────────────────────────────────────────────────────────────────


def mode_stale_why(_argv: Sequence[str]) -> int:
    """Print why each stale module is unmeasured, and which causes a rebuild can move."""
    rows = split_census.stale_why(AG)
    by: dict[str, int] = {}
    for _m, cause, _w in rows:
        by[cause] = by.get(cause, 0) + 1
    _say("-- why each STALE module is unmeasured --")
    for mod, cause, witness in rows:
        _say(f"  {cause:<17} {mod}\n                    ← {witness}")
    _say(f"\n{len(rows)} stale module(s): " + ", ".join(f"{n} {c}" for c, n in _by_count(by)))
    if by.get("unbuilt"):
        _say(f"   ⚑ {by['unbuilt']} are genuinely UNBUILT — `make -C agda -j` "
             f"refreshes those.")
    if by.get("blocked-upstream"):
        _say(f"   ⚑ {by['blocked-upstream']} are BLOCKED behind a failed "
             f"import — no rebuild moves them; fix the cited root.")
    if by.get("no-core"):
        _say(f"   ⚑ {by['no-core']} have a FRESH log and NO .agdai — the "
             f"freshness test and make's\n     up-to-date test disagree "
             f"about these; that is a defect, not a gap.")
    return 0


def mode_last(_argv: Sequence[str]) -> int:
    """Re-read the persisted census without re-running the compiles."""
    if not LEDGER.exists():
        _say("no leaf-verify census recorded; run --verify --leaves")
        return 2
    stamp, rows = _read_ledger()
    tally, deps = _tally(rows)
    for v, n in _by_count(tally):
        _say(f"   {v:<14} {n:>5}")
    total = sum(tally.values())
    if total != len(rows):
        _say(f"   ⚑ verdicts sum to {total} but the census holds {len(rows)} "
             f"rows — {len(rows) - total} unreported")
    for c, n in _by_count(deps)[:TOP]:
        _say(f"   blocked-behind {n:>4}  {c}")
    _say(f"{len(rows)} leaf/leaves in the last census")
    if stamp:
        _say(f"   stamp: {stamp}")
    now = tree_stamp()
    if stamp and str(now) not in stamp:
        _say(f"   ⚑ THE TREE HAS MOVED SINCE — now {now}.  These verdicts "
             f"describe an EARLIER tree;\n     re-run `--verify --leaves` "
             f"before treating any figure here as current.")
    return 0


def _leverage_seeds(argv: Sequence[str]) -> tuple[list[str], str]:
    """Return (seed sources, label) for `--leverage` from the tool that owns each population."""
    if "--applied-open" in argv:
        from agda_lex import agda_files  # noqa: PLC0415 - reached only on this arm
        srcs = [str(Path(p).relative_to(ROOT)) for p in agda_files(str(ROOT / AG))
                if split_lemmas.blockers(p)]
        return srcs, "R11 / the applied-open class"
    if "--failed" in argv:
        _need_ledger("--verify --from-build")
        _stamp, rows = _read_ledger()
        return [p for p, v, _c in rows if v == "build-failed"], "A4 / every build-failed module"
    return _operands(argv), "the given paths"


def mode_leverage(argv: Sequence[str]) -> int:
    """Print how many modules a set of sources transitively blocks, and the cost to work them."""
    srcs, label = _leverage_seeds(argv)
    if not srcs:
        _say("usage: --leverage [--applied-open|--failed|<paths…>]")
        return 2
    srcs = [s.removeprefix(AG + "/") for s in srcs]
    n_cone, n_seeds, top = leverage(srcs)
    _say(label)
    _say(f"  COST     {n_seeds:>5} file(s) to work")
    _say(f"  LEVERAGE {n_cone:>5} module(s) transitively blocked by them")
    if n_seeds:
        _say(f"  ratio    {n_cone / n_seeds:>5.1f} freed per file worked")
    for n, s in top:
        _say(f"     {n:>5} blocked by {s}")
    return 0


def mode_unblock(argv: Sequence[str]) -> int:
    """Chase each file's blocker chain to a fixpoint; report the chain, not a boolean."""
    paths = _operands(argv)
    if not paths:
        _say("usage: split_pipeline.py --unblock <file.agda> [--apply]")
        return 2
    apply = "--apply" in argv
    rc = 0
    for p in paths:
        _say(f"-- unblocking {p} --")
        verdict, chain = unblock(p, apply=apply)
        for i, root in enumerate(chain, 1):
            _say(f"   {i}. repaired {root}")
        _say(f"   verdict: {verdict}  ({len(chain)} link(s) repaired)")
        if verdict not in ("clean", "would-repair"):
            rc = 1
    return rc


def _blockers_worklist() -> tuple[list[str], dict[str, int]]:
    """Return the diagnose population from the persisted census, ranked by blocked-cone size."""
    _need_ledger("--verify --from-build")
    _stamp, rows = _read_ledger()
    verdict = {p: v for p, v, _c in rows}
    cited: dict[str, int] = {}
    for _p, v, c in rows:
        if v == "dependency" and c:
            cited[c] = cited.get(c, 0) + 1
    bf = [p for p, v in verdict.items() if v == "build-failed"]
    if bf:
        cone = {p: len(_blast_radius({p})) for p in bf}
        _say(f"-- {len(bf)} build-failed, ranked by BLOCKED-CONE size --")
        return [p for _n, p in sorted((-cone[p], p) for p in bf)], cone
    return [p for p, _n in _by_count(cited)], cited


def _trace_freshness(tr: list[str], fw: dict[str, object]) -> None:
    """Append the freshness step to a trace."""
    lm, nd = fw.get("log_mtime"), fw.get("newest_dep_mtime")
    if fw.get("newest_dep") and isinstance(lm, float) and isinstance(nd, float):
        tr.append(f"log vs deps: {lm - nd:+.0f}s over {fw['n_deps']} "
                  f"module(s); newest is {fw['newest_dep']}")
    else:
        tr.append(f"freshness: {fw.get('why', '?')}")


Diagnosis = tuple[tuple[str, str, str | None], str, list[str]]


def _diagnose_one(p: str, *, want_trace: bool) -> Diagnosis:
    """Classify one file from its fresh build log, else from a compile: (verdict, via, trace)."""
    tr: list[str] = []
    rel = str(Path(p).relative_to(ROOT)) if p.startswith("/") else p
    fresh, lg, fw = log_is_fresh(rel)
    if want_trace:
        _trace_freshness(tr, fw)
    if lg and fresh:
        txt = Path(lg).read_text(encoding="utf-8", errors="replace")
        shown = Path(lg).relative_to(ROOT) if Path(lg).is_absolute() else lg
        return _classify(p, txt, trace=tr if want_trace else None), f"build log {shown} (fresh)", tr
    src = ("fresh compile (log STALE — describes an earlier tree)" if lg
           else "fresh compile (no build log)")
    return diagnose(p, trace=tr if want_trace else None), src, tr


def mode_diagnose(argv: Sequence[str]) -> int:
    """Classify a population of failures from the build's own logs, with remedies."""
    paths = _operands(argv)
    counts: dict[str, int] = {}
    if "--blockers" in argv:
        paths, counts = _blockers_worklist()
    want_trace = "--trace" in argv
    want_ready = "--ready" in argv
    for p in paths:
        (kind, detail, remedy), src, tr = _diagnose_one(p, want_trace=want_trace)
        n = counts.get(p)
        tag = f"[{n} blocked] " if n else ""
        shown = str(Path(p).relative_to(ROOT)) if p.startswith("/") else p
        _say(f"{tag}{kind:<16} {shown}   {detail}")
        if remedy:
            _say(f"      remedy: {remedy}")
            if want_ready and kind == FILE_NOT_FOUND:
                for line in ready_verdict(detail.strip()):
                    _say(f"      {line}")
        if want_trace:
            _say(f"      via {src}")
            for step in tr:
                _say(f"      · {step}")
    return 0


def mode_why(argv: Sequence[str]) -> int:
    """Print the compiler's own output for each file."""
    for a in _operands(argv):
        rc, txt = why(a)
        _say(f"-- {a}  (exit {rc}) --")
        _say(txt.strip() or "(no output — compiles clean)")
    return 0


def _fold_build_log(rows: list[Row], build_log: str) -> list[Row]:
    """Fold make's own failed targets into the census and split `stale` into gap vs blocked."""
    failed: set[str] = set()
    pat = re.compile(r"\*\*\* \[[^\]]*: _build/[^/]+/agda/(\S+)\.agdai\] Error")
    with Path(build_log).open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                failed.add(str(m.group(1)) + ".agda")
    seen = {r[0] for r in rows}
    rows = [(p, ("build-failed" if p in failed else v), c) for p, v, c in rows]
    rows += [(p, "build-failed", "") for p in sorted(failed - seen)]
    _say(f"   (folded in {len(failed)} failed target(s) from {Path(build_log).name})")
    blocked = _blast_radius(failed)
    return [(p, ("blocked" if (v == "stale" and p in blocked) else v), c) for p, v, c in rows]


def _report_from_build(rows: list[Row]) -> None:
    """Print every verdict present, the top cited dependencies, and the two footers."""
    tally, deps = _tally(rows)
    _say("   ".join(f"{v}={n}" for v, n in _by_count(tally)))
    for c, n in _by_count(deps)[:TOP]:
        _say(f"   blocked-behind {n:>4}  {c}")
    _say(f"{len(rows)} module(s) read from build logs")
    if tally.get("blocked"):
        bf = tally.get("build-failed", 0)
        _say(f"   ⚑ {tally['blocked']} module(s) are BLOCKED — `make -k` "
             f"never attempted them because a dependency failed.\n"
             f"     That is a FINDING, not a gap: they are the blast "
             f"radius of the {bf} build-failed\n"
             f"     module(s) (~{tally['blocked'] / max(bf, 1):.1f} blocked "
             f"per failure).  Fix failures in DEPENDENCY ORDER.")
    if tally.get("stale"):
        _say(f"   ⚠ {tally['stale']} module(s) are STALE — their log "
             f"predates the module or one of its transitive imports,\n"
             f"     and nothing upstream failed.  They are UNMEASURED, "
             f"not passing; `make -C agda -j` refreshes them.")


def _from_build(argv: Sequence[str]) -> int:
    """Roll the build's per-module logs up into verdicts and persist them."""
    rows = [(p, v, c or "") for p, v, c in census_from_build(AG)]
    bl = _flag_value(argv, "--build-log")
    if bl and Path(bl).exists():
        rows = _fold_build_log(rows, bl)
    _report_from_build(rows)
    _write_ledger(tree_stamp(AG), rows)
    return 0


def _verify_compile(argv: Sequence[str]) -> int:
    """Isolate-check a population and report the verdicts; persist only a full-population run."""
    paths = _operands(argv)
    full = "--leaves" in argv
    stamp_before = tree_stamp(AG) if full else None
    if full:
        paths = leaves()
        _say(f"-- verifying {len(paths)} split-emitted leaf/leaves --")
    jobs_s = _flag_value(argv, "--jobs")
    jobs = int(jobs_s) if jobs_s else None
    t0 = time.monotonic()
    rows = verify(paths, jobs=jobs)
    el = time.monotonic() - t0
    rate = len(rows) / max(el, 1e-9)
    _say(f"-- {len(rows)} file(s) in {el:.1f}s (jobs={jobs or 'auto'}, {rate:.1f}/s) --")
    if full:
        after = tree_stamp(AG)
        if stamp_before and after != stamp_before:
            _say(f"   ⚠ THE TREE CHANGED DURING THIS CENSUS ({stamp_before} → {after}).")
            _say("     Rows before and after the edit measure different trees, "
                 "so this run is\n     NOT a snapshot of either. "
                 "Ledger left unchanged — re-run with no concurrent edits.")
        else:
            _write_ledger(after, rows)
    elif LEDGER.exists():
        _say("   (scoped run — the full-population census is left intact)")
    for p, verdict, cited in rows:
        _say(f"{verdict:<10} {p}" + (f"   cites {cited}" if cited else ""))
    tally, deps = _tally(rows)
    n_bad = sum(1 for _p, v, _c in rows if v != "clean")
    _say("   ".join(f"{v}={tally.get(v, 0)}" for v in ("clean", "own", "dependency")))
    for c, n in _by_count(deps)[:TOP]:
        _say(f"   blocked-behind {n:>4}  {c}")
    _say(f"{len(rows)} checked; {len(rows) - n_bad} clean, {n_bad} failing")
    return 1 if n_bad else 0


def mode_verify(argv: Sequence[str]) -> int:
    """Dispatch: `--census` builds then reads; `--from-build` reads; bare `--verify` compiles."""
    argv = list(argv)
    if "--census" in argv:
        jobs_s = _flag_value(argv, "--jobs")
        log = run_census(AG, int(jobs_s) if jobs_s else None)
        if isinstance(log, int):
            return log
        argv += ["--from-build", f"--build-log={log}"]
    if "--from-build" in argv:
        return _from_build(argv)
    return _verify_compile(argv)


def mode_retire(argv: Sequence[str]) -> int:
    """Retire a consumed barrel."""
    return retire(argv[1], apply="--apply" in argv)


def mode_rewire_only(argv: Sequence[str]) -> int:
    """Rewire, sweep and prune the importers of an already-split parent."""
    return rewire_only(argv[1], "--apply" in argv)


def mode_split(argv: Sequence[str]) -> int:
    """Split the given monolith - the default mode."""
    return split_path(argv[1], argv)


# Each mode: its flag (None for the default), a one-line gloss, and its handler.
# The order is the dispatch order; the first flag present wins.
_MODES: tuple[tuple[str | None, str, Callable[[Sequence[str]], int]], ...] = (
    ("--last", "re-read the persisted census without re-running the compiles", mode_last),
    ("--leverage", "how many modules a set blocks: --applied-open | --failed | <paths>",
     mode_leverage),
    ("--unblock", "chase each file's blocker chain to a fixpoint [--apply]", mode_unblock),
    ("--diagnose", "classify failures from the build's logs [--blockers] [--trace] [--ready]",
     mode_diagnose),
    ("--why", "the compiler's own output for each file", mode_why),
    ("--census", "BUILD then READ, one command [--jobs=N]", mode_verify),
    ("--verify", "isolate-check a population; --from-build reads the logs; --leaves names them",
     mode_verify),
    ("--stale-why", "why each unmeasured module is unmeasured", mode_stale_why),
    ("--retire", "delete a consumed barrel once it is dead [--apply]", mode_retire),
    ("--rewire-only", "stages 5-6b for an already-split parent [--apply]", mode_rewire_only),
    (None, "split <file.agda> into one-lemma leaves and run the chain [--apply]", mode_split),
)

# The modes that read only and need no stated intent; every other mode states one at entry.
_READ_ONLY = frozenset({"--last", "--leverage", "--diagnose", "--why", "--verify", "--census",
                        "--stale-why"})


def usage() -> str:
    """Render the mode roster."""
    lines = ["usage: split_pipeline.py <file.agda> [--apply] [--mb=N]",
             "       split_pipeline.py <flag> [operands...]", ""]
    lines += [f"  {flag or '(default)':<14} {gloss}" for flag, gloss, _h in _MODES]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    """Dispatch the first mode flag present; the default is the split."""
    if len(argv) < 2:  # noqa: PLR2004 - the program name plus one operand
        _say(usage())
        return 1
    flag = next((f for f, _g, _h in _MODES if f and f in argv), None)
    handler = next(h for f, _g, h in _MODES if f == flag)
    if flag not in _READ_ONLY:
        edit_snapshot.require_at_entry("split_pipeline", argv=list(argv), paths=[argv[1]])
    return handler(argv)


def _selftest() -> int:
    """Run the package suites this shim composes, then the shim's own roster cases."""
    import subprocess  # noqa: PLC0415 - the suite's only use

    suites = ("agda_blame", "rewire_ready", "agda_build_cmd", "agda_rename_plan", "barrel_retire")
    failed: list[str] = []
    for s in suites:
        p = subprocess.run([sys.executable, "-m", f"substrate.{s}_selftest"],  # noqa: S603 - a fixed roster
                           capture_output=True, text=True, check=False, cwd=ROOT)
        _say(p.stdout.strip().splitlines()[-1] if p.stdout.strip() else f"{s}: no output")
        if p.returncode != 0:
            failed.append(s)
    cases = [
        ("every declared mode has a handler", all(callable(h) for _f, _g, h in _MODES)),
        ("the usage names every flag", all((f or "(default)") in usage() for f, _g, _h in _MODES)),
        ("read-only modes are declared modes", {f for f, _g, _h in _MODES} >= _READ_ONLY),
        ("the docstring's MODES block names every roster flag",
         all(f in (__doc__ or "") for f, _g, _h in _MODES if f)),
        ("--census dispatches with --verify's handler",
         next(h for f, _g, h in _MODES if f == "--census") is mode_verify),
        ("module_of strips the agda prefix",
         module_of("agda/Substrate/A/B.agda") == "Substrate.A.B"),
        ("make_cmd targets the agda dir", make_cmd()[:3] == ["make", "-C", AG]),
        ("the blame re-export is the package's", blame("x.agda", "") == ("clean", None)),
    ]
    for name, ok in cases:
        if not ok:
            failed.append(name)
            _say(f"  FAIL  {name}")
    total = len(suites) + len(cases)
    _say(f"split_pipeline_selftest: {total - len(failed)}/{total}")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main(sys.argv))
