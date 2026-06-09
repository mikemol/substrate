"""Shared Fano-plane / octonion data (agda/Substrate/Algebra/F2/FanoPlane.agda).

The 7 points (nonzero vectors of F₂³), the 7 lines, the Singer 7-cycle, and the
octonion multiplication built from the oriented Fano triples. Used by the 2D
fano_plane / octonion_fano figures and their 3D siblings, so the data lives in
exactly one place.
"""

import numpy as np

# Points named by their F₂³ bit-pattern (index in 1..7 = the integer value).
POINT_NAMES = ["e₁", "e₂", "e₃", "e₁₂", "e₁₃", "e₂₃", "e₁₂₃"]

# Each point as its F₂³ vector (basis order e₁,e₂,e₃).
POINT_VEC = {
    "e₁":   (1, 0, 0),
    "e₂":   (0, 1, 0),
    "e₃":   (0, 0, 1),
    "e₁₂":  (1, 1, 0),
    "e₁₃":  (1, 0, 1),
    "e₂₃":  (0, 1, 1),
    "e₁₂₃": (1, 1, 1),
}

# The 7 lines as point triples (FanoPlane.agda `line-points`).
LINES = {
    "L₁₂":   ("e₁", "e₂", "e₁₂"),
    "L₁₃":   ("e₁", "e₃", "e₁₃"),
    "L₂₃":   ("e₂", "e₃", "e₂₃"),
    "L₁-₂₃": ("e₁", "e₂₃", "e₁₂₃"),
    "L₂-₁₃": ("e₂", "e₁₃", "e₁₂₃"),
    "L₃-₁₂": ("e₃", "e₁₂", "e₁₂₃"),
    "L₁₂-₁₃": ("e₁₂", "e₁₃", "e₂₃"),
}

# Singer 7-cycle on points (FanoPlane.agda `singer`).
SINGER = {
    "e₁": "e₂", "e₂": "e₃", "e₃": "e₁₂", "e₁₂": "e₂₃",
    "e₂₃": "e₁₂₃", "e₁₂₃": "e₁₃", "e₁₃": "e₁",
}

# Oriented octonion triples (a,b,c): eₐe_b = e_c cyclically.
OCTONION_TRIPLES = [(1, 2, 3), (1, 4, 5), (1, 7, 6),
                    (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)]


def octonion_table():
    """Signed 8×8 multiplication table over e₀=1, e₁…e₇.

    Returns (sign, idx): product eᵢ·eⱼ = sign[i,j] · e_{idx[i,j]}.
    """
    sign = np.zeros((8, 8), dtype=int)
    idx = np.zeros((8, 8), dtype=int)
    for i in range(8):
        sign[0][i] = 1; idx[0][i] = i
        sign[i][0] = 1; idx[i][0] = i
    for i in range(1, 8):
        sign[i][i] = -1; idx[i][i] = 0
    for a, b, c in OCTONION_TRIPLES:
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            sign[x][y] = 1; idx[x][y] = z
            sign[y][x] = -1; idx[y][x] = z
    return sign, idx
