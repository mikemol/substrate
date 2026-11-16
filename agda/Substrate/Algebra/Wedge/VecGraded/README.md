# `VecGraded` — `Vec A` founded as a graded wedge-carrier

A silo top (the shred's UNFOUNDED `Vec`, adjacent to ℕ) brought into the wedge
architecture. The grade is the LENGTH; the residue shed at each step is the HEAD:

    C n     = Vec A n
    R n     = A                 the head to shed / prepend
    recon n = a ∷_              cons the head onto the grade-n tail

Building a vector = consing heads = the graded free construction — exactly the
shape of `WitnessTower.Wedge.Graded.tower-graded` (Perm / insert-at), but with a
CONSTANT remainder type. Unconsing is the graded wedge: a `(suc n)`-vector
decomposes against its tail, shedding its head as the residue.

`recon` IS cons definitionally (`ReconIsCons`), so the whole cluster is `refl` —
no certificate is carried, and `VecUncons` is total.
