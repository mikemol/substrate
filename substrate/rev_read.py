# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a path as it was at a git revision, three-valued, without touching the working tree.

⚑⚑⚑ REACHING FOR `git checkout <rev> -- <path>` TO *LOOK* AT HISTORY DESTROYS THE WORKING COPY.
That is the incident this seam exists for: it was used repeatedly to recover a file, including on
files carrying edits worth keeping, and it happened to be harmless only because those edits were
the damage. Reading the blob leaves the tree untouched, so historical text can be diffed, spliced,
or consulted for ONE line without committing to a wholesale revert.

⚑⚑⚑ THE EAGER RESOLVE IS THE WHOLE DESIGN, NOT AN OPTIMISATION. `pygit2` raises `KeyError` for a
bad revision AND for a missing path. If the revision were resolved lazily inside the path lookup,
one `except KeyError` would have to serve both, and **a typo'd sha would report as ABSENT** — the
caller would be told a file is new when in fact the revision was wrong. Resolving FIRST means that
by the time a tree lookup runs the revision is known-good, so a `KeyError` there can only mean the
path, which is what makes ABSENT honest. **The split is in the ORDER, not in the exception types**,
and that is why it cannot be recovered by catching more precisely.

⚑⚑ SO A BAD REVISION IS `BROKEN`, NEVER `ABSENT`. The origin of this seam collapsed both into
`None` on a non-zero exit code, so a typo'd sha, a non-repository, an absent git and a genuinely
new file were one outcome. Two of those are defects and one is an ordinary state.

⚑⚑ THE ROOT IS AN ARGUMENT, REQUIRED, WITH NO FALLBACK — and that is a change from the origin,
deliberately. `Rev(rev, root=None)` there fell back to a module-level `_REPO` derived from
`__file__`, which is the ownership claim this arc is retiring: it makes a packaged module assert
which tree it is reading, and a consumer running from another checkout gets the WRONG tree while
every path still resolves. A caller that must name the tree cannot get it silently wrong.

⚑ THERE IS DELIBERATELY NO WRITE. Git history is not writable, and an API accepting a revision on
a write would be A LIE IN THE TYPE — it would typecheck, read as supported, and either silently
write to the working tree or rewrite history. The absence is the design; `file_write` owns writing,
and it writes to the working tree only.

⚑ AND THE PATH IS WALKED AS A TREE OBJECT, not string-joined onto a filesystem path. There is no
path to escape from, so traversal is structurally absent rather than defended against.

⚑⚑⚑ THE TYPED `pygit2` API IS USED AS TYPED, AND THE PER-FILE GATE FOUND A REAL GAP RATHER THAN A
STYLE ONE. A first cut peeled with a bare integer type code and tested `entry.type_str != "blob"`.
Both were refused: `peel` is overloaded on the literal type, and a STRING comparison does not
narrow the `Tree | Blob` union, so reading `.data` afterwards was unproven — exactly the case where
a tree entry that is a subdirectory would reach a blob-only attribute. `isinstance(entry, Blob)` is
both the narrowing and the honest predicate, and the union is what made the omission visible.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from substrate.file_read import Presence, Result

if TYPE_CHECKING:
    import pygit2

#: The revision every caller means when it does not say. `HEAD` is the committed state of the
#: current branch — the thing a working-tree read is most often being compared against.
DEFAULT_REV = "HEAD"


