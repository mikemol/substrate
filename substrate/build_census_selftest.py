# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for the build census: `build_census_facts`, `_render` and `_skill`.

⚑ EVERY DERIVATION IS A CASE, because each reaches into another module's surface and an attribute
that quietly moves would turn this census into a confident ZERO. A count of 0 renders exactly as
legitimately as a count of 3514; only a case can tell them apart. This surface has ALREADY produced
a false zero of exactly that kind: the tool mode census reported buildtime as "0 undocumented"
while `--mem` dispatched, invisible because the scan missed a tuple-form flag.

⚑ THE REAL-TREE CASES ARE PORTED FROM THE ORIGIN (20 of them), and the parameterisation earns its
keep with FIXTURE cases the origin could not write: it resolved the tree from its own `__file__`,
so a hook or a membudget script that differs from the real one could not be censused at all.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import build_census_facts as facts
from substrate import build_census_render as render
from substrate import build_census_skill as skill
from substrate import build_settings

if TYPE_CHECKING:
    from collections.abc import Callable

# The thresholds the origin's cases asserted, named once.
_MIN_DEPTH = 2
_MIN_GATES = 15
_MIN_CHEAP_GATES = 20
_PHASES_HOLDING_GATES = 2
_TIMES_COLUMNS = 3
_PROFILE_COLUMNS = 7

_FIXTURE_HOOK = """\
run "alpha gate" python3 a.py
run "beta gate" python3 b.py
make -C "$ROOT/agda" -j
# ⟡gqs-precommit-reorder
run "gamma gate" python3 c.py
"""

_FIXTURE_MEMBUDGET = """\
def="${AGDA_MB_DEFAULT:-192}" cap="${AGDA_MB_MAX:-384}"
  run) echo run ;;
  status) echo status ;;
"""


class _Results:
    """Collect `(label, passed)` pairs."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, bool]] = []

    def check(self, label: str, got: object, want: object) -> None:
        """Record whether `got` equals `want`."""
        self.rows.append((label, got == want))

    def holds(self, label: str, got: object) -> None:
        """Record whether `got` is truthy."""
        self.rows.append((label, bool(got)))


def _dag_cases(out: _Results, scripts: Path) -> None:
    """Check that the DAG yields real figures, not a degenerate parse."""
    dag = facts.dag_census(scripts)
    out.holds("the DAG yields modules", dag["modules"] > 0)
    out.holds("the DAG yields edges", dag["edges"] > 0)
    out.holds("the DAG has positive depth", dag["depth"] > 0)
    # ⚑ Depth must be a REAL critical path, not a degenerate 1 from a dropped-edge parse.
    out.holds("depth is a genuine chain, not a flat layer", dag["depth"] > _MIN_DEPTH)
    out.holds(
        "MEM_CAP is read from the generator, not typed here",
        re.match(r"^\d+m$", dag["mem_cap"]),
    )


def _membudget_cases(out: _Results, client: Path) -> None:
    """Check that the lease defaults and the roster parse out of the real client."""
    mb = facts.membudget_census(client)
    out.holds("the membudget lease default parses", mb["default_mb"] > 0)
    out.holds("the membudget ceiling parses", mb["max_mb"] > 0)
    out.holds("membudget declares subcommands", len(mb["commands"]) > 0)


def _gate_cases(out: _Results, root: Path) -> None:
    """Check that the declared gates partition into the phases that HOLD gates."""
    gates = facts.gate_census(root)
    out.holds("the hook declares gates", gates["count"] > 0)
    # ⚑ THE POPULATION IS THE POINT: the observed ledger holds ~13. If this ever drops to that
    # neighbourhood the parse has silently narrowed to what the ledger happens to carry.
    out.holds("the declared gate count exceeds the observed ledger's", gates["count"] > _MIN_GATES)
    # ⚑ THE PHASES MUST ACTUALLY SPLIT, and Phase B holds NO `run` gate: the full build is a bare
    # `make -C "$ROOT/agda" -j`, a phase the gates are partitioned BY, not one that CONTAINS any.
    # The first assertion wanted THREE populated phases, which is a false NON-zero.
    out.check(
        "gates partition into the two phases that HOLD gates",
        len(gates["phases"]),
        _PHASES_HOLDING_GATES,
    )
    in_c = [n for n, p in gates["gates"] if p.startswith("Phase C")]
    out.holds(
        "the cap ratchet lands in Phase C (it reads what the build produced)",
        any("cap ratchet" in n for n in in_c),
    )
    out.holds("Set₁ ratchet is also post-build", any("Set₁" in n for n in in_c))
    in_a = [n for n, p in gates["gates"] if p.startswith("Phase A")]
    out.holds("the cheap gates run before the build", len(in_a) > _MIN_CHEAP_GATES)


def _ledger_cases(out: _Results, scripts: Path, root: Path) -> None:
    """Check that the ledger schemas name their columns and every named tool exists."""
    led = facts.ledger_census(scripts)
    out.check("the times ledger names its columns", len(led["times_cols"]), _TIMES_COLUMNS)
    out.check("the profile ledger names its columns", len(led["profile_cols"]), _PROFILE_COLUMNS)
    missing = [rel for rel, _ in facts.readers_census() if not render.exists(root, rel)]
    out.check("every tool the census names exists", missing, [])


def _splice_cases(out: _Results, root: Path, scripts: Path) -> None:
    """Check that the blocks round-trip through their markers."""
    try:
        src = skill.read_skill(root)
        body = render.render_block(root, scripts)
        once = skill.splice(src, body)
        out.check("splice is idempotent", skill.splice(once, body), once)
        out.check(
            "the block round-trips through its markers",
            skill.current_body(once).strip(),
            body.strip(),
        )
        obs = render.render_observations(root, scripts)
        spliced = skill.splice(src, obs, skill.OBS_BEGIN, skill.OBS_END)
        out.check(
            "the observations block round-trips too",
            skill.current_body(spliced, skill.OBS_BEGIN, skill.OBS_END).strip(),
            obs.strip(),
        )
    except skill.BlockError as exc:
        out.check("the skill carries exactly one marker pair of each kind", str(exc), "")


def _refusal_text(action: Callable[[], object]) -> str:
    """Return the message of the refusal raised by `action`, or `""` when it did not refuse."""
    try:
        action()
    except (RuntimeError, skill.BlockError) as exc:
        return str(exc)
    return ""


def _fixture_cases(out: _Results) -> None:
    """Check that the readers answer for a tree that is NOT the real one, and refuse when odd."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        hook = root / ".githooks" / "pre-commit"
        hook.parent.mkdir()
        hook.write_text(_FIXTURE_HOOK, encoding="utf-8")
        out.check(
            "a fixture hook yields its gates in order, each with its phase",
            facts.gate_census(root)["gates"],
            [
                ("alpha gate", facts.PHASE_A),
                ("beta gate", facts.PHASE_A),
                ("gamma gate", "Phase C — core-reading gates (AFTER the build)"),
            ],
        )
        hook.write_text('run "x" y\n', encoding="utf-8")
        out.holds(
            "a hook without the phase anchors REFUSES instead of flattening to one phase",
            _refusal_text(lambda: facts.gate_census(root)).startswith("build_census: phase anchor"),
        )
        client = root / "membudget"
        client.write_text(_FIXTURE_MEMBUDGET, encoding="utf-8")
        mb = facts.membudget_census(client)
        out.check(
            "a fixture membudget parses its defaults and roster",
            (mb["default_mb"], mb["max_mb"], mb["commands"]),
            (192, 384, ["run", "status"]),
        )
        client.write_text("nothing here\n", encoding="utf-8")
        out.holds(
            "a respelled membudget assignment REFUSES instead of defaulting",
            _refusal_text(lambda: facts.membudget_census(client)).startswith(
                "build_census: could not find the AGDA_MB_DEFAULT"
            ),
        )
        out.holds(
            "a missing host skill is a BlockError, not a traceback",
            _refusal_text(lambda: skill.read_skill(root)).endswith("will not create the file."),
        )


