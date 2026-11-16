# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_write_handlers` — driven through the CLI, against real files.

⚑⚑⚑ THE CASE THIS WHOLE DRAIN EXISTS FOR IS HERE: an `item:` witness that RESOLVES is ACCEPTED. The
origin text-scanned a file the witnesses had vacated, so `--add … check=item:T27` refused while
`items.py T27` exits 0 and reports the item closed — a guard refusing a key its own resolver
answers. That is asserted against the LIVE witness module, not a fixture, because a fixture would
only prove the new predicate agrees with itself.

⚑⚑ THE WRITES GO TO A TEMPORARY BIB, AND THE BENCH IS FAKED. A real snapshot guard reads the
process argv and would refuse a suite driving a write — which is how the origin's own suite died at
its first `--add` case, taking twenty-four cases with it while still printing a count that read as
full coverage.

⚑ THE CASES ARE SPLIT BY VERB, AND THE PER-FILE GATE ASKED FOR THAT. One `_cases` carrying every
verb hit the statement limit, which is the same signal the module itself got at `C901`: the unit is
a verb, not a suite. Each group can now be read on its own.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from substrate import bib_cli, bib_edit, bib_write, bib_write_handlers, corpus

# ⚑ THE GRAMMAR MIRRORS THE ORIGIN'S `_ENTRY`/`_FIELD` so a locate cannot disagree with a read.
_GRAMMAR = bib_edit.Grammar(
    entry_re=re.compile(r"(@\w+)\{([^,]+),(.*?)\n\}", re.DOTALL),
    field_re=re.compile(r"(\w[\w-]*)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"),
)

_SEED = """\
% a comment that must survive every write
@misc{A,
  section  = {s},
  claim    = {alpha},
  check    = {item:A}
}
"""

_COMMENT = "% a comment that must survive"


def _read(path: Path) -> dict[str, dict[str, str]]:
    """Parse a bib with the same grammar the editor locates with."""
    text = bib_edit.mask_comments(path.read_text(encoding="utf-8")) if path.exists() else ""
    out: dict[str, dict[str, str]] = {}
    for entry in _GRAMMAR.entry_re.finditer(text):
        out[str(entry.group(2))] = {
            str(f.group(1)): str(f.group(2))
            for f in _GRAMMAR.field_re.finditer(str(entry.group(3)))
        }
    return out


def _context(log: list[str]) -> bib_write_handlers.Context:
    """Return a context whose bench records rather than snapshots."""

    def snapshot(what: str, targets: list[Path]) -> None:
        del targets
        log.append(f"snapshot:{what}")

    def roundtrip(target: Path) -> list[tuple[str, str, str]]:
        del target
        return []

    def read_back(target: Path) -> dict[str, object]:
        return dict.fromkeys(_read(target), "")

    return bib_write_handlers.Context(
        read=_read,
        bench=bib_write.Bench(snapshot=snapshot, roundtrip=roundtrip, read_back=read_back),
        grammar=_GRAMMAR,
    )


class _Bench:
    """One suite run: a temp dir, a handler table, and the snapshot log."""

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.log: list[str] = []
        self.handlers = bib_write_handlers.bind(_context(self.log))
        self.n = 0

    def fresh(self) -> Path:
        """Return a new seeded bib."""
        self.n += 1
        target = self.tmp / f"w{self.n}.bib"
        target.write_text(_SEED, encoding="utf-8")
        return target

    def run(self, *argv: str) -> tuple[tuple[str, ...], int]:
        """Drive the CLI, as a caller would."""
        return bib_cli.run(list(argv), self.handlers)


def _add_cases(bench: _Bench, check: object) -> list[tuple[str, bool]]:
    """Return the `--add` cases: the dry run, the write, and the validator's refusals."""
    del check
    out: list[tuple[str, bool]] = []

    # ⚑ THE DRY RUN IS THE DEFAULT PATH and the one a careless caller takes, so it goes first.
    target = bench.fresh()
    lines, code = bench.run("--add", "K", "claim=c", "check=traces:x#y", "--bib", str(target))
    out.append(("a dry-run add succeeds", code == 0))
    out.append(("and writes nothing", target.read_text(encoding="utf-8") == _SEED))
    out.append(
        ("and says how to make it write", any(bib_write.APPLY_FLAG in line for line in lines))
    )

    target = bench.fresh()
    _lines, code = bench.run(
        "--add", "K", "claim=c", "check=traces:x#y", "--bib", str(target), "--apply"
    )
    written = target.read_text(encoding="utf-8")
    out.append(("an applied add succeeds", code == 0))
    out.append(("and the entry lands", "@misc{K," in written))
    out.append(("and the leading comment survives", written.startswith(_COMMENT)))
    out.append(
        ("and a snapshot was armed", any(entry.startswith("snapshot:") for entry in bench.log))
    )

    target = bench.fresh()
    _lines, code = bench.run("--add", "A", "claim=c", "check=traces:x#y", "--bib", str(target))
    out.append(("a duplicate key refuses", code == bib_cli.REFUSED))

    lines, code = bench.run(
        "--add", "K", "claim=c", "check=traces:x#y", "from=GONE", "--bib", str(target)
    )
    out.append(("a dangling edge refuses", code == bib_cli.REFUSED))
    out.append(("and names --corpus as the remedy", any("--corpus" in line for line in lines)))

    _lines, code = bench.run("--add", "K", "claim=c", "--bib", str(target))
    out.append(("an entry with no check refuses", code == bib_cli.REFUSED))
    return out