class Rev:
    """A git revision — `HEAD`, a sha, `HEAD~3`. READ-ONLY BY CONSTRUCTION.

    ⚑ THE RESOLUTION IS CACHED ON THE INSTANCE, so a caller reading many paths at one revision
    pays for the revparse once. The cache holds the ERROR too: a bad revision must report the same
    way on the hundredth path as on the first, and re-attempting would make the failure depend on
    which path happened to be asked for.
    """

    def __init__(self, root: Path | str, rev: str = DEFAULT_REV) -> None:
        """Name a revision within the repository at `root`.

        ⚑ `root` IS FIRST AND REQUIRED, while `rev` has a default. That ordering is the point: the
        tree is the fact a caller must supply and the revision is the one with an obvious default,
        so the signature refuses the borrowed-root shape rather than merely discouraging it.
        """
        self.root = Path(root).absolute()
        self.rev = rev
        self._tree: pygit2.Tree | None = None
        self._err: Exception | None = None
        self._done = False

    def __repr__(self) -> str:
        """Return the constructor-shaped form, naming the tree as well as the revision."""
        return f"Rev({str(self.root)!r}, {self.rev!r})"

    def __str__(self) -> str:
        """Return the human name of this source, as it should appear in a report."""
        return f"rev {self.rev}"

    def resolve(self) -> tuple[pygit2.Tree | None, Exception | None]:
        """Return `(tree, error)` — resolving the revision EAGERLY, once, and caching it.

        ⚑ EVERY FAILURE ARM IS A DISTINCT MESSAGE naming what it could not do. The origin returned
        one collapsed absence for all of them, so a caller could not tell a wrong sha from a wrong
        directory, and both read as "the file is new".
        """
        if self._done:
            return self._tree, self._err
        self._done = True
        self._tree, self._err = self._resolve_now()
        return self._tree, self._err

    def _resolve_now(self) -> tuple[pygit2.Tree | None, Exception | None]:
        """Perform the resolution, uncached — the body `resolve` memoises."""
        try:
            import pygit2  # noqa: PLC0415 - the dependency this one method needs, named at its use
        except ImportError as exc:
            return None, RuntimeError(
                f"pygit2 is required to read from a revision ({exc}). "
                f"Install with: uv pip install pygit2"
            )
        try:
            repo = pygit2.Repository(str(self.root))
        except Exception as exc:  # noqa: BLE001 - GitError is unexported; any failure means "not a repo"
            return None, RuntimeError(f"not a git repository at {self.root}: {exc}")
        try:
            obj = repo.revparse_single(self.rev)
        except KeyError as exc:
            # ⚑ A BAD REVISION IS *BROKEN*, NOT ABSENT — the arm the origin's callers collapsed.
            return None, ValueError(f"bad revision {self.rev!r} in {self.root}: {exc}")
        except Exception as exc:  # noqa: BLE001 - revparse raises several unexported types
            return None, RuntimeError(f"cannot resolve {self.rev!r}: {exc}")
        try:
            return obj.peel(pygit2.Tree), None
        except Exception as exc:  # noqa: BLE001 - peel raises unexported types for a non-tree
            return None, ValueError(f"revision {self.rev!r} does not name a tree: {exc}")


def relpath(path: Path | str, root: Path | str) -> str:
    """Return `path` as a repository-relative, forward-slashed key — how a git tree is indexed.

    ⚑ A GIT TREE IS KEYED BY POSIX SPELLING regardless of platform, so this normalises rather than
    handing the OS separator to a lookup that would report a present file as absent.
    """
    where = Path(path)
    rel = where.relative_to(Path(root).absolute()) if where.is_absolute() else where
    return str(PurePosixPath(rel))


def read(path: Path | str, source: Rev) -> Result:
    """Return the three-valued read of `path` at `source`, never raising for absence or breakage.

    ⚑ THE `KeyError` HERE CAN ONLY MEAN THE PATH, because `resolve` has already established the
    revision. That is the property the eager resolve buys, and it is the reason this arm may
    honestly report ABSENT.
    """
    import pygit2  # noqa: PLC0415 - needed to narrow a tree entry; absence is reported by resolve

    tree, err = source.resolve()
    if tree is None:
        # ⚑ The revision itself is bad — BROKEN before any path lookup happens.
        reason = err if err is not None else RuntimeError(f"{source} did not resolve")
        return Result(Presence.BROKEN, Path(path), error=reason, source=source)
    rel = relpath(path, source.root)
    try:
        entry = tree[rel]
    except KeyError:
        # ⚑⚑⚑ THE ABSENT ARM CARRIES NO ERROR, AND THAT IS NOT AN OMISSION — it is what keeps this
        # reader's vocabulary the working-tree reader's. `Result.require` re-raises a stored error
        # FIRST and only synthesises `FileNotFoundError` when there is none, so storing the
        # `KeyError` here would hand a caller a raw git-shaped exception where a filesystem read
        # gives `FileNotFoundError` — and the source clause, which only the synthesised message
        # carries, would be lost with it.
        #
        # ⚑ MEASURED, NOT REASONED: the suite's `require()` arm was written expecting the shared
        # behaviour and FAILED with a bare `KeyError`, which is how the divergence surfaced. The
        # working-tree reader's own absent arm stores no error for exactly this reason.
        return Result(Presence.ABSENT, Path(path), source=source)
    if not isinstance(entry, pygit2.Blob):
        # ⚑ A DIRECTORY IS BROKEN, NOT ABSENT — the same distinction the working-tree reader draws
        # for `IsADirectoryError`, so a caller sees one vocabulary across both sources.
        broke = IsADirectoryError(f"{rel} is a {entry.type_str} at {source}")
        return Result(Presence.BROKEN, Path(path), error=broke, source=source)
    return Result(Presence.PRESENT, Path(path), data=entry.data, source=source)


def text(path: Path | str, source: Rev) -> str | None:
    """Return the decoded text at `source`, `None` when absent, RAISING when broken.

    ⚑⚑ THE ASYMMETRY IS THE SAME ONE `file_read.text` HOLDS, and it must be: a caller comparing a
    revision against the working tree writes one branch for "not there" and must not have a bad
    revision arrive down it. A file absent at a commit is an ordinary fact an ordinary branch
    handles; an unresolvable revision is a defect in the caller's own argument.
    """
    got = read(path, source)
    if got.presence is Presence.BROKEN:
        got.require()
    return got.text() if got else None