def _marker_cases(out: _Results) -> None:
    """Check that missing, duplicated and inverted markers each REFUSE with their own reason."""
    b, e = skill.BEGIN, skill.END
    out.holds(
        "an absent marker pair refuses",
        _refusal_text(lambda: skill.span("no markers", b, e)).startswith("no `"),
    )
    out.holds(
        "a duplicated marker refuses",
        "exactly one of each" in _refusal_text(lambda: skill.span(f"{b}{e}{b}", b, e)),
    )
    out.holds(
        "inverted markers refuse",
        "inverted" in _refusal_text(lambda: skill.span(f"{e} x {b}", b, e)),
    )
    out.check(
        "a splice replaces only the body between the markers",
        skill.splice(f"top\n{b}\nold\n{e}\nbottom", "new"),
        f"top\n{b}\nnew\n{e}\nbottom",
    )


def cases(root: Path, scripts: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, against the tree at `root`."""
    out = _Results()
    _dag_cases(out, scripts)
    _membudget_cases(out, build_settings.MEMBUDGET)
    _gate_cases(out, root)
    _ledger_cases(out, scripts, root)
    _splice_cases(out, root, scripts)
    _fixture_cases(out)
    _marker_cases(out)
    return out.rows


def selftest(root: Path, scripts: Path) -> bool:
    """Run every case, reporting failures by name."""
    rows = cases(root, scripts)
    ok = sum(1 for _, passed in rows if passed)
    for label, passed in rows:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-census selftest: {ok}/{len(rows)}\n")
    return ok == len(rows)


def main() -> int:
    """Run the suite against the tree this file sits in; the tree is resolved here, at the entry."""
    root = Path(__file__).resolve().parent.parent
    return 0 if selftest(root, root / "scripts") else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main() if ("--selftest" in sys.argv or len(sys.argv) == 1) else 1)