def _witness_cases(bench: _Bench) -> list[tuple[str, bool]]:
    """Return the witness-probe cases, run against the LIVE witness module.

    ⚑⚑⚑ THIS IS THE DEFECT Ⓑ24 EXISTS FOR. The origin refuses `item:T27` while `items.py T27`
    exits 0 and reports the item CLOSED — a guard refusing a key its own resolver answers. A
    fixture module would only prove the new predicate agrees with itself, so this asks the real one.
    """
    items = corpus.ROOT / "catalog" / "library" / "items.py"
    if not items.exists():
        return [("the live witness module is present to probe", False)]

    target = bench.fresh()
    _lines, ok_code = bench.run("--add", "K", "claim=c", "check=item:T27", "--bib", str(target))
    _lines, no_code = bench.run(
        "--add", "K2", "claim=c", "check=item:NoSuchWitness", "--bib", str(target)
    )
    return [
        ("an item witness the resolver ANSWERS is accepted", ok_code == 0),
        ("an item witness nothing resolves is refused", no_code == bib_cli.REFUSED),
    ]


def _set_cases(bench: _Bench) -> list[tuple[str, bool]]:
    """Return the `--set` cases: the edit, the joined value, and the refusals."""
    out: list[tuple[str, bool]] = []

    target = bench.fresh()
    _lines, code = bench.run("--set", "A", "claim", "a new claim", "--bib", str(target), "--apply")
    edited = target.read_text(encoding="utf-8")
    out.append(("an applied set succeeds", code == 0))
    out.append(("and the value changes", "a new claim" in edited and "alpha" not in edited))
    out.append(("and the comment survives", edited.startswith(_COMMENT)))

    # ⚑ THE VALUE MAY CONTAIN SPACES — taking only the third operand truncates it.
    target = bench.fresh()
    bench.run("--set", "A", "claim", "two", "words", "here", "--bib", str(target), "--apply")
    out.append(
        (
            "a multi-word value is joined, not truncated",
            "two words here" in target.read_text(encoding="utf-8"),
        )
    )

    _lines, code = bench.run("--set", "A", "--bib", str(target))
    out.append(("a set with too few operands refuses", code == bib_cli.REFUSED))

    _lines, code = bench.run("--set", "NOSUCH", "claim", "x", "--bib", str(target))
    out.append(("a set on an unknown key refuses", code == bib_cli.REFUSED))
    return out


def _addfield_cases(bench: _Bench) -> list[tuple[str, bool]]:
    """Return the `--addfield` cases, including the partition against the other two verbs."""
    out: list[tuple[str, bool]] = []

    target = bench.fresh()
    _lines, code = bench.run(
        "--addfield", "A", "note", "a widening note", "--bib", str(target), "--apply"
    )
    widened = target.read_text(encoding="utf-8")
    out.append(("an applied addfield succeeds", code == 0))
    out.append(("and the new field lands", "note" in widened and "a widening note" in widened))
    out.append(("and the comment survives", widened.startswith(_COMMENT)))
    out.append(
        (
            "and the existing fields are intact",
            "claim    = {alpha}" in widened and "check    = {item:A}" in widened,
        )
    )

    # ⚑⚑ THE THREE VERBS PARTITION, AND BOTH WRONG-VERB CASES ARE ASSERTED. A field that EXISTS is
    # `--set`'s job; an entry that does not exist is `--add`'s. An upsert would make "did I mean to
    # create this?" unanswerable at the call site.
    lines, code = bench.run("--addfield", "A", "claim", "x", "--bib", str(target))
    out.append(("adding a field that exists refuses", code == bib_cli.REFUSED))
    out.append(("and points at --set", any("--set" in line for line in lines)))

    lines, code = bench.run("--addfield", "NOSUCH", "note", "x", "--bib", str(target))
    out.append(("adding a field to an unknown entry refuses", code == bib_cli.REFUSED))
    out.append(("and points at --add", any("--add" in line for line in lines)))

    _lines, code = bench.run("--addfield", "A", "--bib", str(target))
    out.append(("an addfield with too few operands refuses", code == bib_cli.REFUSED))

    # ⚑ THE VALUE MAY CONTAIN SPACES here too — the operand shape matches `--set` deliberately, so
    # a caller who learned one verb has learned all three.
    target = bench.fresh()
    bench.run("--addfield", "A", "note", "two", "words", "here", "--bib", str(target), "--apply")
    out.append(
        (
            "a multi-word value is joined on addfield too",
            "two words here" in target.read_text(encoding="utf-8"),
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    with tempfile.TemporaryDirectory() as tmp:
        bench = _Bench(Path(tmp))
        cases = (
            _add_cases(bench, None)
            + _witness_cases(bench)
            + _set_cases(bench)
            + _addfield_cases(bench)
        )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-write-handlers selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
