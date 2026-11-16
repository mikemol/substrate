# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_write` — the protocol's arms, and the drift it removes.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT EVERY VERB GETS THE READ-BACK ARM. In the origin that arm is
`--add`'s alone, and it exists because `--set` failed the way it catches — a mis-sliced write that
parsed cleanly and held the wrong content. So the verb that motivated the check is one of the two
that never received it. Here it is a field on the edit, and the case asserts it fires for any verb
that names a key.

⚑⚑ THE ORDER IS ASSERTED, NOT ASSUMED. A snapshot armed after the write recovers nothing, and a
verification run before it checks the old bytes. Both are silent when wrong — the file is written
either way — so each is pinned by a case that records what happened and when.

⚑ THE BENCH IS FAKED, AND THAT IS THE POINT OF SPLITTING IT OUT. A test swaps how writes are
snapshotted and verified wholesale, so the protocol can be driven through its failure arms without
a real bib, a real parser, or a real snapshot.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import bib_write


def _bench(
    log: list[str],
    *,
    broken: bool = False,
    holds: tuple[str, ...] = ("K",),
) -> bib_write.Bench:
    """Return a Bench that records what it was asked, in order."""

    def snapshot(what: str, targets: list[Path]) -> None:
        del targets
        log.append(f"snapshot:{what}")

    def roundtrip(target: Path) -> list[tuple[str, str, str]]:
        log.append(f"roundtrip:{target.read_text(encoding='utf-8')}")
        return [("quoted", "field", "detail")] if broken else []

    def read_back(target: Path) -> dict[str, object]:
        del target
        log.append("read_back")
        return dict.fromkeys(holds, "")

    return bib_write.Bench(snapshot=snapshot, roundtrip=roundtrip, read_back=read_back)


def _edit(target: Path, *, new: str = "after", key: str | None = None) -> bib_write.Edit:
    """Return an edit against `target`, whose current text is the `old` side."""
    return bib_write.Edit(
        verb="--add",
        label="K",
        target=target,
        old=target.read_text(encoding="utf-8"),
        new=new,
        expect_key=key,
    )


def _cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def fresh(text: str = "before") -> Path:
        target = tmp / f"bib{len(out)}.bib"
        target.write_text(text, encoding="utf-8")
        return target

    # ── the dry run writes NOTHING, and says so ──────────────────────────────
    # ⚑ THE PREVIEW IS THE ABSENCE OF `--apply`, so this is the default path and the one a
    # careless caller takes. A dry run that wrote would be the worst defect in the file.
    target = fresh()
    log: list[str] = []
    got = bib_write.apply_write(_edit(target), _bench(log), applying=False)
    check(
        "a dry run leaves the file untouched", passed=target.read_text(encoding="utf-8") == "before"
    )
    check("and arms no snapshot and runs no probe", passed=log == [])
    check("and exits OK", passed=got.code == bib_write.OK)
    check(
        "and says how to make it write",
        passed=any(bib_write.APPLY_FLAG in line for line in got.lines),
    )
    check("and still shows the diff", passed=any(line.startswith("  +") for line in got.lines))

    # ── applying writes, in the right ORDER ──────────────────────────────────
    # ⚑⚑ SNAPSHOT BEFORE WRITE, PROBE AFTER. The roundtrip fake records the file's CONTENT when
    # called, so the log proves the probe saw the NEW bytes rather than asserting it.
    target = fresh()
    log = []
    got = bib_write.apply_write(_edit(target, key="K"), _bench(log), applying=True)
    check("applying writes the new text", passed=target.read_text(encoding="utf-8") == "after")
    check("the snapshot is armed before the write", passed=log[0].startswith("snapshot:"))
    check("and the round-trip probe saw the NEW bytes", passed="roundtrip:after" in log)
    check(
        "the read-back runs after the round-trip",
        passed=log.index("read_back") > log.index("roundtrip:after"),
    )
    check("a good write exits OK", passed=got.code == bib_write.OK)

    # ── a broken round-trip reports BROKEN and names the recovery ────────────
    # ⚑ THE FILE IS ALREADY WRITTEN AT THIS POINT, which is why the code is BROKEN and not
    # REFUSED: the caller needs a repair, not a corrected command line.
    target = fresh()
    log = []
    got = bib_write.apply_write(_edit(target), _bench(log, broken=True), applying=True)
    check("a broken round-trip exits BROKEN", passed=got.code == bib_write.BROKEN)
    check("and that is distinct from a refusal", passed=bib_write.BROKEN != bib_write.REFUSED)
    check("and the outcome reports the file changed", passed=got.wrote)
    check(
        "and names the recovery command",
        passed=any(bib_write.RECOVER in line for line in got.lines),
    )
    check("and shows which construct was lost", passed=any("quoted" in line for line in got.lines))

    # ── THE DRIFT THE ORIGIN CARRIES: the read-back arm, for ANY verb ────────
    # ⚑⚑⚑ THIS IS THE CASE THE EXTRACTION EXISTS FOR. A file that round-trips cleanly but does
    # not hold the key is exactly the `--set` failure that motivated the arm — and in the origin
    # `--set` never got it. Here it fires for whichever verb names a key.
    target = fresh()
    log = []
    got = bib_write.apply_write(
        bib_write.Edit(
            verb="--set",
            label="K.claim",
            target=target,
            old="before",
            new="after",
            expect_key="MISSING",
        ),
        _bench(log),
        applying=True,
    )
    check("a clean round-trip that LOSES the key still fails", passed=got.code == bib_write.BROKEN)
    check("and the arm is not spelled per-verb", passed=any("--set" in line for line in got.lines))
    check(
        "and it names the key that did not read back",
        passed=any("MISSING" in line for line in got.lines),
    )

    # ⚑ AND A VERB THAT NAMES NO KEY IS NOT FAILED BY THE ARM — an edit to an existing entry
    # declares by omission that no new key should appear.
    target = fresh()
    got = bib_write.apply_write(_edit(target), _bench([]), applying=True)
    check("a verb naming no key passes without a read-back match", passed=got.code == bib_write.OK)

    # ── a no-op is reported, never written ───────────────────────────────────
    # ⚑ WRITING AN IDENTICAL FILE WOULD ARM A SNAPSHOT FOR NOTHING and tell the author their
    # edit landed when there was nothing to land.
    target = fresh()
    log = []
    got = bib_write.apply_write(_edit(target, new="before"), _bench(log), applying=True)
    check("an unchanged render writes nothing", passed=log == [])
    check("and exits OK rather than failing", passed=got.code == bib_write.OK)
    check(
        "and says there was nothing to write",
        passed=any("nothing to write" in line for line in got.lines),
    )

    # ── the diff is the origin's shape ───────────────────────────────────────
    lines = bib_write.diff_lines("a\nb", "a\nc")
    check("the diff is indented two spaces", passed=all(line.startswith("  ") for line in lines))
    check(
        "and carries both sides",
        passed=any("-b" in line for line in lines) and any("+c" in line for line in lines),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _cases(Path(tmp))
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-write selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
