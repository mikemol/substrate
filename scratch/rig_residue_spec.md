# ⟡rig-UP-residue — the counit-defect AS Wedge.rem (spec, 2026-07-11)

## Goal
Realize the residue (hypothesis − actual of ⊗ᶜ-step) as a PROPER OBJECT: an instance of
`Substrate.Algebra.Wedge.Wedge`, with `DivStr` manufactured from the rig's own ⊗ᶜ/⊕ᶜ, and the
coupling = the `(1,z)` identity corner. Work in the CANONICAL model (LehmerRig, C = LehmerPath,
⊗ᶜ=⊗ˢ, ⊕ᶜ=⊕, zeroᶜ=start, oneᶜ=X = start◂zero, fold idAlg = id).

## The object
`DivStr C = { z : C ; recon : C → C → C → C }`, `recon q b r = "q·b then r"`, `= is (quot=1, rem=z)`.
`Wedge D a b = { quot ; rem ; wedge-eq : a ≡ recon D quot b rem }`.  THE RESIDUE = `rem`.
Rig division on the flattened carrier Σ ℕ LehmerPath:
  z         = (0 , start)
  recon (gq,q) (gb,b) (gr,r) = (gq * gb + gr , (q ⊗ˢ b) ⊕ r)        -- (q·b) then r, in the rig
The `=`-corner is quot=(1,X), rem=(0,start): recon (1,X) (gb,b) (0,start) should reconstruct (gb,b).

## Steps (incremental; --safe --without-K, zero postulates; green-or-honest)
S1  divᴸ : DivStr (Σ ℕ LehmerPath)   as above. (New; the rig recon, NOT flatten's power-recon.)
S2  ⊗ˢ-unit-left : subst LehmerPath (*-identityˡ n) (X ⊗ˢ l) ≡ l
      (X ⊗ˢ l = replayOffset zero l (start ⊗ˢ l) = replay-aux zero n l start; offsetDigit zero n q
       = q up to the 0·n=0 grade / fromℕ<∘toℕ roundtrip — prove replay-aux zero n l start ≡ l by
       induction on l, discharging offsetDigit zero n q ≡ q). THE fiddly lemma.
S3  corner-eq : recon divᴸ (1 , X) (n , b) (0 , start) ≡ (n , b)        -- the (1,z) corner = b
      = Σ-eq of grades (1*n+0 = n) and values ((X ⊗ˢ b) ⊕ start ≡ b), the latter via S2
      (X ⊗ˢ b ≡ b up to 1*n=n) + ⊕-unit-right (OrientationSumLaws: subst … (l ⊕ 0#) ≡ l, n+0=n).
      This IS "= is the (1,z) corner", made concrete for the orientation rig; rem = z = no residue.
S4  couple-is-corner (the payoff): the canonical ⊗ᶜ-step obligation at (l₂,y) — i.e.
      replay-aux p n l₂ (x ⊗ˢ y) ≡ replay-aux p n y (x ⊗ˢ y) for all x,p — holds  ⟺  l₂ ≡ y
      (⟸ cong; ⟹ peel the appended offsetDigits, offsetDigit injective in the digit ⇒ digit-words
       equal ⇒ l₂ ≡ y). Then l₂ ≡ y ⟺ decode l₂ ≡ decode y (decode-injective committed + cong decode).
      CONCLUSION: coupled ⟺ y sits at the (1,z) corner over l₂ ⟺ decode-traces coincide ⟺ rem ≡ z.

## Reuse
Substrate.Algebra.Wedge (DivStr, Wedge, recon), Algebra.Wedge.Product (flatten — the PATTERN, and
gpower if useful), OrientationProductStructural (_⊗ˢ_, replay-aux, replayOffset, offsetDigit),
OrientationSum (_⊕_; ⊕-unit-left refl), OrientationSumLaws (⊕-unit-right, ◂-subst), OrientationFixed
Point (decode-injective), Nat.Properties.Mul (*-identityˡ), Foundation.Fin (fromℕ<, toℕ), Product (Σ,_,_).
Prioritize S1+S3 (the object + the corner). S2 is the fiddly enabler; S4 is the payoff.
