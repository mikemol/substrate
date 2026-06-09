"""S₄ permutohedron core — Cayley graph + Laplacian spectrum + geometry.

Lifts the construction from `SpectralManifold` in scratch/eliza/13.py (BFS
Cayley build over the adjacent transpositions s₁,s₂,s₃ → networkx Laplacian →
np.linalg.eigh), and adds the true permutohedral embedding: each permutation of
(1,2,3,4), as a 4-vector, projected orthogonally onto the 3-space orthogonal to
(1,1,1,1). That projection is the truncated octahedron.

Shared by permutohedron_s4.py and permutohedron_spectrum.py so the graph and
its spectrum are built once.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

GENERATORS = ["s1", "s2", "s3"]
ORIGIN = (1, 2, 3, 4)

# Orthonormal basis of the sum-zero 3-space in R⁴ (orthogonal to (1,1,1,1)).
_B = np.array([
    [1, -1, 0, 0],
    [1, 1, -2, 0],
    [1, 1, 1, -3],
], dtype=float)
_B /= np.linalg.norm(_B, axis=1, keepdims=True)


def _swap(state, i, j):
    lst = list(state)
    lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)


def apply_reflection(state, gen):
    if gen == "s1":
        return _swap(state, 0, 1)
    if gen == "s2":
        return _swap(state, 1, 2)
    if gen == "s3":
        return _swap(state, 2, 3)
    return state


class Permutohedron:
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes_list: list[tuple] = []
        self._build()
        self._geodesics()
        self._spectrum()
        self._embed()

    def _build(self):
        queue = [ORIGIN]
        self.graph.add_node(ORIGIN)
        while queue:
            cur = queue.pop(0)
            if cur not in self.nodes_list:
                self.nodes_list.append(cur)
            for gen in GENERATORS:
                nxt = apply_reflection(cur, gen)
                if nxt not in self.graph:
                    self.graph.add_node(nxt)
                    queue.append(nxt)
                self.graph.add_edge(cur, nxt, generator=gen)

    def _geodesics(self):
        # Shortlex distance from the identity = Coxeter (Bruhat) length.
        self.dist = {ORIGIN: 0}
        queue = [ORIGIN]
        while queue:
            cur = queue.pop(0)
            for gen in GENERATORS:
                nxt = apply_reflection(cur, gen)
                if nxt not in self.dist:
                    self.dist[nxt] = self.dist[cur] + 1
                    queue.append(nxt)

    def _spectrum(self):
        L = nx.laplacian_matrix(self.graph, nodelist=self.nodes_list).todense()
        self.laplacian = np.asarray(L, dtype=float)
        self.eigenvalues, self.eigenvectors = np.linalg.eigh(self.laplacian)
        # Sign-fix the Fiedler vector for reproducibility.
        oi = self.nodes_list.index(ORIGIN)
        if self.eigenvectors[oi, 1] > 0:
            self.eigenvectors[:, 1] *= -1
        self.fiedler = self.eigenvectors[:, 1]
        self.turbulence = self.eigenvectors[:, 2]

    def _embed(self):
        # Permutation (a,b,c,d) → 4-vector centred at the mean, then projected
        # onto the orthonormal sum-zero basis. Gives the permutohedron in R³.
        self.coords3 = {}
        for p in self.nodes_list:
            v = np.array(p, dtype=float) - 2.5
            self.coords3[p] = _B @ v

    def index(self, state):
        return self.nodes_list.index(state)
