"""Eliza.Manifold — Coxeter A₃ system on 24 chambers.

The chamber-step is a StatefulTransducer Gen Chamber Chamber: given a
current chamber and a generator, produce the new chamber. The action is
the standard A₃ Coxeter presentation:

  * s₁ swaps positions 0,1 of the chamber tuple.
  * s₂ swaps positions 1,2.
  * s₃ swaps positions 2,3.

Coxeter relations are postulated in the Agda; here they hold by
construction (each generator is involutive as a swap).

The module also builds the Cayley graph and its Laplacian eigendecomp.
These are consumed by Holonomy; nothing else uses them.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from eliza.alphabets import (
    Chamber,
    Gen,
    GENERATORS,
    ORIGIN,
    W0,
)


def _swap(state: Chamber, i: int, j: int) -> Chamber:
    lst = list(state)
    lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)  # type: ignore[return-value]


def apply(g: Gen, x: Chamber) -> Chamber:
    """The ParamEndomap. Coxeter A₃ action."""
    if g is Gen.s1:
        return _swap(x, 0, 1)
    if g is Gen.s2:
        return _swap(x, 1, 2)
    if g is Gen.s3:
        return _swap(x, 2, 3)
    raise ValueError(f"unknown generator: {g!r}")


class Manifold:
    """The 24-chamber S₄ Cayley graph with shortlex words and Laplacian.

    Exposes:
      - nodes:           ordered list of 24 chambers.
      - shortlex_word:   chamber → list[Gen] (the geodesic from origin).
      - fiedler_value:   chamber → float (sign-anchored so origin ≤ 0).
      - turbulence_value: chamber → float (mode-2 of Laplacian).
      - bruhat_distance: chamber → int (word length).
      - neighbours:      chamber → triple (s1·x, s2·x, s3·x).

    All other modules query these via methods; they do not access the
    networkx graph or numpy arrays directly.
    """

    def __init__(self) -> None:
        self._graph = nx.Graph()
        self._build_graph()
        self.nodes: List[Chamber] = list(self._enumerate_bfs())
        self._idx: Dict[Chamber, int] = {n: i for i, n in enumerate(self.nodes)}
        self._shortlex: Dict[Chamber, Tuple[Gen, ...]] = self._compute_shortlex()
        self._fiedler, self._turbulence = self._compute_harmonics()

    # --- Graph construction ------------------------------------------------

    def _build_graph(self) -> None:
        queue = [ORIGIN]
        self._graph.add_node(ORIGIN)
        seen = {ORIGIN}
        while queue:
            x = queue.pop(0)
            for g in GENERATORS:
                y = apply(g, x)
                if y not in seen:
                    self._graph.add_node(y)
                    seen.add(y)
                    queue.append(y)
                self._graph.add_edge(x, y, generator=g)

    def _enumerate_bfs(self) -> List[Chamber]:
        # Stable order via BFS from origin.
        seen: List[Chamber] = []
        stack = [ORIGIN]
        marked = {ORIGIN}
        while stack:
            x = stack.pop(0)
            seen.append(x)
            for g in GENERATORS:
                y = apply(g, x)
                if y not in marked:
                    marked.add(y)
                    stack.append(y)
        return seen

    # --- Shortlex geodesics ------------------------------------------------

    def _compute_shortlex(self) -> Dict[Chamber, Tuple[Gen, ...]]:
        out: Dict[Chamber, Tuple[Gen, ...]] = {ORIGIN: ()}
        queue: List[Tuple[Chamber, Tuple[Gen, ...]]] = [(ORIGIN, ())]
        while queue:
            x, path = queue.pop(0)
            for g in GENERATORS:
                y = apply(g, x)
                if y not in out:
                    new_path = path + (g,)
                    out[y] = new_path
                    queue.append((y, new_path))
        return out

    # --- Laplacian eigendecomposition --------------------------------------

    def _compute_harmonics(self) -> Tuple[np.ndarray, np.ndarray]:
        L = nx.laplacian_matrix(self._graph, nodelist=self.nodes).todense()
        evals, evecs = np.linalg.eigh(L)
        origin_idx = self._idx[ORIGIN]
        # Sign-anchor Fiedler so the origin sits at the negative end.
        fiedler = np.asarray(evecs[:, 1]).flatten()
        if fiedler[origin_idx] > 0:
            fiedler = -fiedler
        # Mode 2 is the next low-frequency global mode (mode 23 is
        # bipartite parity, redundant with word-length parity).
        turbulence = np.asarray(evecs[:, 2]).flatten()
        # Stash full eigenvectors for Holonomy if needed.
        self._eigenvalues = evals
        self._eigenvectors = np.asarray(evecs)
        self._eigenvectors[:, 1] = fiedler  # re-anchor in storage
        return fiedler, turbulence

    # --- Public query interface -------------------------------------------

    def node_index(self, x: Chamber) -> int:
        return self._idx[x]

    def shortlex_word(self, x: Chamber) -> Tuple[Gen, ...]:
        return self._shortlex[x]

    def bruhat_distance(self, x: Chamber) -> int:
        return len(self._shortlex[x])

    def fiedler_value(self, x: Chamber) -> float:
        return float(self._fiedler[self._idx[x]])

    def turbulence_value(self, x: Chamber) -> float:
        return float(self._turbulence[self._idx[x]])

    def neighbours(self, x: Chamber) -> Tuple[Chamber, Chamber, Chamber]:
        return (apply(Gen.s1, x), apply(Gen.s2, x), apply(Gen.s3, x))

    def macro_coord(self, x: Chamber) -> Tuple[float, float]:
        """The 2D (Fiedler, turbulence) coordinate used by Holonomy."""
        i = self._idx[x]
        return float(self._fiedler[i]), float(self._turbulence[i])

    @property
    def num_chambers(self) -> int:
        return len(self.nodes)

    # --- Convenience -------------------------------------------------------

    @staticmethod
    def origin() -> Chamber:
        return ORIGIN

    @staticmethod
    def w0() -> Chamber:
        return W0


def word_str(path: Tuple[Gen, ...]) -> str:
    """Render a shortlex word as `s1·s2·s3` (or `e` for the empty word)."""
    return "·".join(g.name for g in path) if path else "e"
