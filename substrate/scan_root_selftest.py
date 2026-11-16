# SPDX-License-Identifier: Apache-2.0
# Copyright substrate contributors
"""Pin the operand contract: a file narrows, a typo refuses, and neither widens to the tree."""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import scan_root


def _operand_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what `resolve` does with each shape of operand."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    f = tmp / "one.txt"
    f.write_text("x\n", encoding="utf-8")

    # ⚑⚑⚑ THE DEFECT THIS MODULE EXISTS FOR. The origin tested `isdir`, so a FILE operand was
    # discarded and the root fell back to `.` — a census over 14,402 files answering as though it
    # had been narrowed to one. Asserting the ROOT is not enough: a reader could return the right
    # root and still walk the tree, so `is_file` is asserted beside it.
    got = scan_root.resolve([str(f)])
    check(
        "a FILE operand resolves rather than being discarded",
        passed=isinstance(got, scan_root.Scan) and got.root == str(f),
    )
    check(
        "and it is marked as a file, not a tree",
        passed=isinstance(got, scan_root.Scan) and got.is_file,
    )

    got = scan_root.resolve([str(tmp)])
    check(
        "a DIRECTORY operand still resolves",
        passed=isinstance(got, scan_root.Scan) and got.root == str(tmp),
    )
    check("and is not marked as a file", passed=isinstance(got, scan_root.Scan) and not got.is_file)

    # ⚑ THE THIRD OUTCOME. A path-shaped operand naming nothing used to census the whole tree,
    # which is the same defect wearing a typo as its cause.
    typo = scan_root.resolve([str(tmp / "no" / "such")])
    check(
        "a path-shaped operand naming nothing REFUSES", passed=isinstance(typo, scan_root.Refusal)
    )
    check(
        "and the refusal says what it declined to do",
        passed=isinstance(typo, scan_root.Refusal) and "censusing the tree" in typo.message,
    )

    # ⚑ THE OTHER DIRECTION, or every case above passes against a resolver that refuses always.
    check(
        "no operand at all falls back to the default root",
        passed=isinstance(scan_root.resolve([]), scan_root.Scan),
    )
    check(
        "and a FLAG is not mistaken for a path",
        passed=isinstance(scan_root.resolve(["--where", "all"]), scan_root.Scan),
    )

    # ⚑ A BARE NON-PATH WORD IS NOT REFUSED. It may be another flag's operand, and refusing it
    # would break every caller passing one. Only path-SHAPED tokens are the subject here.
    check(
        "a bare non-path word is passed over, not refused",
        passed=isinstance(scan_root.resolve(["all"]), scan_root.Scan),
    )

    return out


def _files_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for whether the file list matches what the operand named."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    f = tmp / "one.txt"
    f.write_text("x\n", encoding="utf-8")
    (tmp / "two.txt").write_text("y\n", encoding="utf-8")

    one = scan_root.resolve([str(f)])
    tree = scan_root.resolve([str(tmp)])
    if not isinstance(one, scan_root.Scan) or not isinstance(tree, scan_root.Scan):
        check("the fixture resolves at all", passed=False)
        return out

    # ⚑⚑ `os.walk` ON A FILE YIELDS NOTHING, so a reader that only walks reports an EMPTY census
    # for a file the caller named — the same wrong answer as the widening, from the other side.
    check("a file root yields exactly itself", passed=scan_root.files(one) == [str(f)])

    walked = scan_root.files(tree)
    check("a directory root yields more than one file", passed=len(walked) > 1)
    check("and the named file is among them", passed=str(f) in walked)

    # ⚑ THE SUFFIX FILTER APPLIES TO A WALK AND NOT TO A NAMED FILE, because naming a path IS the
    # selection the filter exists to make. Both halves are cased, since a filter firing on neither
    # and one firing on both are indistinguishable from a single assertion.
    check(
        "a walk honours the suffix filter",
        passed=scan_root.files(tree, skip_suffix=frozenset({".txt"})) == [],
    )
    check(
        "but an explicitly named file is exempt from it",
        passed=scan_root.files(one, skip_suffix=frozenset({".txt"})) == [str(f)],
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        cases = _operand_cases(tmp) + _files_cases(tmp)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"scan-root selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
