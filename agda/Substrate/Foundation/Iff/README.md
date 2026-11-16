# `Iff` — logical equivalence of types, at Set₀

⟡rc-het-iff (⟡set1-rerank2). A proof that two TYPES are propositionally EQUAL
(`A ≡ B` with `A B : Set`) intrinsically inhabits **Set₁** — `_≡_ {Set}` lands
there. Where the two sides are only ever used up to a ROUND-TRIP and never
transported along, the honest statement is logical equivalence

    A ⇔ B = (A → B) × (B → A)

which lives in Set₀. Every ex-`≡`-of-Sets in the substrate was a `refl` (the two
sides were definitionally equal), so each converts by `⇔-refl`.
